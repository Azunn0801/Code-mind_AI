import type { ButtonHTMLAttributes, ReactNode } from 'react'

export type Tone = 'info' | 'success' | 'warning' | 'danger'

export function Button({
  tone = 'primary',
  className = '',
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  tone?: 'primary' | 'secondary' | 'ghost' | 'danger'
}) {
  return (
    <button className={`button button--${tone} ${className}`} {...props}>
      {children}
    </button>
  )
}

export function Card({
  children,
  className = '',
  as: Tag = 'section',
}: {
  children: ReactNode
  className?: string
  as?: 'section' | 'article' | 'div'
}) {
  return <Tag className={`card ${className}`}>{children}</Tag>
}

export function Banner({
  tone = 'info',
  title,
  children,
  compact = false,
}: {
  tone?: Tone
  title: string
  children?: ReactNode
  compact?: boolean
}) {
  const icons: Record<Tone, string> = { info: 'i', success: '✓', warning: '!', danger: '×' }
  return (
    <div className={`banner banner--${tone} ${compact ? 'banner--compact' : ''}`} role="status">
      <span className="banner__icon" aria-hidden="true">{icons[tone]}</span>
      <div>
        <strong>{title}</strong>
        {children ? <p>{children}</p> : null}
      </div>
    </div>
  )
}

export function Chip({ children, tone = 'info' }: { children: ReactNode; tone?: Tone | 'muted' }) {
  return <span className={`chip chip--${tone}`}>{children}</span>
}

export function Stat({ value, label, note, tone = 'info' }: { value: string; label: string; note?: string; tone?: Tone }) {
  return (
    <Card className="stat">
      <strong className={`stat__value text-${tone}`}>{value}</strong>
      <b>{label}</b>
      {note ? <small>{note}</small> : null}
    </Card>
  )
}

export function CodeBlock({ children, tone }: { children: ReactNode; tone?: Tone }) {
  return <pre className={`code-block ${tone ? `code-block--${tone}` : ''}`}><code>{children}</code></pre>
}

export function Field({ label, value, type = 'text', onChange, placeholder }: {
  label: string
  value?: string
  type?: string
  onChange?: (value: string) => void
  placeholder?: string
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <input
        type={type}
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange?.(event.target.value)}
      />
    </label>
  )
}

export function EmptyState({ title, children, action }: { title: string; children: ReactNode; action?: ReactNode }) {
  return (
    <Card className="empty-state">
      <span className="empty-state__icon" aria-hidden="true">◇</span>
      <h2>{title}</h2>
      <p>{children}</p>
      {action}
    </Card>
  )
}
