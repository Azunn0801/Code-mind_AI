export type Role = 'student' | 'instructor' | 'content_admin' | 'org_admin'

export type DemoSession = {
  access_token: string
  token_type: string
  expires_in: number
  user_id: string
  role: Role
  display_name: string
}

export type SourceVersion = {
  id: string
  version_label: string
  title: string
  url: string
  checksum: string
  retrieved_at: string
  excerpt: string
}

export type Lesson = {
  slug: string
  version: number
  title: string
  objective: string
  source: SourceVersion
  steps: Array<{ sequence: number; key: string; title: string; objective: string }>
}

export type Consent = {
  purpose: string
  granted: boolean
  policy_version: string
  granted_at: string
}

export type LearningSession = {
  id: string
  user_id: string
  lesson_slug: string
  lesson_version: number
  status: 'in_progress' | 'completed'
  current_step: number
  version: number
  selected_terms: string[]
  concept_score: number
  concept_passed: boolean
  submission_ids: string[]
  hint_levels: number[]
  consents: Consent[]
  completed_at: string | null
}

export type ConceptPair = {
  from_term: string
  to_term: string
  relationship: string
}

export type TestResult = {
  name: string
  passed: boolean
  message: string
}

export type Submission = {
  id: string
  session_id: string
  status: 'queued' | 'completed' | 'failed'
  passed_count: number
  total_count: number
  results: TestResult[]
  idempotency_key: string
  created_at: string
  completed_at: string | null
}

export type Evidence = {
  id: string
  session_id: string
  lesson_slug: string
  before_code: string
  after_code: string
  passed_count: number
  total_count: number
  hint_levels: number[]
  selected_terms: string[]
  completed_at: string
}

export type Completion = { session: LearningSession; evidence: Evidence }

export type AICitation = {
  source_id: string
  version_label: string
  title: string
  url: string
}

export type AIInteraction = {
  id: string
  refused_complete_answer: boolean
  policy_version: string
  model_id: string
  message: string
  next_action: string
  opened_hints: number[]
  policy_decision: string
  citation: AICitation
  quota_cost: number
  quota_remaining: number
  latency_ms: number
}

export type Hint = {
  interaction_id: string
  level: number
  hint: string
  opened_hints: number[]
  remaining: number
}

export type TeacherSessionSummary = {
  session_id: string
  learner_id: string
  lesson_slug: string
  status: 'in_progress' | 'completed'
  current_step: number
  concept_score: number
  concept_passed: boolean
  test_passed: boolean
  hint_levels: number[]
  completed_at: string | null
  teacher_visibility: boolean
  evidence_available: boolean
}

export type AnalyticsEvent = {
  id: string
  event_name: string
  user_id: string
  session_id: string | null
  properties: Record<string, unknown>
  occurred_at: string
  source: string
}

export type AnalyticsEventList = {
  events: AnalyticsEvent[]
  total: number
}

type ErrorPayload = { code?: string; message?: string; details?: Record<string, unknown> }

export class ApiError extends Error {
  status: number
  code: string
  details?: Record<string, unknown>

  constructor(status: number, payload: ErrorPayload) {
    super(payload.message ?? 'Không thể kết nối với máy chủ.')
    this.name = 'ApiError'
    this.status = status
    this.code = payload.code ?? 'request_failed'
    this.details = payload.details
  }
}

const apiBase = (import.meta.env.VITE_API_BASE_URL ?? '/api').replace(/\/$/, '')

async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers)
  headers.set('Accept', 'application/json')
  if (options.body) headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)
  let response: Response
  try {
    response = await fetch(`${apiBase}${path}`, { ...options, headers })
  } catch {
    throw new ApiError(0, { code: 'network_error', message: 'Không kết nối được backend. Hãy kiểm tra API đang chạy.' })
  }
  const payload = await response.json().catch(() => ({})) as ErrorPayload
  if (!response.ok) throw new ApiError(response.status, payload)
  return payload as T
}

const json = (value: unknown): RequestInit => ({ method: 'POST', body: JSON.stringify(value) })

export const learningApi = {
  demoSession: (email = 'student.demo@codemind.local', role?: Role) => request<DemoSession>('/v1/demo/session', json({ email, role })),
  lesson: (slug: string, token?: string) => request<Lesson>(`/v1/lessons/${encodeURIComponent(slug)}`, {}, token),
  createSession: (input: { lesson_slug: string; integrity_consent: boolean; teacher_visibility: boolean }, token: string) => request<LearningSession>('/v1/learning-sessions', { ...json(input) }, token),
  getSession: (sessionId: string, token: string) => request<LearningSession>(`/v1/learning-sessions/${sessionId}`, {}, token),
  progress: (session: LearningSession, step: number, token: string) => request<LearningSession>(`/v1/learning-sessions/${session.id}/progress`, { method: 'PATCH', body: JSON.stringify({ current_step: step, expected_version: session.version }) }, token),
  terms: (sessionId: string, terms: string[], token: string) => request<LearningSession>(`/v1/sessions/${sessionId}/terms`, { ...json({ terms }) }, token),
  concept: (sessionId: string, pairs: ConceptPair[], token: string) => request<{ passed: boolean; score: number; total: number; session: LearningSession }>(`/v1/sessions/${sessionId}/concept-answers`, { ...json({ pairs }) }, token),
  submission: (sessionId: string, code: string, idempotencyKey: string, token: string) => request<Submission>(`/v1/sessions/${sessionId}/submissions`, { ...json({ code, idempotency_key: idempotencyKey }), headers: { 'Idempotency-Key': idempotencyKey } }, token),
  askAi: (sessionId: string, question: string, token: string) => request<AIInteraction>(`/v1/sessions/${sessionId}/ai-interactions`, { ...json({ question }) }, token),
  openHint: (interactionId: string, level: number, token: string) => request<Hint>(`/v1/ai-interactions/${interactionId}/hints/${level}/open`, { ...json({}) }, token),
  complete: (sessionId: string, token: string) => request<Completion>(`/v1/sessions/${sessionId}/complete`, { ...json({}) }, token),
  teacherSummary: (sessionId: string, token: string) => request<TeacherSessionSummary>(`/v1/instructor/sessions/${sessionId}/summary`, {}, token),
  analyticsEvents: (token: string, sessionId?: string) => request<AnalyticsEventList>(`/v1/analytics/events${sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : ''}`, {}, token),
}
