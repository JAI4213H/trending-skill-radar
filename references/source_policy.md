# Source policy

Use official APIs, feeds, public documentation, or user-supplied records. Hugging Face trending and GitHub Trending are discovery surfaces, not proof of adoption. Deduplicate papers across arXiv, scholarly indexes, and reposts. Never scrape Google Scholar or LinkedIn without an explicitly permitted interface. Respect terms, rate limits, cache policy, request timeouts, bounded retries, and source-specific attribution.

Collection failures must be visible and must not be represented as successful empty results. The local core accepts evidence records and deliberately does not execute source-provided code.

### Employment evidence

LinkedIn is not scraped. Employment demand may be reported only from an official/authorized API, licensed provider, public dataset with compatible terms, or records/links supplied and verified by the user. Report the source, collection date, geography, role level, deduplicated posting count, and comparison window. Expected growth is a descriptive change between comparable windows—not a forecast—unless a validated forecasting method and horizon are explicitly provided. Otherwise show `Unavailable`.
