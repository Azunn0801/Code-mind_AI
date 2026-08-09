import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { ApiError, learningApi, type AIInteraction, type Completion, type ConceptPair, type DemoSession, type Evidence, type Hint, type LearningSession, type Lesson, type Role, type Submission } from './api'

type PersistedLearning = {
  token: string | null
  user: DemoSession | null
  lesson: Lesson | null
  session: LearningSession | null
  lastSubmission: Submission | null
  evidence: Evidence | null
  aiInteraction: AIInteraction | null
  openedHints: Hint[]
  lastStudentSessionId: string | null
}

type LearningContextValue = PersistedLearning & {
  busy: boolean
  error: string | null
  errorCode: string | null
  enterDemoAccount: (email: string, role: Role) => Promise<DemoSession>
  startSession: (integrityConsent: boolean, teacherVisibility: boolean) => Promise<LearningSession>
  refreshSession: () => Promise<LearningSession | null>
  advance: (step: number) => Promise<LearningSession | null>
  selectTerms: (terms: string[]) => Promise<LearningSession | null>
  submitConcept: (pairs: ConceptPair[]) => Promise<boolean>
  submitCode: (code: string) => Promise<Submission | null>
  askAi: (question: string) => Promise<AIInteraction | null>
  openHint: (level: number) => Promise<Hint | null>
  complete: () => Promise<Completion | null>
  clearError: () => void
  reset: () => void
}

const storageKey = 'codemind.learning.v2'
const emptyState: PersistedLearning = { token: null, user: null, lesson: null, session: null, lastSubmission: null, evidence: null, aiInteraction: null, openedHints: [], lastStudentSessionId: null }

function readState(): PersistedLearning {
  try {
    const saved = window.localStorage.getItem(storageKey)
    return saved ? { ...emptyState, ...JSON.parse(saved) as PersistedLearning } : emptyState
  } catch {
    return emptyState
  }
}

function friendlyError(error: unknown): string {
  if (error instanceof ApiError) {
    const recoveryCopy: Record<string, string> = {
      network_error: 'Chưa kết nối được backend. Kiểm tra API đang chạy rồi tải lại tiến trình; dữ liệu trên trang vẫn được giữ.',
      version_conflict: 'Phiên học vừa được cập nhật ở nơi khác. Tải lại tiến trình rồi tiếp tục từ bước hiện tại.',
      ai_quota_exceeded: 'Bạn đã dùng hết lượt hỏi AI của phiên này. Bạn vẫn có thể quay lại mã, đọc nguồn và tự sửa bài.',
      evidence_forbidden: 'Người học chưa bật quyền chia sẻ phiên này cho giảng viên. Hãy dùng một phiên đã được cho phép.',
      session_not_found: 'Phiên học không còn trên backend. Hãy tạo một phiên demo mới.',
      step_locked: 'Bước này chưa mở. Hãy hoàn thành bước hiện tại trước khi đi tiếp.',
      hint_order: 'Hãy mở gợi ý theo thứ tự từ mức thấp đến mức cao.',
    }
    return recoveryCopy[error.code] ?? error.message
  }
  return 'Có lỗi xảy ra. Bạn có thể thử lại mà không mất tiến trình đã lưu.'
}

const LearningContext = createContext<LearningContextValue | null>(null)

