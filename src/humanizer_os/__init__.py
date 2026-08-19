"""HumanizerOS: an explainable multilingual text humanization platform."""

from ._version import __version__
from .analyzer import Analyzer
from .models import AuditReport, Finding, RewriteReport, VerificationReport
from .rewriter import Rewriter
from .verify import verify_texts

__all__ = [
    "Analyzer",
    "AuditReport",
    "Finding",
    "Rewriter",
    "RewriteReport",
    "VerificationReport",
    "__version__",
    "verify_texts",
]
