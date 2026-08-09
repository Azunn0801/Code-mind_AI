-- CodeMind P0 logical schema. PostgreSQL 16 / UTC timestamps.

create extension if not exists pgcrypto;
create extension if not exists citext;

create table if not exists organizations (
  id uuid primary key default gen_random_uuid(),
  name varchar(160) not null unique,
  status varchar(24) not null default 'active',
  created_at timestamptz not null default now()
);

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  email citext not null unique,
  display_name varchar(120) not null,
  role varchar(32) not null check (role in ('student', 'instructor', 'content_admin', 'org_admin')),
  organization_id uuid references organizations(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists organization_memberships (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations(id) on delete restrict,
  user_id uuid not null references users(id) on delete cascade,
  role varchar(32) not null check (role in ('student', 'instructor', 'content_admin', 'org_admin')),
  created_at timestamptz not null default now(),
  unique (organization_id, user_id)
);

create table if not exists user_consents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete restrict,
  purpose varchar(40) not null check (purpose in ('academic_integrity', 'teacher_visibility')),
  granted boolean not null,
  policy_version varchar(64) not null,
  granted_at timestamptz not null,
  revoked_at timestamptz,
  unique (user_id, purpose, policy_version)
);

create table if not exists sources (
  id uuid primary key default gen_random_uuid(),
  source_key varchar(160) not null unique,
  title varchar(240) not null,
  canonical_url text not null,
  created_at timestamptz not null default now()
);

create table if not exists source_versions (
  id uuid primary key default gen_random_uuid(),
  source_id uuid not null references sources(id) on delete restrict,
  version_label varchar(80) not null,
  checksum varchar(128) not null,
  snapshot_uri text not null,
  retrieved_at timestamptz not null,
  unique (source_id, version_label, checksum)
);

create table if not exists lessons (
  id uuid primary key default gen_random_uuid(),
  slug varchar(120) not null,
  version integer not null,
  title varchar(240) not null,
  objective text not null,
  status varchar(24) not null default 'published',
  created_at timestamptz not null default now(),
  unique (slug, version)
);

create table if not exists lesson_steps (
  id uuid primary key default gen_random_uuid(),
  lesson_id uuid not null references lessons(id) on delete cascade,
  sequence smallint not null check (sequence between 1 and 6),
  step_key varchar(40) not null,
  title varchar(160) not null,
  objective text not null,
  unique (lesson_id, sequence)
);

create table if not exists lesson_sources (
  lesson_id uuid not null references lessons(id) on delete cascade,
  source_version_id uuid not null references source_versions(id) on delete restrict,
  primary key (lesson_id, source_version_id)
);

create table if not exists learning_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete restrict,
  lesson_id uuid not null references lessons(id) on delete restrict,
  organization_id uuid,
  status varchar(24) not null default 'in_progress',
  current_step smallint not null default 1 check (current_step between 1 and 6),
  version integer not null default 1,
  started_at timestamptz not null default now(),
  completed_at timestamptz
);

create table if not exists step_attempts (
  id uuid primary key default gen_random_uuid(),
  learning_session_id uuid not null references learning_sessions(id) on delete cascade,
  step_sequence smallint not null,
  attempt_no integer not null,
  outcome varchar(32) not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists term_selections (
  id uuid primary key default gen_random_uuid(),
  learning_session_id uuid not null references learning_sessions(id) on delete cascade,
  source_version_id uuid not null references source_versions(id) on delete restrict,
  term varchar(160) not null,
  created_at timestamptz not null default now()
);

create table if not exists concept_answers (
  id uuid primary key default gen_random_uuid(),
  learning_session_id uuid not null references learning_sessions(id) on delete cascade,
  score integer not null,
  total integer not null,
  passed boolean not null,
  answer jsonb not null,
  rule_version varchar(64) not null,
  created_at timestamptz not null default now()
);

create table if not exists code_submissions (
  id uuid primary key default gen_random_uuid(),
  learning_session_id uuid not null references learning_sessions(id) on delete cascade,
  code_text text not null,
  content_hash varchar(128) not null,
  idempotency_key varchar(160) not null,
  created_at timestamptz not null default now(),
  unique (learning_session_id, idempotency_key)
);

create table if not exists test_runs (
  id uuid primary key default gen_random_uuid(),
  submission_id uuid not null references code_submissions(id) on delete cascade,
  status varchar(32) not null,
  passed_count integer not null default 0,
  total_count integer not null,
  duration_ms integer,
  created_at timestamptz not null default now()
);

create table if not exists test_results (
  id uuid primary key default gen_random_uuid(),
  test_run_id uuid not null references test_runs(id) on delete cascade,
  test_case_key varchar(120) not null,
  passed boolean not null,
  safe_message text not null
);

create table if not exists ai_interactions (
  id uuid primary key default gen_random_uuid(),
  learning_session_id uuid not null references learning_sessions(id) on delete cascade,
  question text not null,
  policy_version varchar(64) not null,
  model_id varchar(120) not null,
  refused_complete_answer boolean not null,
  created_at timestamptz not null default now()
);

create table if not exists ai_hints (
  id uuid primary key default gen_random_uuid(),
  ai_interaction_id uuid not null references ai_interactions(id) on delete cascade,
  level smallint not null check (level between 1 and 3),
  created_at timestamptz not null default now(),
  unique (ai_interaction_id, level)
);

create table if not exists learning_evidence (
  id uuid primary key default gen_random_uuid(),
  learning_session_id uuid not null unique references learning_sessions(id) on delete restrict,
  before_submission_id uuid not null references code_submissions(id) on delete restrict,
  after_submission_id uuid not null references code_submissions(id) on delete restrict,
  passed_count integer not null,
  total_count integer not null,
  hint_levels jsonb not null default '[]'::jsonb,
  selected_terms jsonb not null default '[]'::jsonb,
  completed_at timestamptz not null
);

create table if not exists audit_events (
  id uuid primary key default gen_random_uuid(),
  actor_user_id uuid references users(id) on delete set null,
  action varchar(120) not null,
  resource_type varchar(80) not null,
  resource_id varchar(160),
  decision varchar(24) not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_learning_sessions_user on learning_sessions(user_id, started_at desc);
create index if not exists idx_audit_events_actor on audit_events(actor_user_id, created_at desc);

-- P0 runtime adapter. The application keeps its existing domain port while
-- persisting a versioned aggregate state transactionally in PostgreSQL.
-- This is deliberately separate from the normalized logical model above so
-- later entity-by-entity migration can happen without changing HTTP contracts.
create table if not exists application_state (
  state_key varchar(80) primary key,
  schema_version integer not null,
  payload jsonb not null,
  updated_at timestamptz not null default now()
);
