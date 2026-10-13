"""Deterministic, dependency-free evidence pipeline used by the CLI and tests."""
from __future__ import annotations
import hashlib, json, re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

METHODOLOGY_VERSION = "2026.10"
DIMENSIONS = ("trend", "current_value", "future", "learning")
WEIGHTS = {"trend": .30, "current_value": .25, "future": .25, "learning": .20}

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def canonical_url(url: str | None) -> str | None:
    if not url: return None
    p = urlsplit(url.strip())
    query = [(k, v) for k, v in parse_qsl(p.query) if not (k.lower().startswith("utm_") or k.lower() in {"ref", "source"})]
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), urlencode(query), ""))

def stable_id(*parts: object) -> str:
    return hashlib.sha256("|".join(str(x or "") for x in parts).encode()).hexdigest()[:20]

def normalize(record: dict, collected_at: str | None = None) -> dict:
    url = canonical_url(record.get("canonical_url") or record.get("source_url") or record.get("url"))
    source = record.get("source_name") or record.get("source") or "unknown"
    title = (record.get("title") or "").strip()
    evidence_id = record.get("evidence_id") or record.get("id") or stable_id(source, record.get("original_source_id") or url or title)
    out = {
        "schema_version": "1.0", "evidence_id": evidence_id, "source_name": source,
        "source_type": record.get("source_type") or "other", "source_url": record.get("source_url") or url,
        "canonical_url": url, "title": title, "description_or_abstract": record.get("description_or_abstract") or record.get("abstract") or "",
        "author_or_organization": record.get("author_or_organization") or record.get("authors") or record.get("organization"),
        "published_at": record.get("published_at") or record.get("published") or None,
        "source_updated_at": record.get("source_updated_at") or record.get("updated_at") or None,
        "collected_at": record.get("collected_at") or collected_at or utc_now(),
        "retrieved_at": record.get("retrieved_at") or collected_at or utc_now(),
        "source_tier": record.get("source_tier") or "secondary", "claim_type": record.get("claim_type") or "discovery",
        "related_skill_ids": list(record.get("related_skill_ids") or record.get("skills") or []),
        "metrics": dict(record.get("metrics") or {}), "original_source_id": record.get("original_source_id") or record.get("id"),
        "origin_group_id": record.get("origin_group_id"), "verification_status": record.get("verification_status") or "unverified",
        "peer_review_status": record.get("peer_review_status"), "license_or_access_notes": record.get("license_or_access_notes"),
        "counterevidence": bool(record.get("counterevidence", False)),
    }
    return out

def normalize_many(records: list[dict]) -> list[dict]: return [normalize(r) for r in records]

def deduplicate(records: list[dict]) -> list[dict]:
    seen, result = {}, []
    for r in records:
        key = (r.get("original_source_id") or r.get("canonical_url") or stable_id(r.get("title"), r.get("description_or_abstract")))
        if key in seen:
            result[seen[key]].setdefault("duplicate_source_names", []).append(r.get("source_name"))
            continue
        r = dict(r); r["origin_group_id"] = r.get("origin_group_id") or stable_id(key)
        seen[key] = len(result); result.append(r)
    return result

def _number(r: dict, name: str) -> float | None:
    value = r.get(name, r.get("metrics", {}).get(name))
    try: return None if value is None else max(0.0, min(100.0, float(value)))
    except (TypeError, ValueError): return None

def confidence(records: list[dict], coverage: float) -> str:
    families = {r.get("source_type") or r.get("source_name") for r in records}
    contradictions = sum(bool(r.get("counterevidence")) for r in records)
    if coverage < .60 or not records: return "Insufficient Evidence"
    if len(families) >= 3 and contradictions == 0 and coverage >= .80: return "High"
    if len(families) >= 2: return "Medium"
    return "Low"

def historical_growth(records: list[dict]) -> float | None:
    snapshots = []
    for r in records:
        date = r.get("published_at") or r.get("source_updated_at")
        value = _number(r, "activity")
        if date and value is not None: snapshots.append((date[:10], value))
    if len(snapshots) < 2: return None
    snapshots.sort(); first, last = snapshots[0][1], snapshots[-1][1]
    if first <= 0: return None
    return round((last - first) / first * 100, 2)

def job_summary(records: list[dict]) -> dict:
    jobs = [r for r in records if r.get("source_type") in {"jobs", "labor_market"}]
    current = sum(float(r.get("metrics", {}).get("job_count", 0) or 0) for r in jobs)
    previous = sum(float(r.get("metrics", {}).get("previous_job_count", 0) or 0) for r in jobs)
    expected = [r.get("metrics", {}).get("expected_growth_pct") for r in jobs if r.get("metrics", {}).get("expected_growth_pct") is not None]
    horizon = next((r.get("metrics", {}).get("forecast_horizon") for r in jobs if r.get("metrics", {}).get("forecast_horizon")), None)
    if not jobs or current <= 0:
        return {"status": "Unavailable", "source": None, "current_postings": None, "growth_pct": None, "expected_growth_pct": None, "forecast_horizon": None}
    growth = None if previous <= 0 else round((current - previous) / previous * 100, 2)
    return {"status": "Available", "source": ", ".join(sorted({r.get("source_name", "unknown") for r in jobs})), "current_postings": int(current), "growth_pct": growth, "expected_growth_pct": sum(expected) / len(expected) if expected else None, "forecast_horizon": horizon}

