from agent_memory_kit import ActionTier, PermissionBoundary


def make_boundary():
    b = PermissionBoundary()
    b.register("read_file", ActionTier.AUTONOMOUS, lambda path: f"contents of {path}")
    b.register("send_email", ActionTier.CONFIRM, lambda to, body: f"sent to {to}")
    b.register("transfer_funds", ActionTier.BLOCKED, lambda amount: "transferred")
    return b


def test_autonomous_action_runs_without_approval():
    b = make_boundary()
    result = b.execute("read_file", {"path": "notes.txt"})
    assert result == "contents of notes.txt"


def test_blocked_action_never_runs_even_with_approval_granted():
    b = make_boundary()
    result = b.execute("transfer_funds", {"amount": 100}, get_human_approval=lambda n, a: True)
    assert "blocked" in result.lower()


def test_confirm_action_runs_only_if_approved():
    b = make_boundary()
    approved = b.execute("send_email", {"to": "x@example.com", "body": "hi"}, get_human_approval=lambda n, a: True)
    denied = b.execute("send_email", {"to": "x@example.com", "body": "hi"}, get_human_approval=lambda n, a: False)
    assert approved == "sent to x@example.com"
    assert "not approved" in denied.lower()


def test_confirm_action_without_approval_mechanism_does_not_run():
    b = make_boundary()
    result = b.execute("send_email", {"to": "x@example.com", "body": "hi"})
    assert "requires approval" in result.lower()


def test_unknown_action_defaults_to_confirm_not_autonomous():
    b = PermissionBoundary()
    # never registered, so it must not silently run
    result = b.execute("delete_everything", {})
    assert b.tier_for("delete_everything") is ActionTier.CONFIRM
    assert "no approval mechanism" in result.lower() or "requires approval" in result.lower()


def test_collect_pending_confirmations_only_returns_confirm_tier():
    b = make_boundary()
    planned = [
        ("read_file", {"path": "a.txt"}),
        ("send_email", {"to": "x@example.com", "body": "hi"}),
        ("transfer_funds", {"amount": 5}),
    ]
    pending = b.collect_pending_confirmations(planned)
    assert pending == [("send_email", {"to": "x@example.com", "body": "hi"})]
