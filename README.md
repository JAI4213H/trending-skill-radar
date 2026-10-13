<div align="center">

<img src="assets/trending-skill-radar-hero.png" alt="Minimal radar illustration" width="900" />

# Trending Skill Radar

### Find the skills behind the hype.

An evidence-driven radar for deciding what to learn next in AI, ML, and LLM engineering.

[![Tests](https://github.com/JAI4213H/trending-skill-radar/actions/workflows/tests.yml/badge.svg)](https://github.com/JAI4213H/trending-skill-radar/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-22c55e.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3b82f6.svg)](pyproject.toml)

</div>

## The problem

AI moves fast. News moves faster.

Trending Skill Radar separates a headline from a capability, a capability from a learnable skill, and a growing skill from one that is simply useful already.

It answers one practical question:

> **What should I learn next—and what evidence supports that choice?**

## What it gives you

- **Global trend ranking** — what is gaining traction across research, implementations, and official sources.
- **Personal learning ranking** — what is most valuable for a specific learner.
- **Clear comparisons** — trend strength, current value, future potential, confidence, and evidence coverage stay separate.
- **A reality check** — duplicates, missing history, weak evidence, counterevidence, and unavailable job-market data are shown instead of hidden.
- **A next step** — evidence links plus a small project idea to validate the skill in real life.

Recommendations are intentionally concrete: a domain, a capability, a toolchain, and a demonstrable outcome—not vague labels such as “learn AI agents.”

An emerging skill is not automatically the best skill to learn. An established skill can remain highly valuable.

## Quick start

In Codex, activate the skill with:

```text
/trending-skill-radar
```

The skill first asks which domain you want to learn in, unless your request already names one. It then finds specific, demonstrable skills inside that domain.

```bash
python scripts/radar.py scan \
  --input tests/fixtures/evidence.json \
  --output report.md \
  --limit 5
```

The fixture is synthetic and exists only to demonstrate the pipeline. Replace it with normalized records from permitted APIs, browsing, or your own exports.

## The report

Every report includes:

1. Executive summary
2. Top skill candidates
3. Global trend ranking
4. Personal learning ranking
5. Evidence and real-life adaptation ideas
6. Method limitations and source coverage

Scores are deterministic and versioned. Missing evidence is reported as **Insufficient Evidence**—never filled with a guess.

## Sources

The core pipeline works offline and needs no paid model. Optional, documented JSON collectors currently support:

- OpenAlex
- GitHub REST API

arXiv, Semantic Scholar, Hugging Face, job boards, and Google Scholar are intentionally not represented as live coverage unless a permitted connector or user-supplied record is available. No unauthorized scraping or retrieved-code execution is included.

When permitted employment records are supplied, reports include current posting counts and comparable-window change. LinkedIn is never scraped; without an authorized API, licensed dataset, or user-supplied export, job demand and growth are shown as **Unavailable**.

## Use it anywhere

The implementation is platform-neutral:

- **Codex:** use `/trending-skill-radar` or load [`SKILL.md`](SKILL.md)
- **Claude Code:** keep this repository in the project; [`CLAUDE.md`](CLAUDE.md) points to the shared workflow
- **Cursor:** open this repository; [`.cursor/rules/trending-skill-radar.mdc`](.cursor/rules/trending-skill-radar.mdc) provides the rule automatically
- **ChatGPT Projects and other agents:** load [`PORTABLE_PROMPT.md`](PORTABLE_PROMPT.md)
- **Any Python environment:** run the shared CLI and tests

Python 3.10+ is the only required runtime dependency.

## Project map

```text
SKILL.md                 Codex skill entry point
PORTABLE_PROMPT.md       Platform-neutral agent prompt
scripts/radar.py         CLI
scripts/radar_core.py    Normalization, scoring, confidence, reports
scripts/connectors.py    Optional OpenAlex and GitHub collectors
config/                  Source registry and skill taxonomy
references/              Methodology, security, evaluation, limitations
tests/                   Offline fixtures and tests
```

## Trust by design

Third-party text is data, not instructions. Credentials stay in environment variables. Source failures remain visible. Scores do not become facts merely because they look precise.

Read [`SECURITY.md`](SECURITY.md) before enabling external sources.

## Contributing

```bash
python -m unittest discover -s tests -v
```

Keep evidence attributable, changes small, and dependencies minimal. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Status

Ready for public use as an offline-first skill and toolkit. It is not a continuous monitoring service, and it has not been independently validated as a forecasting system.

## License

MIT — see [`LICENSE`](LICENSE).
