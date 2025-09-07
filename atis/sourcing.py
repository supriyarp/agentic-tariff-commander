from __future__ import annotations
from typing import List
import json
from .models import SourcingOption
from .data_loader import DataStore
from .cost_engine import compare_base_vs_option
from yaml import safe_load

def _load_weights(policy_yaml_path: str = "./data/policy.yaml"):
    try:
        with open(policy_yaml_path, "r") as f:
            cfg = safe_load(f)
            return cfg.get("scoring_weights", {"cost_delta":0.5,"lead_time_delta":0.25,"compliance_risk":0.25})
    except Exception:
        return {"cost_delta":0.5,"lead_time_delta":0.25,"compliance_risk":0.25}

def top3_options(ds: DataStore, sku: str, base_route: str, event, price_usd: float) -> List[SourcingOption]:
    weights = _load_weights()
    routes = ds.routes["route_id"].tolist()
    candidates = [r for r in routes if r != base_route]

    out: List[SourcingOption] = []
    for r in candidates:
        cbd = compare_base_vs_option(ds, sku, base_route, r, price_usd, event)
        # positive margin_pp_delta = better margin vs base (good).
        # convert into a "penalty-like" cost_delta so LOW is better:
        cost_delta = max(0.0, -cbd.margin_pp_delta)  # improvement => 0, worse => positive penalty

        legs = ds.routes.set_index("route_id").loc[r, "legs"]
        if isinstance(legs, str): legs = json.loads(legs)
        origin = legs[0].split("->")[0]

        # demo compliance proxy
        compliance_risk = 10 if origin in ("US","MX") else 25 if origin=="VN" else 35

        # normalized simple score (lower better)
        score = (weights["cost_delta"] * cost_delta
                 + weights["lead_time_delta"] * abs(cbd.eta_days_delta)
                 + weights["compliance_risk"] * (compliance_risk/10.0))

        out.append(SourcingOption(
            sku=sku, supplier_id=f"auto-{origin}", route_id=r,
            cost_delta=cost_delta, lead_time_delta=cbd.eta_days_delta,
            risk_score=float(compliance_risk),
            explanation=f"Cost penalty≈{cost_delta:.2f}pp, LeadΔ={cbd.eta_days_delta:.1f}d, Origin={origin}"
        ))

    out.sort(key=lambda o: (o.cost_delta*0.5) + (abs(o.lead_time_delta)*0.25) + ((o.risk_score/10.0)*0.25))
    return out[:3]
