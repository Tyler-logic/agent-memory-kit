from agent_memory_kit import ScratchpadState, CompactionCheckpoint


def test_before_compaction_merges_extracted_patch_into_state():
    state = ScratchpadState()

    def fake_extractor(history):
        # stands in for a real LLM extraction call
        return {"decisions": ["switched to SQLite"], "user_prefs": {"units": "metric"}}

    checkpoint = CompactionCheckpoint(state, extractor=fake_extractor)
    patch = checkpoint.before_compaction(conversation_history=[{"role": "user", "content": "..."}])

    assert patch["decisions"] == ["switched to SQLite"]
    assert state.as_dict()["decisions"] == ["switched to SQLite"]
    assert state.as_dict()["user_prefs"]["units"] == "metric"
