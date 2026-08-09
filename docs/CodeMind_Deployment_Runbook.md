# CodeMind MVP — Deployment Runbook

**Cập nhật:** 09/08/2026  
**Phạm vi:** hướng dẫn triển khai có kiểm soát cho backend Docker Compose và PostgreSQL. Tài liệu tách rõ những gì repository hiện chạy được với những gì phải hoàn thành trước khi public release.

## 1. Cảnh báo trạng thái hiện tại

`backend/docker-compose.yml` hiện khởi động được hai service `api` và `db`, nhưng API được tạo với `PersistentRepository` khi `REPOSITORY_MODE=file`. `DATABASE_URL` có trong cấu hình nhưng **chưa được runtime sử dụng để lưu session/progress/evidence**; migration SQL và PostgreSQL container vì vậy không phải bằng chứng persistence PostgreSQL của MVP.

Ngoài ra, profile compose hiện đặt `CODE_RUNNER_MODE=simulated`, `AI_MODE=canned`, password database mẫu trong file và publish cổng DB. Nó phù hợp cho local/container smoke, **không được deploy nguyên trạng ra Internet**. Chưa có frontend Dockerfile/compose service, migration runner, PostgreSQL repository adapter, production auth, runner cô lập hoặc CI/CD deploy job.

Mọi bước “production/staging” bên dưới là gate phải đạt hoặc template vận hành sau khi các thiếu hụt trên được xử lý; không tự suy diễn rằng việc chạy `docker compose up` đã tạo môi trường production.

## 2. Phân vai và nguyên tắc an toàn

| Vai trò | Trách nhiệm trước khi release |
|---|---|
| Release owner | Phê duyệt phiên bản, URL, rollback decision và bằng chứng incognito |
| Backend/Data owner | Migration, seed, integrity dữ liệu, backup/restore rehearsal |
| DevOps/Security owner | secret store, TLS/domain, network, logs/monitoring, least privilege |
| QA owner | smoke, E2E, RBAC/consent, recovery và test report |

- Không commit `.env`, secret, password demo, backup chứa PII hoặc state file thật.
- Không dùng mật khẩu `codemind` đang hard-code trong compose cho staging/production.
- Không publish `5432` ra Internet. API/frontend là surface duy nhất được expose qua reverse proxy HTTPS sau khi được harden.
- Không chạy migration/restore trên dữ liệu thật nếu chưa có cửa sổ bảo trì, backup đã kiểm chứng và người phê duyệt.
- Không dùng `docker compose down -v` trong sự cố; lệnh đó xóa volume và có thể làm mất dữ liệu.

## 3. Biến môi trường và trạng thái hỗ trợ

`backend/.env.example` được Pydantic đọc khi chạy backend trực tiếp. Compose hiện gán environment trực tiếp trong YAML; một file `.env` cạnh compose **chưa tự thay thế** các giá trị hard-code nếu YAML không dùng `${...}`. Vì vậy cần sửa config/deployment manifest trước release, thay vì chỉ tạo `.env` và giả định nó có hiệu lực.

| Biến | Giá trị local hiện có | Yêu cầu trước staging/production |
|---|---|---|
| `APP_ENV` | `local` | đặt tên môi trường thật; production tắt docs debug theo code hiện có |
| `APP_NAME`, `API_PREFIX` | `CodeMind API`, `/v1` | giữ versioned prefix, không thay đổi contract không có review |
| `DATABASE_URL` | URL PostgreSQL local | dùng secret managed; chỉ gọi PostgreSQL runtime khi repository adapter đã được nối và test |
| `AUTH_MODE` | `demo` | thay bằng cơ chế auth/revocation đã review; account judge không dùng token `demo:<id>` |
| `CORS_ORIGINS` | `http://localhost:5173` | chỉ HTTPS frontend origin thực, ngăn cách bằng dấu phẩy; không wildcard credential |
| `REPOSITORY_MODE` | `file` | chỉ chuyển sang `postgres` sau khi code có adapter, migration và integration test; hiện giá trị khác `file` sẽ rơi về in-memory |
| `STATE_FILE_PATH` | `.data/codemind_state.json` | chỉ dùng local/single-process; volume private và backup riêng nếu còn dùng |
| `CODE_RUNNER_MODE` | `simulated` | runner worker/container cô lập, chặn network, CPU/RAM/time/output limit và test bảo mật |
| `AI_MODE` | `canned` | provider adapter, secret management, timeout/retry, cost guard, citation/source policy |
| `AI_MAX_INTERACTIONS_PER_SESSION` | `3` | quota release được phê duyệt, telemetry redacted và fallback rõ ràng |

