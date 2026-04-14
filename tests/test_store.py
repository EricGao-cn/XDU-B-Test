from smog_demo.store import StateStore


def test_store_reads_and_writes_state(tmp_path):
    store = StateStore(tmp_path / "app-state.json")
    store.save_location({"city": "北京"})
    store.save_dashboard({"weatherNow": {"cityName": "北京"}})

    state = store.read()
    assert state["location"]["city"] == "北京"
    assert state["dashboard"]["weatherNow"]["cityName"] == "北京"
