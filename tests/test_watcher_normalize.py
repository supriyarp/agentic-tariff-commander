from atis.watcher import normalize_to_event

def test_normalize_basic():
    text = "US announces 25% tariff increase on HS 870830 for imports from China starting Sept."
    ev, conf, meta = normalize_to_event(text, hs_hint=None)
    assert ev is not None
    assert ev.hs_code == "870830"
    assert ev.origin == "CN"
    assert ev.new_rate_pct == 25
    assert conf >= 0.75

if __name__ == "__main__":
    test_normalize_basic()
    print("✅ All tests passed!")
