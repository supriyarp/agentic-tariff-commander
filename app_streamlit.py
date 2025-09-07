from __future__ import annotations
import streamlit as st
from atis.data_loader import DataStore
from atis.policy import Policy
from atis.watcher_demo import next_demo_event, try_live_feed
from atis.orchestrator import handle_event, AUDIT_LOG, get_review_queue, approve_hts

st.set_page_config(page_title="ATIS – Tariff Intelligence", layout="wide")
st.title("ATIS – Agentic Tariff Intelligence System (Demo)")

if "last_event" not in st.session_state:
    st.session_state["last_event"] = None

colL, colC, colR = st.columns([1.2, 1.6, 1.2])

with colL:
    st.subheader("Scenario")
    scenario_id = st.selectbox("Pick a story", options=[1,2,3], index=0)
    price = st.number_input("Assumed Selling Price (USD)", value=25.0, min_value=1.0, step=0.5)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Run Watcher ▶ (Demo)"):
            st.session_state["last_event"] = next_demo_event(DataStore("./data"), scenario_id)
    with c2:
        if st.button("Try Live 🌐 (fallback)"):
            ev = try_live_feed(dest="US")
            if ev is not None:
                st.success("Live-lite watcher found a tariff-like bulletin.")
                st.session_state["last_event"] = ev
            else:
                st.warning("No confident live event — using demo scenario.")
                st.session_state["last_event"] = next_demo_event(DataStore("./data"), scenario_id)
    st.caption("Story 1: CN 870830 +15pp • Story 2: duty-on-duty • Story 3: HTS review")

with colC:
    st.subheader("Before / After & Decisions")
    if st.session_state["last_event"] is None:
        st.info("Click **Run Watcher** or **Try Live** to simulate a tariff bulletin.")
    else:
        ds = DataStore("./data")
        pol = Policy("./data/policy.yaml")
        ev = st.session_state["last_event"]
        decisions = handle_event(ds, pol, ev, base_route="R-CN-US", price_usd=price)

        for d in decisions:
            chosen = d.chosen.route_id if d.chosen else "(no option)"
            st.write(f"**SKU**: {d.sku} • **Route chosen**: `{chosen}` • **Auto**: `{d.auto_executed}` • _{d.reason}_")
        st.success("Run complete. See Top Options & Compliance at right.")

with colR:
    st.subheader("Compliance Queue (HTS Review)")
    queue = get_review_queue()
    if not queue:
        st.write("✅ No items require HTS review (≥ 0.90 confidence).")
    else:
        for item in queue:
            with st.expander(f"{item.sku} • HTS {item.hts_code} • conf {item.confidence:.2f}"):
                st.write(item.rationale or "—")
                if st.button(f"Approve {item.sku}", key=f"approve_{item.sku}"):
                    approve_hts(item.sku, new_conf=0.95)
                    st.toast(f"Approved {item.sku}. Re-run watcher to apply.")
    st.caption("Approving sets confidence to 0.95; re-run to see policy auto-exec kick in where applicable.")

st.divider()
st.subheader("Audit Log (latest)")
for rec in AUDIT_LOG[-12:]:
    st.code(f"{rec.sku} | auto={rec.auto_executed} | reason={rec.reason}")
