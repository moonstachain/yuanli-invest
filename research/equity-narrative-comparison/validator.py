"""Validate candidate inputs and output objects against existing Yuanli contracts."""
from __future__ import annotations

from datetime import date, datetime
import hashlib
import json
import math
from pathlib import Path
import re

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
PACK = Path(__file__).resolve().parent
BASE_REVISION = "705dbedf8866453f12d42dde58dbd95dbc032ee7"
CAP_SPEC = "docs/architecture/r2_3b1/CAP-V-01-SPEC-v0.1.json"
DATA_FILES = {"benchmark/financial-inputs.json", "benchmark/financial-outcomes.json",
              "benchmark/market-inputs.json", "benchmark/market-outcomes.json",
              "benchmark/sources.json"}
OUTCOME_FILES = {"benchmark/financial-outcomes.json", "benchmark/market-outcomes.json"}
FORBIDDEN = {"target_price", "canonical_upside_percentage", "recommended_portfolio_weight",
             "recommended_weight", "position_size", "buy_sell_hold", "live_execution_instruction",
             "weighted_PNXEVSR_composite_score", "scalar_master_score", "scalar_engine_master_score"}


class ValidationError(ValueError):
    pass


def read(path):
    def reject_constant(value):
        raise ValidationError(f"nonfinite JSON constant: {value}")
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=reject_constant)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    validate_numeric(value)
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def date_time(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValidationError("invalid timestamp") from exc
    if parsed.tzinfo is None:
        raise ValidationError("timestamp must include timezone")
    return parsed


def calendar_date(value):
    try:
        parsed = date.fromisoformat(value)
    except (ValueError, TypeError) as exc:
        raise ValidationError("invalid calendar date") from exc
    if parsed.isoformat() != value:
        raise ValidationError("calendar date must use YYYY-MM-DD")
    return parsed


def nonempty_strings(value, name):
    if (not isinstance(value, list) or not value
            or any(not isinstance(x, str) or not x.strip() for x in value)
            or len(set(value)) != len(value)):
        raise ValidationError(f"{name}: nonempty unique string list required")
    return value


def unique_index(rows, key, name):
    if not isinstance(rows, list) or not rows:
        raise ValidationError(f"{name}: nonempty record list required")
    index = {}
    for row in rows:
        identity = row.get(key) if isinstance(row, dict) else None
        if not isinstance(identity, str) or not identity.strip() or identity in index:
            raise ValidationError(f"{name}: missing or duplicate {key}")
        index[identity] = row
    return index


def sha256_value(value, name):
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValidationError(f"{name}: invalid SHA256")


def source_catalog(sources):
    index = unique_index(sources.get("sources"), "source_id", "source catalog")
    for source in index.values():
        sha256_value(source.get("sha256"), "source hash")
        published = calendar_date(source["published_date"])
        if source["role"] not in {"T0_INPUT", "OUTCOME"}:
            raise ValidationError("unknown source role")
        if calendar_date(source["period_end"]) > published:
            raise ValidationError("source accounting period ends after publication")
        known = date_time(source["known_available_at"]) if source.get("known_available_at") else None
        if source["role"] == "T0_INPUT" and known is None:
            raise ValidationError("T0 source requires a known-availability timestamp")
        if known is not None and published > known.date():
            raise ValidationError("source claimed available before its publication date")
        if source.get("published_at") is not None:
            published_at = date_time(source["published_at"])
            if published_at.date() != published or (known is not None and published_at > known):
                raise ValidationError("source publication timestamp is inconsistent")
    return index


def validate_numeric(value):
    if isinstance(value, dict):
        for v in value.values():
            validate_numeric(v)
    elif isinstance(value, list):
        for v in value:
            validate_numeric(v)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        numeric(value, "numeric value")


def validate_no_action_fields(value):
    if isinstance(value, dict):
        found = FORBIDDEN.intersection(value)
        if found:
            raise ValidationError(f"prohibited output fields: {sorted(found)}")
        for v in value.values():
            validate_no_action_fields(v)
    elif isinstance(value, list):
        for v in value:
            validate_no_action_fields(v)


def validate_schema(value, name):
    schema = read(ROOT / "packages/contracts/schemas/vnext" / name)
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
                    key=lambda e: str(list(e.path)))
    if errors:
        raise ValidationError(f"{name}: {errors[0].message}")


