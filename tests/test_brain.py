"""
Tests for the Brain - the core orchestrator

Following TDD: write the API we want first, then make it work
"""

import pytest
from unittest.mock import Mock, patch
from homelab_brain.brain import Brain
from homelab_brain.models import Response


class TestBrainBasics:
    """Test core Brain functionality"""

    @patch('homelab_brain.brain.OllamaClient')
    def test_brain_can_answer_simple_question(self, mock_ollama_class):
        """
        The dream: Ask Winston a simple question and get an answer

        This is our "hello world" - if this works, the magic is real!
        """
        # Mock Ollama to return a simple answer
        mock_ollama = Mock()
        mock_ollama.ensure_available.return_value = True
        mock_ollama.generate.return_value = "The answer is 4"
        mock_ollama_class.return_value = mock_ollama

        brain = Brain()
        response = brain.ask("What is 2+2?")

        # Should get a Response object back
        assert isinstance(response, Response)

        # Answer should contain "4"
        assert "4" in response.answer.lower()

        # Should have confidence
        assert response.confidence >= 0
        assert response.confidence <= 1.0

        # Should track duration
        assert response.duration_ms > 0

    @patch('homelab_brain.brain.OllamaClient')
    def test_brain_response_has_timestamp(self, mock_ollama_class):
        """Every response should be timestamped"""
        mock_ollama = Mock()
        mock_ollama.ensure_available.return_value = True
        mock_ollama.generate.return_value = "Hello! How can I help?"
        mock_ollama_class.return_value = mock_ollama

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
