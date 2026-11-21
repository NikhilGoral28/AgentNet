"""Text processing agents."""

from agentnet.agents.text.proofreader import (
    CorrectionItem,
    Proofreader,
    ProofreadResult,
)
from agentnet.agents.text.rewriter import Rewriter
from agentnet.agents.text.summarizer import Summarizer
from agentnet.agents.text.translator import Translator

__all__ = [
    "CorrectionItem",
    "ProofreadResult",
    "Proofreader",
    "Rewriter",
    "Summarizer",
    "Translator",
]
