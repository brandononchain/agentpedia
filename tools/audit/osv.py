"""CVE lookup seam. Network stays off unless a caller constructs OsvClient and invokes it.

Phase 1 does not call api.osv.dev. AGENTPEDIA_AUDIT_OSV=1 selects the stub client,
which still performs no request.
"""

from __future__ import annotations

import os
from typing import Protocol

OSV_ENDPOINT = "https://api.osv.dev/v1/query"


class PackageRef:
    def __init__(self, name: str, ecosystem: str, version: str = "") -> None:
        self.name = name
        self.ecosystem = ecosystem
        self.version = version


class OsvLookup(Protocol):
    def query(self, packages: list[PackageRef]) -> list[dict]:
        """Return advisory dicts. An empty list means none were reported."""


class DisabledOsv:
    """Default client. It never opens a socket."""

    name = "disabled"

    def query(self, packages: list[PackageRef]) -> list[dict]:
        return []


class OsvClient:
    """Stub for a later OSV.dev client. Calling it does not touch the network."""

    name = "stub"
    endpoint = OSV_ENDPOINT

    def query(self, packages: list[PackageRef]) -> list[dict]:
        raise NotImplementedError(
            "OSV lookup is not implemented in phase 1. "
            f"A later client would POST packages to {self.endpoint}."
        )


def lookup_from_env() -> OsvLookup:
    if os.environ.get("AGENTPEDIA_AUDIT_OSV", "").strip() == "1":
        return OsvClient()
    return DisabledOsv()
