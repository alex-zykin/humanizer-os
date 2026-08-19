from __future__ import annotations

from .facts import verify_facts
from .models import VerificationReport


def verify_texts(original: str, revised: str) -> VerificationReport:
    """Compare protected facts between an original and a revised text."""
    return verify_facts(original, revised)
