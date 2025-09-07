from __future__ import annotations
import pandas as pd
from pathlib import Path

class DataStore:
    def __init__(self, root: str = "./data"):
        p = Path(root)
        self.bom = pd.read_csv(p / "bom.csv")
        self.suppliers = pd.read_csv(p / "suppliers.csv")
        self.routes = pd.read_csv(p / "routes.csv")
        self.tariffs = pd.read_csv(p / "tariffs.csv", parse_dates=["effective_date"])
        self.scenarios = pd.read_csv(p / "scenarios.csv")
        # normalize types
        self.bom["hts_code"] = self.bom["hts_code"].astype(str)

    def get_skus_by_hs(self, hs_code: str):
        return self.bom[self.bom["hts_code"] == str(hs_code)]["sku"].unique().tolist()

    def get_components(self, sku: str):
        return self.bom[self.bom["sku"] == sku].copy()

    def latest_tariff(self, hs_code: str, origin: str, dest: str = "US") -> float:
        df = self.tariffs
        df = df[(df["hs_code"].astype(str) == str(hs_code)) & (df["origin"] == origin) & (df["destination"] == dest)]
        if df.empty:
            return 0.0
        row = df.sort_values("effective_date").iloc[-1]
        return float(row["rate_pct"])
