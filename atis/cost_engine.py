from __future__ import annotations
from typing import Dict
import json
from .data_loader import DataStore
from .models import CostBreakdown, TariffChangeEvent

def _duty_on_value(value_usd: float, rate_pct: float) -> float:
    return value_usd * (rate_pct/100.0)

def compute_cost_for_route(ds: DataStore, sku: str, route_id: str, event: TariffChangeEvent | None) -> Dict[str, float]:
    comps = ds.get_components(sku)
    materials = float((comps["qty_per"] * comps["unit_cost_usd"]).sum())
    freight = 0.05 * materials  # toy assumption; replace with your own model
    duties = 0.0

    legs = ds.routes.set_index("route_id").loc[route_id, "legs"]
    if isinstance(legs, str):
        legs = json.loads(legs)

    value = materials + freight
    # Use affected HS from event or first component HS
    hs = str(event.hs_code) if event else str(comps.iloc[0]["hts_code"])

    for leg in legs:
        origin, dest = leg.split("->")
        rate = ds.latest_tariff(hs, origin, dest)
        duty = _duty_on_value(value, rate)
        duties += duty
        value += duty  # duty-on-duty

    cogs = materials + freight + duties
    return {"materials": materials, "freight": freight, "duties": duties, "cogs": cogs}

def compare_base_vs_option(ds: DataStore, sku: str, base_route: str, opt_route: str, price_usd: float, event: TariffChangeEvent | None):
    base = compute_cost_for_route(ds, sku, base_route, event)
    opt  = compute_cost_for_route(ds, sku, opt_route, event)

    margin_base = (price_usd - base["cogs"]) / price_usd
    margin_opt  = (price_usd - opt["cogs"]) / price_usd
    margin_pp_delta = (margin_opt - margin_base) * 100.0

    # Lead-time proxy: use origin country’s mean lead time
    base_legs = ds.routes.set_index("route_id").loc[base_route, "legs"]
    if isinstance(base_legs, str): base_legs = json.loads(base_legs)
    base_origin = base_legs[0].split("->")[0]

    opt_legs = ds.routes.set_index("route_id").loc[opt_route, "legs"]
    if isinstance(opt_legs, str): opt_legs = json.loads(opt_legs)
    opt_origin = opt_legs[0].split("->")[0]

    lt_base = float(ds.suppliers[ds.suppliers["country"] == base_origin]["lead_time_days"].mean())
    lt_opt  = float(ds.suppliers[ds.suppliers["country"] == opt_origin]["lead_time_days"].mean())
    eta_delta = lt_opt - lt_base

    return CostBreakdown(
        sku=sku, cogs_usd=opt["cogs"], margin_pp_delta=margin_pp_delta,
        eta_days_delta=eta_delta, components=opt
    )
