"""Comprehensive tests for validation/core.py"""

from datetime import datetime

from amplifier.memory.models import StoredMemory
from amplifier.validation.core import ClaimValidator


class TestClaimValidator:
    """Comprehensive tests for ClaimValidator"""

    def test_numeric_contradiction_detected(self):
        """Numeric differences trigger contradiction"""
        validator = ClaimValidator()

        memories = [
            StoredMemory(
                id="mem-1",
                timestamp=datetime.now(),
                content="Use 4.5:1 contrast ratio for accessibility",
                category="decision",
                metadata={},
                accessed_count=0,
            )
        ]

        claim = "We should use 7:1 contrast ratio for accessibility"
        result = validator.validate_claim(claim, memories)

        assert result.contradicts is True
        assert result.verdict == "contradicted"

    def test_negation_prevents_false_positive(self):
        """Negation words detected (changes verdict)"""
        validator = ClaimValidator()

        memories = [
            StoredMemory(
                id="mem-1",
                timestamp=datetime.now(),
                content="Use PostgreSQL for primary storage",
                category="decision",
                metadata={},
                accessed_count=0,
            )
        ]

        claim = "Not using PostgreSQL anymore for primary storage"
        result = validator.validate_claim(claim, memories)

        # Negation is detected and creates contradiction
        # The validator checks if claim_has_negation != memory_has_negation
        assert result.contradicts is True or result.verdict == "contradicted"

    def test_database_technology_contradiction(self):
        """Different databases contradict"""
        validator = ClaimValidator()

        memories = [
            StoredMemory(
                id="mem-1",
                timestamp=datetime.now(),
                content="Using MongoDB as primary database",
                category="decision",
                metadata={},
                accessed_count=0,
            )
        ]

        claim = "We will use PostgreSQL as primary database"
        result = validator.validate_claim(claim, memories)

        assert result.contradicts is True
        assert result.verdict == "contradicted"

    def test_framework_contradiction(self):
        """Different frameworks contradict"""
        validator = ClaimValidator()

        memories = [
            StoredMemory(
                id="mem-1",
                timestamp=datetime.now(),
                content="Built with Django framework for API endpoints",
                category="decision",
                metadata={},
                accessed_count=0,
            )
        ]

        claim = "We are building API endpoints with FastAPI framework"
        result = validator.validate_claim(claim, memories)

        assert result.contradicts is True

    def test_version_numbers_dont_contradict(self):
        """Similar version numbers allowed"""
        validator = ClaimValidator()

        memories = [
            StoredMemory(
                id="mem-1",
                timestamp=datetime.now(),
                content="Using Python 3.11 for development",
                category="preference",
                metadata={},
                accessed_count=0,
            )
        ]

        claim = "Using Python 3.12 for development"
        result = validator.validate_claim(claim, memories)

        # Version upgrades shouldn't be flagged as contradictions
        # The numeric check should allow small differences
        assert result.verdict in ["supported", "unknown"]

    def test_empty_memories_returns_no_contradictions(self):
        """Empty memory list returns no contradictions"""
        validator = ClaimValidator()

        claim = "We use React for frontend"
        result = validator.validate_claim(claim, [])

        assert result.contradicts is False
        assert result.verdict == "unknown"
        assert result.confidence == 0.0

    def test_technical_terms_extracted(self):
        """Technical terms identified in claims"""
        validator = ClaimValidator()

        text = "We will use React framework. The database is PostgreSQL. API built with FastAPI."
        claims = validator.extract_claims_from_text(text)

        # Should extract claims with technical terms
        assert len(claims) > 0
        claim_text = " ".join(claims).lower()
        assert "react" in claim_text or "postgresql" in claim_text or "fastapi" in claim_text

    def test_claim_extraction_patterns(self):
        """Claims extracted from text"""
        validator = ClaimValidator()

        text = "The system uses React for the frontend. PostgreSQL is the primary database. API performance is good."
        claims = validator.extract_claims_from_text(text)

        # Should extract factual claims
        assert len(claims) >= 2  # At least the React and PostgreSQL claims

        # Should include the database claim
        claims_text = " ".join(claims)
        assert "PostgreSQL" in claims_text or "React" in claims_text

    def test_supports_detected_for_matching_claim(self):
        """Matching claim shows support"""
        validator = ClaimValidator()

        memories = [
            StoredMemory(
                id="mem-1",
                timestamp=datetime.now(),
                content="Prefer TypeScript over JavaScript for frontend development",
                category="preference",
                metadata={},
                accessed_count=0,
            )
        ]

        claim = "Using TypeScript for frontend development"
        result = validator.validate_claim(claim, memories)

        assert result.supports is True
        assert result.verdict == "supported"

    def test_javascript_typescript_contradiction(self):
        """JavaScript vs TypeScript preferences contradict"""
        validator = ClaimValidator()

        memories = [
            StoredMemory(
                id="mem-1",
                timestamp=datetime.now(),
                content="Prefer TypeScript over JavaScript for frontend",
                category="preference",
                metadata={},
                accessed_count=0,
            )
        ]

        claim = "Should stick with JavaScript for frontend instead of TypeScript"
        result = validator.validate_claim(claim, memories)

        # Should detect as contradiction
        assert result.contradicts is True
