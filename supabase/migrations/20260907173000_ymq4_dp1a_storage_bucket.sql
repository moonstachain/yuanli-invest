-- YMQ4-DP1-A private raw evidence bucket.
-- S3 server credentials are used by the GitHub Actions worker; no public Storage policy is added.

insert into storage.buckets (id, name, public)
values ('ymq4-raw-evidence', 'ymq4-raw-evidence', false)
on conflict (id) do update set public = false;
