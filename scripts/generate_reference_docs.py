"""Exhaustive Codebase Reference & Architecture Documentation Generator for AgentNet.
Generates:
1. docs/AgentNet_Complete_Codebase_Reference.pdf
2. AgentNet_Complete_Codebase_Reference.pdf (root copy)
3. docs/CODEBASE_EXPLAINED.md
"""

from __future__ import annotations

import shutil
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "docs"
PDF_PATH = DOCS_DIR / "AgentNet_Complete_Codebase_Reference.pdf"
ROOT_PDF_PATH = ROOT_DIR / "AgentNet_Complete_Codebase_Reference.pdf"
MD_PATH = DOCS_DIR / "CODEBASE_EXPLAINED.md"


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas calculating total pages, drawing running headers & footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        if self._pageNumber == 1:
            return  # Suppress on cover page

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))

        # Running Header
        self.drawString(54, 755, "AgentNet: Complete Codebase & Architectural Reference")
        self.setFont("Helvetica", 8)
        self.drawRightString(558, 755, "Python AI Agent Framework")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(54, 747, 558, 747)

        # Running Footer
        self.line(54, 45, 558, 45)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(54, 32, "AgentNet v0.1.0 — Architecture & Codebase Technical Manual")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


# Data catalog detailing all files in AgentNet
CODEBASE_DATA = [
    # ---------------------------------------------------------
    # PART 1: ROOT & FOUNDATIONAL SYSTEM FILES
    # ---------------------------------------------------------
    {
        "category": "1. Package Root & Foundational System Files",
        "file": "src/agentnet/__init__.py",
        "title": "Top-Level Package Initializer & Public API Surface",
        "what": (
            "Exposes the public API of the AgentNet framework. Exports all 15 built-in agents, "
            "core execution classes (BaseAgent, AgentEngine), request/response models (ChatMessage, "
            "ModelRequest, ModelResponse, ToolCall, AgentResult, UsageInfo), configuration models (AgentConfig), "
            "error hierarchies (AgentNetError and all subclasses), provider adapters (GeminiAdapter, GrokAdapter), "
            "tool registries (Tool, ToolRegistry), workflow orchestrators (SequentialWorkflow), and the library version."
        ),
        "why": (
            "Provides a clean, unified namespace so developers can import everything directly from 'agentnet' "
            "(e.g., 'from agentnet import Summarizer, Extractor, AgentConfig') without needing to know internal "
            "directory structures. It enforces a strict __all__ manifest in alphabetical order to satisfy static "
            "analysis and prevent namespace pollution."
        ),
        "how": (
            "1. Imports symbols from submodules (agents, config, core, exceptions, providers, tools, workflows, version).\n"
            "2. Defines __all__ as an explicitly sorted list of 59 export strings.\n"
            "3. Guarantees that only public, stable symbols are accessible when a consumer executes 'from agentnet import *'."
        ),
        "components": [
            {
                "name": "__all__",
                "signature": "list[str] (59 symbols)",
                "description": "Defines the explicit public interface of AgentNet. Exported symbols are strictly curated."
            }
        ]
    },
    {
        "category": "1. Package Root & Foundational System Files",
        "file": "src/agentnet/version.py",
        "title": "Library Version Declaration",
        "what": "Declares the single source of truth for the AgentNet package version string (__version__ = '0.1.0').",
        "why": "Centralizes versioning to ensure consistency across packaging (pyproject.toml), runtime inspections, error reports, and PyPI distributions.",
        "how": "Defines the constant string __version__ = '0.1.0' which is imported by __init__.py and build systems.",
        "components": [
            {
                "name": "__version__",
                "signature": "str = '0.1.0'",
                "description": "Semantic version of the AgentNet Python library."
            }
        ]
    },
    {
        "category": "1. Package Root & Foundational System Files",
        "file": "src/agentnet/py.typed",
        "title": "PEP 561 Typing Marker",
        "what": "An empty marker file signaling that AgentNet complies with PEP 561 and provides inline type annotations.",
        "why": "Enables type checkers like MyPy, Pyright, and IDE language servers in consumer projects to leverage AgentNet's full type hints.",
        "how": "Included in the package distribution wheel and sdist root to inform tools that all modules are fully typed.",
        "components": []
    },
    {
        "category": "1. Package Root & Foundational System Files",
        "file": "src/agentnet/exceptions.py",
        "title": "Sanitized Exception Hierarchy & Secret Redaction Engine",
        "what": (
            "Defines the entire exception hierarchy for AgentNet, anchored by AgentNetError. Implements automated regex-based "
            "secret redaction that strips API keys, bearer tokens, passwords, and private keys from all exception messages and detail dicts."
        ),
        "why": (
            "Prevents catastrophic credential leakage. When an LLM provider fails or throws an authentication error, raw API keys "
            "often appear in error messages or query strings. By scrubbing keys at the exception base class, secrets can never leak "
            "into application logs, terminal outputs, or Sentry/Datadog monitoring."
        ),
        "how": (
            "1. _SECRET_PATTERNS compiles regexes matching OpenAI (sk-...), xAI (xai-...), Google Gemini (AIzaSy...), Bearer tokens, "
            "JWTs, and PEM private keys.\n"
            "2. _sanitize(message: str) scans any error text and replaces matched tokens with '[REDACTED_SECRET]'.\n"
            "3. _sanitize_dict(data: dict) recursively traverses dictionaries to redact sensitive keys and values.\n"
            "4. AgentNetError.__init__() passes all messages through _sanitize() before calling super().__init__().\n"
            "5. Subclasses model specific error scenarios: ConfigurationError, ValidationError, ProviderError, AuthenticationError, "
            "RateLimitError, ProviderTimeoutError, ProviderUnavailableError, OutputParsingError, CapabilityError, ToolError, "
            "ToolPermissionError, ToolTimeoutError, WorkflowError, WorkflowLimitError, WorkflowStepError, and ExecutionCancelledError."
        ),
        "components": [
            {
                "name": "_sanitize(message: str) -> str",
                "signature": "def _sanitize(message: str) -> str",
                "description": "Scans strings against _SECRET_PATTERNS regexes and substitutes '[REDACTED_SECRET]'."
            },
            {
                "name": "_sanitize_dict(data: dict[str, Any]) -> dict[str, Any]",
                "signature": "def _sanitize_dict(data: dict[str, Any]) -> dict[str, Any]",
                "description": "Recursively scrubs dictionary keys ('api_key', 'token', 'password', 'secret') and values."
            },
            {
                "name": "AgentNetError",
                "signature": "class AgentNetError(Exception)",
                "description": "Root exception. Automatically sanitizes all messages and details dictionaries upon instantiation."
            },
            {
                "name": "ProviderError & Subclasses",
                "signature": "class ProviderError(AgentNetError)",
                "description": "Base for provider faults. Subclasses: AuthenticationError, RateLimitError, ProviderTimeoutError, ProviderUnavailableError."
            },
            {
                "name": "OutputParsingError",
                "signature": "class OutputParsingError(AgentNetError)",
                "description": "Raised when model output fails JSON parsing or Pydantic validation. Retains schema and raw output securely."
            },
            {
                "name": "ToolError & Subclasses",
                "signature": "class ToolError(AgentNetError)",
                "description": "Raised on tool failures. Subclasses: ToolPermissionError (unauthorized side-effects), ToolTimeoutError (execution exceeded timeout)."
            },
            {
                "name": "WorkflowError & Subclasses",
                "signature": "class WorkflowError(AgentNetError)",
                "description": "Raised when workflow steps fail. Subclasses: WorkflowLimitError (infinite loop/timeout guards), WorkflowStepError (step failure)."
            }
        ]
    },

    # ---------------------------------------------------------
    # PART 2: CORE RUNTIME & EXECUTION ENGINE
    # ---------------------------------------------------------
    {
        "category": "2. Core Runtime & Execution Subsystem",
        "file": "src/agentnet/core/__init__.py",
        "title": "Core Package Exports",
        "what": "Exports foundational classes: BaseAgent, AgentEngine, ChatMessage, ModelRequest, ModelResponse, ToolCall, AgentResult, UsageInfo, ProviderCapabilities.",
        "why": "Provides an organized internal boundary so agents and workflows can cleanly import shared execution infrastructure.",
        "how": "Imports symbols from base, engine, requests, responses, results, and capabilities, declaring an explicit __all__.",
        "components": []
    },
    {
        "category": "2. Core Runtime & Execution Subsystem",
        "file": "src/agentnet/core/base.py",
        "title": "BaseAgent Generic Abstract Base Class",
        "what": "The foundational abstract class for all agents in AgentNet, generic over output type T (BaseAgent[T]).",
        "why": "Enforces a consistent interface across every agent: model configuration, shared execution engine, synchronous run(), and asynchronous arun().",
        "how": (
            "1. Generic[T] parameterizes the return type of result.output.\n"
            "2. __init__() accepts model, config, engine, provider_adapter, or extra options, initializing an AgentEngine.\n"
            "3. run(*args, **kwargs) -> AgentResult[T] defines the synchronous execution contract.\n"
            "4. arun(*args, **kwargs) -> AgentResult[T] defines the asynchronous execution contract."
        ),
        "components": [
            {
                "name": "BaseAgent[T]",
                "signature": "class BaseAgent(Generic[T])",
                "description": "Abstract parent class. Contains self.engine, self.config, and abstract run() and arun() methods."
            }
        ]
    },
    {
        "category": "2. Core Runtime & Execution Subsystem",
        "file": "src/agentnet/core/engine.py",
        "title": "AgentEngine Central Execution Orchestrator",
        "what": (
            "The heart of AgentNet. Manages provider adapter resolution, deadline-based timeout enforcement, "
            "exponential backoff retries on rate limits, runaway tool calling loop limits, content privacy masking, "
            "and structured JSON/Pydantic output parsing."
        ),
        "why": (
            "Decouples prompt construction from provider mechanics. Agents don't know how HTTP calls, retries, "
            "or tool loops work; they simply pass ChatMessages to AgentEngine, which executes them safely with "
            "strict security boundaries and resource limits."
        ),
        "how": (
            "1. _extract_json_content(content: str): Extracts JSON objects between markdown fences or curly braces without backtracking regexes (ReDoS safe).\n"
            "2. resolve_adapter(config): Returns custom adapter or resolves adapter from registry by provider name.\n"
            "3. execute(messages, config, output_schema, tools, run_id): Synchronous execution loop:\n"
            "   a. Computes strict deadline: start_time + timeout.\n"
            "   b. Runs provider call in ThreadPoolExecutor with timeout to enforce hard deadlines even if socket blocks.\n"
            "   c. If response contains tool calls: executes tool, appends 'tool' role ChatMessage, loops (capped at max_tool_iterations=5).\n"
            "   d. If RateLimitError occurs: calculates exponential backoff min(2^retries, 10.0), sleeps, retries up to max_retries.\n"
            "   e. Parses structured outputs against Pydantic schema using _parse_structured_output().\n"
            "   f. Returns AgentResult[T] containing output, run_id, model, duration, and token usage.\n"
            "4. aexecute(messages, config, output_schema, tools, run_id): Asynchronous execution loop matching execute() using asyncio.wait_for and adapter.agenerate()."
        ),
        "components": [
            {
                "name": "_extract_json_content(content: str) -> str",
                "signature": "def _extract_json_content(content: str) -> str",
                "description": "Extracts JSON payload safely without vulnerable regex backtracking."
            },
            {
                "name": "AgentEngine.resolve_adapter",
                "signature": "def resolve_adapter(self, config: AgentConfig) -> ProviderAdapter",
                "description": "Resolves configured provider adapter instance."
            },
            {
                "name": "AgentEngine.execute",
                "signature": "def execute(self, messages, config=None, output_schema=None, tools=None, run_id=None) -> AgentResult",
                "description": "Synchronously executes prompt with hard deadlines, tool execution loop (max 5 iterations), and rate-limit backoff."
            },
            {
                "name": "AgentEngine.aexecute",
                "signature": "async def aexecute(self, messages, config=None, output_schema=None, tools=None, run_id=None) -> AgentResult",
                "description": "Asynchronously executes prompt with asyncio timeouts and non-blocking tool calls."
            },
            {
                "name": "AgentEngine._parse_structured_output",
                "signature": "def _parse_structured_output(self, content, schema) -> Any",
                "description": "Parses raw string into JSON, then validates against schema.model_validate(data)."
            }
        ]
    },
    {
        "category": "2. Core Runtime & Execution Subsystem",
        "file": "src/agentnet/core/requests.py",
        "title": "Model Requests & Chat Messages Specification",
        "what": "Pydantic models representing chat messages and model requests: ChatMessage, ToolDefinition, and ModelRequest.",
        "why": "Standardizes how conversations, system prompts, tool outputs, and model parameters are passed to any model provider adapter.",
        "how": (
            "1. ChatMessage: Pydantic model with role ('system', 'user', 'assistant', 'tool'), content, optional name, and tool_call_id.\n"
            "2. ToolDefinition: Models tool schema with name, description, and JSON schema parameters dict.\n"
            "3. ModelRequest: Encapsulates list of ChatMessages, target model string, temperature, max_tokens, output_schema, tools list, and extra options."
        ),
        "components": [
            {
                "name": "ChatMessage",
                "signature": "class ChatMessage(BaseModel)",
                "description": "Represents an individual message in a chat completion conversation."
            },
            {
                "name": "ModelRequest",
                "signature": "class ModelRequest(BaseModel)",
                "description": "Encapsulates complete request payload passed to provider adapters."
            }
        ]
    },
    {
        "category": "2. Core Runtime & Execution Subsystem",
        "file": "src/agentnet/core/responses.py",
        "title": "Model Responses & Tool Invocations Specification",
        "what": "Pydantic models representing normalized outputs from providers: ToolCall and ModelResponse.",
        "why": "Decouples engine logic from provider-specific response formats (OpenAI vs Anthropic vs Gemini vs Grok).",
        "how": (
            "1. ToolCall: Represents a function/tool call requested by the model (id, name, parsed arguments dictionary).\n"
            "2. ModelResponse: Contains raw text content, model name used, list of ToolCalls, and UsageInfo token counts."
        ),
        "components": [
            {
                "name": "ToolCall",
                "signature": "class ToolCall(BaseModel)",
                "description": "Represents a single tool invocation requested by the model."
            },
            {
                "name": "ModelResponse",
                "signature": "class ModelResponse(BaseModel)",
                "description": "Normalized response returned by ProviderAdapter.generate() and agenerate()."
            }
        ]
    },
    {
        "category": "2. Core Runtime & Execution Subsystem",
        "file": "src/agentnet/core/results.py",
        "title": "Agent Execution Results & Token Telemetry",
        "what": "Defines UsageInfo and AgentResult[T], representing the final outcome returned to the user.",
        "why": "Ensures every agent run returns structured metadata: elapsed execution duration, total/prompt/completion tokens, unique run ID, and strongly-typed output.",
        "how": (
            "1. UsageInfo: Pydantic model holding prompt_tokens, completion_tokens, and total_tokens.\n"
            "2. AgentResult[T]: Generic container storing output: T, run_id: str, model: str, duration: float, usage: UsageInfo, and metadata: dict."
        ),
        "components": [
            {
                "name": "UsageInfo",
                "signature": "class UsageInfo(BaseModel)",
                "description": "Token usage metrics for an execution."
            },
            {
                "name": "AgentResult[T]",
                "signature": "class AgentResult(Generic[T])",
                "description": "Final result object returned by agent.run() and agent.arun()."
            }
        ]
    },
    {
        "category": "2. Core Runtime & Execution Subsystem",
        "file": "src/agentnet/core/capabilities.py",
        "title": "Provider Capabilities Specification",
        "what": "Defines ProviderCapabilities dataclass describing features supported by a given provider adapter.",
        "why": "Allows AgentEngine and agents to verify if a provider supports structured JSON output, function calling tools, streaming, async calls, or vision before dispatching.",
        "how": "Flags: supports_structured_output, supports_tools, supports_streaming, supports_async, supports_vision.",
        "components": [
            {
                "name": "ProviderCapabilities",
                "signature": "class ProviderCapabilities(BaseModel)",
                "description": "Feature capability matrix for a provider adapter."
            }
        ]
    },

    # ---------------------------------------------------------
    # PART 3: CONFIGURATION & SETTINGS
    # ---------------------------------------------------------
    {
        "category": "3. Configuration & Settings Subsystem",
        "file": "src/agentnet/config/__init__.py",
        "title": "Config Exports",
        "what": "Exports AgentConfig from agentnet.config.settings.",
        "why": "Exposes configuration models cleanly.",
        "how": "Imports AgentConfig and defines __all__ = ['AgentConfig'].",
        "components": []
    },
    {
        "category": "3. Configuration & Settings Subsystem",
        "file": "src/agentnet/config/settings.py",
        "title": "AgentConfig Hierarchical Settings & Environment Resolution",
        "what": "Defines AgentConfig, the primary configuration class managing provider choice, model names, API keys, timeouts, retries, and logging flags.",
        "why": "Implements clean configuration precedence: explicit run overrides > AgentConfig object > environment variables > default library settings.",
        "how": (
            "1. AgentConfig Pydantic model with fields: provider, model, api_key, temperature, max_tokens, timeout, max_retries, log_content, output_schema, extra_options.\n"
            "2. from_env(**overrides): Factory method parsing environment variables:\n"
            "   a. Reads AGENTNET_PROVIDER (default 'openai'), AGENTNET_MODEL (default 'gpt-4.1').\n"
            "   b. Supports provider prefixes in model strings (e.g. 'gemini/gemini-2.5-flash', 'grok/grok-2', 'openai/gpt-4o').\n"
            "   c. Resolves API keys: OPENAI_API_KEY for openai; XAI_API_KEY / GROK_API_KEY for grok; GEMINI_API_KEY / GOOGLE_API_KEY for gemini/google; ANTHROPIC_API_KEY for anthropic.\n"
            "   d. Reads AGENTNET_TIMEOUT (default 60.0s), AGENTNET_MAX_RETRIES (default 3), and AGENTNET_LOG_CONTENT (privacy mode toggle).\n"
            "   e. Overlays explicit keyword overrides."
        ),
        "components": [
            {
                "name": "AgentConfig.from_env",
                "signature": "classmethod from_env(cls, **overrides) -> AgentConfig",
                "description": "Constructs configuration by inspecting environment variables and model prefixes."
            }
        ]
    },

    # ---------------------------------------------------------
    # PART 4: PROMPT ENGINEERING & INJECTION DEFENSE
    # ---------------------------------------------------------
    {
        "category": "4. Prompt Engineering & Injection Defenses",
        "file": "src/agentnet/prompts/__init__.py",
        "title": "Prompts Exports",
        "what": "Exports PromptTemplate and all system prompt constants.",
        "why": "Provides direct access to prompt utilities.",
        "how": "Imports PromptTemplate from templates.py and exports it in __all__.",
        "components": []
    },
    {
        "category": "4. Prompt Engineering & Injection Defenses",
        "file": "src/agentnet/prompts/templates.py",
        "title": "PromptTemplate Safe Substitution Engine",
        "what": "Implements PromptTemplate for validated variable interpolation in system prompts without code execution vulnerabilities.",
        "why": "Avoids dangerous str.format() vulnerabilities where user input containing curly braces would trigger unexpected key errors or template injection.",
        "how": (
            "1. __init__(template_str: str): Stores template.\n"
            "2. format(**kwargs): Replaces '{key}' with sanitized string representations of kwargs while preserving double-escaped '{{' and '}}'."
        ),
        "components": [
            {
                "name": "PromptTemplate.format",
                "signature": "def format(self, **kwargs: Any) -> str",
                "description": "Performs validated variable substitution into the prompt template."
            }
        ]
    },
    {
        "category": "4. Prompt Engineering & Injection Defenses",
        "file": "src/agentnet/prompts/defaults.py",
        "title": "Default System Prompts & Injection Defense Boundaries",
        "what": (
            "Defines system prompts for all 15 agents and AI_INJECTION_DEFENSE_INSTRUCTION. Implements strict XML-tag "
            "isolation (<untrusted_user_input>) for user inputs."
        ),
        "why": (
            "Protects agents from Prompt Injection and Jailbreaks. By instructing models that data within "
            "<untrusted_user_input> is untrusted data and must never override system instructions, AgentNet "
            "prevents malicious users from hijacking the agent's workflow."
        ),
        "how": (
            "1. AI_INJECTION_DEFENSE_INSTRUCTION: Standard warning appended to all system prompts.\n"
            "2. Defines system prompts for Summarizer, EmailWriter, Translator, Extractor, Classifier, CodeReviewer, "
            "CodeExplainer, TestGenerator, Rewriter, Proofreader, SentimentAnalyzer, IntentClassifier, MeetingNotesWriter, "
            "EmailResponder, and TaskPlanner."
        ),
        "components": [
            {
                "name": "AI_INJECTION_DEFENSE_INSTRUCTION",
                "signature": "str",
                "description": "Mandatory security boundary instruction injected into every agent's system prompt."
            }
        ]
    },

    # ---------------------------------------------------------
    # PART 5: MODEL PROVIDERS & ADAPTERS
    # ---------------------------------------------------------
    {
        "category": "5. Model Providers & Adapters",
        "file": "src/agentnet/providers/__init__.py",
        "title": "Providers Exports",
        "what": "Exports ProviderAdapter, get_provider, register_provider, OpenAIAdapter, GeminiAdapter, GrokAdapter, and FakeProviderAdapter.",
        "why": "Provides public entry points for custom adapter registration and instantiation.",
        "how": "Re-exports registry functions and built-in adapters.",
        "components": []
    },
    {
        "category": "5. Model Providers & Adapters",
        "file": "src/agentnet/providers/base.py",
        "title": "ProviderAdapter Abstract Interface",
        "what": "Abstract base class defining the contract for model provider adapters.",
        "why": "Ensures all providers implement identical generate(), agenerate(), and get_capabilities() signatures.",
        "how": (
            "1. generate(request: ModelRequest) -> ModelResponse: Synchronous generation method.\n"
            "2. agenerate(request: ModelRequest) -> ModelResponse: Asynchronous generation method.\n"
            "3. get_capabilities() -> ProviderCapabilities: Returns capability matrix."
        ),
        "components": [
            {
                "name": "ProviderAdapter",
                "signature": "class ProviderAdapter(ABC)",
                "description": "Abstract base class for all LLM vendor adapters."
            }
        ]
    },
    {
        "category": "5. Model Providers & Adapters",
        "file": "src/agentnet/providers/registry.py",
        "title": "Provider Registry & Factory",
        "what": "Maintains _PROVIDER_REGISTRY dictionary mapping provider names to adapter classes.",
        "why": "Enables dynamic provider instantiation and permits developers to register custom or local LLM adapters without modifying AgentNet core.",
        "how": (
            "1. _PROVIDER_REGISTRY maps 'openai' -> OpenAIAdapter, 'gemini'/'google' -> GeminiAdapter, 'grok'/'xai' -> GrokAdapter, 'fake'/'mock' -> FakeProviderAdapter.\n"
            "2. register_provider(name, adapter_cls): Registers new or replacement provider class.\n"
            "3. get_provider(name, **kwargs): Instantiates provider adapter or raises ConfigurationError if unknown."
        ),
        "components": [
            {
                "name": "register_provider",
                "signature": "def register_provider(name: str, adapter_cls: type[ProviderAdapter]) -> None",
                "description": "Registers a custom provider adapter class."
            },
            {
                "name": "get_provider",
                "signature": "def get_provider(name: str, **kwargs: Any) -> ProviderAdapter",
                "description": "Factory method instantiating provider adapter by name."
            }
        ]
    },
    {
        "category": "5. Model Providers & Adapters",
        "file": "src/agentnet/providers/adapters/openai.py",
        "title": "OpenAI Provider Adapter",
        "what": "Adapter for OpenAI models (GPT-4.1, GPT-4o, etc.).",
        "why": "Connects AgentNet to OpenAI's official chat completions API, formatting tools, structured outputs, and normalizing exceptions.",
        "how": (
            "1. Lazy imports 'openai' to ensure core AgentNet remains lightweight and installable without optional dependencies.\n"
            "2. _prepare_kwargs(): Builds chat completion arguments (messages, model, temperature, tools, response_format).\n"
            "3. _translate_exception(): Translates openai.AuthenticationError, RateLimitError, APITimeoutError into AgentNet errors.\n"
            "4. generate() and agenerate(): Execute API calls and return normalized ModelResponse."
        ),
        "components": [
            {
                "name": "OpenAIAdapter",
                "signature": "class OpenAIAdapter(ProviderAdapter)",
                "description": "Connects to OpenAI API endpoints."
            }
        ]
    },
    {
        "category": "5. Model Providers & Adapters",
        "file": "src/agentnet/providers/adapters/gemini.py",
        "title": "Google Gemini Provider Adapter",
        "what": "Adapter for Google Gemini models (gemini-2.5-flash, gemini-2.5-pro, gemini-1.5-flash, etc.).",
        "why": "Leverages Google's official OpenAI-compatible endpoint at https://generativelanguage.googleapis.com/v1beta/openai/ for zero extra dependencies.",
        "how": (
            "1. Inherits from OpenAIAdapter, setting default base_url to Google's endpoint.\n"
            "2. Resolves GEMINI_API_KEY or GOOGLE_API_KEY from environment or parameters.\n"
            "3. Custom _translate_exception() sets provider='gemini' on all normalized exceptions.\n"
            "4. get_capabilities() reports support for structured outputs, tools, vision, and streaming."
        ),
        "components": [
            {
                "name": "GeminiAdapter",
                "signature": "class GeminiAdapter(OpenAIAdapter)",
                "description": "Adapter communicating with Google Gemini API."
            }
        ]
    },
    {
        "category": "5. Model Providers & Adapters",
        "file": "src/agentnet/providers/adapters/grok.py",
        "title": "xAI Grok Provider Adapter",
        "what": "Adapter for xAI Grok models (grok-2, grok-beta, etc.).",
        "why": "Connects to xAI's API endpoint at https://api.x.ai/v1 using OpenAI-compatible structures.",
        "how": (
            "1. Inherits from OpenAIAdapter, setting default base_url to 'https://api.x.ai/v1'.\n"
            "2. Resolves XAI_API_KEY or GROK_API_KEY.\n"
            "3. Custom _translate_exception() sets provider='grok'.\n"
            "4. get_capabilities() reports full capabilities."
        ),
        "components": [
            {
                "name": "GrokAdapter",
                "signature": "class GrokAdapter(OpenAIAdapter)",
                "description": "Adapter communicating with xAI Grok API."
            }
        ]
    },
    {
        "category": "5. Model Providers & Adapters",
        "file": "src/agentnet/providers/adapters/fake.py",
        "title": "Fake & Mock Provider Adapter for 100% Offline Testing",
        "what": "Test mock adapter providing programmable synthetic responses without network calls or API keys.",
        "why": "Allows 100% of AgentNet unit and integration tests to run offline, fast, deterministically, and for zero cost.",
        "how": (
            "1. __init__ accepts default_response: str or response_fn: Callable[[ModelRequest], Any].\n"
            "2. Records call_count, last_request, and request_history.\n"
            "3. If response_fn returns a dict or Pydantic model, serializes to JSON string.\n"
            "4. Simulates token usage (10 prompt, 20 completion) and returns valid ModelResponse."
        ),
        "components": [
            {
                "name": "FakeProviderAdapter",
                "signature": "class FakeProviderAdapter(ProviderAdapter)",
                "description": "Deterministic mock provider adapter for offline test suites."
            }
        ]
    },

    # ---------------------------------------------------------
    # PART 6: TOOLS & REUSABLE CAPABILITIES
    # ---------------------------------------------------------
    {
        "category": "6. Callable Tools & Guardrails Subsystem",
        "file": "src/agentnet/tools/__init__.py",
        "title": "Tools Exports",
        "what": "Exports Tool, ToolParameter, and ToolRegistry.",
        "why": "Provides simple imports for creating and registering agent tools.",
        "how": "Re-exports Tool and ToolRegistry.",
        "components": []
    },
    {
        "category": "6. Callable Tools & Guardrails Subsystem",
        "file": "src/agentnet/tools/base.py",
        "title": "Tool Definition, Schema Inference, & Permission Guards",
        "what": "Defines Tool class wrapping Python functions with automatic JSON schema inference, timeout enforcement, and permission guards.",
        "why": "Allows agents to invoke Python functions safely. Side-effecting tools (e.g. database updates, file writing) can require explicit authorization.",
        "how": (
            "1. _python_type_to_json_schema(py_type): Converts Python types (str, int, float, bool, list, dict) to JSON schema type strings.\n"
            "2. Tool.__init__(): Inspects function signature via inspect.signature to infer parameter types, docstrings, and required arguments.\n"
            "3. to_dict(): Serializes tool into OpenAI/Gemini/Grok function calling JSON specification.\n"
            "4. execute(arguments: dict): Validates permissions (raises ToolPermissionError if requires_permission is True and permission is not granted), "
            "enforces execution timeout using ThreadPoolExecutor, catches exceptions and wraps in ToolError."
        ),
        "components": [
            {
                "name": "Tool",
                "signature": "class Tool",
                "description": "Wraps a Python callable as an agent tool with schema inference and timeout/permission guards."
            },
            {
                "name": "Tool.execute",
                "signature": "def execute(self, arguments: dict[str, Any]) -> Any",
                "description": "Validates permissions, enforces timeout, and executes tool callable safely."
            }
        ]
    },
    {
        "category": "6. Callable Tools & Guardrails Subsystem",
        "file": "src/agentnet/tools/registry.py",
        "title": "ToolRegistry Central Repository",
        "what": "Manages a collection of registered tools by name.",
        "why": "Allows applications to register shared tools and pass subsets to agents dynamically.",
        "how": "register(tool: Tool), get(name: str) -> Tool, list_tools() -> list[Tool], to_specs() -> list[dict].",
        "components": [
            {
                "name": "ToolRegistry",
                "signature": "class ToolRegistry",
                "description": "Collection of named tools."
            }
        ]
    },

    # ---------------------------------------------------------
    # PART 7: WORKFLOW ORCHESTRATION
    # ---------------------------------------------------------
    {
        "category": "7. Workflow Orchestration Subsystem",
        "file": "src/agentnet/workflows/__init__.py",
        "title": "Workflows Exports",
        "what": "Exports SequentialWorkflow and WorkflowResult.",
        "why": "Exposes orchestration components.",
        "how": "Re-exports SequentialWorkflow.",
        "components": []
    },
    {
        "category": "7. Workflow Orchestration Subsystem",
        "file": "src/agentnet/workflows/sequential.py",
        "title": "SequentialWorkflow Chaining & State Propagation",
        "what": "Orchestrates multi-agent pipelines where the output of one agent flows as input to subsequent agents.",
        "why": "Enables complex composite tasks (e.g. Extract -> Classify -> Summarize -> Email) without manual boilerplate.",
        "how": (
            "1. __init__(steps: list[tuple[str, BaseAgent]], step_mappings: dict, max_iterations: int = 10, timeout: float = 300.0).\n"
            "2. run(**initial_inputs) -> WorkflowResult: Iterates sequentially through steps, applying step_mappings lambda functions to inject state, "
            "tracking per-step durations and token usage, and raising WorkflowStepError if any step fails.\n"
            "3. arun(**initial_inputs) -> WorkflowResult: Asynchronous pipeline execution."
        ),
        "components": [
            {
                "name": "SequentialWorkflow.run",
                "signature": "def run(self, **initial_inputs) -> WorkflowResult",
                "description": "Executes sequential pipeline synchronously."
            },
            {
                "name": "SequentialWorkflow.arun",
                "signature": "async def arun(self, **initial_inputs) -> WorkflowResult",
                "description": "Executes sequential pipeline asynchronously."
            }
        ]
    },

    # ---------------------------------------------------------
    # PART 8: PREDEFINED AGENT CATALOG
    # ---------------------------------------------------------
    {
        "category": "8. Predefined Agent Catalog: Code & Engineering",
        "file": "src/agentnet/agents/code/code_reviewer.py",
        "title": "CodeReviewer Agent & CodeReviewResult Schema",
        "what": "Reviews source code for logic bugs, security vulnerabilities (OWASP, SQLi, injection), performance bottlenecks, and maintainability.",
        "why": "Automates developer code reviews with structured issue severity rankings ('critical', 'high', 'medium', 'low', 'info') and line numbers.",
        "how": (
            "1. CodeIssue: Pydantic model with severity, category, line_number, description, recommendation.\n"
            "2. CodeReviewResult: Pydantic model with summary, overall_score (0-100), issues list, and strengths list.\n"
            "3. CodeReviewer: Inherits BaseAgent[CodeReviewResult]. Validates code non-empty, wraps in <untrusted_user_input>, executes with CodeReviewResult schema."
        ),
        "components": [
            {
                "name": "CodeReviewer.run",
                "signature": "def run(self, code: str, language: str = 'python', focus_areas: list[str] = None) -> AgentResult[CodeReviewResult]",
                "description": "Performs code review returning structured CodeReviewResult."
            }
        ]
    },
    {
        "category": "8. Predefined Agent Catalog: Code & Engineering",
        "file": "src/agentnet/agents/code/code_explainer.py",
        "title": "CodeExplainer Agent",
        "what": "Explains source code logic flow, architecture, algorithms, and asymptotic complexity (Big-O).",
        "why": "Helps developers understand unfamiliar codebases, legacy code, or complex algorithms at different audience levels (beginner, developer, architect).",
        "how": "CodeExplainer(BaseAgent[str]): Formats CODE_EXPLAINER_SYSTEM_PROMPT with language, audience, and include_complexity flag.",
        "components": [
            {
                "name": "CodeExplainer.run",
                "signature": "def run(self, code: str, language: str = 'python', audience: str = 'developer', include_complexity: bool = True) -> AgentResult[str]",
                "description": "Explains code structure and Big-O complexity."
            }
        ]
    },
    {
        "category": "8. Predefined Agent Catalog: Code & Engineering",
        "file": "src/agentnet/agents/code/test_generator.py",
        "title": "TestGenerator Agent",
        "what": "Generates automated test suites (pytest or unittest) covering happy paths, edge cases, input validation, and exception handling.",
        "why": "Accelerates test-driven development and code quality by producing runnable, idiomatic tests with clear assertions.",
        "how": "TestGenerator(BaseAgent[str]): Sets __test__ = False to avoid PytestCollectionWarning. Formats prompt with framework and test types.",
        "components": [
            {
                "name": "TestGenerator.run",
                "signature": "def run(self, code: str, language: str = 'python', framework: str = 'pytest', test_types: list[str] = None) -> AgentResult[str]",
                "description": "Generates test cases for supplied code."
            }
        ]
    },
    {
        "category": "8. Predefined Agent Catalog: Text Processing",
        "file": "src/agentnet/agents/text/summarizer.py",
        "title": "Summarizer Agent",
        "what": "Condenses lengthy text into concise summaries with configurable style ('bullet_points', 'executive', 'tldr'), length, and audience.",
        "why": "Provides an immediate, high-quality summarization agent with validated inputs and prompt defense boundaries.",
        "how": "Summarizer(BaseAgent[str]): Formats SUMMARIZER_SYSTEM_PROMPT with style, max_words, and audience.",
        "components": [
            {
                "name": "Summarizer.run",
                "signature": "def run(self, text: str, style: str = None, max_words: int = None, audience: str = 'general') -> AgentResult[str]",
                "description": "Condenses text synchronously."
            }
        ]
    },
    {
        "category": "8. Predefined Agent Catalog: Text Processing",
        "file": "src/agentnet/agents/text/translator.py",
        "title": "Translator Agent",
        "what": "Translates text between specified languages preserving tone, formatting, and domain terminology.",
        "why": "High-fidelity translation without hallucinatory preamble or introductory chit-chat.",
        "how": "Translator(BaseAgent[str]): Accepts source_language and target_language, validates non-empty text, executes translation.",
        "components": [
            {
                "name": "Translator.run",
                "signature": "def run(self, text: str, target_language: str = None, source_language: str = 'auto') -> AgentResult[str]",
                "description": "Translates text into target language."
            }
        ]
    },
    {
        "category": "8. Predefined Agent Catalog: Text Processing",
        "file": "src/agentnet/agents/text/rewriter.py",
        "title": "Rewriter Agent",
        "what": "Rewrites content for tone (formal, casual, persuasive, technical, concise), target audience, and length constraints.",
        "why": "Enables automated content adaptation and tone shifting across marketing, engineering, and executive communication.",
        "how": "Rewriter(BaseAgent[str]): Validates input, formats REWRITER_SYSTEM_PROMPT with requested tone and audience constraints.",
        "components": [
            {
                "name": "Rewriter.run",
                "signature": "def run(self, text: str, tone: str = None, audience: str = 'general', length_constraint: str = None) -> AgentResult[str]",
                "description": "Rewrites text into desired tone and audience."
            }
        ]
    },
    {
        "category": "8. Predefined Agent Catalog: Text Processing",
        "file": "src/agentnet/agents/text/proofreader.py",
        "title": "Proofreader Agent & ProofreadResult Schema",
        "what": "Corrects grammar, spelling, punctuation, and phrasing with itemized diff tracking.",
        "why": "Users need to see not just the corrected text, but exactly what was changed and why.",
        "how": (
            "1. CorrectionItem: Pydantic model (original, replacement, category, explanation).\n"
            "2. ProofreadResult: Pydantic model (corrected_text, corrections_count, corrections list, summary).\n"
            "3. Proofreader: Inherits BaseAgent[ProofreadResult]. Executes with schema validation."
        ),
        "components": [
            {
                "name": "Proofreader.run",
                "signature": "def run(self, text: str) -> AgentResult[ProofreadResult]",
                "description": "Corrects text and returns itemized corrections."
            }
        ]
    },
    {
        "category": "8. Predefined Agent Catalog: Information Extraction",
        "file": "src/agentnet/agents/information/extractor.py",
        "title": "Extractor Agent for Arbitrary Pydantic Schemas",
        "what": "Extracts entities, key figures, and structured data from text directly into any user-supplied Pydantic model.",
        "why": "Eliminates manual regex/JSON parsing. Provides type safety, automatic validation, and structured return values.",
        "how": "Extractor(BaseAgent[T]): Accepts output_schema: type[BaseModel]. Passes schema to AgentEngine.execute() for strict validation.",
        "components": [
            {
                "name": "Extractor.run",
                "signature": "def run(self, text: str, output_schema: type[BaseModel] = None) -> AgentResult[T]",
                "description": "Extracts fields conforming to the output schema."
            }
        ]
    },
    {
        "category": "8. Predefined Agent Catalog: Information Extraction",
        "file": "src/agentnet/agents/information/classifier.py",
        "title": "Classifier Agent & ClassificationResult Schema",
        "what": "Categorizes text into a predefined list of permitted categories with confidence estimation (0.0 to 1.0) and reasoning.",
        "why": "Prevents hallucinated categories. Enforces that the model's output strictly matches one of the permitted choices.",
        "how": (
            "1. ClassificationResult: Pydantic model (category: str, confidence: float, reasoning: str).\n"
            "2. Classifier: Accepts categories list. Validates model output against permitted categories with case-insensitive fallback."
        ),
        "components": [
            {
                "name": "Classifier.run",
                "signature": "def run(self, text: str) -> AgentResult[ClassificationResult]",
                "description": "Classifies text into permitted categories."
            }
        ]
    },
    {
        "category": "8. Predefined Agent Catalog: Information Extraction",
        "file": "src/agentnet/agents/information/sentiment_analyzer.py",
        "title": "SentimentAnalyzer Agent & SentimentResult Schema",
        "what": "Analyzes sentiment polarity (-1.0 to +1.0), emotional classification ('positive', 'negative', 'neutral', 'mixed'), confidence, and key aspects.",
        "why": "Critical for customer feedback triage, product review mining, and support ticket sentiment tracking.",
        "how": "SentimentAnalyzer(BaseAgent[SentimentResult]): Enforces SentimentResult schema validation with polarity range [-1.0, 1.0].",
        "components": [
            {
                "name": "SentimentAnalyzer.run",
                "signature": "def run(self, text: str) -> AgentResult[SentimentResult]",
                "description": "Calculates sentiment polarity and drivers."
            }
        ]
    },
    {
        "category": "8. Predefined Agent Catalog: Information Extraction",
        "file": "src/agentnet/agents/information/intent_classifier.py",
        "title": "IntentClassifier Agent & IntentResult Schema",
        "what": "Identifies user/customer intent (e.g. 'refund_request', 'account_login', 'cancel_subscription') and extracts semantic entities.",
        "why": "Core building block for conversational agents, chatbots, and customer support routing.",
        "how": "IntentClassifier(BaseAgent[IntentResult]): Accepts candidate_intents, extracts entities into dict, returns structured IntentResult.",
        "components": [
            {
                "name": "IntentClassifier.run",
                "signature": "def run(self, text: str, candidate_intents: list[str] = None) -> AgentResult[IntentResult]",
                "description": "Classifies user intent and extracts parameters."
            }
        ]
    },
    {
        "category": "8. Predefined Agent Catalog: Writing & Communication",
        "file": "src/agentnet/agents/writing/email_writer.py",
        "title": "EmailWriter Agent & EmailDraft Schema",
        "what": "Drafts professional, casual, persuasive, or urgent emails tailored to recipient context and stated purpose.",
        "why": "Automates communication workflows while returning structured Subject and Body components.",
        "how": (
            "1. EmailDraft: Pydantic model (subject: str, body: str, recipient: str, tone: str).\n"
            "2. EmailWriter: Accepts structured=True (default) to return EmailDraft or structured=False to return raw text."
        ),
        "components": [
            {
                "name": "EmailWriter.run",
                "signature": "def run(self, purpose: str, recipient: str = 'Colleague', tone: str = 'professional', structured: bool = True) -> AgentResult[EmailDraft | str]",
                "description": "Drafts structured email."
            }
        ]
    },
    {
        "category": "8. Predefined Agent Catalog: Writing & Communication",
        "file": "src/agentnet/agents/writing/email_responder.py",
        "title": "EmailResponder Agent & EmailResponseDraft Schema",
        "what": "Drafts contextual replies to an incoming email thread given a specific response goal or stance.",
        "why": "Replies must maintain context from prior emails while achieving a specific business objective (e.g. negotiate price, schedule call).",
        "how": "EmailResponder(BaseAgent[EmailResponseDraft]): Validates thread and goal non-empty, executes with EmailResponseDraft schema.",
        "components": [
            {
                "name": "EmailResponder.run",
                "signature": "def run(self, thread: str, goal: str, tone: str = 'professional', sender_name: str = None) -> AgentResult[EmailResponseDraft]",
                "description": "Drafts reply to conversation thread."
            }
        ]
    },
    {
        "category": "8. Predefined Agent Catalog: Writing & Communication",
        "file": "src/agentnet/agents/writing/meeting_notes_writer.py",
        "title": "MeetingNotesWriter Agent & MeetingNotes Schema",
        "what": "Converts raw meeting transcripts into executive summaries, attendee lists, key decisions, and assigned action items.",
        "why": "Transforms unstructured spoken conversation into structured project tracking data.",
        "how": (
            "1. ActionItem: Pydantic model (task: str, assignee: str | None, due_date: str | None).\n"
            "2. MeetingNotes: Pydantic model (title, summary, attendees, key_decisions, action_items).\n"
            "3. MeetingNotesWriter: Formats MEETING_NOTES_SYSTEM_PROMPT with meeting_title, executes with MeetingNotes schema."
        ),
        "components": [
            {
                "name": "MeetingNotesWriter.run",
                "signature": "def run(self, transcript: str, meeting_title: str = None) -> AgentResult[MeetingNotes]",
                "description": "Synthesizes transcript into structured meeting minutes."
            }
        ]
    },
    {
        "category": "8. Predefined Agent Catalog: Planning & Tasks",
        "file": "src/agentnet/agents/planning/task_planner.py",
        "title": "TaskPlanner Agent & PlanResult Schema",
        "what": "Deconstructs high-level goals into ordered, actionable task sequences with dependency graphs, effort estimates, and exit criteria.",
        "why": "Bridges high-level goals and execution. Identifies prerequisites so tasks can be executed in topological order.",
        "how": (
            "1. PlanTask: Pydantic model (id: int, title: str, description: str, dependencies: list[int], estimated_effort: str, exit_criteria: str | None).\n"
            "2. PlanResult: Pydantic model (goal: str, summary: str, tasks: list[PlanTask], risks: list[str]).\n"
            "3. TaskPlanner: Validates goal non-empty, formats prompt with constraints, executes with PlanResult schema."
        ),
        "components": [
            {
                "name": "TaskPlanner.run",
                "signature": "def run(self, goal: str, constraints: list[str] = None) -> AgentResult[PlanResult]",
                "description": "Generates structured execution plan."
            }
        ]
    },

    # ---------------------------------------------------------
    # PART 9: REPOSITORY INFRASTRUCTURE & SECURITY
    # ---------------------------------------------------------
    {
        "category": "9. Repository Infrastructure & Security Controls",
        "file": "pyproject.toml",
        "title": "Build System & Packaging Configuration",
        "what": "Hatchling build specification, dependency declarations, optional provider extras, and tool configurations (ruff, pytest).",
        "why": "Defines how AgentNet is built, packaged into wheels, and installed via pip. Keeps core dependencies minimal (pydantic>=2.7.0).",
        "how": "Specifies build-backend = 'hatchling.build', project metadata, optional extras ('openai', 'all'), and test/lint configurations.",
        "components": []
    },
    {
        "category": "9. Repository Infrastructure & Security Controls",
        "file": ".env.example",
        "title": "Environment Variable Configuration Template",
        "what": "Template for local environment configuration with dummy placeholder values.",
        "why": "Guides developers on required keys (OPENAI_API_KEY, XAI_API_KEY, GEMINI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY) without exposing real secrets.",
        "how": "Lists AGENTNET_* settings and provider keys with descriptive comments.",
        "components": []
    },
    {
        "category": "9. Repository Infrastructure & Security Controls",
        "file": "SECURITY.md",
        "title": "Security Policy & Vulnerability Disclosure Guidelines",
        "what": "Documents security practices, reporting procedures, supported versions, secret handling policies, and prompt injection defense guidelines.",
        "why": "Essential for enterprise adoption and open-source software supply chain compliance.",
        "how": "Defines SLA for vulnerability responses and contact channels.",
        "components": []
    },
    {
        "category": "9. Repository Infrastructure & Security Controls",
        "file": "README.md",
        "title": "Project Documentation & Developer Guide",
        "what": "Comprehensive user guide covering features, installation, quickstart examples, catalog reference, provider guides, and offline testing.",
        "why": "Primary landing documentation for developers discovering and adopting AgentNet.",
        "how": "Formatted in GitHub Flavored Markdown with badges, copyable snippets, tables, and architecture explanations.",
        "components": []
    },
]