def validate_profile(profile):
    b0 = read(ROOT / "docs/architecture/r2_3b0/R2-3B0-CONTRACT-SCHEMA-v0.1.json")
    for block in b0["required_blocks"]:
        if block not in profile:
            raise ValidationError(f"missing B0 block: {block}")
        for field in b0[block].get("required_fields", []):
            if field not in profile[block]:
                raise ValidationError(f"missing B0 field: {block}.{field}")
    if profile["identity"]["capability_id"] != "CAP-V-01":
        raise ValidationError("profile must preserve parent capability identity")


def verify_rule_freeze(pack=PACK):
    freeze = read(pack / "benchmark/protocol-freeze.json")
    for key, relative in [("protocol_sha256", "benchmark/protocol.json"),
                          ("settings_sha256", "settings.json")]:
        if freeze[key] != digest(pack / relative):
            raise ValidationError(f"frozen rule changed: {relative}; use an explicit successor version")


def verify_data_freeze(pack=PACK, *, include_outcomes=True):
    pack = Path(pack)
    manifest = read(pack / "benchmark/data-freeze.json")
    records = unique_index(manifest.get("files"), "path", "data freeze")
    if set(records) != DATA_FILES:
        raise ValidationError("data freeze must cover exactly the declared input and outcome packets")
    for relative, record in records.items():
        sha256_value(record.get("sha256"), "frozen data hash")
        # Read the manifest metadata, but never open outcome bytes during prepare.
        if not include_outcomes and relative in OUTCOME_FILES:
            continue
        if digest(pack / relative) != record["sha256"]:
            raise ValidationError(f"frozen data changed: {relative}")


