"""
Tests for the Brain - the core orchestrator

Following TDD: write the API we want first, then make it work
"""

import pytest
from homelab_brain.brain import Brain
from homelab_brain.models import Response


class TestBrainBasics:
    """Test core Brain functionality"""

    def test_brain_can_answer_simple_question(self):
        """
        The dream: Ask Winston a simple question and get an answer

        This is our "hello world" - if this works, the magic is real!
        """
        brain = Brain()
        response = brain.ask("What is 2+2?")

        # Should get a Response object back
        assert isinstance(response, Response)

        # Answer should contain "4"
        assert "4" in response.answer.lower()

        # Should have confidence (even if low for mock)
        assert response.confidence >= 0
        assert response.confidence <= 1.0

        # Should track duration
        assert response.duration_ms > 0

    def test_brain_response_has_timestamp(self):
        """Every response should be timestamped"""
        brain = Brain()
        response = brain.ask("Hello")

        assert response.timestamp is not None

    def test_brain_handles_empty_query(self):
        """Should gracefully handle empty queries"""
        brain = Brain()
        response = brain.ask("")

        # Should still return valid Response, not crash
        assert isinstance(response, Response)
        assert len(response.answer) > 0  # Some error message


class TestBrainWithContext:
    """Test Brain gathering and using system context"""

    @pytest.mark.skip(reason="Implement after basic Brain works")
    def test_brain_gathers_relevant_context(self):
        """
        When asked about CPU, Brain should gather CPU metrics
        """
        brain = Brain()
        response = brain.ask("What's my CPU usage?")

        assert "cpu" in response.context_gathered
        assert "cpu_percent" in response.metrics

    @pytest.mark.skip(reason="Implement after basic Brain works")
    def test_brain_only_gathers_relevant_context(self):
        """
        Don't gather everything - be smart about it
        """
        brain = Brain()
        response = brain.ask("How much disk space?")

        assert "disk" in response.context_gathered
        assert "network" not in response.context_gathered  # Irrelevant


class TestBrainIntegration:
    """Integration tests with real Ollama"""

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires tgoml to be awake")
    def test_brain_with_real_ollama(self):
        """
        End-to-end test with actual Ollama

        Run with: pytest -m integration
        """
        brain = Brain()
        response = brain.ask("Explain Docker in one sentence")

        assert "container" in response.answer.lower()
        assert response.confidence > 0.5  # Should be confident