## 4. Container smoke hiện có (local-only)

Chạy từ thư mục `backend`:

```powershell
docker compose config
docker compose up --build -d
docker compose ps
Invoke-RestMethod -Uri 'http://127.0.0.1:8765/health/live'
Invoke-RestMethod -Uri 'http://127.0.0.1:8765/health/ready'
docker compose logs --tail=100 api
```

Kết quả `ready` hiện phải tự mô tả `repository: file` và `runner: simulated`. Nếu response nói `ok` thì đó chỉ xác nhận process/container healthy, **không** chứng minh PostgreSQL persistence hay isolated code execution. Khi kết thúc smoke mà vẫn muốn giữ dữ liệu, dùng:

```powershell
docker compose stop
```

Không thêm `-v` trừ khi đã sao lưu và chủ sở hữu phê duyệt việc hủy môi trường.

## 5. Migration và seed: ranh giới hiện tại và gate bắt buộc

### 5.1 Migration SQL có trong repository

`backend/migrations/001_initial.sql` là baseline PostgreSQL 16. Nó có thể được apply thủ công vào container DB để kiểm tra cú pháp/schema, nhưng ứng dụng hiện **không ghi/đọc** các bảng này. Chỉ chạy trên DB rỗng, disposable và lưu lại output:

```powershell
Set-Location backend
Get-Content .\migrations\001_initial.sql -Raw |
  docker compose exec -T db sh -lc 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"'

docker compose exec -T db sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dt"'
```

Đây không phải là “migration chạy khi deploy”. Trước staging/production cần bổ sung và xác nhận tất cả điều kiện sau:

- [ ] Repository PostgreSQL thật, nhất quán với domain/API và được chọn khi `REPOSITORY_MODE=postgres`.
- [ ] Công cụ migration versioned chạy một lần, có bảng version, fail-fast và không race khi nhiều replica khởi động.
- [ ] Migration rollback/forward có test trên bản sao dữ liệu; schema/UUID/data dictionary đồng bộ.
- [ ] Health readiness kiểm tra kết nối DB thực, không chỉ echo cấu hình.
- [ ] Seed command idempotent dành riêng cho môi trường demo; không tự seed vào production có người dùng.

### 5.2 Seed hiện có

`app/infrastructure/seed.py` chỉ seed vào `PersistentRepository`/in-memory khi app local khởi tạo. Hiện **không có** lệnh seed vào PostgreSQL và không có mật khẩu production. Không ghi trong proposal hay README rằng demo accounts PostgreSQL đã được seed cho tới khi đã có command/output/evidence tương ứng.

Một quy trình seed hợp lệ sau khi adapter được hoàn thiện phải: chạy migration trước; chạy seed idempotent; tạo account judge riêng qua secret manager; xác minh role/RBAC; ghi fixture/version; và có reset không đụng dữ liệu người dùng thật.

## 6. Kiến trúc deploy mục tiêu và pre-flight bắt buộc

Trước khi mở public URL, manifest triển khai phải tách ít nhất: frontend static host, API, PostgreSQL private network, runner worker tách process/network, AI gateway và monitoring. Dùng image tag/digest bất biến; không build từ working tree trực tiếp trên production.

Pre-flight release:

- [ ] Secret/config nằm trong secret manager hoặc biến môi trường của platform, không có trong Git/compose mẫu.
- [ ] TLS domain, HTTPS redirect, HSTS/CORS, reverse-proxy limits và access log được kiểm tra.
- [ ] DB không có published port; volume persistent và encryption/backup policy được xác nhận.
- [ ] Migration + seed demo có log, checksum/version và người phê duyệt.
- [ ] `/health/live` và readiness DB thật; health endpoint public phải được giới hạn nếu cần.
- [ ] Smoke và E2E từ cửa sổ ẩn danh đạt theo `CodeMind_MVP_Experience_Guide.md`.
- [ ] Runner/AI degradation không làm API treo; recovery, timeout, quota và error UI đã test.
- [ ] Có release ID, image digest, owner, rollback plan và cửa sổ bảo trì.

## 7. Backup và restore rehearsal

### 7.1 File-state local hiện tại

