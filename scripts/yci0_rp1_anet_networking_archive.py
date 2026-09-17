#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, re
from datetime import datetime, timezone
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
PROJECT_REF="tbmoimbdhsrltvospwpu"
REGION="us-east-2"
BUCKET=os.getenv("YMQ4_RAW_BUCKET","ymq4-raw-evidence")
SOURCES=[
{"quarter":"2025Q3","url":"https://www.sec.gov/Archives/edgar/data/1596532/000159653225000284/ex991q325-earningsrelease.htm","accession":"0001596532-25-000284","value_usd_bn":2.308,"quarter_end":"2025-09-30","released_at":"2025-11-04"},
{"quarter":"2025Q4","url":"https://www.sec.gov/Archives/edgar/data/1596532/000159653226000010/ex991q425-earningsrelease.htm","accession":"0001596532-26-000010","value_usd_bn":2.488,"quarter_end":"2025-12-31","released_at":"2026-02-12"},
{"quarter":"2026Q1","url":"https://www.sec.gov/Archives/edgar/data/1596532/000159653226000074/ex991q126-earningsrelease.htm","accession":"0001596532-26-000074","value_usd_bn":2.709,"quarter_end":"2026-03-31","released_at":"2026-05-05"},
{"quarter":"2026Q2","url":"https://www.sec.gov/Archives/edgar/data/1596532/000159653226000174/ex991q226-earningsrelease.htm","accession":"0001596532-26-000174","value_usd_bn":3.036,"quarter_end":"2026-06-30","released_at":"2026-08-04"},
]
def require_env(name):
    value=os.getenv(name,"").strip()
    if not value: raise RuntimeError(f"missing required secret binding: {name}")
    return value
def http_session():
    s=requests.Session(); r=Retry(total=3,connect=3,read=3,backoff_factor=1.0,status_forcelist=(429,500,502,503,504),allowed_methods=frozenset(["GET"])); s.mount("https://",HTTPAdapter(max_retries=r)); s.headers.update({"User-Agent":"YuanliResearchEvidenceBot/1.0","Accept":"text/html,application/xhtml+xml","Accept-Language":"en-US,en;q=0.9"}); return s
def visible_text(raw):
    h=raw.decode("utf-8",errors="ignore"); t=re.sub(r"<script\b[^>]*>.*?</script>"," ",h,flags=re.I|re.S); t=re.sub(r"<style\b[^>]*>.*?</style>"," ",t,flags=re.I|re.S); t=re.sub(r"<[^>]+>"," ",t); t=t.replace("&nbsp;"," ").replace("&#160;"," "); return re.sub(r"\s+"," ",t)
def validate(raw,spec):
    v=visible_text(raw); low=v.lower()
    if "arista networks" not in low: raise RuntimeError(f"Arista identity marker missing for {spec['quarter']}")
    if "networking" not in low: raise RuntimeError(f"networking marker missing for {spec['quarter']}")
    value=f"{spec['value_usd_bn']:.3f}"
    if not re.search(rf"Revenue\s+of\s+\${re.escape(value)}\s+billion",v,flags=re.I): raise RuntimeError(f"expected revenue marker missing for {spec['quarter']}: ${value} billion")
    return {"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}
def s3_client(access_key,secret_key):
    import boto3
    from botocore.config import Config
    return boto3.client("s3",region_name=REGION,endpoint_url=f"https://{PROJECT_REF}.storage.supabase.co/storage/v1/s3",aws_access_key_id=access_key,aws_secret_access_key=secret_key,config=Config(s3={"addressing_style":"path"},signature_version="s3v4"))
def main():
    s3=s3_client(require_env("YMQ4_SUPABASE_S3_ACCESS_KEY_ID"),require_env("YMQ4_SUPABASE_S3_SECRET_ACCESS_KEY")); s3.head_bucket(Bucket=BUCKET); session=http_session(); archived=[]
    for spec in SOURCES:
        response=session.get(spec["url"],timeout=(20,45)); response.raise_for_status(); raw=response.content; checked=validate(raw,spec); sha=checked["sha256"]; key=f"yci0-rp1/arista/networking/{spec['quarter'].lower()}/{sha}.html"
        s3.put_object(Bucket=BUCKET,Key=key,Body=raw,ContentType=response.headers.get("Content-Type","text/html"),Metadata={"sha256":sha,"proof-contract":"YCI0-RP1-G4-ANET-NETWORKING","sec-accession":spec["accession"]}); reread=s3.get_object(Bucket=BUCKET,Key=key)["Body"].read(); reread_sha=hashlib.sha256(reread).hexdigest()
        if reread_sha!=sha: raise RuntimeError(f"S3 SHA mismatch for {spec['quarter']}: {reread_sha} != {sha}")
        archived.append({**spec,"metric":"Arista total quarterly revenue","http_status":response.status_code,"content_type":response.headers.get("Content-Type","text/html"),"bytes":len(raw),"sha256":sha,"storage_bucket":BUCKET,"storage_path":key,"storage_readback_sha256":reread_sha})
    print(json.dumps({"program":"YCI0-RP1","gate":"G4_NETWORKING_RAW_EVIDENCE","status":"PASS","provider":"Arista company-filed EX-99 via SEC EDGAR","source_role":"FIRST_PARTY_FILED_DISCLOSURE_ARCHIVED_BY_SEC","series_id":"ANET_TOTAL_REVENUE_QUARTERLY_USD_BN","metric_id":"AIINFRA.NETWORKING.REVENUE_BACKLOG","measurement_regime":"ARISTA_QUARTERLY_TOTAL_REVENUE","proxy_boundary":"Networking-vendor demand proxy; not AI-only networking revenue","archived":archived,"authority":{"evidence_promotion_authorized":False,"research_authorized":False,"capital_authorized":False,"execution_authorized":False},"generated_at":datetime.now(timezone.utc).isoformat()},ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
