-- Run in SS-OIL-MERKEZ Supabase SQL Editor. Do not run on the PC database.
create table if not exists public.ssoil_events (
 id bigint generated always as identity primary key,
 event_id text not null unique,
 section text not null check (section in ('labels','orders','suppliers','supplierOf','minimum','discrepancies','orderUnits','barcodeErrors')),
 item_key text not null,
 value jsonb,
 created_at timestamptz not null default now(),
 created_by uuid default auth.uid()
);
create index if not exists ssoil_events_lookup on public.ssoil_events(section,item_key,id desc);
alter table public.ssoil_events enable row level security;
-- Only authenticated staff accounts may read/write; never expose service_role key in the app.
create policy "staff read events" on public.ssoil_events for select to authenticated using (true);
create policy "staff append events" on public.ssoil_events for insert to authenticated with check (created_by = auth.uid());
-- Event history is append-only: deletions are represented by value=null.
-- Do not add public/anon access policies.

-- Read-only snapshots from the PC bridge. The mobile app can only SELECT.
create table if not exists public.ssoil_snapshots (
 kind text primary key,
 data jsonb not null,
 updated_at timestamptz not null default now()
);
alter table public.ssoil_snapshots enable row level security;
create policy "staff read snapshots" on public.ssoil_snapshots for select to authenticated using (true);
-- No mobile insert/update/delete policy for snapshots.