Khi chạy compose hiện tại, state file host nằm tại `backend/.data/codemind_state.json` qua volume mount. Nó có thể chứa tiến trình/evidence demo. Sao lưu khi API đã dừng để tránh copy giữa lúc ghi:

```powershell
Set-Location backend
docker compose stop api
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
New-Item -ItemType Directory -Force -Path .\backups | Out-Null
Copy-Item .\.data\codemind_state.json (".\backups\codemind-state-" + $stamp + '.json')
Get-FileHash (".\backups\codemind-state-" + $stamp + '.json') -Algorithm SHA256
docker compose start api
```

Giữ file backup ngoài Git và hạn chế truy cập. Restore local chỉ sau khi đã dừng API, sao lưu state đang có và được owner phê duyệt; sau đó khởi động API, gọi health, đăng nhập fixture và xác minh session/evidence dự kiến. Không dùng thủ tục này để tuyên bố đã có disaster recovery production.

### 7.2 PostgreSQL target runbook (chỉ sau khi DB là runtime thật)

DB container hiện có chưa chứa runtime application state; backup dưới đây là **mẫu target**, chỉ áp dụng sau khi adapter PostgreSQL đã được release và pre-flight ở phần 6 đạt.

```powershell
Set-Location backend
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
New-Item -ItemType Directory -Force -Path .\backups | Out-Null
docker compose exec -T db sh -lc 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom' > (".\backups\codemind-pg-" + $stamp + '.dump')
Get-FileHash (".\backups\codemind-pg-" + $stamp + '.dump') -Algorithm SHA256
```

Restore vào **môi trường disposable/staging trước**, dưới cửa sổ bảo trì và sau khi copy backup hiện tại:

```powershell
Set-Location backend
docker compose stop api
$restoreFile = '.\backups\<ten-file-dump-da-xac-nhan>.dump'
Get-Content -LiteralPath $restoreFile -AsByteStream -ReadCount 0 |
  docker compose exec -T db sh -lc 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner'
docker compose start api
```

Ngay sau restore: chạy migration version check, health/readiness DB, demo login, một session đọc lại và một test RBAC. Lưu RTO/RPO đo được, hash backup, phiên bản source/image và người xác nhận. Nếu bất kỳ bước nào fail, không mở public release.

## 8. Rollback

Hiện repository chưa có image registry/tag bất biến hay deployment workflow, nên chưa có rollback production có thể xác nhận. Đừng gọi thao tác build lại từ working tree là rollback.

Quy trình target sau khi có release pipeline:

1. Release owner quyết định rollback dựa trên lỗi/metric và đóng ghi dữ liệu hoặc bật maintenance mode.
2. Giữ nguyên DB volume; không chạy `down -v`.
3. Redeploy **image digest đã được kiểm thử trước đó** cùng manifest/version config tương ứng.
4. Chỉ restore DB khi migration mới gây incompatibility hoặc integrity fail; ưu tiên forward-fix khi an toàn.
5. Chạy health, smoke incognito, RBAC/consent và kiểm tra migration version trước mở lại traffic.
6. Ghi incident time, release IDs, quyết định, dữ liệu ảnh hưởng và follow-up vào release log.

## 9. CI/CD: ranh giới bằng chứng hiện có

Workflow `.github/workflows/ci.yml` hiện chạy khi push `main`/pull request và chỉ gồm:

- Backend: install, Ruff, compile, API contract checker, pytest.
- Frontend: `npm ci`, ESLint và production build.

CI hiện **không** build/push image, không chạy Docker Compose, migration, seed, browser E2E, security/dependency/secret scan, load test, backup/restore hoặc deploy. Vì vậy một CI xanh không phải bằng chứng staging/production.

Trước khi tự động deploy, cần thêm pipeline hoặc gate thủ công có bằng chứng cho: image SBOM/vulnerability scan, secret scan, build/push signed image, migration job có approval, smoke/E2E sau deploy, observability alert, backup rehearsal và approval release owner. Không tự bật auto-deploy chỉ vì lint/test hiện tại pass.

## 10. Điều kiện đóng stage deploy

Chỉ đóng khi tất cả pre-flight, migration/seed runtime, backup-restore rehearsal, rollback evidence, public incognito acceptance và account handoff đều có link/log/date/owner. Cho đến thời điểm đó, trạng thái đúng là **Stage 3 local hoàn tất; staging/production chưa xác nhận**.