def rating(value: float | None) -> str:
    if value is None: return "Insufficient Evidence"
    return "Excellent" if value >= 80 else "Strong" if value >= 65 else "Developing" if value >= 50 else "Weak"

def score_skill(skill_id: str, records: list[dict], profile: dict | None = None) -> dict:
    vals = {d: [_number(r, d) for r in records if _number(r, d) is not None] for d in DIMENSIONS}
    observed = {d: (sum(v)/len(v) if v else None) for d, v in vals.items()}
    # Learning is a distinct dimension; profile adjustment is explicit and bounded.
    if profile and observed["learning"] is not None:
        readiness = float(profile.get("readiness", 50)); goal = float(profile.get("goal_relevance", 50))
        observed["learning"] = round((observed["learning"] + readiness + goal) / 3, 2)
    present = [d for d, v in observed.items() if v is not None]
    coverage = sum(WEIGHTS[d] for d in present)
    total = round(sum(observed[d] * WEIGHTS[d] for d in present) / coverage, 2) if coverage else None
    growth = historical_growth(records)
    stage = "Insufficient Evidence" if coverage < .60 else ("Accelerating" if growth is not None and growth >= 50 else "Emerging" if growth is not None and growth > 0 else "Early Signal")
    return {"skill_id": skill_id, "scores": observed, "overall": total, "coverage": round(coverage, 2), "confidence": confidence(records, coverage), "independent_source_types": len({r.get("source_type") for r in records}), "historical_growth_pct": growth, "maturity_stage": stage, "methodology_version": METHODOLOGY_VERSION, "evidence_ids": [r["evidence_id"] for r in records]}

def build_report(records: list[dict], profile: dict | None = None) -> dict:
    unique = deduplicate(normalize_many(records)); grouped = defaultdict(list)
    for r in unique:
        for skill in r.get("related_skill_ids") or ["unclassified"]: grouped[skill].append(r)
    scores = [score_skill(skill, rs, profile) for skill, rs in grouped.items()]
    for score in scores:
        score["recommendation"] = recommendation(score)
        score["rating"] = rating(score["overall"])
        score["jobs"] = job_summary(next((rs for skill, rs in grouped.items() if skill == score["skill_id"]), []))
    scores.sort(key=lambda x: (x["overall"] is not None, x["overall"] or -1), reverse=True)
    return {"methodology_version": METHODOLOGY_VERSION, "generated_at": utc_now(), "records": unique, "skills": scores,
            "jobs": job_summary(unique), "coverage": {"input_records": len(records), "unique_records": len(unique), "source_types": sorted({r.get("source_type") for r in unique}), "failed_sources": []}}

def recommendation(score: dict) -> str:
    if score["confidence"] == "Insufficient Evidence": return "Monitor"
    current, learning = score["scores"].get("current_value"), score["scores"].get("learning")
    if current is not None and current >= 70 and (learning is None or learning >= 60): return "Learn Now"
    if score["scores"].get("trend") is not None and score["scores"]["trend"] >= 60: return "Explore Next"
    return "Monitor"

def _fmt(value: float | None) -> str:
    return "Insufficient Evidence" if value is None else f"{value:.1f}"

