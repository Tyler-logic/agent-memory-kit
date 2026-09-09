from agent_memory_kit import ScratchpadState


def test_set_pref_and_render():
    s = ScratchpadState()
    s.set_pref("timezone", "America/Edmonton")
    assert "America/Edmonton" in s.render()


def test_decisions_are_deduplicated():
    s = ScratchpadState()
    s.record_decision("using SQLite")
    s.record_decision("using SQLite")
    assert s.as_dict()["decisions"] == ["using SQLite"]


def test_task_lifecycle():
    s = ScratchpadState()
    s.add_task("fix flaky test")
    assert "fix flaky test" in s.as_dict()["open_tasks"]
    s.complete_task("fix flaky test")
    assert "fix flaky test" not in s.as_dict()["open_tasks"]


def test_update_merges_lists_and_dicts_without_duplicating():
    s = ScratchpadState()
    s.add_task("task a")
    s.update({"open_tasks": ["task a", "task b"], "user_prefs": {"units": "metric"}})
    data = s.as_dict()
    assert data["open_tasks"] == ["task a", "task b"]
    assert data["user_prefs"]["units"] == "metric"


def test_as_dict_is_a_copy_not_a_reference():
    s = ScratchpadState()
    d = s.as_dict()
    d["decisions"].append("mutated externally")
    assert s.as_dict()["decisions"] == []
