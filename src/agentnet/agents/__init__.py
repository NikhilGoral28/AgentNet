"""Built-in AgentNet agents catalog."""

from agentnet.agents.code.code_explainer import CodeExplainer
from agentnet.agents.code.code_reviewer import CodeIssue, CodeReviewer, CodeReviewResult
from agentnet.agents.code.test_generator import TestGenerator
from agentnet.agents.information.classifier import ClassificationResult, Classifier
from agentnet.agents.information.extractor import Extractor
from agentnet.agents.information.intent_classifier import IntentClassifier, IntentResult
from agentnet.agents.information.sentiment_analyzer import (
    SentimentAnalyzer,
    SentimentResult,
)
from agentnet.agents.planning.task_planner import PlanResult, PlanTask, TaskPlanner
from agentnet.agents.text.proofreader import (
    CorrectionItem,
    Proofreader,
    ProofreadResult,
)
from agentnet.agents.text.rewriter import Rewriter
from agentnet.agents.text.summarizer import Summarizer
from agentnet.agents.text.translator import Translator
from agentnet.agents.writing.email_responder import EmailResponder, EmailResponseDraft
from agentnet.agents.writing.email_writer import EmailDraft, EmailWriter
from agentnet.agents.writing.meeting_notes_writer import (
    ActionItem,
    MeetingNotes,
    MeetingNotesWriter,
)

__all__ = [
    "ActionItem",
    "ClassificationResult",
    "Classifier",
    "CodeExplainer",
    "CodeIssue",
    "CodeReviewResult",
    "CodeReviewer",
    "CorrectionItem",
    "EmailDraft",
    "EmailResponder",
    "EmailResponseDraft",
    "EmailWriter",
    "Extractor",
    "IntentClassifier",
    "IntentResult",
    "MeetingNotes",
    "MeetingNotesWriter",
    "PlanResult",
    "PlanTask",
    "ProofreadResult",
    "Proofreader",
    "Rewriter",
    "SentimentAnalyzer",
    "SentimentResult",
    "Summarizer",
    "TaskPlanner",
    "TestGenerator",
    "Translator",
]
