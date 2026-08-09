import { Banner, Button } from '../components/UI'
import { navigate } from '../components/navigation'
import { useLearning } from '../learning/LearningContext'

type RecoveryConfig = {
  title: string
  detail: string
  action: 'refresh' | 'practice' | 'restart'
  label: string
}

const recoveryByCode: Record<string, RecoveryConfig> = {
  network_error: {
    title: 'Chưa kết nối được máy chủ MVP',
    detail: 'Kiểm tra backend đang chạy, sau đó tải lại phiên. Tiến trình hiện có không bị xóa khỏi màn hình này.',
    action: 'refresh',
    label: 'Tải lại phiên học',
  },
  version_conflict: {
    title: 'Tiến trình vừa thay đổi ở nơi khác',
    detail: 'Tải lại phiên để lấy trạng thái mới nhất trước khi tiếp tục.',
    action: 'refresh',
    label: 'Tải lại tiến trình',
  },
  ai_quota_exceeded: {
    title: 'Đã hết lượt hỏi AI của phiên này',
    detail: 'Hạn mức AI không khóa bài học. Bạn vẫn có thể quay lại mã, đọc nguồn và tự sửa bài.',
    action: 'practice',
    label: 'Quay lại mã',
  },
  evidence_forbidden: {
    title: 'Giảng viên chưa được phép xem phiên này',
    detail: 'Hãy dùng một phiên mà người học đã bật “Cho phép giảng viên xem quá trình làm bài”.',
    action: 'restart',
    label: 'Đổi tài khoản demo',
  },
  session_not_found: {
    title: 'Phiên học không còn trên backend',
    detail: 'Tạo một phiên demo mới để tiếp tục trải nghiệm luồng học.',
    action: 'restart',
    label: 'Tạo lại phiên demo',
  },
  step_locked: {
    title: 'Bước này chưa mở',
    detail: 'Hãy hoàn thành bước hiện tại rồi tiếp tục theo thanh tiến trình.',
    action: 'refresh',
    label: 'Tải lại tiến trình',
  },
  hint_order: {
    title: 'Gợi ý cần được mở theo thứ tự',
    detail: 'Bắt đầu từ gợi ý mức 1, rồi mở dần các mức tiếp theo khi cần.',
    action: 'refresh',
    label: 'Làm mới trạng thái gợi ý',
  },
}

export function LiveApiRecovery({ fallbackPath = '/demo/access' }: { fallbackPath?: string }) {
  const { error, errorCode, session, busy, refreshSession, clearError, reset } = useLearning()
  if (!error) return null

  const config = recoveryByCode[errorCode ?? ''] ?? {
    title: 'Chưa hoàn tất được thao tác',
    detail: error,
    action: session ? 'refresh' : 'restart',
    label: session ? 'Tải lại tiến trình' : 'Về tài khoản demo',
  }

  const recover = async () => {
    if (config.action === 'practice') {
      clearError()
      navigate('/demo/practice')
      return
    }
    if (config.action === 'restart' || !session) {
      reset()
      navigate(fallbackPath)
      return
    }
    try {
      await refreshSession()
      clearError()
    } catch {
      // The mapped message stays visible until the backend is available again.
    }
  }

  return <section className="live-api-recovery" aria-live="polite">
    <Banner tone="danger" title={config.title}>{config.detail}</Banner>
    <div className="action-row">
      <Button disabled={busy} onClick={() => void recover()}>{busy ? 'Đang kiểm tra…' : config.label}</Button>
      <Button tone="secondary" onClick={clearError}>Đóng thông báo</Button>
    </div>
  </section>
}
