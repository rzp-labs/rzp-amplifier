"""Tests for knowledge synthesis store"""

from amplifier.knowledge_synthesis.store import KnowledgeStore


class TestKnowledgeStore:
    """Tests for KnowledgeStore class"""

    def test_save_rejects_missing_source_id(self, tmp_path):
        """Extraction without source_id rejected"""
        store = KnowledgeStore(path=tmp_path / "test.jsonl")

        extraction = {
            "concepts": [{"name": "test", "description": "test concept"}],
            "relationships": [],
        }

        # Should not save (warning logged)
        store.save(extraction)

        # File should not be created or should be empty
        if store.path.exists():
            content = store.path.read_text()
            assert content == "" or not content.strip()

    def test_save_rejects_empty_extractions(self, tmp_path):
        """Empty extraction list not saved"""
        store = KnowledgeStore(path=tmp_path / "test.jsonl")

        extraction = {
            "source_id": "src-123",
            "concepts": [],
            "relationships": [],
            "insights": [],
            "patterns": [],
        }

        store.save(extraction)

        # Should not save empty extraction
        if store.path.exists():
            content = store.path.read_text()
            assert content == "" or not content.strip()

    def test_save_incremental_appends(self, tmp_path):
        """Multiple saves append, don't overwrite"""
        store = KnowledgeStore(path=tmp_path / "test.jsonl")

        extraction1 = {
            "source_id": "src-1",
            "concepts": [{"name": "concept1"}],
            "relationships": [],
        }
        extraction2 = {
            "source_id": "src-2",
            "concepts": [{"name": "concept2"}],
            "relationships": [],
        }

        store.save(extraction1)
        store.save(extraction2)

        # Load and verify both are present
        all_extractions = store.load_all()
        assert len(all_extractions) == 2
        assert all_extractions[0]["source_id"] == "src-1"
        assert all_extractions[1]["source_id"] == "src-2"

    def test_is_processed_detects_duplicates(self, tmp_path):
        """Duplicate source_id detected"""
        store = KnowledgeStore(path=tmp_path / "test.jsonl")

        extraction = {
            "source_id": "src-duplicate",
            "concepts": [{"name": "test"}],
            "relationships": [],
        }

        store.save(extraction)

        # Should detect as processed
        assert store.is_processed("src-duplicate") is True

    def test_load_all_returns_all_extractions(self, tmp_path):
        """All saved extractions loaded"""
        store = KnowledgeStore(path=tmp_path / "test.jsonl")

        # Save 3 extractions
        for i in range(3):
            extraction = {
                "source_id": f"src-{i}",
                "concepts": [{"name": f"concept{i}"}],
                "relationships": [],
            }
            store.save(extraction)

        all_extractions = store.load_all()
        assert len(all_extractions) == 3

    def test_failed_extraction_logged_not_saved(self, tmp_path):
        """Extraction marked failed is logged"""
        store = KnowledgeStore(path=tmp_path / "test.jsonl")

        extraction = {
            "source_id": "src-failed",
            "success": False,
            "error_type": "timeout",
            "error_detail": "LLM timeout",
            "concepts": [],
        }

        store.save(extraction)

        # Failed extraction not saved (no concepts/relationships)
        all_extractions = store.load_all()
        assert len(all_extractions) == 0

        # Error stats should track it
        assert store.error_stats["failed_extractions"] == 1

    def test_get_by_source_retrieves_specific_extraction(self, tmp_path):
        """Get extraction for specific source"""
        store = KnowledgeStore(path=tmp_path / "test.jsonl")

        extraction = {
            "source_id": "src-specific",
            "concepts": [{"name": "unique_concept"}],
            "relationships": [],
        }
        store.save(extraction)

        # Retrieve by source_id
        retrieved = store.get_by_source("src-specific")

        assert retrieved is not None
        assert retrieved["source_id"] == "src-specific"
        assert retrieved["concepts"][0]["name"] == "unique_concept"

    def test_count_returns_total_extractions(self, tmp_path):
        """Count total number of extractions"""
        store = KnowledgeStore(path=tmp_path / "test.jsonl")

        # Save 5 extractions
        for i in range(5):
            extraction = {
                "source_id": f"src-{i}",
                "concepts": [{"name": f"concept{i}"}],
                "relationships": [],
            }
            store.save(extraction)

        count = store.count()
        assert count == 5

    def test_clear_removes_all_data(self, tmp_path):
        """Clear removes all stored extractions"""
        store = KnowledgeStore(path=tmp_path / "test.jsonl")

        # Save some extractions
        for i in range(3):
            extraction = {
                "source_id": f"src-{i}",
                "concepts": [{"name": f"concept{i}"}],
                "relationships": [],
            }
            store.save(extraction)

        # Clear all
        store.clear()

        # Should be empty
        assert store.count() == 0
        assert not store.path.exists()

    def test_load_all_handles_malformed_lines(self, tmp_path):
        """Malformed JSON lines skipped gracefully"""
        path = tmp_path / "test.jsonl"

        # Write mixed valid and invalid lines
        with open(path, "w") as f:
            f.write('{"source_id": "src-1", "concepts": [{"name": "valid1"}], "relationships": []}\n')
            f.write("{invalid json}\n")
            f.write('{"source_id": "src-2", "concepts": [{"name": "valid2"}], "relationships": []}\n')

        store = KnowledgeStore(path=path)
        all_extractions = store.load_all()

        # Should only load valid lines
        assert len(all_extractions) == 2
        assert store.error_stats["parse_errors"] == 1
