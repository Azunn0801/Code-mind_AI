import { useEffect, useMemo, useState } from 'react'
import { designs, designsById, groupLabels } from './designs'
import type { DesignSpec } from './designs'
import { PublicHeader } from './components/Shell'
import { navigate } from './components/navigation'
import { Button, Card, Chip } from './components/UI'
import { AuthPage, CampusPage, CheckoutPage, ContactPage, HelpPage, HomePage, LegalPage, PaymentPage, PricingPage } from './screens/PublicPages'
import { AIPage, ConceptPage, ErrorPage, EvidencePage, ObjectivePage, PracticePage, SetupPage, SourcePage } from './screens/LearningDemo'
import { StudentConcept, StudentDocs, StudentHome, StudentNotes, StudentPractice, StudentReview } from './screens/StudentPages'
import { AssignmentBuilder, AssignmentReview, AssignmentsPage, ClassesPage, RosterPage, TeacherHome } from './screens/TeacherPages'
import { AdminHome, FeedbackPage, GlossaryPage, SecurityPage, SourceGovernance, SupportPage } from './screens/AdminPages'
import './index.css'

type Route = { path: string; query: URLSearchParams; design?: DesignSpec }

function parseRoute(): Route {
  const raw = window.location.hash.replace(/^#/, '') || '/'
  const [pathname, search = ''] = raw.split('?')
  if (pathname.startsWith('/design/')) {
    const design = designsById.get(pathname.split('/').pop() ?? '')
    if (design) {
      const [path, query = ''] = design.path.split('?')
      return { path, query: new URLSearchParams(query), design }
    }
  }
  return { path: pathname || '/', query: new URLSearchParams(search) }
}

function useRoute() {
  const [route, setRoute] = useState(parseRoute)
  useEffect(() => {
    const onHash = () => setRoute(parseRoute())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])
  return route
}

function DesignGallery() {
  const [filter, setFilter] = useState<DesignSpec['group'] | 'all'>('all')
  const filtered = useMemo(() => filter === 'all' ? designs : designs.filter(item => item.group === filter), [filter])
  const groups: Array<DesignSpec['group'] | 'all'> = ['all', 'public', 'lesson', 'student', 'teacher', 'admin']
  return <div className="public-page design-gallery"><PublicHeader /><main className="public-container page-pad"><div className="page-heading page-heading--actions"><div><span className="eyebrow">FIGMA IMPLEMENTATION CATALOG</span><h1>{designs.length} thiết kế đã ánh xạ</h1><p>Mỗi node Figma trỏ tới route, viewport và state tương ứng trong cùng một hệ thống component.</p></div><Button onClick={() => navigate('/demo/setup')}>Mở happy path</Button></div><div className="filter-row">{groups.map(group => <button key={group} className={filter === group ? 'active' : ''} onClick={() => setFilter(group)}>{group === 'all' ? `Tất cả (${designs.length})` : `${groupLabels[group]} (${designs.filter(item => item.group === group).length})`}</button>)}</div><div className="catalog-grid">{filtered.map(item => <Card key={item.id} className="catalog-card"><div><Chip tone={item.viewport === 'mobile' ? 'warning' : 'info'}>{item.viewport}</Chip><Chip tone="muted">{groupLabels[item.group]}</Chip></div><h3>{item.name}</h3><code>{item.id}</code><p>{item.path}</p><Button tone="secondary" onClick={() => navigate(`/design/${item.id.replace(':', '-')}`)}>Mở thiết kế</Button></Card>)}</div></main></div>
}

function NotFound() {
  return <div className="public-page"><PublicHeader /><main className="public-container centered-page"><Card className="payment-card"><h1>Không tìm thấy màn hình</h1><p>Route này chưa tồn tại trong catalog CodeMind.</p><Button onClick={() => navigate('/designs')}>Mở catalog thiết kế</Button></Card></main></div>
}

function RouteView({ route }: { route: Route }) {
  const q = route.query
  const isMobileDesign = route.design?.viewport === 'mobile'
  switch (route.path) {
    case '/': return <HomePage mobile={isMobileDesign} />
    case '/designs': return <DesignGallery />
    case '/login': return <AuthPage mode="login" state={q.get('state') ?? undefined} />
    case '/register': return <AuthPage mode="register" state={q.get('state') ?? undefined} />
    case '/pricing': return <PricingPage />
    case '/campus': return <CampusPage />
    case '/about': return <LegalPage kind="about" />
    case '/privacy': return <LegalPage kind="privacy" />
    case '/terms': return <LegalPage kind="terms" />
    case '/ai-policy': return <LegalPage kind="ai" />
    case '/integrity': return <LegalPage kind="integrity" />
    case '/help': return <HelpPage />
    case '/help/source-reliability': return <HelpPage article offline={q.get('state') === 'offline'} />
    case '/contact': return <ContactPage submitted={q.get('state') === 'submitted'} />
    case '/checkout': return <CheckoutPage />
    case '/payment/success': return <PaymentPage success />
    case '/payment/failed': return <PaymentPage success={false} />
    case '/demo/setup': return <SetupPage initial={q.get('state') ?? 'required'} />
    case '/demo/objective': return <ObjectivePage mobile={isMobileDesign} />
    case '/demo/source': return <SourcePage selected={q.get('state') === 'selected'} mobile={isMobileDesign} />
    case '/demo/concept': return <ConceptPage initial={q.get('state') ?? 'initial'} mobile={isMobileDesign} />
    case '/demo/practice': return <PracticePage initial={q.get('state') ?? 'ready'} mobile={isMobileDesign} />
    case '/demo/ai': return <AIPage initial={q.get('state') ?? 'question'} mobile={isMobileDesign} />
    case '/demo/evidence': return <EvidencePage mobile={isMobileDesign} />
    case '/demo/error': return <ErrorPage state={q.get('state') ?? 'source'} mobile={isMobileDesign} />
    case '/student': return <StudentHome />
    case '/student/docs': return <StudentDocs selected={q.get('state') === 'selected'} />
    case '/student/concept': return <StudentConcept state={q.get('state') ?? 'initial'} />
    case '/student/practice': return <StudentPractice initial={q.get('state') ?? 'idle'} />
    case '/student/review': return <StudentReview />
    case '/student/notes': return <StudentNotes empty={q.get('state') === 'empty'} />
    case '/teacher': return <TeacherHome />
    case '/teacher/classes': return <ClassesPage />
    case '/teacher/roster': return <RosterPage />
    case '/teacher/assignments': return <AssignmentsPage />
    case '/teacher/builder': return <AssignmentBuilder ready={q.get('state') === 'ready'} />
    case '/teacher/review': return <AssignmentReview saved={q.get('state') === 'saved'} />
    case '/admin': return <AdminHome />
    case '/admin/sources': return <SourceGovernance initial={q.get('state') ?? 'initial'} />
    case '/admin/glossary': return <GlossaryPage />
    case '/admin/glossary/microtask': return <GlossaryPage detail />
    case '/admin/support': return <SupportPage />
    case '/admin/support/CM-204': return <SupportPage detail />
    case '/admin/feedback': return <FeedbackPage />
    case '/admin/approval/microtask': return <FeedbackPage approval />
    case '/admin/security': return <SecurityPage confirm={q.get('state') === 'confirm'} />
    default: return <NotFound />
  }
}

export default function App() {
  const route = useRoute()
  return <div className={route.design?.viewport === 'mobile' ? 'figma-mobile-preview' : ''}><RouteView route={route} /></div>
}