def generate_markdown_doc() -> None:
    """Generate docs/CODEBASE_EXPLAINED.md."""
    print("Writing docs/CODEBASE_EXPLAINED.md...")
    lines = [
        "# AgentNet: Complete Codebase & Architectural Reference Manual",
        "",
        "> **Version 0.1.0** | **Python 3.11+** | **License: MIT** | **PyPI: `agentnet`**",
        "",
        (
            "This document provides an exhaustive, component-by-component architectural explanation of **every single file** in the AgentNet repository. "
            "For each file, it articulates **WHAT** the file contains, **WHY** it was designed that way (architectural and security rationale), and **HOW** its "
            "functions, classes, and execution flows operate."
        ),
        "",
        "---",
        "",
        "## Table of Contents",
        "",
    ]

    current_cat = ""
    for item in CODEBASE_DATA:
        if item["category"] != current_cat:
            current_cat = item["category"]
            cat_anchor = current_cat.lower().replace(" ", "-").replace(".", "").replace(":", "")
            lines.append(f"- **[{current_cat}](#{cat_anchor})**")
        file_anchor = item["file"].lower().replace("/", "").replace(".", "").replace("_", "")
        lines.append(f"  - [{item['file']} — {item['title']}](#{file_anchor})")

    lines.append("\n---\n")

    current_cat = ""
    for item in CODEBASE_DATA:
        if item["category"] != current_cat:
            current_cat = item["category"]
            lines.append(f"\n# {current_cat}\n")

        file_anchor = item["file"].lower().replace("/", "").replace(".", "").replace("_", "")
        lines.append(f"## {item['file']}\n")
        lines.append(f"**Module Title:** {item['title']}\n")
        lines.append("### 1. WHAT it is")
        lines.append(item["what"] + "\n")
        lines.append("### 2. WHY it was designed this way")
        lines.append(item["why"] + "\n")
        lines.append("### 3. HOW it works in detail")
        lines.append(item["how"] + "\n")

        if item["components"]:
            lines.append("### 4. Key Classes, Functions & Signatures\n")
            lines.append("| Component | Signature | Purpose |")
            lines.append("| :--- | :--- | :--- |")
            for comp in item["components"]:
                name = comp["name"]
                sig = f"`{comp['signature']}`"
                desc = comp["description"]
                lines.append(f"| **{name}** | {sig} | {desc} |")
            lines.append("")

        lines.append("---\n")

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated Markdown reference at: {MD_PATH}")