def markdown_report(report: dict, limit: int = 5) -> str:
    limit = max(1, limit); skills = report["skills"][:limit]
    global_rank = sorted(report["skills"], key=lambda x: (x["scores"].get("trend") is not None, x["scores"].get("trend") or -1), reverse=True)[:limit]
    emerging = [s["skill_id"] for s in global_rank if s["maturity_stage"] in {"Early Signal", "Emerging", "Accelerating"}]
    valuable = [s["skill_id"] for s in skills if (s["scores"].get("current_value") or 0) >= 70]
    jobs = report.get("jobs", {})
    job_text = "Unavailable" if jobs.get("status") != "Available" else f"{jobs['current_postings']} postings from {jobs['source']}; comparable-window change: {('Unavailable' if jobs['growth_pct'] is None else str(jobs['growth_pct']) + '%')}; expected growth: {('Unavailable' if jobs.get('expected_growth_pct') is None else str(round(jobs['expected_growth_pct'], 1)) + '% over ' + str(jobs.get('forecast_horizon') or 'unspecified horizon'))}"
    lines = [f"# AI Skill Radar — {report['generated_at'][:10]}", "", f"**Methodology version:** {report['methodology_version']}", f"**Collection status:** {len(report['records'])} normalized records; source failures: {', '.join(report['coverage']['failed_sources']) or 'none reported'}", "", "## Executive summary", "", f"- **Strongest emerging candidates:** {', '.join(emerging) or 'Insufficient Evidence'}.", f"- **Most valuable to investigate now:** {', '.join(valuable) or 'Insufficient Evidence'}.", f"- **Promising early-stage directions:** {', '.join([s['skill_id'] for s in global_rank if s['maturity_stage'] == 'Early Signal']) or 'Insufficient Evidence'}.", f"- **Employment signal:** {job_text}. Do not infer LinkedIn-wide demand from research or developer activity.", "- **Biggest limitation:** Scores depend on supplied evidence, and missing dimensions remain unavailable.", f"- **Next action:** Investigate the top candidate's linked implementation and build a small measurable project; current recommendation is **{skills[0]['recommendation'] if skills else 'Monitor'}**.", "", "An emerging trend is not the same as an established skill that remains valuable; the rankings below keep those judgments separate.", "", "## Top skill candidates", "", f"Maximum candidates shown: {limit}. **Methodology:** {report['methodology_version']}.", "", "| Rank | Skill | Rating | Maturity stage | Trend score | Current value | Future potential | Current jobs | Confidence | Evidence coverage | Recommendation |", "|---:|---|---|---|---:|---:|---:|---|---|---:|---|"]
    for rank, s in enumerate(skills, 1):
        v=s["scores"]
        jobs_for_skill = s.get("jobs", {})
        jobs_text = "Unavailable" if jobs_for_skill.get("status") != "Available" else str(jobs_for_skill.get("current_postings")) + " (" + ("growth unavailable" if jobs_for_skill.get("growth_pct") is None else str(jobs_for_skill["growth_pct"]) + "% window change") + ")"
        lines.append(f"| {rank} | {s['skill_id']} | {s['rating']} | {s['maturity_stage']} | {_fmt(v.get('trend'))} | {_fmt(v.get('current_value'))} | {_fmt(v.get('future'))} | {jobs_text} | {s['confidence']} | {s['coverage']:.0%} | {s['recommendation']} |")
    lines += ["", "## Global trend ranking", "", "| Rank | Skill | Trend score | Maturity | Confidence |", "|---:|---|---:|---|---|"]
    for rank, s in enumerate(global_rank, 1): lines.append(f"| {rank} | {s['skill_id']} | {_fmt(s['scores'].get('trend'))} | {s['maturity_stage']} | {s['confidence']} |")
    lines += ["", "## Personal learning ranking", "", "This ranking uses the learner profile when supplied; otherwise it is a general learning-priority ranking.", "", "| Rank | Skill | Learning priority | Current value | Recommendation |", "|---:|---|---:|---:|---|"]
    for rank, s in enumerate(skills, 1): lines.append(f"| {rank} | {s['skill_id']} | {_fmt(s['scores'].get('learning'))} | {_fmt(s['scores'].get('current_value'))} | {s['recommendation']} |")
    lines += ["", "## Detailed skill reports", ""]
    for s in skills:
        evidence = [r for r in report["records"] if r["evidence_id"] in s["evidence_ids"]]
        links = "; ".join(f"[{r['title']}]({r.get('canonical_url')})" if r.get('canonical_url') else f"{r['title']} (link unavailable)" for r in evidence)
        v = s["scores"]; jobs_for_skill = s.get("jobs", {})
        jobs_detail = "Unavailable" if jobs_for_skill.get("status") != "Available" else f"{jobs_for_skill['current_postings']} postings from {jobs_for_skill['source']}; window change: {jobs_for_skill.get('growth_pct') if jobs_for_skill.get('growth_pct') is not None else 'Unavailable'}"
        lines += [f"### {s['skill_id']}", f"- **Rating:** {s['rating']} | **Maturity:** {s['maturity_stage']} | **Recommendation:** {s['recommendation']}", f"- **Scores:** trend {_fmt(v.get('trend'))}; current value {_fmt(v.get('current_value'))}; future potential {_fmt(v.get('future'))}; learning priority {_fmt(v.get('learning'))}.", f"- **Confidence:** {s['confidence']} | **Evidence coverage:** {s['coverage']:.0%} | **Methodology:** {s['methodology_version']}.", f"- **Current jobs:** {jobs_detail}.", f"- **Evidence and links:** {links}.", "- **Practical next step:** use a linked implementation or paper as the basis for a small project with a measurable before/after evaluation; if no adaptation link is available, this is the recommended validation path."]
    lines += ["", "## Method limitations", "", "Scores are deterministic summaries of supplied evidence, not calibrated probabilities. Missing dimensions remain missing; historical growth is unavailable without two dated activity observations. Review source independence, counterevidence, and access restrictions before acting.", "", "## All evidence", ""]
    for r in report["records"]: lines.append(f"- `{r['evidence_id']}` [{r['source_name']}] {r['title']} — {r.get('canonical_url') or 'link unavailable'}")
    return "\n".join(lines) + "\n"
