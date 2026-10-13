# Trending Skill Radar

An offline-first Codex skill and small Python toolkit for finding AI/ML/LLM capabilities worth learning. It ranks traceable evidence rather than summarizing headlines.

The implementation is portable across Codex, Claude Code, ChatGPT Projects, and other agent hosts. `SKILL.md` is the Codex entry point, `CLAUDE.md` is the Claude project entry point, and `PORTABLE_PROMPT.md` is the platform-neutral prompt. All hosts share the same dependency-free Python pipeline.

## Install

Copy this directory to a Codex skills directory, for example `~/.codex/skills/trending-skill-radar`, or invoke the included CLI from the checkout. For Claude Code, place the repository in the project and keep `CLAUDE.md`; for ChatGPT or another agent, upload/reference `PORTABLE_PROMPT.md` and the repository. Python 3.10+ is the only runtime requirement. No paid LLM or network access is required for the core pipeline.

## Run

```bash
python scripts/radar.py scan --input tests/fixtures/evidence.json --output report.md
python scripts/radar.py scan --input tests/fixtures/evidence.json --output report.md --limit 5
python -m unittest discover -s tests -v
```

Input is a JSON array of normalized or source-shaped evidence records. Opt-in stdlib collectors currently support documented OpenAlex and GitHub JSON APIs (`scripts/connectors.py`); they use bounded retries and environment-based credentials. arXiv, Semantic Scholar, Hugging Face, job boards, and Google Scholar remain user-supplied or future adapters rather than pretending to have live coverage. No scraping or execution of retrieved code is enabled.

## What it reports

The pipeline deduplicates origins, separates trend/current/future/learning scores, measures historical change only with comparable snapshots, and labels confidence separately from score. Reports include source coverage, counterevidence, limitations, and reproducible methodology version.

See `references/` for source policy, scoring, output, security, evaluation, and the flaw-coverage matrix. The included fixture is synthetic and is not evidence of a real-world trend.

## Public-release status

This checkout is prepared for public release but has not been pushed or published. Optional live connectors need their documented APIs, credentials, and current terms configured by the user.
