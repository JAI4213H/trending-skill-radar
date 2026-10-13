"""Small, opt-in collectors for documented JSON APIs; never scrapes pages."""
from __future__ import annotations
import json, os, random, time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

class CollectionError(RuntimeError): pass

def fetch_json(url: str, headers: dict[str, str] | None = None, timeout: float = 15, retries: int = 2) -> dict:
    for attempt in range(retries + 1):
        try:
            req = Request(url, headers={"User-Agent": "trending-skill-radar/0.1 (+local research tool)", **(headers or {})})
            with urlopen(req, timeout=timeout) as response: return json.load(response)
        except HTTPError as exc:
            if exc.code == 429 and attempt < retries:
                try: delay = min(30, float(exc.headers.get("Retry-After", "1")))
                except ValueError: delay = 1
            elif 500 <= exc.code < 600 and attempt < retries: delay = 2 ** attempt + random.random()
            else: raise CollectionError(f"HTTP {exc.code} from {url}") from exc
        except URLError as exc:
            if attempt >= retries: raise CollectionError(f"network failure from {url}") from exc
            delay = 2 ** attempt + random.random()
        time.sleep(delay)
    raise CollectionError(f"collection failed after {retries + 1} attempts")

def collect_openalex(query: str, per_page: int = 25) -> list[dict]:
    mailto = os.getenv("OPENALEX_MAILTO")
    url = "https://api.openalex.org/works?search=" + query.replace(" ", "+") + f"&per-page={min(per_page, 100)}"
    if mailto: url += "&mailto=" + mailto
    data = fetch_json(url)
    return [{"source_name":"openalex", "source_type":"research", "source_tier":"scholarly index", "original_source_id":x.get("id"), "title":x.get("title"), "published_at":x.get("publication_date"), "source_url":x.get("doi") or x.get("id"), "metrics":{"citations":x.get("cited_by_count")}} for x in data.get("results", [])]

def collect_github(query: str, per_page: int = 25) -> list[dict]:
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept":"application/vnd.github+json"}
    if token: headers["Authorization"] = f"Bearer {token}"
    url = "https://api.github.com/search/repositories?q=" + query.replace(" ", "+") + f"&per_page={min(per_page, 100)}"
    data = fetch_json(url, headers)
    return [{"source_name":"github", "source_type":"implementation", "source_tier":"implementation", "original_source_id":x.get("full_name"), "title":x.get("name"), "description_or_abstract":x.get("description") or "", "source_url":x.get("html_url"), "source_updated_at":x.get("updated_at"), "metrics":{"stars":x.get("stargazers_count"), "activity":x.get("forks_count")}} for x in data.get("items", [])]