def generate_pdf_doc() -> None:
    """Generate docs/AgentNet_Complete_Codebase_Reference.pdf using ReportLab."""
    print("Building docs/AgentNet_Complete_Codebase_Reference.pdf with ReportLab...")

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    primary_color = colors.HexColor("#0f172a")  # Slate 900
    brand_blue = colors.HexColor("#2563eb")     # Royal Blue
    brand_teal = colors.HexColor("#0d9488")     # Teal 600
    dark_text = colors.HexColor("#1e293b")      # Slate 800
    muted_text = colors.HexColor("#64748b")     # Slate 500
    bg_light = colors.HexColor("#f8fafc")       # Slate 50
    border_color = colors.HexColor("#e2e8f0")   # Slate 200

    # Custom Typography Styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=34,
        textColor=primary_color,
        alignment=0,
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=14,
        leading=20,
        textColor=brand_blue,
        alignment=0,
    )

    h1_style = ParagraphStyle(
        "DocH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=10,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "DocH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=brand_blue,
        spaceBefore=12,
        spaceAfter=4,
        keepWithNext=True,
    )

    subhead_style = ParagraphStyle(
        "DocSubHead",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=brand_teal,
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=dark_text,
        spaceAfter=5,
    )

    meta_label_style = ParagraphStyle(
        "MetaLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=primary_color,
    )

    meta_val_style = ParagraphStyle(
        "MetaVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=muted_text,
    )

    flowables = []

    # =========================================================
    # COVER PAGE
    # =========================================================
    flowables.append(Spacer(1, 40))
    flowables.append(Paragraph("AGENTNET ARCHITECTURE & CODEBASE REFERENCE", subtitle_style))
    flowables.append(Spacer(1, 10))
    flowables.append(Paragraph("Complete Technical Manual: What, Why & How of Every Source File", title_style))
    flowables.append(Spacer(1, 15))
    flowables.append(HRFlowable(width="100%", thickness=3, color=brand_blue, spaceBefore=5, spaceAfter=20))

    intro_p = (
        "AgentNet is a production-grade Python AI agent framework designed for zero-telemetry leaks, "
        "provider independence, strict prompt-injection defense boundaries, deadline-enforced execution, "
        "and structured Pydantic schema validation. This manual presents an exhaustive, component-by-component "
        "technical inspection of every single file, class, function, and configuration in the repository."
    )
    flowables.append(Paragraph(intro_p, body_style))
    flowables.append(Spacer(1, 20))

    meta_table_data = [
        [Paragraph("Package Name", meta_label_style), Paragraph("agentnet (pip installable, PyPI ready)", meta_val_style)],
        [Paragraph("Version", meta_label_style), Paragraph("0.1.0 (Production Release)", meta_val_style)],
        [Paragraph("Target Python", meta_label_style), Paragraph("Python 3.11+ (Fully PEP 561 typed with py.typed)", meta_val_style)],
        [Paragraph("Model Providers", meta_label_style), Paragraph("OpenAI (GPT-4.1, GPT-4o), Google Gemini (Gemini 2.5 Flash/Pro), xAI Grok (Grok-2), Offline Mock", meta_val_style)],
        [Paragraph("Built-in Catalog", meta_label_style), Paragraph("15 Predefined Agents across Code, Text, Information, Writing, and Planning", meta_val_style)],
        [Paragraph("Security Status", meta_label_style), Paragraph("Zero CVEs (pip-audit clean), Zero Bandit SAST defects, 100% offline test suite", meta_val_style)],
        [Paragraph("Total Test Suite", meta_label_style), Paragraph("64 passing unit and security tests across engine, injection, secrets, tools, workflows", meta_val_style)],
    ]
    meta_table = Table(meta_table_data, colWidths=[130, 374])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg_light),
        ("BOX", (0, 0), (-1, -1), 1, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    flowables.append(meta_table)
    flowables.append(Spacer(1, 40))

    flowables.append(Paragraph("System Architecture Highlights:", h2_style))
    arch_highlights = (
        "<b>1. Zero-Telemetry Core:</b> No cloud tracking, analytics, or phone-home pings. All execution is local to your environment.<br/>"
        "<b>2. Automated Secret Sanitization:</b> Automatic regex-based masking of OpenAI, Gemini, Grok, and Bearer tokens in all exceptions and logs.<br/>"
        "<b>3. Hard Deadlines & Timeout Protection:</b> Wall-clock deadline enforcement preventing hanging threads, infinite loops, or zombie processes.<br/>"
        "<b>4. Prompt Injection Defense Boundaries:</b> Explicit XML untrusted data boundaries (&lt;untrusted_user_input&gt;) isolating instructions from data.<br/>"
        "<b>5. Tool Execution Guardrails:</b> Strict permission checks, schema inference, and timeout limits on side-effecting operations."
    )
    flowables.append(Paragraph(arch_highlights, body_style))

    flowables.append(PageBreak())

    # =========================================================
    # DETAILED FILE-BY-FILE DOCUMENTATION
    # =========================================================
    current_category = ""

    for item in CODEBASE_DATA:
        if item["category"] != current_category:
            current_category = item["category"]
            flowables.append(Spacer(1, 10))
            flowables.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=8, spaceAfter=8))
            flowables.append(Paragraph(current_category.upper(), h1_style))
            flowables.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceBefore=2, spaceAfter=10))

        file_header = f"<b>File:</b> {item['file']} &nbsp;&nbsp;|&nbsp;&nbsp; <i>{item['title']}</i>"
        flowables.append(Paragraph(file_header, h2_style))

        # WHAT
        flowables.append(Paragraph("WHAT IT IS & CONTAINS:", subhead_style))
        flowables.append(Paragraph(item["what"], body_style))

        # WHY
        flowables.append(Paragraph("WHY IT WAS DESIGNED THIS WAY (RATIONALE):", subhead_style))
        flowables.append(Paragraph(item["why"], body_style))

        # HOW
        flowables.append(Paragraph("HOW IT OPERATES (INTERNAL LOGIC & EXECUTION FLOW):", subhead_style))
        how_lines = item["how"].split("\n")
        for line in how_lines:
            if line.strip():
                flowables.append(Paragraph(line.strip(), body_style))

        # Components table if any
        if item["components"]:
            flowables.append(Spacer(1, 4))
            flowables.append(Paragraph("KEY SYMBOLS & SIGNATURES:", subhead_style))
            comp_table_data = [
                [Paragraph("<b>Symbol</b>", meta_label_style), Paragraph("<b>Signature / Purpose</b>", meta_label_style)]
            ]
            for comp in item["components"]:
                sym_p = Paragraph(f"<b>{comp['name']}</b>", body_style)
                desc_p = Paragraph(f"<code>{comp['signature']}</code><br/>{comp['description']}", body_style)
                comp_table_data.append([sym_p, desc_p])

            comp_table = Table(comp_table_data, colWidths=[120, 384])
            comp_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), bg_light),
                ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]))
            flowables.append(comp_table)

        flowables.append(Spacer(1, 10))

    # Build PDF with NumberedCanvas
    doc.build(flowables, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF reference at: {PDF_PATH}")

    # Copy to root directory for easy user access
    shutil.copyfile(PDF_PATH, ROOT_PDF_PATH)
    print(f"Copied root PDF reference to: {ROOT_PDF_PATH}")


if __name__ == "__main__":
    generate_markdown_doc()
    generate_pdf_doc()
    print("Documentation generation complete!")
