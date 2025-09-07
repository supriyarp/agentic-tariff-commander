from __future__ import annotations
from typing import List, Dict
from .models import DecisionRecord, HTSClassification, SourcingOption, TariffChangeEvent
from .data_loader import DataStore
from .policy import Policy
from .sourcing import top3_options

AUDIT_LOG: List[DecisionRecord] = []
REVIEW_QUEUE: Dict[str, HTSClassification] = {}      # sku -> classification needing review
APPROVED_HTS_CONF: Dict[str, float] = {}             # sku -> approved confidence override

def naive_classifier(sku: str, hts_code: str) -> HTSClassification:
    # override if user approved previously
    if sku in APPROVED_HTS_CONF:
        return HTSClassification(sku=sku, hts_code=hts_code, confidence=APPROVED_HTS_CONF[sku], rationale="Approved by reviewer")

    # toy heuristic: known-length codes get higher conf
    conf = 0.93 if hts_code and len(hts_code) >= 6 else 0.82
    return HTSClassification(sku=sku, hts_code=hts_code, confidence=conf, rationale="few-shot match (demo)")

def get_review_queue() -> List[HTSClassification]:
    return list(REVIEW_QUEUE.values())

def approve_hts(sku: str, new_conf: float = 0.95) -> None:
    APPROVED_HTS_CONF[sku] = new_conf
    if sku in REVIEW_QUEUE:
        del REVIEW_QUEUE[sku]

def handle_event(ds: DataStore, pol: Policy, event: TariffChangeEvent, base_route="R-CN-US", price_usd=25.0) -> List[DecisionRecord]:
    skus = ds.get_skus_by_hs(event.hs_code)
    decisions: List[DecisionRecord] = []

    # clear old queue; it will be repopulated this run
    REVIEW_QUEUE.clear()

    for sku in skus:
        comps = ds.get_components(sku)
        cls = naive_classifier(sku, str(comps.iloc[0]["hts_code"]))
        if cls.confidence < 0.9:
            REVIEW_QUEUE[sku] = cls

        options = top3_options(ds, sku, base_route, event, price_usd)
        best: SourcingOption | None = options[0] if options else None

        action = {
            "sku": sku,
            "delta_margin_pp": (0.0 if best is None else ( -best.cost_delta )), # convert penalty back to Δmargin (approx)
            "lead_time_days": 0.0 if best is None else best.lead_time_delta,
            "risk_score": 100.0 if best is None else best.risk_score,
            "hts_confidence": cls.confidence,
            "regulatory_change_type": event.regulatory_change_type,
        }
        outcome = pol.policy_check(action)

        if outcome.allowed and best:
            decisions.append(DecisionRecord(sku=sku, event=event, chosen=best, auto_executed=True, reason=outcome.reason))
        else:
            decisions.append(DecisionRecord(sku=sku, event=event, chosen=best, auto_executed=False, reason=outcome.reason))

    AUDIT_LOG.extend(decisions)
    return decisions
