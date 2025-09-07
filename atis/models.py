from __future__ import annotations
from pydantic import BaseModel
from typing import Dict, Optional, Literal

class TariffChangeEvent(BaseModel):
    hs_code: str
    origin: str
    destination: str = "US"
    new_rate_pct: float
    effective_date: str
    regulatory_change_type: Literal["tariff_increase","tariff_decrease","structural","ambiguous"] = "tariff_increase"
    source: str = "demo"

class HTSClassification(BaseModel):
    sku: str
    hts_code: str
    confidence: float
    rationale: str = ""

class CostBreakdown(BaseModel):
    sku: str
    cogs_usd: float
    margin_pp_delta: float
    eta_days_delta: float
    components: Dict[str, float]

class SourcingOption(BaseModel):
    sku: str
    supplier_id: str
    route_id: str
    cost_delta: float           # lower is better (we treat this as "penalty")
    lead_time_delta: float      # days (positive = slower)
    risk_score: float           # 0..100 (lower is better)
    explanation: str

class PolicyOutcome(BaseModel):
    allowed: bool
    reason: str

class DecisionRecord(BaseModel):
    sku: str
    event: TariffChangeEvent
    chosen: Optional[SourcingOption]
    auto_executed: bool
    reason: str
