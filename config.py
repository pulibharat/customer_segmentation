"""
Configuration settings for Customer Support Agent
"""

import os
from typing import Literal

# ============================================================================
# ENVIRONMENT
# ============================================================================
ENVIRONMENT: Literal["development", "staging", "production"] = os.getenv(
    "ENVIRONMENT", "development"
)
DEBUG = ENVIRONMENT == "development"

# ============================================================================
# API KEYS & CREDENTIALS
# ============================================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "")
HINDSIGHT_NAMESPACE = os.getenv("HINDSIGHT_NAMESPACE", "support_agent")
HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL", "")
HINDSIGHT_BANK_ID = os.getenv("HINDSIGHT_BANK_ID", HINDSIGHT_NAMESPACE)

# ============================================================================
# LLM SETTINGS
# ============================================================================
# Groq models: openai/gpt-oss-120b, qwen/qwen3-32b, meta-llama/llama-3-70b-versatile
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))

# ============================================================================
# MEMORY SETTINGS (Hindsight)
# ============================================================================
HINDSIGHT_BATCH_SIZE = int(os.getenv("HINDSIGHT_BATCH_SIZE", "100"))
HINDSIGHT_TIMEOUT_SECONDS = int(os.getenv("HINDSIGHT_TIMEOUT_SECONDS", "10"))
MEMORY_RETENTION_DAYS = int(os.getenv("MEMORY_RETENTION_DAYS", "365"))
PATTERN_MIN_FREQUENCY = int(os.getenv("PATTERN_MIN_FREQUENCY", "2"))

# ============================================================================
# AGENT SETTINGS
# ============================================================================
# Escalation triggers
ESCALATION_THRESHOLD_URGENCY = float(
    os.getenv("ESCALATION_THRESHOLD_URGENCY", "0.8"))
ESCALATION_THRESHOLD_SATISFACTION = float(
    os.getenv("ESCALATION_THRESHOLD_SATISFACTION", "4.0"))
ESCALATION_THRESHOLD_REPEAT_ISSUES = int(
    os.getenv("ESCALATION_THRESHOLD_REPEAT_ISSUES", "3"))

# Resolution time expectations (in minutes)
MAX_RESOLUTION_TIME_MINUTES = int(
    os.getenv("MAX_RESOLUTION_TIME_MINUTES", "30"))
TARGET_RESOLUTION_TIME_MINUTES = int(
    os.getenv("TARGET_RESOLUTION_TIME_MINUTES", "15"))

# Context settings
MAX_PAST_TICKETS_TO_RETRIEVE = int(
    os.getenv("MAX_PAST_TICKETS_TO_RETRIEVE", "20"))
MIN_SIMILARITY_THRESHOLD = float(os.getenv("MIN_SIMILARITY_THRESHOLD", "0.7"))

# ============================================================================
# SYNTHETIC DATA SETTINGS
# ============================================================================
NUM_SYNTHETIC_CUSTOMERS = int(os.getenv("NUM_SYNTHETIC_CUSTOMERS", "50"))
NUM_SYNTHETIC_TICKETS = int(os.getenv("NUM_SYNTHETIC_TICKETS", "500"))
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))

# Customer tiers
CUSTOMER_TIERS = ["Basic", "Pro", "Enterprise"]
TIER_DISTRIBUTION = {
    "Basic": 0.50,      # 50% of customers
    "Pro": 0.35,        # 35% of customers
    "Enterprise": 0.15  # 15% of customers
}

# Issue categories
ISSUE_CATEGORIES = [
    "API",
    "Billing",
    "Account",
    "Technical",
    "Integration",
    "Performance",
    "Authentication",
    "Documentation",
    "Feature_Request",
    "Other"
]

# Issue severity levels
ISSUE_SEVERITY_LEVELS = ["Low", "Medium", "High", "Critical"]

# ============================================================================
# CUSTOMER SETTINGS
# ============================================================================
CHURN_RISK_THRESHOLDS = {
    "low": (0.0, 0.3),
    "medium": (0.3, 0.7),
    "high": (0.7, 1.0)
}

COMMUNICATION_STYLES = ["technical", "non-technical", "balanced"]

# ============================================================================
# DEMO SETTINGS
# ============================================================================
DEMO_CUSTOMER_ID = "demo_cust_001"
DEMO_SHOW_MEMORY_DIFF = True  # Show side-by-side with/without memory

# ============================================================================
# API SETTINGS
# ============================================================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_WORKERS = int(os.getenv("API_WORKERS", "4"))

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# METRICS & EVALUATION
# ============================================================================
TRACK_METRICS = os.getenv("TRACK_METRICS", "true").lower() == "true"
METRICS_UPDATE_INTERVAL_SECONDS = int(
    os.getenv("METRICS_UPDATE_INTERVAL_SECONDS", "300"))

# ============================================================================
# SENTIMENT ANALYSIS THRESHOLDS
# ============================================================================
SENTIMENT_THRESHOLDS = {
    "frustration_high": 0.7,
    "frustration_medium": 0.4,
    "urgency_high": 0.8,
    "urgency_medium": 0.5
}

# ============================================================================
# PATTERN ANALYSIS
# ============================================================================
PATTERN_ANALYSIS_ENABLED = os.getenv(
    "PATTERN_ANALYSIS_ENABLED", "true").lower() == "true"
PATTERN_UPDATE_FREQUENCY = "daily"  # "daily", "per_ticket", "weekly"

# ============================================================================
# VALIDATION
# ============================================================================


def validate_config():
    """Validate configuration at startup.

    For local demo usage, we allow empty credentials so the mock memory path can
    run without external API setup. Production deployments still enforce them.
    """
    errors = []

    if ENVIRONMENT == "production":
        if not GROQ_API_KEY:
            errors.append("GROQ_API_KEY not set")

        if not HINDSIGHT_API_KEY:
            errors.append("HINDSIGHT_API_KEY not set")

    if LLM_TEMPERATURE < 0 or LLM_TEMPERATURE > 1:
        errors.append("LLM_TEMPERATURE must be between 0 and 1")

    if MIN_SIMILARITY_THRESHOLD < 0 or MIN_SIMILARITY_THRESHOLD > 1:
        errors.append("MIN_SIMILARITY_THRESHOLD must be between 0 and 1")

    if NUM_SYNTHETIC_CUSTOMERS < 1:
        errors.append("NUM_SYNTHETIC_CUSTOMERS must be at least 1")

    if errors:
        raise ValueError(
            "Configuration validation failed:\n" + "\n".join(errors))


# Validate on import
validate_config()
