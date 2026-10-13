import json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from radar_core import build_report, confidence, historical_growth, job_summary, markdown_report, normalize

class PipelineTests(unittest.TestCase):
    def test_normalize_preserves_missing_and_strips_tracking(self):
        r = normalize({"source":"x","url":"HTTPS://Example.com/a/?utm_source=x","title":" T "})
        self.assertEqual(r["canonical_url"], "https://example.com/a")
        self.assertIsNone(r["published_at"])

    def test_dedup_and_independence(self):
        rows=[{"source":"a","source_type":"research","id":"1","url":"https://x.test/a","title":"x","skills":["s"]},{"source":"b","source_type":"research","id":"1","url":"https://x.test/a?utm_medium=y","title":"x","skills":["s"]}]
        report=build_report(rows)
        self.assertEqual(len(report["records"]),1)
        self.assertEqual(report["skills"][0]["independent_source_types"],1)

    def test_historical_growth_and_zero_baseline(self):
        self.assertEqual(historical_growth([{"published_at":"2026-01-01","metrics":{"activity":10}},{"published_at":"2026-02-01","metrics":{"activity":20}}]),100)
        self.assertIsNone(historical_growth([{"published_at":"2026-01-01","metrics":{"activity":0}},{"published_at":"2026-02-01","metrics":{"activity":20}}]))

    def test_missing_dimensions_are_not_filled(self):
        skill=build_report([{"source":"x","source_type":"research","title":"x","skills":["s"],"metrics":{"trend":80}}])["skills"][0]
        self.assertIsNone(skill["scores"]["learning"])
        self.assertLess(skill["coverage"],1)

    def test_confidence_is_not_score(self):
        self.assertEqual(confidence([],1),"Insufficient Evidence")

    def test_job_growth_requires_comparable_baseline(self):
        available = job_summary([{"source_name":"linkedin-export","source_type":"jobs","metrics":{"job_count":150,"previous_job_count":100}}])
        self.assertEqual(available["growth_pct"], 50)
        unavailable = job_summary([])
        self.assertEqual(unavailable["status"], "Unavailable")

    def test_report_exposes_rating_and_jobs(self):
        report = build_report([{"source":"x","source_type":"implementation","title":"tool","skills":["s"],"metrics":{"trend":80,"current_value":80,"future":80,"learning":80}}, {"source":"jobs","source_type":"jobs","title":"roles","skills":["s"],"metrics":{"job_count":10,"previous_job_count":5}}])
        self.assertEqual(report["skills"][0]["rating"], "Excellent")
        self.assertEqual(report["skills"][0]["jobs"]["current_postings"], 10)

    def test_every_displayed_skill_has_detail_report(self):
        report = build_report([{"source":"x","source_type":"implementation","title":"tool","skills":["s"],"metrics":{"trend":80,"current_value":80,"future":80,"learning":80}}])
        rendered = markdown_report(report, limit=5)
        self.assertIn("## Detailed skill reports", rendered)
        self.assertIn("### s", rendered)
        self.assertIn("**Confidence:**", rendered)

if __name__ == "__main__": unittest.main()
