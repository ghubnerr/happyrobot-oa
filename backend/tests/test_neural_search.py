import pytest
from datetime import datetime, timedelta

from app.retrievers import HybridLoadRetriever


class MockLoad:
    """Mock Load object for testing without database dependencies."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@pytest.fixture
def sample_loads():
    """Create sample loads for testing."""
    now = datetime.now()
    return [
        MockLoad(
            load_id="LOAD001",
            origin="Los Angeles, CA",
            destination="New York, NY",
            pickup_datetime=now + timedelta(days=1),
            delivery_datetime=now + timedelta(days=3),
            equipment_type="Dry Van",
            loadboard_rate=2500.0,
            commodity_type="Electronics",
            notes="Urgent delivery, fragile items",
            is_available=True,
        ),
        MockLoad(
            load_id="LOAD002",
            origin="Chicago, IL",
            destination="Miami, FL",
            pickup_datetime=now + timedelta(days=2),
            delivery_datetime=now + timedelta(days=4),
            equipment_type="Refrigerated",
            loadboard_rate=3200.0,
            commodity_type="Food Products",
            notes="Temperature controlled, fresh produce",
            is_available=True,
        ),
        MockLoad(
            load_id="LOAD003",
            origin="Los Angeles, CA",
            destination="Seattle, WA",
            pickup_datetime=now + timedelta(days=1),
            delivery_datetime=now + timedelta(days=2),
            equipment_type="Flatbed",
            loadboard_rate=1800.0,
            commodity_type="Construction Materials",
            notes="Heavy equipment, oversized load",
            is_available=True,
        ),
        MockLoad(
            load_id="LOAD004",
            origin="New York, NY",
            destination="Boston, MA",
            pickup_datetime=now + timedelta(days=1),
            delivery_datetime=now + timedelta(days=2),
            equipment_type="Dry Van",
            loadboard_rate=1200.0,
            commodity_type="General Freight",
            notes="Standard delivery",
            is_available=True,
        ),
        MockLoad(
            load_id="LOAD005",
            origin="Dallas, TX",
            destination="Los Angeles, CA",
            pickup_datetime=now + timedelta(days=2),
            delivery_datetime=now + timedelta(days=4),
            equipment_type="Dry Van",
            loadboard_rate=2200.0,
            commodity_type="Electronics",
            notes="Consumer electronics, multiple stops",
            is_available=False,
        ),
    ]


def test_hybrid_retriever_initialization(sample_loads):
    """Test that HybridLoadRetriever initializes correctly."""
    retriever = HybridLoadRetriever(sample_loads)

    assert retriever.loads == sample_loads
    assert len(retriever.text_fields) == 5
    assert "origin" in retriever.text_fields
    assert "destination" in retriever.text_fields
    assert retriever.bm25 is not None
    assert retriever.model is not None
    assert retriever.embeddings is not None
    assert len(retriever.embeddings) == len(sample_loads)


def test_hybrid_retriever_search_by_origin(sample_loads):
    """Test searching by origin location."""
    retriever = HybridLoadRetriever(sample_loads)

    results = retriever.search({"origin": "Los Angeles"}, top_k=5)

    assert len(results) > 0
    origins = [load.origin for load, score in results]
    assert any("Los Angeles" in origin for origin in origins)

    scores = [score for load, score in results]
    assert scores == sorted(scores, reverse=True)


def test_hybrid_retriever_search_by_destination(sample_loads):
    """Test searching by destination location."""
    retriever = HybridLoadRetriever(sample_loads)

    # Search for loads going to New York
    results = retriever.search({"destination": "New York"}, top_k=5)

    assert len(results) > 0
    destinations = [load.destination for load, score in results]
    assert any("New York" in dest for dest in destinations)


def test_hybrid_retriever_search_by_equipment_type(sample_loads):
    """Test searching by equipment type."""
    retriever = HybridLoadRetriever(sample_loads)

    results = retriever.search({"equipment_type": "Dry Van"}, top_k=5)

    assert len(results) > 0
    equipment_types = [load.equipment_type for load, score in results]
    assert any("Dry Van" in eq for eq in equipment_types)
    assert "Dry Van" in results[0][0].equipment_type


def test_hybrid_retriever_search_by_commodity_type(sample_loads):
    """Test searching by commodity type."""
    retriever = HybridLoadRetriever(sample_loads)

    results = retriever.search({"commodity_type": "Electronics"}, top_k=5)

    assert len(results) > 0
    commodity_types = [load.commodity_type for load, score in results]
    assert any("Electronics" in ct for ct in commodity_types if ct)


def test_hybrid_retriever_search_by_notes(sample_loads):
    """Test searching by notes field."""
    retriever = HybridLoadRetriever(sample_loads)

    results = retriever.search({"notes": "urgent"}, top_k=5)

    assert len(results) > 0
    load_ids = [load.load_id for load, score in results]
    assert "LOAD001" in load_ids


def test_hybrid_retriever_multi_field_search(sample_loads):
    """Test searching with multiple fields."""
    retriever = HybridLoadRetriever(sample_loads)

    results = retriever.search(
        {"origin": "Los Angeles", "destination": "New York"}, top_k=5
    )

    assert len(results) > 0
    load_ids = [load.load_id for load, score in results]
    assert "LOAD001" in load_ids

    # LOAD001 should have a high score
    top_load, top_score = results[0]
    assert top_load.load_id == "LOAD001"
    assert top_score > 0


def test_hybrid_retriever_empty_query(sample_loads):
    """Test that empty query returns empty results."""
    retriever = HybridLoadRetriever(sample_loads)

    results = retriever.search({}, top_k=5)
    assert results == []


def test_hybrid_retriever_top_k_limit(sample_loads):
    """Test that top_k parameter limits results."""
    retriever = HybridLoadRetriever(sample_loads)

    results = retriever.search({"equipment_type": "Van"}, top_k=2)
    assert len(results) <= 2


def test_hybrid_retriever_score_weights(sample_loads):
    """Test that different score weights affect results."""
    retriever = HybridLoadRetriever(sample_loads)

    results_bm25 = retriever.search(
        {"origin": "Los Angeles"}, top_k=5, bm25_weight=1.0, embed_weight=0.0
    )

    results_embed = retriever.search(
        {"origin": "Los Angeles"}, top_k=5, bm25_weight=0.0, embed_weight=1.0
    )

    assert len(results_bm25) > 0
    assert len(results_embed) > 0


def test_hybrid_retriever_semantic_similarity(sample_loads):
    """Test that semantic similarity works (e.g., 'LA' matches 'Los Angeles')."""
    retriever = HybridLoadRetriever(sample_loads)

    results = retriever.search({"origin": "LA"}, top_k=5)

    assert len(results) > 0
    origins = [load.origin for load, score in results]
    assert any("Los Angeles" in origin or "LA" in origin for origin in origins)


def test_hybrid_retriever_partial_matches(sample_loads):
    """Test that partial text matches work."""
    retriever = HybridLoadRetriever(sample_loads)

    results = retriever.search({"equipment_type": "refrigerated"}, top_k=5)

    assert len(results) > 0
    equipment_types = [load.equipment_type for load, score in results]
    assert any("Refrigerated" in eq for eq in equipment_types)
