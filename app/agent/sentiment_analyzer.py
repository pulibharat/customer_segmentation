"""Utilities to detect urgency and frustration in customer messages."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class SentimentResult:
    frustration: float
    urgency: float
    keywords: list[str]
    category: str


class SentimentAnalyzer:
    """Simple heuristic analyzer that does not require LLM access."""

    def __init__(self) -> None:
        self.frustration_words = {
            "urgent", "asap", "immediately", "angry", "frustrated", "broken", "failed", "not working",
            "critical", "urgent", "unacceptable", "disaster", "down", "failing"
        }
        self.urgency_words = {
            "urgent", "asap", "immediately", "today", "right now", "critical", "down", "outage", "broken"
        }

    def analyze(self, message: str) -> SentimentResult:
        text = (message or "").lower()
        keywords = []
        for word in sorted(set(self.frustration_words) | set(self.urgency_words)):
            if word in text:
                keywords.append(word)

        frustration = min(1.0, 0.15 + 0.12 * len(keywords))
        urgency = min(1.0, 0.2 + 0.14 * len(keywords))

        if "thanks" in text or "resolved" in text:
            frustration = max(0.0, frustration - 0.2)
            urgency = max(0.0, urgency - 0.2)

        if len(re.findall(r"!+", message or "")):
            frustration = min(1.0, frustration + 0.2)

        category = "normal"
        if urgency >= 0.75 or frustration >= 0.75:
            category = "high"
        elif urgency >= 0.5 or frustration >= 0.5:
            category = "medium"

        return SentimentResult(
            frustration=round(frustration, 3),
            urgency=round(urgency, 3),
            keywords=keywords,
            category=category,
        )