export function LearningProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<PersistedLearning>(readState)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [errorCode, setErrorCode] = useState<string | null>(null)
  const hydratedRef = useRef(false)

  useEffect(() => {
    try { window.localStorage.setItem(storageKey, JSON.stringify(state)) } catch { /* storage is optional */ }
  }, [state])

  useEffect(() => {
    if (hydratedRef.current) return
    hydratedRef.current = true
    if (!state.token || !state.session) return
    void learningApi.getSession(state.session.id, state.token)
      .then((session) => setState((current) => ({ ...current, session })))
      .catch(() => undefined)
  }, [state.session, state.session?.id, state.token])

  const run = useCallback(async <T,>(operation: () => Promise<T>): Promise<T> => {
    setBusy(true)
    setError(null)
    setErrorCode(null)
    try { return await operation() } catch (caught) { setError(friendlyError(caught)); setErrorCode(caught instanceof ApiError ? caught.code : 'request_failed'); throw caught } finally { setBusy(false) }
  }, [])

  const enterDemoAccount = useCallback((email: string, role: Role) => run(async () => {
    const user = await learningApi.demoSession(email, role)
    setState((current) => ({
      ...emptyState,
      token: user.access_token,
      user,
      lastStudentSessionId: current.lastStudentSessionId,
    }))
    return user
  }), [run])

  const startSession = useCallback((integrityConsent: boolean, teacherVisibility: boolean) => run(async () => {
    const user = state.user?.role === 'student' && state.token ? state.user : await learningApi.demoSession('student.demo@codemind.local', 'student')
    const lesson = await learningApi.lesson('deque', user.access_token)
    const session = await learningApi.createSession({ lesson_slug: 'deque', integrity_consent: integrityConsent, teacher_visibility: teacherVisibility }, user.access_token)
    setState((current) => ({ token: user.access_token, user, lesson, session, lastSubmission: null, evidence: null, aiInteraction: null, openedHints: [], lastStudentSessionId: session.id || current.lastStudentSessionId }))
    return session
  }), [run, state.token, state.user])

  const refreshSession = useCallback(() => {
    if (!state.token || !state.session) return Promise.resolve(null)
    return run(async () => {
      const session = await learningApi.getSession(state.session!.id, state.token!)
      setState((current) => ({ ...current, session }))
      return session
    })
  }, [run, state.session, state.token])

  const advance = useCallback((step: number) => {
    if (!state.token || !state.session || state.session.current_step >= step) return Promise.resolve(state.session)
    return run(async () => {
      const session = await learningApi.progress(state.session!, step, state.token!)
      setState((current) => ({ ...current, session }))
      return session
    })
  }, [run, state.session, state.token])

  const selectTerms = useCallback((terms: string[]) => {
    if (!state.token || !state.session) return Promise.resolve(null)
    return run(async () => {
      const session = await learningApi.terms(state.session!.id, terms, state.token!)
      setState((current) => ({ ...current, session }))
      return session
    })
  }, [run, state.session, state.token])

  const submitConcept = useCallback((pairs: ConceptPair[]) => {
    if (!state.token || !state.session) return Promise.resolve(false)
    return run(async () => {
      const result = await learningApi.concept(state.session!.id, pairs, state.token!)
      setState((current) => ({ ...current, session: result.session }))
      return result.passed
    })
  }, [run, state.session, state.token])

  const submitCode = useCallback((code: string) => {
    if (!state.token || !state.session) return Promise.resolve(null)
    return run(async () => {
      const idempotencyKey = `web-${state.session!.id}-${code.length}-${code.includes('if not page') ? 'fixed' : 'draft'}`
      const submission = await learningApi.submission(state.session!.id, code, idempotencyKey, state.token!)
      const session = await learningApi.getSession(state.session!.id, state.token!)
      setState((current) => ({ ...current, session, lastSubmission: submission }))
      return submission
    })
  }, [run, state.session, state.token])

  const complete = useCallback(() => {
    if (!state.token || !state.session) return Promise.resolve(null)
    return run(async () => {
      const result = await learningApi.complete(state.session!.id, state.token!)
      setState((current) => ({ ...current, session: result.session, evidence: result.evidence }))
      return result
    })
  }, [run, state.session, state.token])

  const askAi = useCallback((question: string) => {
    if (!state.token || !state.session) return Promise.resolve(null)
    return run(async () => {
      const interaction = await learningApi.askAi(state.session!.id, question, state.token!)
      setState((current) => ({ ...current, aiInteraction: interaction, openedHints: [] }))
      return interaction
    })
  }, [run, state.session, state.token])

  const openHint = useCallback((level: number) => {
    if (!state.token || !state.aiInteraction) return Promise.resolve(null)
    return run(async () => {
      const hint = await learningApi.openHint(state.aiInteraction!.id, level, state.token!)
      setState((current) => ({ ...current, openedHints: [...current.openedHints.filter((item) => item.level !== hint.level), hint] }))
      return hint
    })
  }, [run, state.aiInteraction, state.token])

  const clearError = useCallback(() => { setError(null); setErrorCode(null) }, [])
  const reset = useCallback(() => { setState(emptyState); setError(null); setErrorCode(null) }, [])
  const value = useMemo(() => ({ ...state, busy, error, errorCode, enterDemoAccount, startSession, refreshSession, advance, selectTerms, submitConcept, submitCode, askAi, openHint, complete, clearError, reset }), [state, busy, error, errorCode, enterDemoAccount, startSession, refreshSession, advance, selectTerms, submitConcept, submitCode, askAi, openHint, complete, clearError, reset])
  return <LearningContext.Provider value={value}>{children}</LearningContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useLearning() {
  const context = useContext(LearningContext)
  if (!context) throw new Error('useLearning must be used inside LearningProvider')
  return context
}
