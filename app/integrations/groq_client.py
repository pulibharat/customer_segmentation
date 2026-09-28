"""Optional Groq integration for context-aware support responses."""

from __future__ import annotations

import json
import logging
from typing import Any

from config import GROQ_API_KEY, LLM_MAX_TOKENS, LLM_MODEL, LLM_TEMPERATURE, LLM_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)


class GroqSupportClient:
    """Generate structured support decisions when Groq is configured.

    The SDK is imported lazily so local demo mode does not require the package or
    an API key. Any provider failure returns ``None`` and lets the caller use its
    deterministic fallback.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else GROQ_API_KEY
        self._client: Any | None = None

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _get_client(self) -> Any:
        if self._client is None:
            from groq import AsyncGroq

            self._client = AsyncGroq(
                api_key=self.api_key,
                timeout=LLM_TIMEOUT_SECONDS,
            )
        return self._client

    async def generate_support_decision(
        self,
        customer_id: str,
        message: str,
        context: Any,
        fallback_sentiment: Any,
    ) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        prompt = {
            "customer_id": customer_id,
            "message": message,
            "memory_summary": getattr(context, "memory_summary", ""),
            "customer_profile": getattr(context, "customer_profile", {}),
            "recent_tickets": getattr(context, "recent_tickets", [])[-5:],
            "fallback_sentiment": {
                "frustration": getattr(fallback_sentiment, "frustration", 0.0),
                "urgency": getattr(fallback_sentiment, "urgency", 0.0),
                "keywords": getattr(fallback_sentiment, "keywords", []),
            },
        }
        system_message = (
            "You are a customer support triage and response engine. Return only valid JSON "
            "with keys: sentiment, category, response, resolution_time_minutes, confidence. "
            "sentiment must contain frustration and urgency numbers from 0 to 1 and a keywords list. "
            "category must be one of api, billing, authentication, technical. Keep response concise, "
            "empathetic, actionable, and never invent account facts. Do not include hidden reasoning."
        )

        try:
            completion = await self._get_client().chat.completions.create(
                model=LLM_MODEL,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": json.dumps(prompt)},
                ],
            )
            content = completion.choices[0].message.content
            if not content:
                return None
            decision = json.loads(content)
            return self._validate_decision(decision)
        except Exception:
            logger.warning(
                "Groq support decision failed; using deterministic fallback", exc_info=True)
            return None

    @staticmethod
    def _validate_decision(decision: Any) -> dict[str, Any] | None:
        if not isinstance(decision, dict):
            return None

        sentiment = decision.get("sentiment")
        response = decision.get("response")
        category = decision.get("category")
        if not isinstance(sentiment, dict) or not isinstance(response, str) or not response.strip():
            return None
        if category not in {"api", "billing", "authentication", "technical"}:
            return None

        try:
            frustration = min(
                1.0, max(0.0, float(sentiment.get("frustration", 0.0))))
            urgency = min(1.0, max(0.0, float(sentiment.get("urgency", 0.0))))
            resolution_time = max(
                1, int(decision.get("resolution_time_minutes", 15)))
            confidence = min(
                1.0, max(0.0, float(decision.get("confidence", 0.7))))
        except (TypeError, ValueError):
            return None

        keywords = sentiment.get("keywords", [])
        if not isinstance(keywords, list):
            keywords = []

        return {
            "sentiment": {
                "frustration": round(frustration, 3),
                "urgency": round(urgency, 3),
                "keywords": [str(keyword) for keyword in keywords[:10]],
            },
            "category": category,
            "response": response.strip(),
            "resolution_time_minutes": resolution_time,
            "confidence": round(confidence, 3),
        }
