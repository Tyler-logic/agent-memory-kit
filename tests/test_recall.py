import os
import tempfile

from agent_memory_kit import FuzzyRecall


def test_remember_and_recall_ranks_closest_match():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "mem.jsonl")
        r = FuzzyRecall(path=path)
        r.remember("the deploy target is Netlify")
        r.remember("the user prefers dark mode")
        r.remember("the deploy target changed to Cloudflare Pages")

        results = r.recall("what is the deploy target", top_k=2)
        assert len(results) == 2
        assert all("deploy target" in res["text"] for res in results)


def test_recall_on_empty_store_returns_empty_list():
    with tempfile.TemporaryDirectory() as tmp:
        r = FuzzyRecall(path=os.path.join(tmp, "missing.jsonl"))
        assert r.recall("anything") == []


def test_clear_removes_the_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "mem.jsonl")
        r = FuzzyRecall(path=path)
        r.remember("something")
        assert os.path.exists(path)
        r.clear()
        assert not os.path.exists(path)


def test_custom_scorer_is_used():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "mem.jsonl")
        # a scorer that only ever prefers exact matches
        r = FuzzyRecall(path=path, scorer=lambda q, c: 1.0 if q == c else 0.0)
        r.remember("exact")
        r.remember("not it")
        top = r.recall("exact", top_k=1)[0]
        assert top["text"] == "exact"
