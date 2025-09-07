from __future__ import annotations
import hashlib, json, re, time
from dataclasses import dataclass
from typing import Iterable, List, Optional, Dict, Any
import httpx, feedparser

from .models import TariffChangeEvent

# --- Utilities ---
def _hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

def _save_jsonl(path: str, rec: Dict[str, Any]) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def _load_seen(path: str) -> set[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return {json.loads(line).get("_id","") for line in f if line.strip()}
    except FileNotFoundError:
        return set()

# --- Config ---
@dataclass
class Source:
    name: str
    kind: str            # "rss" | "json" | "html" (keep rss/json for demo)
    url: str
    hs_hint: Optional[str] = None

@dataclass
class WatcherConfig:
    sources: List[Source]
    destination: str = "US"
    cache_path: str = "./cache/watch_cache.jsonl"
    timeout_s: float = 2.0
    retries: int = 1

# --- Parser: turn messy text into a candidate event ---
HS_PAT = re.compile(r"\b(HS|HTS)\s*([0-9]{4,8})\b", re.IGNORECASE)
PCT_PAT = re.compile(r"(\+|-)?\s*([0-9]{1,2}(\.[0-9]+)?)\s?%")
COUNTRY_PAT = re.compile(r"\b(China|CN|Vietnam|VN|Mexico|MX|United States|US|EU)\b", re.IGNORECASE)

COUNTRY_MAP = {
    "cn":"CN","china":"CN",
    "vn":"VN","vietnam":"VN",
    "mx":"MX","mexico":"MX",
    "us":"US","united states":"US",
    "eu":"EU"
}

def normalize_to_event(text: str,
                       hs_hint: Optional[str],
                       default_dest: str = "US") -> tuple[Optional[TariffChangeEvent], float, Dict[str, Any]]:
    text_l = text.lower()

    # HS code
    hs_match = HS_PAT.search(text)
    hs_code = hs_match.group(2) if hs_match else (hs_hint if hs_hint else None)

    # percent
    pct_match = PCT_PAT.search(text)
    pct = float(pct_match.group(2)) if pct_match else None
    # crude heuristic: if text contains "increase", keep pct pos; if "decrease"/"cut", make negative (we still store positive in event.new_rate_pct)
    change_type = "tariff_increase" if "increase" in text_l or "+" in (pct_match.group(1) if pct_match else "") else "tariff_decrease" if "decrease" in text_l or "cut" in text_l else "tariff_increase"

    # origin/destination guesses
    # first country mention is origin; destination defaults to US for the workshop
    cands = COUNTRY_PAT.findall(text)
    origin = None
    if cands:
        for c in cands:
            k = c[0].lower()
            origin = COUNTRY_MAP.get(k, None)
            if origin:
                break

    # crude confidence
    conf = 0.0
    if hs_code: conf += 0.4
    if pct is not None: conf += 0.3
    if origin: conf += 0.2
    if "tariff" in text_l or "duty" in text_l: conf += 0.1
    conf = min(conf, 0.99)

    meta = {"hs_code_found": bool(hs_match), "pct_found": bool(pct_match), "origin_found": bool(origin), "raw": text[:280]}

    if not hs_code or pct is None or conf < 0.6:
        return (None, conf, meta)

    ev = TariffChangeEvent(
        hs_code=str(hs_code),
        origin=origin or "CN",
        destination=default_dest,
        new_rate_pct=abs(pct),  # store magnitude
        effective_date="(unknown)",
        regulatory_change_type=change_type,
        source="watcher:normalized"
    )
    return (ev, conf, meta)

# --- Fetchers ---
def _fetch_rss(url: str, timeout: float) -> List[Dict[str, Any]]:
    feed = feedparser.parse(url)
    out = []
    for e in feed.entries[:10]:
        title = getattr(e, "title", "")
        summary = getattr(e, "summary", "")
        out.append({"title": title, "summary": summary})
    return out

def _fetch_json(url: str, timeout: float) -> Any:
    with httpx.Client(timeout=timeout) as client:
        r = client.get(url)
        r.raise_for_status()
        return r.json()

# --- Main watcher run ---
def run_once(cfg: WatcherConfig) -> List[TariffChangeEvent]:
    seen = _load_seen(cfg.cache_path)
    emitted: List[TariffChangeEvent] = []

    for src in cfg.sources:
        data_items = []
        for attempt in range(cfg.retries + 1):
            try:
                if src.kind == "rss":
                    data_items = _fetch_rss(src.url, cfg.timeout_s)
                elif src.kind == "json":
                    data_items = _fetch_json(src.url, cfg.timeout_s)
                    # expect a list of dicts with "title"/"summary" keys; adapt if needed
                    if isinstance(data_items, dict):  # try typical "items" key
                        data_items = data_items.get("items", [])
                else:
                    data_items = []
                break
            except Exception:
                if attempt >= cfg.retries:
                    data_items = []
                else:
                    time.sleep(0.2)

        # normalize
        for item in data_items:
            text = (item.get("title","") + " " + item.get("summary","")).strip()
            if not text:
                continue
            _id = _hash(src.name + "|" + text)
            if _id in seen:
                continue

            ev, conf, meta = normalize_to_event(text, hs_hint=src.hs_hint, default_dest=cfg.destination)
            rec = {"_id": _id, "source": src.name, "text": text, "confidence": conf, "meta": meta}
            _save_jsonl(cfg.cache_path, rec)
            seen.add(_id)

            # emit only if confident enough; otherwise your demo can show it in a triage list
            if ev and conf >= 0.75:
                emitted.append(ev)

    return emitted