def numeric(value, name, *, positive=False, ratio=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{name}: finite numeric input required")
    try:
        value = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValidationError(f"{name}: finite numeric input required") from exc
    if not math.isfinite(value):
        raise ValidationError(f"{name}: finite numeric input required")
    if positive and value <= 0:
        raise ValidationError(f"{name}: positive value required")
    if ratio and not 0 <= value <= 1:
        raise ValidationError(f"{name}: ratio outside zero to one")
    return value


def validate_inputs(financial, market, protocol, sources):
    validate_numeric(financial)
    validate_numeric(market)
    cutoff = date_time(protocol["as_of"])
    if date_time(financial["t0"]) != cutoff or date_time(market["as_of"]) != cutoff:
        raise ValidationError("all methods must use the identical information cutoff")
    universe = nonempty_strings(protocol["universe"], "frozen universe")
    financial_index = unique_index(financial.get("records"), "ticker", "financial inputs")
    if set(financial_index) != set(universe):
        raise ValidationError("financial universe differs from frozen protocol")
    source_index = source_catalog(sources)
    for record in financial_index.values():
        source = source_index.get(record.get("input_source_id"))
        if source is None:
            raise ValidationError("unknown financial input source")
        if source["role"] != "T0_INPUT" or date_time(record["known_available_at"]) > cutoff:
            raise ValidationError("future or outcome source in input packet")
        if date_time(source["known_available_at"]) != date_time(record["known_available_at"]):
            raise ValidationError("observation availability differs from source catalog")
        if record["source_sha256"] != source["sha256"]:
            raise ValidationError("financial observation source hash mismatch")
        published = calendar_date(record["source_published_date"])
        if published != calendar_date(source["published_date"]) or published > cutoff.date():
            raise ValidationError("financial publication date differs from T0 source catalog")
        if source.get("published_at") is not None and date_time(source["published_at"]) > cutoff:
            raise ValidationError("source publication timestamp is after T0")
        quarter_end = calendar_date(record["latest_quarter"]["period_end"])
        if quarter_end != calendar_date(source["period_end"]) or quarter_end > published:
            raise ValidationError("financial accounting period differs from published source")
        if quarter_end > cutoff.date():
            raise ValidationError("future accounting period in lagged inputs")
        numeric(record["latest_quarter"]["revenue_usd_million"], "lagged revenue", positive=True)
        numeric(record["latest_quarter"]["gaap_gross_margin_ratio"], "lagged GAAP margin", ratio=True)
        fy = record["fiscal_year"]
        if calendar_date(fy["period_end"]) > min(quarter_end, published, cutoff.date()):
            raise ValidationError("future fiscal-year accounting period in input packet")
        numeric(fy["gaap_diluted_eps_usd"], "annual GAAP diluted EPS")
        numeric(fy["diluted_weighted_average_shares_million"], "annual diluted shares", positive=True)
        numeric(fy["ocf_minus_cash_capital_purchases_proxy_usd_million"], "cash flow proxy")
        capital_key = fy.get("cash_capital_purchase_component_key")
        if not isinstance(capital_key, str) or capital_key not in fy:
            raise ValidationError("missing declared cash capital-purchase component")
        operating_cf = numeric(fy["ocf_usd_million"], "operating cash flow")
        purchases = numeric(fy[capital_key], "cash capital purchases")
        if purchases < 0:
            raise ValidationError("cash capital purchases must be nonnegative")
        proxy = numeric(operating_cf - purchases, "derived cash flow proxy")
        if not math.isclose(proxy, fy["ocf_minus_cash_capital_purchases_proxy_usd_million"],
                            rel_tol=1e-10, abs_tol=1e-10):
            raise ValidationError("cash flow proxy does not reconcile to OCF minus declared cash purchases")
        if (fy["equity_free_cash_flow_identity_asserted"] is not False
                or fy["cash_flow_proxy_is_unlevered_fcff"] is not False):
            raise ValidationError("cash flow proxy must not claim normalized FCFE or unlevered FCFF identity")
        derived = fy["ocf_minus_cash_capital_purchases_proxy_usd_million"] / fy["diluted_weighted_average_shares_million"]
        numeric(derived, "derived cash flow per share")
        reported = fy["ocf_minus_cash_capital_purchases_proxy_usd_per_annual_diluted_share"]
        numeric(reported, "cash flow per share")
        if not math.isclose(derived, reported, rel_tol=1e-10, abs_tol=1e-10):
            raise ValidationError("cash flow per share does not reconcile")
        guidance = record["guidance"]
        for part in ("low", "mid", "high"):
            numeric(guidance[f"revenue_{part}_usd_million"], "guidance revenue", positive=True)
            for basis in ("gaap", "non_gaap"):
                margin = guidance.get(f"{basis}_gross_margin_{part}_ratio")
                if margin is not None:
                    numeric(margin, f"{basis} margin", ratio=True)
        if not (guidance["revenue_low_usd_million"] <= guidance["revenue_mid_usd_million"]
                <= guidance["revenue_high_usd_million"]):
            raise ValidationError("inconsistent guidance interval")
        if guidance["revenue_basis"] != "GAAP_REVENUE_NO_NON_GAAP_ADJUSTMENT":
            raise ValidationError("incomparable revenue basis")
        for basis in ("gaap", "non_gaap"):
            present = [guidance.get(f"{basis}_gross_margin_{part}_ratio") for part in ("low", "mid", "high")]
            present = [value for value in present if value is not None]
            if present != sorted(present):
                raise ValidationError("inconsistent gross-margin guidance interval")
    market_rows = market["observations"]
    expected = set(protocol["universe"] + [protocol["market_benchmark"]])
    if set(unique_index(market_rows, "symbol", "market inputs")) != expected:
        raise ValidationError("market universe or benchmark mismatch")
    for record in market_rows:
        sha256_value(record.get("source_sha256"), "market source hash")
        if calendar_date(record["t0"]["date"]) != cutoff.date():
            raise ValidationError("price not at common T0")
        if calendar_date(record["lookback"]["date"]) >= cutoff.date():
            raise ValidationError("invalid momentum input window")
        if record["lookback_sessions"] != protocol["momentum_lookback_sessions"]:
            raise ValidationError("lookback differs from frozen rule")
        for price in (record["lookback"]["close"], record["t0"]["close"], record["reported_T0_price_unit_factor"]):
            numeric(price, "market input", positive=True)
        if record["price_basis"] != "split_adjusted_as_retrieved" or record["currency"] != "USD":
            raise ValidationError("unsupported price basis or currency")


def validate_outcomes(outcomes, market_outcomes, financial, protocol, sources, market_inputs):
    validate_numeric(outcomes)
    validate_numeric(market_outcomes)
    if date_time(outcomes["t0"]) != date_time(protocol["as_of"]) or date_time(market_outcomes["as_of"]) != date_time(protocol["as_of"]):
        raise ValidationError("outcome packet cutoff mismatch")
    cutoff = date_time(protocol["as_of"]).date()
    deadline_at = date_time(protocol["financial_settlement_deadline"])
    deadline = deadline_at.date()
    expected = unique_index(financial.get("records"), "ticker", "financial inputs")
    source_index = source_catalog(sources)
    actual_index = unique_index(outcomes.get("records"), "ticker", "financial outcomes")
    if set(actual_index) != set(expected):
        raise ValidationError("outcome universe mismatch")
    for actual in actual_index.values():
        published = calendar_date(actual["published_date"])
        if actual["outcome_only"] is not True or not cutoff < published <= deadline:
            raise ValidationError("outcome lies outside settlement window")
        if actual["target_period_label"] != expected[actual["ticker"]]["guidance"]["target_period_label"]:
            raise ValidationError("fiscal target period mismatch")
        source = source_index.get(actual.get("source_id"))
        if source is None or source["role"] != "OUTCOME" or source["sha256"] != actual["source_sha256"]:
            raise ValidationError("outcome source role or hash mismatch")
        if source["published_date"] != actual["published_date"]:
            raise ValidationError("outcome publication date differs from source catalog")
        actual_period_end = calendar_date(actual["period_end"])
        if actual_period_end != calendar_date(source["period_end"]) or not cutoff < actual_period_end <= published:
            raise ValidationError("outcome accounting period is invalid")
        for field in ("published_at",):
            actual_time = date_time(actual[field]) if actual.get(field) is not None else None
            source_time = date_time(source[field]) if source.get(field) is not None else None
            if actual_time != source_time or (actual_time is not None and actual_time > deadline_at):
                raise ValidationError("outcome publication timestamp mismatch or outside deadline")
        numeric(actual["revenue_usd_million"], "actual revenue", positive=True)
        numeric(actual["gaap_gross_margin_ratio"], "actual GAAP margin", ratio=True)
    market_rows = market_outcomes["observations"]
    input_index = unique_index(market_inputs.get("observations"), "symbol", "market inputs")
    if set(unique_index(market_rows, "symbol", "market outcomes")) != set(input_index):
        raise ValidationError("market settlement universe mismatch")
    for row in market_rows:
        for field in ("source_sha256", "price_basis", "currency"):
            if row[field] != input_index[row["symbol"]][field]:
                raise ValidationError("market input/outcome provenance or basis mismatch")
        if [h["sessions"] for h in row["horizons"]] != protocol["market_horizons_sessions"]:
            raise ValidationError("market horizon mismatch")
        for horizon in row["horizons"]:
            numeric(horizon["close"], "settlement price", positive=True)
            if not cutoff < calendar_date(horizon["date"]) <= deadline:
                raise ValidationError("invalid market outcome window")
        if [h["date"] for h in row["horizons"]] != sorted({h["date"] for h in row["horizons"]}):
            raise ValidationError("settlement windows must advance")
    benchmark = next(r for r in market_rows if r["symbol"] == protocol["market_benchmark"])
    if any([h["date"] for h in row["horizons"]] != [h["date"] for h in benchmark["horizons"]] for row in market_rows):
        raise ValidationError("assets must share benchmark settlement dates")


def validate_observation_times(value, cutoff):
    """Retrieval timestamps may be later; claimed knowledge/publication may not."""
    if isinstance(value, dict):
        if value.get("role") == "OUTCOME" or (
                "outcome_only" in value and value["outcome_only"] is not False):
            raise ValidationError("outcome observation in capability input bundle")
        for key in ("known_available_at", "published_at"):
            if value.get(key) is not None and date_time(value[key]) > cutoff:
                raise ValidationError("future observation in capability input bundle")
        if value.get("source_published_date") is not None:
            if calendar_date(value["source_published_date"]) > cutoff.date():
                raise ValidationError("future publication in capability input bundle")
        for child in value.values():
            validate_observation_times(child, cutoff)
    elif isinstance(value, list):
        for child in value:
            validate_observation_times(child, cutoff)


def validate_generated(bundle):
    """Package-level constraints supplement, without modifying, global schemas."""
    validate_numeric(bundle)
    validate_no_action_fields(bundle)
    if not isinstance(bundle, dict):
        raise ValidationError("generated bundle must be an object")
    protocol = read(PACK / "benchmark/protocol.json")
    cutoff = date_time(protocol["as_of"])
    universe = nonempty_strings(protocol["universe"], "frozen universe")
    targets = unique_index(bundle.get("targets"), "target_id", "targets")
    theses = unique_index(bundle.get("engine_theses"), "engine_thesis_id", "engine theses")
    requests = unique_index(bundle.get("invocations"), "request_id", "invocations")
    inputs_by_id = unique_index(bundle.get("input_bundles"), "bundle_id", "input bundles")
    results = unique_index(bundle.get("capability_results"), "result_id", "capability results")
    receipts = unique_index(bundle.get("research_receipts"), "request_id", "research receipts")
    count = len(universe)
    if any(len(items) != count for items in (targets, requests, inputs_by_id, results, receipts)) or len(theses) != 3 * count:
        raise ValidationError("each frozen target requires one invocation/input/result/receipt and three engine theses")
    for key, name in (("targets", "research-target-v2.schema.json"),
                      ("engine_theses", "engine-thesis.schema.json"),
                      ("invocations", "capability-invocation.schema.json"),
                      ("input_bundles", "capability-input-bundle.schema.json"),
                      ("capability_results", "capability-result.schema.json")):
        for obj in bundle[key]:
            validate_schema(obj, name)
    symbols = [target.get("identifiers", {}).get("ticker") for target in targets.values()]
    if any(not isinstance(symbol, str) for symbol in symbols) or set(symbols) != set(universe):
        raise ValidationError("generated target universe differs from frozen protocol")
    for target in targets.values():
        if target["active_status"] != "candidate" or date_time(target["created_at"]) <= cutoff:
            raise ValidationError("retrospective target must remain a newly declared candidate")
    requests_by_target = unique_index(bundle["invocations"], "target_id", "invocation targets")
    inputs_by_request = unique_index(bundle["input_bundles"], "request_id", "input requests")
    results_by_request = unique_index(bundle["capability_results"], "request_id", "result requests")
    if (set(requests_by_target) != set(targets) or set(inputs_by_request) != set(requests)
            or set(results_by_request) != set(requests) or set(receipts) != set(requests)):
        raise ValidationError("generated invocation/input/result/receipt links must be one-to-one")
    for invocation in requests.values():
        if invocation["capability_id"] != "CAP-V-01" or date_time(invocation["as_of"]) != cutoff:
            raise ValidationError("invocation must preserve CAP-V-01 and the frozen information cutoff")
    for obj in bundle["input_bundles"] + bundle["capability_results"]:
        request = requests[obj["request_id"]]
        if any(request[k] != obj[k] for k in ("target_id", "capability_id", "as_of")):
            raise ValidationError("capability invocation/result reference mismatch")
    for inputs in inputs_by_id.values():
        if inputs["pit_status"] != "provisional":
            raise ValidationError("reconstructed inputs must remain PIT provisional")
        if inputs["input_manifest_hash"] != "sha256:" + canonical_hash(inputs["observations"]):
            raise ValidationError("capability input observation hash mismatch")
        validate_observation_times(inputs["observations"], cutoff)
    for result in results.values():
        state, uncertainty = result["state"], result["uncertainty"]
        identification = state.get("identification_status")
        expected_status = {"underidentified": "partial", "unsupported": "unknown"}.get(identification)
        if expected_status is None or result["status"] != expected_status:
            raise ValidationError("reconstructed diagnostics cannot claim a successful or identified result")
        if (state.get("state_type") != "PriceImpliedExpectationState" or state.get("research_only") is not True
                or date_time(state.get("as_of")) != cutoff or uncertainty.get("pit_status") != "provisional"
                or uncertainty.get("probabilities_calibrated") is not False):
            raise ValidationError("result must disclose provisional, uncalibrated research-only semantics")
        regions = state.get("assumption_regions")
        solutions = state.get("solution_count")
        if (not isinstance(regions, list) or not regions or isinstance(solutions, bool)
                or not isinstance(solutions, int) or solutions < 0
                or any(not isinstance(region, dict) for region in regions)):
            raise ValidationError("invalid joint-assumption region or solution count")
        if any(region.get("status") not in {"conditional_solution", "unsupported", "outside_search_domain"}
               for region in regions):
            raise ValidationError("unknown conditional-solver state")
        numeric(result["metrics"].get("conditional_grid_solutions"), "reported conditional solution count")
        conditional_growths = []
        for region in regions:
            discount = numeric(region.get("discount_rate"), "region discount rate", positive=True)
            terminal = numeric(region.get("terminal_growth"), "region terminal growth")
            numeric(region.get("cashflow_scale"), "region cash flow scale", positive=True)
            horizon = region.get("horizon_years")
            if (isinstance(horizon, bool) or not isinstance(horizon, int) or not 1 <= horizon <= 50
                    or not -1 < terminal < discount):
                raise ValidationError("conditional assumption region is outside the model domain")
            if region["status"] == "conditional_solution":
                growth = numeric(region.get("annual_cashflow_growth"), "conditional cash flow growth")
                multiple = numeric(region.get("terminal_cashflow_multiple"), "terminal cash flow multiple", positive=True)
                residual = numeric(region.get("relative_identity_residual"), "conditional identity residual")
                if growth <= -1 or not 0 <= residual <= 1e-8:
                    raise ValidationError("conditional growth or numerical identity residual is invalid")
                try:
                    expected_multiple = (1 + growth) ** horizon
                except OverflowError as exc:
                    raise ValidationError("terminal cash flow multiple overflow") from exc
                numeric(expected_multiple, "derived terminal cash flow multiple", positive=True)
                if not math.isclose(multiple, expected_multiple, rel_tol=1e-10, abs_tol=1e-10):
                    raise ValidationError("terminal cash flow multiple does not reconcile")
                conditional_growths.append(growth)
        if (solutions != sum(region["status"] == "conditional_solution" for region in regions)
                or (solutions > 0) != (identification == "underidentified")
                or result["metrics"].get("conditional_grid_solutions") != solutions):
            raise ValidationError("conditional-solver state and reported solution count disagree")
        growth_range = state.get("conditional_growth_range")
        if solutions:
            if not isinstance(growth_range, list) or len(growth_range) != 2:
                raise ValidationError("conditional growth range is required")
            for growth in growth_range:
                numeric(growth, "conditional growth range")
            if growth_range != [min(conditional_growths), max(conditional_growths)]:
                raise ValidationError("conditional growth range does not match the reported joint regions")
        elif growth_range is not None:
            raise ValidationError("unsupported cashflow must not receive an invented growth range")
        nonempty_strings(state.get("evidence_refs"), "result evidence references")
    engines_by_target = {target_id: set() for target_id in targets}
    falsifiers = unique_index(bundle.get("falsifier_registry"), "falsifier_id", "falsifier registry")
    for thesis in theses.values():
        target_id = thesis["target_id"]
        engine = thesis["identity_core"]["primary_engine"]
        if target_id not in targets or engine not in {"ENG-C", "ENG-R", "ENG-X"}:
            raise ValidationError("unexpected thesis target or return engine")
        if engine in engines_by_target[target_id]:
            raise ValidationError("duplicate engine thesis for a target")
        engines_by_target[target_id].add(engine)
        expected_result = results_by_request[requests_by_target[target_id]["request_id"]]["result_id"]
        if thesis["evidence"]["capability_output_refs"] != [expected_result]:
            raise ValidationError("thesis capability reference must point to its own target result")
        opened = date_time(thesis["identity_core"]["opened_at"])
        evidence = thesis["evidence"]
        if (opened <= cutoff or date_time(evidence.get("recorded_at")) <= cutoff
                or any(date_time(evidence.get(field)) != cutoff for field in
                       ("knowledge_cutoff", "known_as_of", "replay_cutoff"))):
            raise ValidationError("retrospective thesis declaration and historical evidence cutoff must remain distinct")
        lifecycle = thesis["lifecycle"]
        if (lifecycle["status"] != "draft" or date_time(lifecycle["as_of"]) != opened
                or date_time(lifecycle["valid_from"]) != opened):
            raise ValidationError("candidate thesis lifecycle must remain a newly declared draft")
        refs = nonempty_strings(thesis["falsification"]["falsifier_refs"], "thesis falsifiers")
        if any(ref not in falsifiers for ref in refs):
            raise ValidationError("dangling thesis falsifier reference")
        conditions = nonempty_strings(thesis["falsification"]["challenge_conditions"], "challenge conditions")
        if conditions != [falsifiers[ref].get("condition") for ref in refs]:
            raise ValidationError("falsifier references and stated challenge conditions disagree")
    if any(engines != {"ENG-C", "ENG-R", "ENG-X"} for engines in engines_by_target.values()):
        raise ValidationError("each target requires separate C/R/X draft theses")
    contract = read(ROOT / "docs/architecture/r2_3b0/R2-3B0-CONTRACT-SCHEMA-v0.1.json")
    governance = contract["runtime_receipt_governance"]
    expected_canon_hash = "sha256:" + digest(ROOT / CAP_SPEC)
    for request_id, receipt in receipts.items():
        for field in governance["research_receipt_fields"]:
            if field not in receipt:
                raise ValidationError(f"missing receipt field: {field}")
        envelope = receipt["invocation_envelope"]
        if not isinstance(envelope, dict):
            raise ValidationError("receipt invocation envelope must be an object")
        for field in governance["invocation_envelope_fields"]:
            if not isinstance(envelope.get(field), str) or not envelope[field].strip():
                raise ValidationError(f"missing or empty invocation field: {field}")
        request = requests[request_id]
        result = results_by_request[request_id]
        target_id = request["target_id"]
        if receipt.get("result_id") != result["result_id"]:
            raise ValidationError("receipt must identify the result of its own request")
        if envelope["canon_revision"] != BASE_REVISION or envelope["canon_hash"] != expected_canon_hash:
            raise ValidationError("parent canon revision or actual source-file hash mismatch")
        if receipt.get("canon_hash_basis") != CAP_SPEC:
            raise ValidationError("receipt must name the actual parent capability hash basis")
        if (envelope["research_target"] != target_id or envelope["capability_id"] != request["capability_id"]
                or envelope["capability_contract_version"] != request.get("capability_version")
                or envelope["provider_runtime"] != request["runtime"]
                or envelope["A0_asset_form"] != targets[target_id]["asset_form"]
                or date_time(envelope["as_of"]) != cutoff or date_time(envelope["evidence_cutoff"]) != cutoff):
            raise ValidationError("receipt invocation envelope does not match its request and target")
        identification = result["state"]["identification_status"]
        degrade = nonempty_strings(receipt["degrade_state"], "receipt degrade state")
        if set(degrade) != {"research_only", identification, "insufficient_evidence"}:
            raise ValidationError("receipt must preserve all research-only degradation states")
        if (receipt.get("identification_status") != identification
                or receipt.get("input_snapshot_hash") != inputs_by_request[request_id]["input_manifest_hash"]
                or receipt.get("parameter_region_ref") != result["result_id"] + "#state.assumption_regions"):
            raise ValidationError("receipt state, input snapshot, or parameter-region reference mismatch")
        evidence_refs = nonempty_strings(receipt["evidence_refs"], "receipt evidence references")
        if set(evidence_refs) != set(result["state"]["evidence_refs"]):
            raise ValidationError("receipt evidence differs from its result")
        for field in ("algorithm_family", "output_state_version"):
            if not isinstance(receipt[field], str) or not receipt[field].strip():
                raise ValidationError(f"empty receipt field: {field}")
        if receipt["algorithm_family"] != result["state"].get("model_family"):
            raise ValidationError("receipt algorithm differs from its result")
        consumer_refs = nonempty_strings(receipt.get("consumer_thesis_refs"), "receipt consumer theses")
        target_theses = {tid for tid, thesis in theses.items() if thesis["target_id"] == target_id}
        if set(consumer_refs) != target_theses or receipt.get("engine_thesis_id") not in target_theses:
            raise ValidationError("receipt thesis references must belong to the same target")
        if receipt.get("primary_engine") != theses[receipt["engine_thesis_id"]]["identity_core"]["primary_engine"]:
            raise ValidationError("receipt primary engine differs from its named thesis")
