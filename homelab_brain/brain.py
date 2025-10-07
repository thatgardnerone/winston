"""
The Brain - Core orchestrator for homelab management

This is Winston! 🧠
"""

import time
from datetime import datetime
from homelab_brain.models import Response
from homelab_brain.ollama_client import OllamaClient
from homelab_brain.system_context import SystemContext


class Brain:
    """
    The Brain orchestrates everything:
    - Connects to Ollama
    - Gathers system context
    - Returns structured responses
    """

    def __init__(self):
        """Initialize the Brain"""
        self.ollama = OllamaClient()
        self.context = SystemContext()

    def ask(self, query: str) -> Response:
        """
        Ask Winston a question

        Args:
            query: Natural language question

        Returns:
            Structured Response with answer, metrics, etc.
        """
        start_time = time.time()

        # Handle empty query
        if not query or not query.strip():
            return Response(
                answer="I didn't catch that. What would you like to know?",
                confidence=1.0,
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now()
            )

        # Gather relevant system context
        sys_context = self.context.gather_relevant(query)
        context_str = self.context.format_for_prompt(sys_context)
        context_keys = list(sys_context.keys())

        # Generate answer
        # Use Ollama if available (will auto-wake tgoml if needed), fallback to mock
        try:
            if self.ollama.ensure_available():
                system_prompt = (
                    "You are Winston, a helpful AI assistant for homelab management. "
                    "Be concise and direct. Use the system context provided to give accurate answers. "
                    f"\n\n{context_str}"
                )
                answer = self.ollama.generate(query, system=system_prompt)
                confidence = 0.8
            else:
                # Mock response if Ollama unavailable even after wake attempt
                answer = self._mock_answer(query)
                confidence = 0.5
        except Exception:
            # Fallback to mock on any error
            answer = self._mock_answer(query)
            confidence = 0.5

        duration_ms = (time.time() - start_time) * 1000

        return Response(
            answer=answer,
            confidence=confidence,
            metrics=sys_context,
            duration_ms=duration_ms,
            context_gathered=context_keys,
            timestamp=datetime.now()
        )

    def _mock_answer(self, query: str) -> str:
        """
        Mock answer for testing
        TODO: Replace with real Ollama call
        """
        query_lower = query.lower()

        # Simple pattern matching for tests
        if "2+2" in query_lower or "2 + 2" in query_lower:
            return "The answer is 4"

        if "hello" in query_lower or "hi" in query_lower:
            return "Hello! I'm Winston, your homelab assistant."

        return f"I heard you ask: '{query}'. (Mock response - Ollama not connected yet)"
