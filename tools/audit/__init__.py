"""Static security audit for Agentpedia skills and agents.

Phase 1 is a stdlib scanner. It does not run the entry, does not call the
network, and does not look up CVEs unless a later phase turns that on.
"""

RULESET_VERSION = "1.0.0"
AUDITOR = "agentpedia-audit v1"
AUDIT_DAYS = 90

WEIGHTS = {
    "critical": 40,
    "high": 18,
    "medium": 8,
    "low": 3,
    "info": 1,
}

DEFAULT_GRACE_DAYS = 14
