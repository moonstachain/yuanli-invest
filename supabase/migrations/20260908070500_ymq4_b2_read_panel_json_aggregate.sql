-- YMQ4-B2 readback hotfix.
-- PostgREST caps set-returning RPC responses at its configured max rows.
-- Return the complete PIT panel as one JSONB value so the 2,336-row
-- integrity gate is enforced by the research runtime, not truncated by HTTP.
-- No B3-B7 authority and no direct table grants are introduced here.

drop function if exists public.ymq4_b2_read_panel(text);

create function public.ymq4_b2_read_panel(p_panel_id text)
returns jsonb
language sql
security definer
set search_path = public, pit, pg_temp
as $$
  select coalesce(
    jsonb_agg(to_jsonb(q) order by q.decision_date, q.factor_id),
    '[]'::jsonb
  )
  from (
    select
      v.panel_id,
      v.decision_date,
      v.factor_id,
      v.value_numeric,
      v.known_as_of
    from pit.decision_asof_values v
    where v.panel_id = p_panel_id
    order by decision_date, factor_id
  ) q;
$$;

revoke all on function public.ymq4_b2_read_panel(text) from public, anon, authenticated;
grant execute on function public.ymq4_b2_read_panel(text) to service_role;
