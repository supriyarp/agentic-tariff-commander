from __future__ import annotations
from typing import Dict, Any
import yaml
from .models import PolicyOutcome

class Policy:
    def __init__(self, path: str = "./data/policy.yaml"):
        with open(path, "r") as f:
            self.cfg = yaml.safe_load(f)

    def policy_check(self, action: Dict[str, Any]) -> PolicyOutcome:
        # action: {delta_margin_pp, lead_time_days, risk_score, hts_confidence, regulatory_change_type}
        auto = self.cfg["auto_execute_if"]
        req  = self.cfg["requires_approval_if"]

        if action.get("regulatory_change_type") in set(req.get("regulatory_change_type", [])):
            return PolicyOutcome(allowed=False, reason="Structural/ambiguous change requires approval")

        if action.get("hts_confidence") is not None and action["hts_confidence"] < 0.9:
            return PolicyOutcome(allowed=False, reason="HTS confidence below 0.9")

        if (abs(action.get("delta_margin_pp", 0)) <= auto["margin_hit_pp_lt"]
            and abs(action.get("lead_time_days", 0)) <= auto["lead_time_increase_days_lt"]
            and action.get("risk_score", 100) <= auto["supplier_switch_risk_score_lt"]):
            return PolicyOutcome(allowed=True, reason="Within auto-exec thresholds")

        return PolicyOutcome(allowed=False, reason="Outside auto thresholds — approval needed")
