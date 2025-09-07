from __future__ import annotations
from typing import Optional, List
from .models import TariffChangeEvent
from .data_loader import DataStore

# Production-style watcher (optional live-lite)
from .watcher import WatcherConfig, Source, run_once as watcher_run_once

def next_demo_event(ds: DataStore, scenario_id: int = 1) -> TariffChangeEvent:
    row = ds.scenarios[ds.scenarios["id"] == scenario_id].iloc[0]
    return TariffChangeEvent(
        hs_code=str(row["affected_hs"]),
        origin=row["origin"],
        destination="US",
        new_rate_pct=float(row["new_rate_pct"]),
        effective_date=str(row["start_date"]),
        regulatory_change_type="tariff_increase",
        source="demo:scenarios.csv"
    )

def try_live_feed(dest: str = "US") -> Optional[TariffChangeEvent]:
    """
    Live-lite: poll a tiny whitelist of stable feeds (RSS/JSON). 
    If nothing confident is found, return None (the app should fallback to the demo scenario).
    """
    cfg = WatcherConfig(
        sources=[
            # Replace/augment with known-stable official feeds in your org
            Source(name="USTRPressRSS", kind="rss", url="https://ustr.gov/feeds/press-releases/rss.xml", hs_hint=None),
            # Source(name="EUCustomsRSS", kind="rss", url="https://ec.europa.eu/taxation_customs/rss.xml", hs_hint=None),
        ],
        destination=dest,
        cache_path="./cache/watch_cache.jsonl",
        timeout_s=2.0,
        retries=1
    )
    try:
        events: List[TariffChangeEvent] = watcher_run_once(cfg)
        return events[0] if events else None
    except Exception:
        return None
