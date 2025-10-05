# Amplifier Core Exploration (from v1 to v2)

**Created:** 9/29/2025 18:31:11  
**Updated:** 10/5/2025 9:26:36  
**Exported:** 10/5/2025 9:27:10  
**Link:** [https://claude.ai/chat/538c840f-2621-4869-9831-8242a0bf01f6](https://claude.ai/chat/538c840f-2621-4869-9831-8242a0bf01f6)

## Prompt:

9/29/2025, 6:31:13 PM

Are you able to clone my repo at github.com/microsoft/amplifier to do some work on it?

## Response:

9/29/2025, 6:31:25 PM

```plaintext
Thought process: Evaluated GitHub repository interaction capabilities and limitations.

The user is asking if I can clone their repo at github.com/microsoft/amplifier to do work on it.

Let me think about what capabilities I have:

1. I have access to a DeepWiki tool that can interact with GitHub repositories - I can ask questions about repos and read their documentation
2. I have a REPL/analysis tool that can execute JavaScript code
3. I have web_search and web_fetch tools

However, I cannot actually clone repositories in the traditional sense - I don't have git access or the ability to execute git commands. The DeepWiki tool allows me to ask questions about a repository and read its wiki/documentation, but that's different from cloning it.

What I CAN do:
- Use DeepWiki to ask questions about the repository
- Use DeepWiki to read the repository's documentation structure and contents
- Use web_fetch to potentially read files from the GitHub repository if they're accessible via raw URLs
- Help the user understand the repository
- Write code based on understanding the repository

What I CANNOT do:
- Actually git clone the repository to a local filesystem
- Make commits or push changes to the repository
- Run the code from the repository locally

I should be honest with the user about my capabilities. I can help them understand and work with the repository, but I can't clone it in the traditional sense.
```

I can't clone repositories in the traditional git sense - I don't have access to git commands or a filesystem where I could clone and work with the full repository.

However, I _can_ help you work with the repository in several ways:

1. **Use DeepWiki** - I have access to a tool that can read and analyze GitHub repositories. I can ask questions about the code, understand its structure, and read documentation.

2. **Fetch specific files** - I can use web_fetch to read specific files from the repository if you point me to them.

3. **Write code** - Based on understanding the repository, I can write new code, modifications, or help you work on specific features.

Would you like me to:

- Explore the microsoft/amplifier repository using DeepWiki to understand its structure and help you with something specific?
- Help you write code for a particular feature or modification you have in mind?

What kind of work were you looking to do on the repository?

## Prompt:

9/29/2025, 6:33:10 PM

Ok, sure, let's start with deep research. I want to replace our dependency on Claude Code with our own solution and support for any model.

## Response:

9/29/2025, 6:33:25 PM

```plaintext
Thought process: Strategized research approach for custom multi-model code replacement.

The user wants to replace the dependency on Claude Code in their microsoft/amplifier repository with their own solution that supports any model.

Let me think about whether this is clear enough to proceed with research or if I need clarifying questions:

1. What is the scope of the replacement - are they looking to understand how Claude Code currently works, or do they already know and just need architecture advice?
2. Do they want to understand what features of Claude Code they're currently using?
3. What models specifically are they thinking about supporting?
4. Are they looking for implementation guidance, architecture design, or understanding the current integration?

Actually, looking at this more carefully - the request is fairly clear. They want to:
- Replace a dependency on Claude Code
- Build their own solution
- Support any model (not just Claude)

The research agent will need to:
1. Understand the microsoft/amplifier repository
2. Find how Claude Code is currently being used
3. Understand what Claude Code does
4. Figure out what would be needed to build a replacement that supports multiple models

I think I should ask a couple of clarifying questions to make the research more targeted:
1. What aspects of Claude Code functionality do they need to preserve/replace?
2. What other models are they primarily interested in supporting?
3. Are they looking for architecture recommendations, implementation guidance, or both?

Actually, let me reconsider. The user said "let's start with deep research" which suggests they want comprehensive research first. They may not know all the details yet, which is why they want research.

I'll ask 1-2 targeted clarifying questions to help narrow the scope:
1. Are they looking to understand the current Claude Code integration first, or do they already know how it's used and need architecture/implementation guidance?
2. What models are they thinking of supporting (OpenAI, Anthropic API directly, local models, etc.)?

These are useful and not obvious from the request.
```

I'll help you research how to replace Claude Code with a multi-model solution for the microsoft/amplifier repository. Before I dive into the research, let me clarify a couple of things to make sure I focus on the right areas:

1. **Current understanding**: Do you already know how Claude Code is integrated in your project and need architecture/implementation guidance for the replacement? Or would you like me to first research and document the current Claude Code usage?

2. **Target models**: Which models are you primarily interested in supporting? (e.g., OpenAI GPT models, Anthropic API directly, local models like Ollama, other providers like Google/Gemini, etc.)

These details will help me tailor the research to give you the most actionable guidance.

## Prompt:

9/29/2025, 6:34:10 PM

Research first, and at least support latest anthropic and openai models

## Response:

9/29/2025, 7:41:45 PM

```plaintext
Thought process: Strategized repository research for multi-model AI integration

The user wants me to do deep research on their microsoft/amplifier repository. They want to:
1. Research how Claude Code is currently used in the repository
2. Replace it with their own solution that supports multiple models
3. At minimum, support latest Anthropic and OpenAI models

The user has already clarified what they want, so I should use the launch_extended_search_task tool right away. I need to pass a detailed command that includes:
- Research the microsoft/amplifier repository to understand current Claude Code usage
- Figure out how to replace it with a multi-model solution
- Support for latest Anthropic and OpenAI models
- Architecture and implementation guidance

I should use the launch_extended_search_task tool now with a comprehensive command parameter.
```

Great! I'll dive into comprehensive research on the microsoft/amplifier repository to understand how Claude Code is currently integrated and provide you with architecture and implementation guidance for replacing it with a multi-model solution supporting the latest Anthropic and OpenAI models.

**launch_extended_search_task**

_Request_

```javascript
{
  "command": "Research the microsoft/amplifier GitHub repository to understand:\n\n1. How Claude Code is currently integrated and used in the codebase - identify all dependencies, integration points, API calls, and functionality that relies on Claude Code\n\n2. Document the current architecture and what Claude Code provides to the amplifier project\n\n3. Design a replacement architecture that:\n   - Removes the Claude Code dependency\n   - Supports multiple AI models with a provider-agnostic interface\n   - At minimum supports the latest Anthropic Claude models (Claude Sonnet 4.5, Opus 4.1) and latest OpenAI models (GPT-4, GPT-4 Turbo, o1, etc.)\n   - Is extensible to add more providers in the future\n\n4. Provide implementation guidance including:\n   - Recommended design patterns (e.g., strategy pattern, factory pattern for model providers)\n   - API client architecture for Anthropic and OpenAI\n   - Configuration management for API keys and model selection\n   - How to handle model-specific features and capabilities\n   - Error handling and retry logic\n   - Rate limiting considerations\n\n5. Identify any potential challenges or gotchas in migrating away from Claude Code\n\nUse the DeepWiki tool to analyze the microsoft/amplifier repository and supplement with web research about the latest Anthropic and OpenAI API capabilities."
}
```

_Response_

```javascript
{"task_id": "wf-2c77411e-7804-4e3c-8d30-010a273b3301"}
```

**Replacing Claude Code in Microsoft Amplifier: Provider-Agnostic Multi-Model AI Architecture Design and Implementation Guide**

````markdown
# Replacing Claude Code in Microsoft Amplifier: Architecture Design & Implementation Guide

**Claude Code is deeply integrated into Microsoft Amplifier as the primary development environment.** This project wraps Claude Code with 20+ specialized agents, custom commands, conversation preservation hooks, and knowledge extraction systems. Removing this dependency requires rethinking core workflows while building a provider-agnostic AI infrastructure that supports multiple LLM providers.

## Current Claude Code integration and architecture

Microsoft Amplifier positions Claude Code not as a tool but as **the fundamental runtime environment**. Every feature—from agent invocation to transcript management—assumes Claude Code's presence. The integration operates at multiple architectural layers:

**Primary integration surface: the .claude/ directory**. This hidden configuration directory contains the entire agent catalog, custom slash commands, hook scripts, and project settings. When developers run `claude` in the amplifier directory, Claude Code loads this configuration and transforms into a specialized development assistant with access to 20+ domain-specific agents like zen-architect, modular-builder, bug-hunter, and security-guardian. These agents are essentially sophisticated prompt templates that leverage Claude's capabilities for specific development tasks.

**The PreCompact hook represents critical functionality**. Claude Code has token limits that trigger automatic conversation compaction (compression of context to fit limits). The PreCompact hook intercepts this event, exporting the complete conversation transcript—including all messages, tool calls, and thinking blocks—to `.data/transcripts/`. Users can restore these transcripts via the `/transcripts` command, enabling continuous multi-hour development sessions without context loss. This solves a fundamental LLM limitation that other assistants haven't addressed as elegantly.

**Custom commands implement complex workflows**. The `/modular-build` command orchestrates an entire module creation pipeline: contract definition, specification, planning, code generation, and review. It operates in different modes (auto, assist, dry-run) with varying autonomy levels. This represents multi-step agentic behavior built atop Claude Code's command infrastructure.

**Status line integration provides real-time awareness**. A custom shell script displays current model, session cost, duration, git status, and project location at the terminal bottom. This cost-consciousness enables developers to make informed decisions about when to use expensive models like Opus 4.1 versus cost-effective options like Sonnet 4.

**Knowledge extraction optimized for Claude environment**. Documentation explicitly states knowledge extraction "works best in Claude environment." The system processes source materials (documentation, specs, notes), extracts concepts and relationships, and makes them queryable. The Makefile provides `knowledge-update` and `knowledge-query` commands, but these depend on Claude's reasoning capabilities for extraction quality.

**Parallel worktree workflows leverage Claude's context awareness**. Developers can spin up multiple git worktrees for experimental approaches, each with isolated branches and environments. Claude Code's workspace awareness enables it to understand which worktree context it's operating in, maintaining separate conversation threads per experiment.

## What Claude Code provides that must be replaced

**NPM Package Dependency**: `@anthropic-ai/claude-code` - The actual Claude CLI installed via `make install`

**Core capabilities leveraged**:

1. **Tool execution with approval workflows** - Claude Code can edit files, run commands, execute tests, and perform git operations with user review/approval
2. **Hook system** - PreCompact, SessionStart/Stop hooks for automation and conversation preservation
3. **Custom command infrastructure** - Slash commands for specialized workflows and agent invocation
4. **Large context windows** - Handles up to 100K tokens before compaction triggers
5. **Multi-file project awareness** - Maintains understanding across entire codebase
6. **MCP (Model Context Protocol) support** - Integration with external data sources (Google Drive, Figma, Slack)
7. **Session persistence and state tracking** - Transcript export/import for cross-session continuity
8. **Cost and usage tracking** - Real-time monitoring via status line

**Key technical architecture**:

```
User ←→ Claude Code CLI ←→ Amplifier Configuration
                ↓
        .claude/ Directory
                ↓
        ┌──────┴──────────────┐
        │                     │
    Agents              PreCompact Hook
    (20+ specialists)   (Transcript Export)
        │                     │
    /modular-build      Transcript Restore
    Custom Commands     Session Continuity
        │                     │
    Knowledge Base      Worktree Management
    Extraction          Parallel Experiments
        │                     │
    Status Line         Cost Tracking
    Real-time Metrics   Model Selection
```

## Replacement architecture: provider-agnostic multi-model system

The replacement architecture eliminates Claude Code dependency while **preserving and enhancing** Amplifier's capabilities through a layered provider-agnostic design. This enables teams to leverage the best model for each task while maintaining unified interfaces and workflows.

### Architecture layers

**Layer 1: Provider abstraction (底层 - Base Layer)**

Define a unified interface that abstracts all LLM provider differences. This is the foundation enabling provider swapping without touching business logic:

```typescript
// Core provider interface
interface LLMProvider {
  // Identification
  readonly name: string;
  readonly version: string;

  // Core capabilities
  createCompletion(request: CompletionRequest): Promise<CompletionResponse>;
  createStreamingCompletion(
    request: CompletionRequest
  ): AsyncIterator<CompletionChunk>;

  // Advanced features
  supportsFeature(feature: ModelFeature): boolean;
  getModelCapabilities(modelId: string): ModelCapabilities;

  // Cost management
  estimateCost(request: CompletionRequest): CostEstimate;
  trackUsage(): UsageMetrics;
}

// Unified request format
interface CompletionRequest {
  model: string;
  messages: Message[];
  systemPrompt?: string;
  temperature?: number;
  maxTokens?: number;
  tools?: Tool[];
  responseFormat?: ResponseFormat;
  streamingCallback?: (chunk: CompletionChunk) => void;
}

// Unified response format
interface CompletionResponse {
  id: string;
  content: string;
  toolCalls?: ToolCall[];
  usage: TokenUsage;
  finishReason: "stop" | "length" | "tool_calls" | "content_filter";
  metadata: ResponseMetadata;
}

// Feature detection
enum ModelFeature {
  STREAMING = "streaming",
  FUNCTION_CALLING = "function_calling",
  VISION = "vision",
  EXTENDED_CONTEXT = "extended_context",
  JSON_MODE = "json_mode",
  REASONING = "reasoning",
}

interface ModelCapabilities {
  maxContextTokens: number;
  maxOutputTokens: number;
  supportedFeatures: Set<ModelFeature>;
  costPerInputToken: number;
  costPerOutputToken: number;
  supportsMultimodal: boolean;
}
```

**Layer 2: Provider implementations**

Implement concrete providers for Anthropic and OpenAI, handling their specific API quirks while presenting the unified interface:

```typescript
// Anthropic Provider Implementation
class AnthropicProvider implements LLMProvider {
  private client: Anthropic;
  readonly name = "anthropic";
  readonly version = "2025-09-30";

  constructor(config: AnthropicConfig) {
    this.client = new Anthropic({
      apiKey: config.apiKey,
      maxRetries: config.maxRetries || 3,
      timeout: config.timeout || 600000, // 10 minutes
    });
  }

  async createCompletion(
    request: CompletionRequest
  ): Promise<CompletionResponse> {
    // Transform unified format to Anthropic format
    const anthropicRequest = {
      model: this.mapModelName(request.model),
      max_tokens: request.maxTokens || 4096,
      messages: request.messages.map(this.transformMessage),
      system: request.systemPrompt,
      temperature: request.temperature ?? 1.0,
      tools: request.tools?.map(this.transformTool),
    };

    const response = await this.client.messages.create(anthropicRequest);

    // Transform Anthropic response to unified format
    return this.transformResponse(response);
  }

  async *createStreamingCompletion(
    request: CompletionRequest
  ): AsyncIterator<CompletionChunk> {
    const stream = await this.client.messages.create({
      ...this.prepareRequest(request),
      stream: true,
    });

    for await (const event of stream) {
      if (event.type === "content_block_delta") {
        yield this.transformStreamChunk(event);
      }
    }
  }

  supportsFeature(feature: ModelFeature): boolean {
    const capabilities = {
      [ModelFeature.STREAMING]: true,
      [ModelFeature.FUNCTION_CALLING]: true,
      [ModelFeature.VISION]: true,
      [ModelFeature.EXTENDED_CONTEXT]: true,
      [ModelFeature.JSON_MODE]: false, // Anthropic uses tool calling for structured output
      [ModelFeature.REASONING]: true, // Claude 3.7+, Sonnet 4+, Opus 4.1
    };
    return capabilities[feature] || false;
  }

  getModelCapabilities(modelId: string): ModelCapabilities {
    // Latest Anthropic models (September 2025)
    const models = {
      "claude-sonnet-4-5-20250929": {
        maxContextTokens: 200000,
        maxOutputTokens: 8192,
        supportedFeatures: new Set([
          ModelFeature.STREAMING,
          ModelFeature.FUNCTION_CALLING,
          ModelFeature.VISION,
          ModelFeature.EXTENDED_CONTEXT,
          ModelFeature.REASONING,
        ]),
        costPerInputToken: 3.0 / 1_000_000,
        costPerOutputToken: 15.0 / 1_000_000,
        supportsMultimodal: true,
      },
      "claude-opus-4-1-20250805": {
        maxContextTokens: 200000,
        maxOutputTokens: 32768, // Significantly higher than Sonnet
        supportedFeatures: new Set([
          ModelFeature.STREAMING,
          ModelFeature.FUNCTION_CALLING,
          ModelFeature.VISION,
          ModelFeature.EXTENDED_CONTEXT,
          ModelFeature.REASONING,
        ]),
        costPerInputToken: 15.0 / 1_000_000,
        costPerOutputToken: 75.0 / 1_000_000,
        supportsMultimodal: true,
      },
      "claude-3-5-haiku-20241022": {
        maxContextTokens: 200000,
        maxOutputTokens: 8192,
        supportedFeatures: new Set([
          ModelFeature.STREAMING,
          ModelFeature.FUNCTION_CALLING,
          ModelFeature.VISION,
        ]),
        costPerInputToken: 0.8 / 1_000_000,
        costPerOutputToken: 4.0 / 1_000_000,
        supportsMultimodal: true,
      },
    };

    return models[modelId] || models["claude-sonnet-4-5-20250929"];
  }

  private mapModelName(model: string): string {
    // Handle version aliasing: "claude-sonnet-4.5" -> "claude-sonnet-4-5-20250929"
    const aliases = {
      "claude-sonnet-4.5": "claude-sonnet-4-5-20250929",
      "claude-opus-4.1": "claude-opus-4-1-20250805",
      "claude-haiku-3.5": "claude-3-5-haiku-20241022",
    };
    return aliases[model] || model;
  }
}

// OpenAI Provider Implementation
class OpenAIProvider implements LLMProvider {
  private client: OpenAI;
  readonly name = "openai";
  readonly version = "2025-09-30";

  constructor(config: OpenAIConfig) {
    this.client = new OpenAI({
      apiKey: config.apiKey,
      maxRetries: config.maxRetries || 3,
      timeout: config.timeout || 600000,
      organization: config.organizationId,
    });
  }

  async createCompletion(
    request: CompletionRequest
  ): Promise<CompletionResponse> {
    const openaiRequest = {
      model: this.mapModelName(request.model),
      messages: request.messages.map(this.transformMessage),
      max_tokens: request.maxTokens,
      temperature: request.temperature,
      tools: request.tools?.map(this.transformTool),
      response_format: request.responseFormat,
    };

    const response = await this.client.chat.completions.create(openaiRequest);
    return this.transformResponse(response);
  }

  async *createStreamingCompletion(
    request: CompletionRequest
  ): AsyncIterator<CompletionChunk> {
    const stream = await this.client.chat.completions.create({
      ...this.prepareRequest(request),
      stream: true,
    });

    for await (const chunk of stream) {
      yield this.transformStreamChunk(chunk);
    }
  }

  supportsFeature(feature: ModelFeature): boolean {
    const capabilities = {
      [ModelFeature.STREAMING]: true,
      [ModelFeature.FUNCTION_CALLING]: true,
      [ModelFeature.VISION]: true,
      [ModelFeature.EXTENDED_CONTEXT]: true,
      [ModelFeature.JSON_MODE]: true,
      [ModelFeature.REASONING]: true, // o1, o3, o4-mini series
    };
    return capabilities[feature] || false;
  }

  getModelCapabilities(modelId: string): ModelCapabilities {
    // Latest OpenAI models (September 2025)
    const models = {
      "gpt-4.1": {
        maxContextTokens: 1_000_000, // Massive context window
        maxOutputTokens: 16384,
        supportedFeatures: new Set([
          ModelFeature.STREAMING,
          ModelFeature.FUNCTION_CALLING,
          ModelFeature.VISION,
          ModelFeature.EXTENDED_CONTEXT,
          ModelFeature.JSON_MODE,
        ]),
        costPerInputToken: 2.5 / 1_000_000,
        costPerOutputToken: 10.0 / 1_000_000,
        supportsMultimodal: true,
      },
      "gpt-4o": {
        maxContextTokens: 128000,
        maxOutputTokens: 16384,
        supportedFeatures: new Set([
          ModelFeature.STREAMING,
          ModelFeature.FUNCTION_CALLING,
          ModelFeature.VISION,
          ModelFeature.JSON_MODE,
        ]),
        costPerInputToken: 2.5 / 1_000_000,
        costPerOutputToken: 10.0 / 1_000_000,
        supportsMultimodal: true,
      },
      o1: {
        maxContextTokens: 200000,
        maxOutputTokens: 100000,
        supportedFeatures: new Set([
          ModelFeature.STREAMING,
          ModelFeature.FUNCTION_CALLING,
          ModelFeature.VISION,
          ModelFeature.REASONING,
        ]),
        costPerInputToken: 15.0 / 1_000_000,
        costPerOutputToken: 60.0 / 1_000_000,
        supportsMultimodal: true,
      },
      "o1-mini": {
        maxContextTokens: 128000,
        maxOutputTokens: 65536,
        supportedFeatures: new Set([
          ModelFeature.STREAMING,
          ModelFeature.FUNCTION_CALLING,
          ModelFeature.REASONING,
        ]),
        costPerInputToken: 3.0 / 1_000_000,
        costPerOutputToken: 12.0 / 1_000_000,
        supportsMultimodal: false,
      },
      "gpt-4o-mini": {
        maxContextTokens: 128000,
        maxOutputTokens: 16384,
        supportedFeatures: new Set([
          ModelFeature.STREAMING,
          ModelFeature.FUNCTION_CALLING,
          ModelFeature.VISION,
          ModelFeature.JSON_MODE,
        ]),
        costPerInputToken: 0.15 / 1_000_000,
        costPerOutputToken: 0.6 / 1_000_000,
        supportsMultimodal: true,
      },
    };

    return models[modelId] || models["gpt-4o"];
  }
}
```

**Layer 3: Provider factory and registry**

Use the Factory Pattern to instantiate providers and manage provider lifecycle:

```typescript
// Provider Factory
class LLMProviderFactory {
  private static providers = new Map<string, () => LLMProvider>();

  static register(name: string, factory: () => LLMProvider): void {
    this.providers.set(name, factory);
  }

  static create(providerName: string, config: ProviderConfig): LLMProvider {
    const factory = this.providers.get(providerName);
    if (!factory) {
      throw new Error(`Unknown provider: ${providerName}`);
    }
    return factory();
  }

  static listAvailable(): string[] {
    return Array.from(this.providers.keys());
  }
}

// Register providers at application startup
LLMProviderFactory.register(
  "anthropic",
  () => new AnthropicProvider(config.anthropic)
);
LLMProviderFactory.register("openai", () => new OpenAIProvider(config.openai));

// Usage
const provider = LLMProviderFactory.create("anthropic", config);
```

**Layer 4: Intelligent model selection and routing**

Implement routing logic that selects optimal models based on task characteristics:

```typescript
// Model Router - Strategy Pattern
interface ModelSelectionStrategy {
  selectModel(request: RoutingRequest): ModelSelection;
}

interface RoutingRequest {
  task: TaskType;
  priority: "cost" | "quality" | "speed";
  contextSize: number;
  requiresVision: boolean;
  requiresReasoning: boolean;
  budgetConstraint?: number;
}

interface ModelSelection {
  provider: string;
  model: string;
  reasoning: string;
}

enum TaskType {
  CODE_GENERATION = "code_generation",
  CODE_REVIEW = "code_review",
  DEBUGGING = "debugging",
  DOCUMENTATION = "documentation",
  ARCHITECTURE = "architecture",
  TESTING = "testing",
  SIMPLE_QA = "simple_qa",
  COMPLEX_REASONING = "complex_reasoning",
}

class OptimalModelRouter implements ModelSelectionStrategy {
  selectModel(request: RoutingRequest): ModelSelection {
    // Reasoning models for complex tasks
    if (
      request.task === TaskType.COMPLEX_REASONING ||
      request.task === TaskType.ARCHITECTURE
    ) {
      if (request.priority === "quality") {
        return {
          provider: "openai",
          model: "o1",
          reasoning:
            "o1 excels at multi-step reasoning and complex problem solving",
        };
      } else if (request.priority === "cost") {
        return {
          provider: "anthropic",
          model: "claude-sonnet-4.5",
          reasoning:
            "Sonnet 4.5 offers best coding performance at moderate cost",
        };
      }
    }

    // Code-heavy tasks
    if (
      request.task === TaskType.CODE_GENERATION ||
      request.task === TaskType.DEBUGGING
    ) {
      return {
        provider: "anthropic",
        model: "claude-sonnet-4.5",
        reasoning:
          "Sonnet 4.5 is the best coding model (77.2% SWE-bench Verified)",
      };
    }

    // High-volume, cost-sensitive tasks
    if (request.priority === "cost" && request.contextSize < 50000) {
      return {
        provider: "anthropic",
        model: "claude-haiku-3.5",
        reasoning:
          "Haiku 3.5 is fastest and most cost-effective for simple tasks",
      };
    }

    // Long context requirements
    if (request.contextSize > 200000) {
      return {
        provider: "openai",
        model: "gpt-4.1",
        reasoning: "GPT-4.1 supports 1M token context window",
      };
    }

    // Default balanced option
    return {
      provider: "anthropic",
      model: "claude-sonnet-4.5",
      reasoning: "Best general-purpose model for most coding tasks",
    };
  }
}

// Cost-aware routing with fallbacks
class CostAwareRouter implements ModelSelectionStrategy {
  private budgetTracker: BudgetTracker;

  selectModel(request: RoutingRequest): ModelSelection {
    const availableBudget = this.budgetTracker.getRemainingBudget();

    if (
      request.budgetConstraint &&
      availableBudget < request.budgetConstraint
    ) {
      // Force cheaper models when approaching budget limits
      return {
        provider: "anthropic",
        model: "claude-haiku-3.5",
        reasoning: "Budget constraint requires most economical option",
      };
    }

    // Otherwise use optimal router
    return new OptimalModelRouter().selectModel(request);
  }
}
```

**Layer 5: Unified client interface**

Provide a high-level client that orchestrates providers, routing, and error handling:

```typescript
// Unified Client
class AmplifierAIClient {
  private providers: Map<string, LLMProvider>;
  private router: ModelSelectionStrategy;
  private retryManager: RetryManager;
  private cacheManager: CacheManager;
  private costTracker: CostTracker;

  constructor(config: AmplifierConfig) {
    // Initialize providers
    this.providers = new Map();
    config.providers.forEach((providerConfig) => {
      const provider = LLMProviderFactory.create(
        providerConfig.name,
        providerConfig
      );
      this.providers.set(providerConfig.name, provider);
    });

    // Initialize routing strategy
    this.router =
      config.routing.strategy === "cost-aware"
        ? new CostAwareRouter()
        : new OptimalModelRouter();

    this.retryManager = new RetryManager(config.retry);
    this.cacheManager = new CacheManager(config.cache);
    this.costTracker = new CostTracker();
  }

  async complete(request: CompletionRequest): Promise<CompletionResponse> {
    // Check cache first
    const cacheKey = this.cacheManager.generateKey(request);
    const cached = await this.cacheManager.get(cacheKey);
    if (cached) {
      this.costTracker.recordCacheHit();
      return cached;
    }

    // Route to appropriate model
    const selection = this.router.selectModel({
      task: request.task,
      priority: request.priority || "quality",
      contextSize: this.estimateContextSize(request),
      requiresVision: request.messages.some((m) => m.images?.length > 0),
      requiresReasoning: request.requiresReasoning || false,
    });

    const provider = this.providers.get(selection.provider);
    if (!provider) {
      throw new Error(`Provider not available: ${selection.provider}`);
    }

    // Execute with retry logic
    const response = await this.retryManager.execute(async () => {
      return await provider.createCompletion({
        ...request,
        model: selection.model,
      });
    });

    // Track costs
    this.costTracker.recordUsage({
      provider: selection.provider,
      model: selection.model,
      tokens: response.usage,
      cost: this.calculateCost(selection, response.usage),
    });

    // Cache successful responses
    await this.cacheManager.set(cacheKey, response);

    return response;
  }

  async *stream(request: CompletionRequest): AsyncIterator<CompletionChunk> {
    const selection = this.router.selectModel({
      task: request.task,
      priority: request.priority || "speed",
      contextSize: this.estimateContextSize(request),
      requiresVision: false,
      requiresReasoning: false,
    });

    const provider = this.providers.get(selection.provider);

    for await (const chunk of provider.createStreamingCompletion({
      ...request,
      model: selection.model,
    })) {
      yield chunk;
    }
  }

  // Agent invocation (replaces Claude Code custom commands)
  async invokeAgent(
    agentName: string,
    context: AgentContext
  ): Promise<AgentResponse> {
    const agent = AgentRegistry.get(agentName);
    if (!agent) {
      throw new Error(`Unknown agent: ${agentName}`);
    }

    // Agents can specify preferred models
    const request: CompletionRequest = {
      model: agent.preferredModel,
      messages: agent.buildPrompt(context),
      systemPrompt: agent.systemPrompt,
      temperature: agent.temperature,
      maxTokens: agent.maxTokens,
      tools: agent.tools,
    };

    return await this.complete(request);
  }

  getCostSummary(): CostSummary {
    return this.costTracker.getSummary();
  }
}
```

## Implementation guidance

### Configuration management

Use layered configuration with environment variables, config files, and runtime overrides:

```yaml
# amplifier-config.yaml
providers:
  anthropic:
    api_key: ${ANTHROPIC_API_KEY}
    enabled: true
    models:
      - claude-sonnet-4-5-20250929
      - claude-opus-4-1-20250805
      - claude-3-5-haiku-20241022
    rate_limits:
      requests_per_minute: 50
      tokens_per_minute: 40000
    retry:
      max_attempts: 3
      backoff_multiplier: 2

  openai:
    api_key: ${OPENAI_API_KEY}
    organization_id: ${OPENAI_ORG_ID}
    enabled: true
    models:
      - gpt-4.1
      - gpt-4o
      - o1
      - o1-mini
      - gpt-4o-mini
    rate_limits:
      requests_per_minute: 500
      tokens_per_minute: 150000
    retry:
      max_attempts: 3
      backoff_multiplier: 2

routing:
  strategy: cost-aware # Options: optimal, cost-aware, custom
  default_provider: anthropic
  default_model: claude-sonnet-4-5-20250929
  fallback_chain:
    - provider: anthropic
      model: claude-sonnet-4-5-20250929
    - provider: openai
      model: gpt-4o
    - provider: anthropic
      model: claude-haiku-3.5

caching:
  enabled: true
  ttl_seconds: 3600
  max_size_mb: 500
  strategy: lru

cost_tracking:
  enabled: true
  budget_alerts:
    - threshold: 50.00
      channel: slack
    - threshold: 100.00
      channel: email
  daily_budget: 150.00

agents:
  zen-architect:
    preferred_model: claude-opus-4-1-20250805
    priority: quality
  modular-builder:
    preferred_model: claude-sonnet-4-5-20250929
    priority: balanced
  bug-hunter:
    preferred_model: o1
    priority: quality
  test-coverage:
    preferred_model: gpt-4o
    priority: speed
```

```typescript
// Configuration loader with validation
class ConfigurationManager {
  private config: AmplifierConfig;

  static load(configPath?: string): AmplifierConfig {
    // Load from file or use defaults
    const rawConfig = configPath
      ? yaml.load(fs.readFileSync(configPath, "utf8"))
      : this.getDefaults();

    // Interpolate environment variables
    const interpolated = this.interpolateEnvVars(rawConfig);

    // Validate configuration
    this.validate(interpolated);

    return interpolated as AmplifierConfig;
  }

  private static interpolateEnvVars(obj: any): any {
    if (typeof obj === "string" && obj.startsWith("${") && obj.endsWith("}")) {
      const envVar = obj.slice(2, -1);
      const value = process.env[envVar];
      if (!value) {
        throw new Error(`Missing required environment variable: ${envVar}`);
      }
      return value;
    }

    if (Array.isArray(obj)) {
      return obj.map((item) => this.interpolateEnvVars(item));
    }

    if (typeof obj === "object" && obj !== null) {
      return Object.fromEntries(
        Object.entries(obj).map(([k, v]) => [k, this.interpolateEnvVars(v)])
      );
    }

    return obj;
  }

  private static validate(config: any): void {
    // Ensure at least one provider is configured
    if (!config.providers || Object.keys(config.providers).length === 0) {
      throw new Error("At least one provider must be configured");
    }

    // Validate each provider has required fields
    for (const [name, provider] of Object.entries(config.providers)) {
      if (!provider.api_key) {
        throw new Error(`Provider ${name} missing api_key`);
      }
      if (!provider.models || provider.models.length === 0) {
        throw new Error(`Provider ${name} must specify at least one model`);
      }
    }

    // Validate routing configuration
    if (config.routing?.fallback_chain) {
      for (const fallback of config.routing.fallback_chain) {
        if (!config.providers[fallback.provider]) {
          throw new Error(
            `Fallback references unknown provider: ${fallback.provider}`
          );
        }
      }
    }
  }
}
```

### Error handling and retry logic

Implement sophisticated retry logic with exponential backoff and circuit breakers:

```typescript
// Retry Manager with Circuit Breaker
class RetryManager {
  private config: RetryConfig;
  private circuitBreakers: Map<string, CircuitBreaker>;

  constructor(config: RetryConfig) {
    this.config = config;
    this.circuitBreakers = new Map();
  }

  async execute<T>(
    operation: () => Promise<T>,
    context?: RetryContext
  ): Promise<T> {
    const maxAttempts = context?.maxAttempts || this.config.maxAttempts || 3;
    const backoffMultiplier = this.config.backoffMultiplier || 2;
    const maxBackoffMs = this.config.maxBackoffMs || 60000;

    let lastError: Error;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        // Check circuit breaker
        if (context?.circuitBreakerKey) {
          const breaker = this.getCircuitBreaker(context.circuitBreakerKey);
          if (breaker.isOpen()) {
            throw new Error(
              `Circuit breaker open for ${context.circuitBreakerKey}`
            );
          }
        }

        const result = await operation();

        // Success - reset circuit breaker
        if (context?.circuitBreakerKey) {
          this.getCircuitBreaker(context.circuitBreakerKey).recordSuccess();
        }

        return result;
      } catch (error) {
        lastError = error;

        // Record failure in circuit breaker
        if (context?.circuitBreakerKey) {
          this.getCircuitBreaker(context.circuitBreakerKey).recordFailure();
        }

        // Don't retry on certain errors
        if (this.isNonRetryableError(error)) {
          throw error;
        }

        // Don't retry on last attempt
        if (attempt === maxAttempts - 1) {
          break;
        }

        // Calculate backoff with jitter
        const backoffMs = Math.min(
          Math.pow(backoffMultiplier, attempt) * 1000 + Math.random() * 1000,
          maxBackoffMs
        );

        console.warn(
          `Attempt ${attempt + 1} failed, retrying in ${backoffMs}ms...`
        );
        await this.sleep(backoffMs);
      }
    }

    throw new Error(
      `Operation failed after ${maxAttempts} attempts: ${lastError.message}`
    );
  }

  private isNonRetryableError(error: any): boolean {
    // Don't retry on authentication errors, invalid requests, etc.
    const nonRetryableStatuses = [400, 401, 403, 404];
    return nonRetryableStatuses.includes(error.status);
  }

  private getCircuitBreaker(key: string): CircuitBreaker {
    if (!this.circuitBreakers.has(key)) {
      this.circuitBreakers.set(
        key,
        new CircuitBreaker({
          failureThreshold: 5,
          resetTimeoutMs: 60000,
        })
      );
    }
    return this.circuitBreakers.get(key)!;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// Circuit Breaker Pattern
class CircuitBreaker {
  private state: "CLOSED" | "OPEN" | "HALF_OPEN" = "CLOSED";
  private failureCount: number = 0;
  private successCount: number = 0;
  private lastFailureTime: number = 0;
  private config: CircuitBreakerConfig;

  constructor(config: CircuitBreakerConfig) {
    this.config = config;
  }

  isOpen(): boolean {
    if (this.state === "OPEN") {
      // Check if reset timeout has elapsed
      if (Date.now() - this.lastFailureTime > this.config.resetTimeoutMs) {
        this.state = "HALF_OPEN";
        this.successCount = 0;
        return false;
      }
      return true;
    }
    return false;
  }

  recordSuccess(): void {
    this.failureCount = 0;

    if (this.state === "HALF_OPEN") {
      this.successCount++;
      if (this.successCount >= 2) {
        this.state = "CLOSED";
      }
    }
  }

  recordFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    if (this.failureCount >= this.config.failureThreshold) {
      this.state = "OPEN";
    }
  }
}
```

### Rate limiting

Implement token bucket algorithm for rate limiting:

```typescript
// Rate Limiter using Token Bucket Algorithm
class RateLimiter {
  private buckets: Map<string, TokenBucket>;

  async acquire(key: string, tokens: number = 1): Promise<void> {
    const bucket = this.getBucket(key);
    await bucket.consume(tokens);
  }

  private getBucket(key: string): TokenBucket {
    if (!this.buckets.has(key)) {
      // Get rate limits from provider config
      const limits = this.getProviderLimits(key);
      this.buckets.set(key, new TokenBucket(limits));
    }
    return this.buckets.get(key)!;
  }

  private getProviderLimits(providerKey: string): RateLimits {
    // Return provider-specific rate limits
    const limits = {
      anthropic: {
        requestsPerMinute: 50,
        tokensPerMinute: 40000,
      },
      openai: {
        requestsPerMinute: 500,
        tokensPerMinute: 150000,
      },
    };

    return limits[providerKey] || limits["anthropic"];
  }
}

class TokenBucket {
  private capacity: number;
  private tokens: number;
  private refillRate: number;
  private lastRefill: number;
  private queue: Array<{ tokens: number; resolve: () => void }>;

  constructor(limits: RateLimits) {
    this.capacity = limits.requestsPerMinute;
    this.tokens = this.capacity;
    this.refillRate = this.capacity / 60; // Refill per second
    this.lastRefill = Date.now();
    this.queue = [];

    // Start refill loop
    this.startRefillLoop();
  }

  async consume(tokens: number): Promise<void> {
    this.refill();

    if (this.tokens >= tokens) {
      this.tokens -= tokens;
      return;
    }

    // Queue the request
    return new Promise<void>((resolve) => {
      this.queue.push({ tokens, resolve });
    });
  }

  private refill(): void {
    const now = Date.now();
    const elapsed = (now - this.lastRefill) / 1000; // seconds
    const tokensToAdd = elapsed * this.refillRate;

    this.tokens = Math.min(this.capacity, this.tokens + tokensToAdd);
    this.lastRefill = now;

    // Process queue
    while (this.queue.length > 0 && this.tokens >= this.queue[0].tokens) {
      const request = this.queue.shift()!;
      this.tokens -= request.tokens;
      request.resolve();
    }
  }

  private startRefillLoop(): void {
    setInterval(() => this.refill(), 1000);
  }
}
```

### Agent system implementation

Preserve Amplifier's agent-based workflow with the new architecture:

```typescript
// Agent Registry and Implementation
class AgentRegistry {
  private static agents = new Map<string, Agent>();

  static register(agent: Agent): void {
    this.agents.set(agent.name, agent);
  }

  static get(name: string): Agent | undefined {
    return this.agents.get(name);
  }

  static list(): Agent[] {
    return Array.from(this.agents.values());
  }
}

// Base Agent Interface
interface Agent {
  name: string;
  description: string;
  systemPrompt: string;
  preferredModel: string;
  temperature: number;
  maxTokens: number;
  tools?: Tool[];

  buildPrompt(context: AgentContext): Message[];
  execute(
    context: AgentContext,
    client: AmplifierAIClient
  ): Promise<AgentResponse>;
}

// Example: Zen Architect Agent
class ZenArchitectAgent implements Agent {
  name = "zen-architect";
  description = "Designs with ruthless simplicity";
  systemPrompt = `You are a zen architect who values simplicity, elegance, and clarity above all else.
Your designs are minimalist yet powerful, removing unnecessary complexity while maintaining full functionality.
You think deeply about trade-offs, always preferring simpler solutions that solve 80% of problems perfectly
over complex solutions that try to solve 100% imperfectly.`;

  preferredModel = "claude-opus-4-1-20250805"; // High-quality reasoning
  temperature = 0.7;
  maxTokens = 4096;

  buildPrompt(context: AgentContext): Message[] {
    return [
      {
        role: "user",
        content: `Design a system architecture for: ${
          context.userRequest
        }\n\nContext:\n${
          context.additionalContext || "None"
        }\n\nProvide a clear, simple design that prioritizes maintainability and understandability.`,
      },
    ];
  }

  async execute(
    context: AgentContext,
    client: AmplifierAIClient
  ): Promise<AgentResponse> {
    const response = await client.complete({
      messages: this.buildPrompt(context),
      systemPrompt: this.systemPrompt,
      model: this.preferredModel,
      temperature: this.temperature,
      maxTokens: this.maxTokens,
      task: TaskType.ARCHITECTURE,
    });

    return {
      agent: this.name,
      content: response.content,
      usage: response.usage,
    };
  }
}

// Example: Bug Hunter Agent with tools
class BugHunterAgent implements Agent {
  name = "bug-hunter";
  description = "Systematic debugging with root cause analysis";
  systemPrompt = `You are an expert debugger who approaches problems systematically.
You form hypotheses, test them methodically, and always trace issues to their root cause.
You never guess - you verify through careful analysis and testing.`;

  preferredModel = "o1"; // Reasoning model for complex debugging
  temperature = 0.5;
  maxTokens = 8192;

  tools = [
    {
      name: "read_file",
      description: "Read contents of a file",
      input_schema: {
        type: "object",
        properties: {
          path: { type: "string", description: "File path" },
        },
        required: ["path"],
      },
    },
    {
      name: "run_command",
      description: "Execute a shell command",
      input_schema: {
        type: "object",
        properties: {
          command: { type: "string", description: "Shell command to execute" },
        },
        required: ["command"],
      },
    },
    {
      name: "search_code",
      description: "Search for patterns in codebase",
      input_schema: {
        type: "object",
        properties: {
          pattern: { type: "string", description: "Search pattern" },
          file_glob: { type: "string", description: "File pattern to search" },
        },
        required: ["pattern"],
      },
    },
  ];

  buildPrompt(context: AgentContext): Message[] {
    return [
      {
        role: "user",
        content: `Debug the following issue:\n\n${
          context.userRequest
        }\n\nError details:\n${
          context.errorDetails || "See attached logs"
        }\n\nUse the available tools to investigate and identify the root cause.`,
      },
    ];
  }

  async execute(
    context: AgentContext,
    client: AmplifierAIClient
  ): Promise<AgentResponse> {
    const response = await client.complete({
      messages: this.buildPrompt(context),
      systemPrompt: this.systemPrompt,
      model: this.preferredModel,
      temperature: this.temperature,
      maxTokens: this.maxTokens,
      tools: this.tools,
      task: TaskType.DEBUGGING,
      requiresReasoning: true,
    });

    return {
      agent: this.name,
      content: response.content,
      toolCalls: response.toolCalls,
      usage: response.usage,
    };
  }
}

// Register all agents at startup
function registerAgents(): void {
  AgentRegistry.register(new ZenArchitectAgent());
  AgentRegistry.register(new BugHunterAgent());
  AgentRegistry.register(new ModularBuilderAgent());
  AgentRegistry.register(new TestCoverageAgent());
  AgentRegistry.register(new SecurityGuardianAgent());
  // ... register all 20+ agents
}
```

### Conversation management and persistence

Replace Claude Code's PreCompact hook with custom conversation management:

```typescript
// Conversation Manager (replaces PreCompact hook)
class ConversationManager {
  private transcriptsDir: string;
  private currentConversation: Conversation;
  private tokenCounter: TokenCounter;

  constructor(config: ConversationConfig) {
    this.transcriptsDir = config.transcriptsDir || ".data/transcripts";
    this.currentConversation = this.createNew();
    this.tokenCounter = new TokenCounter();

    // Ensure transcripts directory exists
    fs.mkdirSync(this.transcriptsDir, { recursive: true });
  }

  addMessage(message: Message): void {
    this.currentConversation.messages.push(message);
    this.currentConversation.tokenCount = this.tokenCounter.count(
      this.currentConversation.messages
    );

    // Auto-save periodically
    if (this.currentConversation.messages.length % 10 === 0) {
      this.save();
    }

    // Check if approaching context limit
    if (this.shouldCompact()) {
      this.compact();
    }
  }

  private shouldCompact(): boolean {
    // Conservative limit - compact before hitting model limits
    const maxContextTokens = 150000; // Lower than model limits for safety
    return this.currentConversation.tokenCount > maxContextTokens;
  }

  private async compact(): Promise<void> {
    console.log("Context limit approaching, compacting conversation...");

    // Save full transcript before compaction
    await this.save();

    // Implement intelligent summarization
    const summary = await this.summarizeHistory();

    // Keep recent messages + summary
    const recentMessages = this.currentConversation.messages.slice(-20);

    this.currentConversation.messages = [
      {
        role: "system",
        content: `Previous conversation summary:\n${summary}`,
      },
      ...recentMessages,
    ];

    this.currentConversation.tokenCount = this.tokenCounter.count(
      this.currentConversation.messages
    );

    console.log(
      `Compacted conversation. Tokens: ${this.currentConversation.tokenCount}`
    );
  }

  private async summarizeHistory(): Promise<string> {
    // Use AI to summarize conversation history
    const summaryRequest: CompletionRequest = {
      model: "claude-haiku-3.5", // Fast, cheap model for summarization
      messages: [
        {
          role: "user",
          content: `Summarize the key points, decisions, and context from this conversation:\n\n${JSON.stringify(
            this.currentConversation.messages.slice(0, -20)
          )}`,
        },
      ],
      maxTokens: 2000,
    };

    // Assume we have access to client
    const response = await globalClient.complete(summaryRequest);
    return response.content;
  }

  async save(): Promise<string> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    const filename = `transcript-${timestamp}.json`;
    const filepath = path.join(this.transcriptsDir, filename);

    const transcriptData = {
      ...this.currentConversation,
      savedAt: new Date().toISOString(),
      version: "1.0",
    };

    await fs.promises.writeFile(
      filepath,
      JSON.stringify(transcriptData, null, 2),
      "utf8"
    );

    console.log(`Transcript saved: ${filepath}`);
    return filepath;
  }

  async restore(transcriptPath: string): Promise<void> {
    const data = await fs.promises.readFile(transcriptPath, "utf8");
    const transcript = JSON.parse(data);

    this.currentConversation = {
      id: uuid.v4(), // New ID for restored conversation
      messages: transcript.messages,
      tokenCount: this.tokenCounter.count(transcript.messages),
      startedAt: new Date(),
      metadata: {
        ...transcript.metadata,
        restoredFrom: transcriptPath,
        restoredAt: new Date().toISOString(),
      },
    };

    console.log(`Conversation restored from: ${transcriptPath}`);
  }

  async search(query: string): Promise<TranscriptSearchResult[]> {
    const transcripts = await this.listTranscripts();
    const results: TranscriptSearchResult[] = [];

    for (const transcriptFile of transcripts) {
      const content = await fs.promises.readFile(
        path.join(this.transcriptsDir, transcriptFile),
        "utf8"
      );

      if (content.toLowerCase().includes(query.toLowerCase())) {
        const transcript = JSON.parse(content);
        results.push({
          filename: transcriptFile,
          timestamp: transcript.startedAt,
          matchCount: (content.match(new RegExp(query, "gi")) || []).length,
          preview: this.generatePreview(transcript, query),
        });
      }
    }

    return results.sort((a, b) => b.matchCount - a.matchCount);
  }

  private createNew(): Conversation {
    return {
      id: uuid.v4(),
      messages: [],
      tokenCount: 0,
      startedAt: new Date(),
      metadata: {},
    };
  }
}
```

## Migration challenges and gotchas

**The PreCompact hook is irreplaceable one-to-one**. Claude Code's hook system triggers automatically before context compaction, ensuring zero conversation loss. Replicating this requires building your own context monitoring, triggering compaction proactively, and managing the complexity of conversation summarization. The challenge: determining _when_ to compact (before hitting limits but not too early) and _how_ to summarize effectively without losing critical context. Consider implementing a sliding window approach where you keep recent messages intact while progressively summarizing older context.

**Agent specialization relies on prompt engineering, not built-in magic**. The current agent system works because Claude Code provides the runtime. With a custom implementation, each agent becomes a carefully crafted prompt template + model selection strategy. The gotcha: prompt engineering is fragile. Small changes can dramatically impact quality. Recommendation: version control all agent prompts, implement A/B testing, and gather metrics on agent effectiveness. Build a prompt template system that allows easy updates without code changes.

**Custom commands require building workflow orchestration**. The `/modular-build` command orchestrates contract → spec → plan → generate → review. This isn't a single LLM call—it's a multi-step workflow with conditional logic, tool usage, and human-in-the-loop decision points. You'll need to implement workflow state machines, handle intermediate failures gracefully, and provide clear progress indicators. Consider using a workflow engine or building a simple state machine system that can persist workflow state and resume after interruptions.

**Status line integration requires architectural rethinking**. Claude Code's status line displays real-time session metrics because it controls the entire session lifecycle. In a custom implementation, you need to decide: CLI tool with status line? Web interface with dashboard? VS Code extension? Each has different UX implications. The status line also requires accurate token counting _before_ API calls (for cost estimation) and real-time cost tracking _during_ streaming responses. Build a robust token counter that matches each provider's tokenization logic (tiktoken for OpenAI, Claude's tokenizer for Anthropic).

**Knowledge extraction currently optimized for "Claude environment"**. The documentation explicitly states this works best in Claude environment, suggesting tight integration with Claude's reasoning. When migrating, you'll need to test knowledge extraction quality across providers. OpenAI's o1 might be better for certain extraction tasks, while Claude Sonnet 4.5 excels at others. Implement A/B testing and quality metrics. Consider building a hybrid approach where you use different models for different extraction phases (structure identification vs. concept extraction vs. relationship mapping).

**Tool execution and approval workflows need careful design**. Claude Code has built-in file editing with user approval. Your implementation needs equivalent safety: never auto-execute file writes or destructive commands without explicit approval. Implement a permission system with different trust levels for different tool types. Consider sandboxing for code execution. Use git integration for automatic commits before risky operations, enabling easy rollback.

**Context window differences create subtle bugs**. GPT-4.1 has 1M tokens vs. Claude Sonnet 4.5's 200K standard. But more context doesn't always mean better results—some models degrade with very long contexts ("lost in the middle" problem). Design your conversation manager to be context-aware, potentially using different strategies based on the active model's strengths. Implement context window testing to identify degradation points.

**Rate limits vary dramatically between providers**. Anthropic Tier 1: 50 RPM. OpenAI Tier 1: 500 RPM. Your fallback strategy might hit rate limits on the fallback provider. Implement smart queueing that considers rate limits across _all_ configured providers. Build a predictive system that estimates time-to-availability across providers and chooses intelligently.

**Model-specific features create abstraction leakage**. Claude's extended thinking, OpenAI's o1 reasoning tokens, response format differences—complete abstraction is impossible. Design your interfaces to gracefully degrade when features aren't available. Use capability detection (the `supportsFeature()` method) throughout your codebase. Document clearly which features work with which providers.

**Cost optimization is complex with multiple providers**. Anthropic offers prompt caching (90% savings on repeated content). OpenAI offers batch processing (50% discount). Your architecture needs provider-specific optimizations while maintaining a clean interface. Build a cost optimization layer that automatically applies the best strategy per provider (caching for repeated context, batching for non-urgent work, model selection for price/performance).

**Testing and debugging become significantly harder**. With Claude Code, you have one system to debug. With multiple providers + routing + retry logic + caching, debugging becomes complex. Implement comprehensive logging with request IDs that trace through the entire stack. Build debugging tools that show decision trees (why this model was selected, why this retry happened, why this cache miss occurred). Consider request replay capabilities for debugging production issues.

**Migration is risky because Amplifier is deeply integrated**. You can't migrate incrementally—the entire system depends on Claude Code. Recommendation: Build the new architecture in parallel as "Amplifier 2.0" rather than attempting in-place migration. Implement feature parity testing where you run identical requests through both systems and compare outputs. Plan for a transition period where advanced users can opt into the new system while maintaining the Claude Code version for stability.

**Dependency on external tool changes**. Both Anthropic and OpenAI update their APIs regularly. New models, deprecated models, changed rate limits, new features. Build an abstraction layer that can adapt to these changes without breaking your entire system. Implement provider version pinning with graceful upgrades. Monitor provider changelogs and have a process for testing and rolling out API changes.

**The "magic" of Claude Code is hard to replicate**. Claude Code isn't just an API client—it's an opinionated, integrated development environment. The hooks, commands, and integrations create emergent workflows that are greater than the sum of parts. When building your replacement, focus on preserving the _workflows_ rather than replicating the _implementation_. Think about what developers actually do with Amplifier, not just what features Claude Code provides.
````

## Prompt:

10/5/2025, 1:52:28 AM

Separate from that, explain the unix principles to me.

## Response:

10/5/2025, 1:52:53 AM

```plaintext
Thought process: Mapped out Unix principles for clear, concise explanation.

The user is asking me to explain the Unix principles. This is a straightforward educational request about computer science/software engineering concepts. I should explain the core Unix philosophy principles clearly and concisely.

The Unix philosophy consists of several key principles that have guided Unix and Unix-like operating system design since the 1970s. I should cover:

1. The core principles (do one thing well, composability, text as interface, etc.)
2. Who articulated them (Doug McIlroy, Ken Thompson, etc.)
3. Examples showing how they work in practice
4. Why they matter

I should keep this conversational and accessible, not overly academic.
```

# The Unix Philosophy

The Unix philosophy is a set of design principles that emerged from the original Unix operating system in the 1970s. These principles have profoundly influenced software design far beyond Unix itself.

## Core Principles

**1. Do One Thing and Do It Well**

Programs should have a single, well-defined purpose rather than trying to be Swiss Army knives. A program that does one thing can do it excellently, while a program that tries to do everything does nothing particularly well.

Example: `grep` searches text. It doesn't edit files, sort results, or send emails. It just searches, and it's excellent at it.

**2. Make Programs Work Together**

Design programs to be composable—the output of one program should be suitable as input to another. This creates building blocks that can be combined in countless ways.

Example: `cat file.txt | grep "error" | wc -l` chains three programs to count error lines.

**3. Use Text as the Universal Interface**

Text streams are the common currency. They're human-readable, tool-agnostic, and easy to manipulate. Avoid binary formats or proprietary interfaces between programs.

**4. Build Prototype Early**

Get something working quickly, even if it's rough. Real usage reveals design flaws faster than planning. You can always refine later.

**5. Choose Portability Over Efficiency**

Write clear, portable code that works across systems rather than optimizing prematurely for one platform. Machines get faster; rewriting code is expensive.

**6. Store Data in Flat Files**

Use simple, text-based formats rather than complex databases when possible. Flat files are easy to inspect, edit, backup, and process with standard tools.

**7. Use Software Leverage**

Reuse existing tools rather than reinventing them. Shell scripts that chain existing utilities often beat writing custom programs.

**8. Use Shell Scripts to Increase Leverage**

The shell is the glue that connects tools. A few lines of shell script can automate complex workflows.

**9. Avoid Captive User Interfaces**

Programs shouldn't force users into interactive sessions. They should work in pipelines, accept input from files, and be scriptable.

**10. Make Every Program a Filter**

Design programs to read from standard input and write to standard output by default. This makes them naturally composable.

## The Articulation

Doug McIlroy (inventor of Unix pipes) famously summarized it:

> "This is the Unix philosophy: Write programs that do one thing and do it well. Write programs to work together. Write programs to handle text streams, because that is a universal interface."

Ken Thompson added:

> "When in doubt, use brute force."

Meaning: Simple, direct solutions often beat clever ones.

## Practical Example

Instead of building one monolithic program that processes logs, Unix philosophy suggests:

```bash
# Find errors, sort by frequency, show top 10
cat /var/log/app.log | \
  grep "ERROR" | \
  cut -d: -f3 | \
  sort | \
  uniq -c | \
  sort -rn | \
  head -10
```

Each tool (`cat`, `grep`, `cut`, `sort`, `uniq`, `head`) does one thing. Together they solve complex problems.

## Why It Matters

**Simplicity**: Small, focused programs are easier to understand, test, and maintain.

**Flexibility**: Composable tools can be combined in ways the original authors never imagined.

**Longevity**: Unix tools from the 1970s still work today because they follow these principles.

**Learning curve**: Master a few tools deeply rather than learning hundreds of specialized programs superficially.

## Modern Relevance

These principles influenced:

- **Microservices**: Small services that do one thing well
- **API design**: Simple, composable endpoints
- **Functional programming**: Pure functions, composition
- **DevOps**: Scriptable infrastructure, configuration as code

The Unix philosophy isn't just about operating systems—it's a timeless approach to building software that lasts.

## Prompt:

10/5/2025, 1:54:00 AM

Perfect, now explain to me the Linux kernel principles.

## Response:

10/5/2025, 1:54:46 AM

```plaintext
Thought process: Excavated Linux kernel principles through comparative analysis.

The user is asking about Linux kernel principles. This is interesting because Linux and Unix are related but distinct. Linux was created by Linus Torvalds as a Unix-like operating system, but the kernel development has its own set of principles and philosophies that differ from the Unix philosophy.

Let me think about the key Linux kernel principles:

1. "Release early, release often" - From the open source development model
2. Never break userspace - A strict policy
3. Performance matters
4. The right tool for the job (pragmatic)
5. No theoretical purity (practical over elegant)
6. Worse is better / working code beats perfect design
7. Community-driven development
8. Meritocracy
9. Code talks, BS walks
10. Scalability
11. Hardware support as a priority

I should contrast this with Unix philosophy where appropriate, and highlight Linus Torvalds' specific influence on these principles.
```

# Linux Kernel Principles

The Linux kernel has its own development philosophy that's distinct from (and sometimes contradicts) the Unix philosophy. These principles emerged from Linus Torvalds' leadership and the kernel community's evolution over 30+ years.

## Core Principles

**1. Never Break Userspace**

This is the **cardinal rule** of Linux kernel development. Once a user-facing API or behavior exists, it must be supported forever, even if it was a mistake.

If a change causes existing applications to break, the change is wrong—period. The kernel takes the pain so users don't have to.

Example: Linus has rejected countless "clean" patches because they would break some obscure application somewhere.

**2. Code Talks, BS Walks**

Working code matters more than theoretical discussions. Show your implementation, don't just talk about how things _should_ work.

The kernel community values patches over philosophical debates. You earn respect by contributing working code, not by having credentials or arguing eloquently.

**3. Performance Is a Feature**

Linux aggressively optimizes for performance. Fast code is better than elegant code. Micro-optimizations matter when you're running on billions of devices.

This contrasts with "portability over efficiency"—Linux will use platform-specific optimizations without hesitation.

**4. Practical Over Pure**

Linux is pragmatic, not ideological. If something works and solves real problems, it goes in. Theoretical elegance takes a back seat to practical utility.

Example: The kernel includes massive binary firmware blobs for hardware support, even though purists hate this.

**5. No Stable Internal APIs**

Unlike userspace (which never breaks), kernel internal APIs change constantly. This allows rapid evolution and prevents external modules from constraining development.

Out-of-tree drivers that break when internals change? Not the kernel's problem. This forces vendors to upstream their code.

**6. "Good Taste" in Code**

Linus emphasizes elegant, readable code that minimizes special cases. Code should be obvious, not clever. The best code deletes complexity rather than adding it.

Famous example: Linus praised code that removed an `if` statement for a special case by restructuring the logic to handle all cases uniformly.

**7. Scalability From the Start**

The kernel must scale from tiny embedded devices to supercomputers. Code must work efficiently whether you have one CPU or 1,000.

This principle drives many design decisions—from scheduler design to memory management.

**8. Release Early, Release Often**

New kernels release every 9-11 weeks like clockwork. This rapid cadence means features get tested quickly, bugs get fixed fast, and development never stagnates.

The "merge window" opens after each release for 2 weeks, then testing/fixing for the rest of the cycle.

**9. No -stable Branches Live Forever**

Only select kernel versions get long-term support. Most versions are maintained briefly. This forces the ecosystem to keep moving forward rather than sitting on ancient kernels.

**10. Meritocracy Rules**

Your contributions matter, not your employer or credentials. A unknown developer can have their patch accepted over a corporate submission if the code is better.

Maintainers earn their position through consistent, high-quality work.

**11. The Maintainer Is Always Right (For Their Subsystem)**

Each subsystem has maintainers who have final say over their domain. Linus rarely overrules maintainers. This distributed authority scales development.

**12. Support Real Hardware, Not Hypotheticals**

The kernel supports actual hardware that people use, not theoretical devices. "Show me the hardware" is a common response to adding support for non-existent devices.

**13. Security Through Code Quality**

Linux doesn't believe in security through obscurity or formal verification. Security comes from many eyes reviewing code, fixing bugs quickly, and good engineering practices.

## Linus's Philosophy

Linus Torvalds articulated key viewpoints:

**"Talk is cheap. Show me the code."**
Actions over words.

**"Bad programmers worry about the code. Good programmers worry about data structures and their relationships."**
Design your data structures right, and the code becomes obvious.

**"I'm a bastard. I have absolutely no clue why people can think I'm doing anything wrong."**
Linus is famously blunt in code reviews, valuing technical correctness over politeness (though this has moderated in recent years).

**"Worse is better."**
A working solution now beats a perfect solution later. Iterate and improve.

**"Software is like sex: it's better when it's free."**
Open source enables rapid evolution through collaboration.

## Development Model

**Patch-based workflow**: Everything goes through mailing lists as patches, reviewed publicly. No pull requests, no private discussions.

**Hierarchical maintainership**: Subsystem maintainers feed to area maintainers who feed to Linus. This scales to thousands of contributors.

**Signed-off-by chain**: Every patch has a chain of people vouching for it, establishing accountability.

**No regressions**: If a new kernel works worse than an old one for some use case, that's a bug. Fix it or revert the change.

## Contrasts with Unix Philosophy

**Unix**: Do one thing well
**Linux**: The kernel does _everything_—from scheduling to filesystems to networking to graphics. It's intentionally monolithic (though modular).

**Unix**: Text as universal interface
**Linux**: Binary interfaces, system calls, performance-optimized data structures. Text is for userspace tools.

**Unix**: Portability over efficiency
**Linux**: Performance first, with heavy architecture-specific optimization.

**Unix**: Small is beautiful
**Linux**: The kernel is massive (28+ million lines of code) because supporting all hardware and use cases requires it.

## Why These Principles Work

**Stability**: Users trust Linux because userspace never breaks. Systems run for years across kernel updates.

**Innovation**: Internal flexibility allows aggressive optimization and evolution.

**Quality**: Public review, meritocracy, and working code requirements keep quality high.

**Adoption**: Pragmatism and performance made Linux run everything from Android phones to supercomputers.

**Community**: Clear principles and distributed authority enabled thousands of developers to coordinate effectively.

## Modern Impact

These principles influenced:

- **Open source governance**: How large projects manage distributed development
- **API stability**: The importance of not breaking users
- **Code review culture**: Public, merit-based review
- **Release cadence**: Regular, predictable releases
- **Pragmatic engineering**: Working code over theoretical purity

The Linux kernel principles aren't about elegance or minimalism—they're about building a robust, high-performance system that serves real users on real hardware, developed by a global community that values working code above all else.

## Prompt:

10/5/2025, 2:19:28 AM

OK, given your understanding of how Amplifier is currently using Claude Code, which got the bulk of it (subagents, hooks, commands, context files, tools, re-entrant through sdk, etc.), take a look at this deep dive on how Claude Code works.

What would it look like to create a version of Amplifier that did not require use of Claude Code and had its own agent loop and other capabilities and workflow that Claude Code has, BUT was built as a modular system on top of a new amplifier-core library? The core should be as thin as possible by making as many of its component implementations modular, making the core more the layer that stitches them all together.

In addition, everything built on top of it should follow similar modular design patterns. The goal is to have the smallest thing possible that balances a stable foundation for all developers to built upon and coordinate through, but is maintainable by a single individual. We want to both enable and encourage large scale distributed, parallel exploration of ideas in every possible part of the overall system, while keeping the core stable. Think the Linux kernel for the core and everything else is user space - but, in our case, to make it thinner, even the implementations side of core internal systems are modular as well, keeping the actual code of the core as small as possible while still providing that opinionated approach to the Amplifier system.

Strongly consider the Unix principles and the Linux principles and how those would affect this idea. What could this look like? Also consider the two other philosophy docs I've attached, they are the ones our team holds dear while building.

## Response:

10/5/2025, 3:14:02 AM

I'll dive deep into how Claude Code works and design a modular amplifier-core architecture that embodies the Unix and Linux kernel principles along with your team's philosophy docs.

**launch_extended_search_task**

_Request_

```javascript
{
  "command": "Deep research task on Claude Code architecture and implementation:\n\n1. Research how Claude Code actually works internally - its architecture, agent loop, tool execution, context management, hook system, re-entrant SDK capabilities, command infrastructure, and how it manages multi-turn conversations with tools.\n\n2. Analyze the technical implementation details of Claude Code's core capabilities:\n   - Agent/agentic loop architecture\n   - Tool use and approval workflows\n   - Context window management and compaction\n   - Hook system (PreCompact, SessionStart, SessionStop, etc.)\n   - Custom command infrastructure\n   - Re-entrant capabilities through SDK\n   - Session persistence and transcript management\n   - MCP (Model Context Protocol) integration\n\n3. Based on understanding Claude Code's architecture and the principles from:\n   - Unix philosophy (do one thing well, composability, text streams, simple tools)\n   - Linux kernel principles (never break userspace, stable APIs, internal flexibility, meritocracy, code over talk)\n   - The attached team philosophy documents\n\nDesign a modular amplifier-core library architecture that:\n   - Provides the thinnest possible stable core (like Linux kernel)\n   - Makes even core implementation components modular and swappable\n   - Enables distributed parallel innovation in all parts (like Linux userspace)\n   - Maintains stability for coordination (like Linux's stable syscall interface)\n   - Can be maintained by a single individual\n   - Follows Unix composability principles while having Linux-style pragmatism\n   - Treats everything outside core as \"userspace\" that can evolve independently\n\n4. Provide a detailed architectural design showing:\n   - What belongs in amplifier-core vs what's modular\n   - The stable interfaces/contracts that core provides\n   - How subsystems plug in and compose\n   - How this enables parallel development while maintaining coherence\n   - Specific examples of modular implementations (providers, tools, agents, hooks, etc.)\n   - How this scales from single developer to distributed team\n\nUse the DeepWiki tool to analyze the microsoft/amplifier repository to understand current structure, and supplement with research on Claude Code's technical implementation and agentic architecture patterns."
}
```

_Response_

```javascript
{"task_id": "wf-7374889a-3d14-4bdc-9f29-790ccffb104c"}
```

**Amplifier-Core: Modular Architecture Design for AI Coding Assistants**

````markdown
# Amplifier-Core: Modular Architecture Design

## Executive Summary

This report synthesizes research on Claude Code's architecture, Unix/Linux design principles, and modern plugin systems to propose a comprehensive modular architecture for amplifier-core. The design follows the principle of a **thin, stable core with rich, extensible periphery**, enabling distributed parallel innovation while maintaining coherence through stable interfaces.

**Core Philosophy**: Like the Linux kernel provides stable syscalls while allowing internal flexibility, amplifier-core provides stable extension points while remaining pragmatic and evolvable internally.

---

## 1. CLAUDE CODE ARCHITECTURE INSIGHTS

### 1.1 Key Architectural Patterns Discovered

**Master Agent Loop (nO)**:

- Single-threaded, simple while loop: `while(tool_call) → execute → feed results → repeat`
- Terminates naturally when no tool calls remain
- Maximum one sub-agent branch to prevent chaos
- Sub-agents cannot spawn sub-agents (depth limitation)

**Context Management (wU2 Compressor)**:

- Automatic compaction at ~92% context usage
- Uses cheaper model (Haiku) for summarization
- Manual compaction encouraged at logical breakpoints
- CLAUDE.md files provide cross-session persistence

**Hook System (8 Lifecycle Events)**:

- **SessionStart**: Setup and initialization
- **UserPromptSubmit**: Pre-processing and validation (stdout → context)
- **PreToolUse**: Validation and permission checks (exit 2 = block)
- **PostToolUse**: Post-processing and side effects
- **Notification**: Event notifications
- **Stop**: Cleanup and finalization
- **SubagentStop**: Subagent lifecycle management
- **PreCompact**: Context preservation before compaction

**MCP (Model Context Protocol) Integration**:

- JSON-RPC 2.0 based communication
- Three primitives: Tools (model-controlled), Resources (app-controlled), Prompts (user-controlled)
- Transport-agnostic (stdio, HTTP/SSE, custom)
- In-process SDK servers for performance

**Critical Design Decisions**:

1. **Simplicity over sophistication**: "Do the simple thing first" - regex over embeddings, markdown over databases
2. **Debuggability paramount**: Flat structures, transparent data flow, clear audit trails
3. **Tool descriptions as documentation**: 9,400 tokens of detailed tool descriptions
4. **Separation of concerns**: Master loop, tool execution, context management all independent

### 1.2 What Makes This Architecture Work

**Clarity Through Constraint**:

- Single-threaded execution prevents race conditions
- Depth limits prevent infinite recursion
- Clear lifecycle boundaries enable predictable behavior

**Extensibility Through Hooks**:

- 8 well-defined extension points
- Structured input/output (JSON via stdin/stdout)
- Exit codes control behavior (0=success, 2=block, other=warn)
- Can return JSON for sophisticated control

**Re-entrance Through Subagents**:

- Specialized agents with independent context
- Parallel execution for speed
- Results summarized back to main loop
- Prevents context pollution

---

## 2. UNIX/LINUX PRINCIPLES FOR LIBRARY DESIGN

### 2.1 Never Break Userspace (The Prime Directive)

**Linus Torvalds' Absolute Rule**: "We do not break userspace. Period."

**Application to Libraries**:

- Public APIs are **sacred contracts** - never remove or change behavior
- Old code must run on new versions without modification
- Even "bad" decisions must be maintained for compatibility
- Only exception: serious security issues

**Benefits**:

- Users trust the platform
- No forced upgrade cascades
- Long-term stability
- Predictable evolution

### 2.2 Stable External API, Flexible Internal Implementation

**The Linux Kernel Model**:

- **External (syscall) API**: Extremely stable, backward compatible, well-documented
- **Internal API**: Changes constantly, no stability promises, free to refactor

**Application to amplifier-core**:

```
┌─────────────────────────────────────────────┐
│  Public API Layer (STABLE - Never Break)    │
│  • Extension points                         │
│  • Plugin interfaces                        │
│  • Configuration format                     │
│  • Event contracts                          │
└─────────────────────────────────────────────┘
              ↕ (contract)
┌─────────────────────────────────────────────┐
│  Core Implementation (FLEXIBLE - Can Change)│
│  • Agent loop logic                         │
│  • Context management                       │
│  • Tool execution                           │
│  • Internal optimization                    │
└─────────────────────────────────────────────┘
```

### 2.3 Mechanism vs. Policy Separation

**Core Principle**: Mechanisms age slowly, policies age quickly. Never hardwire them together.

**For amplifier-core**:

- **Mechanisms (Core)**: How amplification works, data flow, plugin loading, event dispatch
- **Policies (Plugins/Config)**: What gets amplified, when it happens, which features are active

**Benefits**:

- Policy experimentation without core changes
- Multiple use cases without core modifications
- Easier testing (mechanisms are testable, policies are often not worth testing)

### 2.4 Unix Philosophy Applied

**Do One Thing Well**: Core does orchestration, plugins do specific work

**Composability**: Plugin outputs become inputs to other plugins

**Text Streams**: Use human-readable formats (JSON, YAML) as interchange format

**Simple Tools**: Prefer simple implementations with clear data structures over complex algorithms

---

## 3. AMPLIFIER-CORE ARCHITECTURAL DESIGN

### 3.1 The Thin Core Model

**Core Responsibilities (Minimal Set)**:

```typescript
// amplifier-core provides ONLY:

1. Plugin Discovery & Loading
   - Scan directories for plugins
   - Validate plugin contracts
   - Load and initialize plugins
   - Manage plugin lifecycle

2. Event System / Hook Infrastructure
   - Define lifecycle events
   - Event dispatch to registered handlers
   - Hook execution (parallel/sequential)
   - Error handling and recovery

3. Context Management
   - Session state management
   - Context window tracking
   - Automatic compaction
   - CLAUDE.md memory management

4. Common Services
   - Logging infrastructure
   - Configuration management
   - File I/O utilities
   - Error reporting

5. Agent Loop Orchestration
   - Master control loop
   - Tool execution workflow
   - Result aggregation
   - Termination conditions
```

**NOT in Core** (Delegated to Plugins):

- Specific amplification strategies
- Custom tools and commands
- Knowledge extraction logic
- Agent specializations
- UI/presentation layer
- External integrations

### 3.2 Stable Interface Layer

**Public API Contract** (Version 1.0 - Never Break):

```typescript
// ===== STABLE PUBLIC API =====
// This interface NEVER changes (only extends)

/**
 * Core plugin interface - all plugins must implement this
 * @stable Since 1.0.0
 */
export interface AmplifierPlugin {
  /** Plugin name (must be unique) */
  readonly name: string;

  /** Semantic version */
  readonly version: string;

  /** Plugin dependencies (optional) */
  readonly dependencies?: string[];

  /** Initialize plugin with core context */
  initialize?(context: PluginContext): void | Promise<void>;

  /** Cleanup on plugin unload */
  cleanup?(): void | Promise<void>;
}

/**
 * Context provided to plugins by core
 * @stable Since 1.0.0
 */
export interface PluginContext {
  /** Plugin can emit files/assets */
  emitFile(options: EmitFileOptions): string;

  /** Access configuration */
  readonly config: ReadonlyConfig;

  /** Logging interface */
  readonly log: Logger;

  /** Access to core services */
  readonly services: CoreServices;
}

/**
 * Hook system - plugins register for lifecycle events
 * @stable Since 1.0.0
 */
export interface HookSystem {
  /** Register hook handler */
  on(event: LifecycleEvent, handler: HookHandler): Disposable;

  /** Emit event to all registered handlers */
  emit(event: LifecycleEvent, data: unknown): Promise<void>;
}

/**
 * Lifecycle events (inspired by Claude Code)
 * @stable Since 1.0.0
 */
export enum LifecycleEvent {
  SessionStart = "session:start",
  PromptSubmit = "prompt:submit",
  PreToolUse = "tool:pre",
  PostToolUse = "tool:post",
  PreCompact = "context:pre-compact",
  SessionEnd = "session:end",
}

/**
 * Agent interface for specialized workers
 * @stable Since 1.0.0
 */
export interface Agent {
  readonly name: string;
  readonly description: string;
  readonly tools: string[];
  readonly model?: string;

  /** Execute agent task */
  execute(task: Task, context: AgentContext): Promise<AgentResult>;
}
```

**API Stability Levels**:

1. **@stable**: Public API, semantic versioning, never break
2. **@experimental**: Opt-in, can change in minor versions, clearly marked
3. **@internal**: Not exposed, free to change

### 3.3 Plugin Architecture

**Plugin Types**:

```typescript
/**
 * 1. Tool Plugins - Extend available tools
 * @stable Since 1.0.0
 */
export interface ToolPlugin extends AmplifierPlugin {
  readonly type: "tool";

  /** Tool definition for LLM */
  readonly tool: ToolDefinition;

  /** Execute tool */
  execute(input: ToolInput, context: PluginContext): Promise<ToolOutput>;
}

/**
 * 2. Agent Plugins - Specialized subagents
 * @stable Since 1.0.0
 */
export interface AgentPlugin extends AmplifierPlugin {
  readonly type: "agent";

  /** Agent metadata */
  readonly agent: AgentDefinition;

  /** Agent execution logic */
  execute(task: Task, context: AgentContext): Promise<AgentResult>;
}

/**
 * 3. Hook Plugins - Extend lifecycle behavior
 * @stable Since 1.0.0
 */
export interface HookPlugin extends AmplifierPlugin {
  readonly type: "hook";

  /** Register hooks during initialization */
  registerHooks(hooks: HookSystem): void;
}

/**
 * 4. Processor Plugins - Transform data
 * @stable Since 1.0.0
 */
export interface ProcessorPlugin extends AmplifierPlugin {
  readonly type: "processor";

  /** Process input and return output */
  process(input: unknown, context: PluginContext): Promise<unknown>;
}

/**
 * 5. Provider Plugins - External service integration
 * @stable Since 1.0.0
 */
export interface ProviderPlugin extends AmplifierPlugin {
  readonly type: "provider";

  /** MCP server instance or configuration */
  readonly mcpServer: MCPServer | MCPConfig;
}
```

**Plugin Discovery**:

```
amplifier-core/
  ├── core/              # Core implementation (internal, flexible)
  ├── api/               # Public API definitions (stable)
  └── plugins/           # Plugin system (stable interfaces)

amplifier-plugins/       # Official plugins (separate repo)
  ├── tools/
  │   ├── grep/
  │   ├── edit/
  │   └── bash/
  ├── agents/
  │   ├── zen-architect/
  │   ├── bug-hunter/
  │   └── test-coverage/
  ├── processors/
  │   └── knowledge-extraction/
  └── providers/
      ├── github/
      └── filesystem/

.amplifier/              # Project-specific plugins
  └── plugins/

~/.amplifier/            # User-global plugins
  └── plugins/
```

### 3.4 Hook System Design

**Event-Driven Architecture**:

```typescript
/**
 * Hook execution engine
 */
class HookEngine {
  private handlers = new Map<LifecycleEvent, HookHandler[]>();

  /**
   * Register hook handler
   * Handlers execute in registration order
   */
  on(event: LifecycleEvent, handler: HookHandler): Disposable {
    const handlers = this.handlers.get(event) || [];
    handlers.push(handler);
    this.handlers.set(event, handlers);

    return {
      dispose: () => {
        const idx = handlers.indexOf(handler);
        if (idx >= 0) handlers.splice(idx, 1);
      },
    };
  }

  /**
   * Emit event to all registered handlers
   * Supports both sync and async handlers
   * Can be configured for parallel or sequential execution
   */
  async emit(event: LifecycleEvent, data: HookData): Promise<HookResult> {
    const handlers = this.handlers.get(event) || [];

    // Sequential execution with short-circuit on deny
    for (const handler of handlers) {
      const result = await handler(data);

      if (result.action === "deny") {
        return result; // Short-circuit
      }

      if (result.action === "modify") {
        data = result.modifiedData; // Chain modifications
      }
    }

    return { action: "continue", data };
  }
}

/**
 * Hook handler contract
 */
type HookHandler = (data: HookData) => Promise<HookResult> | HookResult;

interface HookResult {
  action: "continue" | "deny" | "modify";
  reason?: string;
  modifiedData?: HookData;
}
```

**Hook Usage Example**:

```typescript
// In a plugin
class FormatterPlugin implements HookPlugin {
  registerHooks(hooks: HookSystem) {
    // Run formatter after file edits
    hooks.on(LifecycleEvent.PostToolUse, async (data) => {
      if (data.tool === "Edit" || data.tool === "Write") {
        await this.formatFiles(data.filePaths);
      }
      return { action: "continue" };
    });
  }
}

// In another plugin
class SecurityPlugin implements HookPlugin {
  registerHooks(hooks: HookSystem) {
    // Block dangerous commands
    hooks.on(LifecycleEvent.PreToolUse, async (data) => {
      if (data.tool === "Bash" && this.isDangerous(data.input)) {
        return {
          action: "deny",
          reason: "Dangerous command blocked for security",
        };
      }
      return { action: "continue" };
    });
  }
}
```

### 3.5 Agent Orchestration System

**Master Agent Loop** (Inspired by Claude Code's nO):

```typescript
/**
 * Core agent loop orchestration
 * @internal - Implementation can change
 */
class AgentOrchestrator {
  private context: SessionContext;
  private hooks: HookEngine;
  private tools: Map<string, Tool>;

  async execute(prompt: string): Promise<void> {
    // SessionStart hook
    await this.hooks.emit(LifecycleEvent.SessionStart, {
      sessionId: this.context.id,
      source: "user-prompt",
    });

    // PromptSubmit hook (can modify prompt)
    const promptResult = await this.hooks.emit(LifecycleEvent.PromptSubmit, {
      prompt,
    });

    if (promptResult.action === "deny") return;

    const modifiedPrompt = promptResult.modifiedData?.prompt || prompt;

    // Main agent loop
    let response = await this.callLLM(modifiedPrompt);

    while (response.hasToolCalls) {
      for (const toolCall of response.toolCalls) {
        // PreToolUse hook (can block execution)
        const preResult = await this.hooks.emit(LifecycleEvent.PreToolUse, {
          tool: toolCall.name,
          input: toolCall.input,
        });

        if (preResult.action === "deny") {
          // Inform LLM of blocked tool
          response = await this.callLLM(
            `Tool ${toolCall.name} was blocked: ${preResult.reason}`
          );
          continue;
        }

        // Execute tool
        const tool = this.tools.get(toolCall.name);
        const result = await tool.execute(toolCall.input, this.context);

        // PostToolUse hook (can process results)
        await this.hooks.emit(LifecycleEvent.PostToolUse, {
          tool: toolCall.name,
          input: toolCall.input,
          output: result,
        });

        // Feed result back to LLM
        response = await this.callLLM(result);
      }
    }

    // No more tool calls - final response
    return response.text;
  }

  /**
   * Spawn specialized subagent
   * @internal
   */
  async spawnSubagent(agent: Agent, task: Task): Promise<AgentResult> {
    const subContext = this.context.createChild({
      agent: agent.name,
      tools: agent.tools,
      model: agent.model,
    });

    // Subagents have independent context window
    // Results are summarized back to parent
    return await agent.execute(task, subContext);
  }
}
```

**Subagent System**:

```typescript
/**
 * Subagent manager - enables parallel specialized workers
 * @internal
 */
class SubagentManager {
  private agents = new Map<string, Agent>();

  /**
   * Register agent from plugin
   */
  registerAgent(agent: Agent) {
    this.agents.set(agent.name, agent);
  }

  /**
   * Execute multiple agents in parallel
   * Returns when all complete
   */
  async executeParallel(
    tasks: Array<{ agent: string; task: Task }>
  ): Promise<AgentResult[]> {
    const promises = tasks.map(({ agent, task }) => {
      const agentInstance = this.agents.get(agent);
      if (!agentInstance) {
        throw new Error(`Agent ${agent} not found`);
      }
      return agentInstance.execute(task, this.createContext(agent));
    });

    return await Promise.all(promises);
  }
}
```

### 3.6 Context Management

**Context Window Management** (Inspired by Claude Code's wU2):

```typescript
/**
 * Context manager - handles message history and compaction
 * @internal - Implementation details can change
 */
class ContextManager {
  private messages: Message[] = [];
  private maxTokens: number = 200_000;
  private compactThreshold: number = 0.92;

  async addMessage(message: Message) {
    this.messages.push(message);

    const usage = await this.calculateUsage();

    if (usage >= this.compactThreshold) {
      await this.compact();
    }
  }

  /**
   * Automatic compaction when threshold reached
   */
  private async compact() {
    // PreCompact hook - can backup transcripts
    await this.hooks.emit(LifecycleEvent.PreCompact, {
      trigger: "auto",
      messages: this.messages,
      usage: await this.calculateUsage(),
    });

    // Summarize old messages
    const summary = await this.summarizeMessages(
      this.messages.slice(0, -10) // Keep recent 10 verbatim
    );

    // Replace old messages with summary
    this.messages = [
      { role: "system", content: summary },
      ...this.messages.slice(-10),
    ];

    // Reload CLAUDE.md memory
    await this.reloadMemory();
  }

  /**
   * Memory persistence across sessions
   */
  private async reloadMemory() {
    const claudeMd = await this.readClaudeMd();
    this.messages.unshift({
      role: "system",
      content: claudeMd,
    });
  }
}
```

### 3.7 MCP Integration Layer

**MCP as Provider Plugin**:

```typescript
/**
 * MCP integration - providers expose tools/resources/prompts
 * @stable Since 1.0.0
 */
interface MCPProviderPlugin extends ProviderPlugin {
  /** MCP server configuration */
  readonly mcpConfig: {
    type: "stdio" | "sse" | "http";
    command?: string;
    args?: string[];
    url?: string;
    env?: Record<string, string>;
  };

  /** Tools exposed by this MCP server */
  getTools(): Promise<ToolDefinition[]>;

  /** Resources exposed by this MCP server */
  getResources(): Promise<ResourceDefinition[]>;

  /** Prompts exposed by this MCP server */
  getPrompts(): Promise<PromptDefinition[]>;
}

/**
 * Core manages MCP server lifecycle
 * @internal
 */
class MCPManager {
  private servers = new Map<string, MCPServer>();

  async registerProvider(plugin: MCPProviderPlugin) {
    const server = await this.connectMCPServer(plugin.mcpConfig);
    this.servers.set(plugin.name, server);

    // Register tools from MCP server
    const tools = await plugin.getTools();
    tools.forEach((tool) => {
      this.toolRegistry.register({
        name: `mcp__${plugin.name}__${tool.name}`,
        definition: tool,
        execute: (input) => server.callTool(tool.name, input),
      });
    });
  }
}
```

---

## 4. MODULAR SUBSYSTEMS

### 4.1 What Belongs Where

**amplifier-core (Minimal, Stable)**:

```
src/
├── api/                      # Public interfaces (STABLE)
│   ├── plugin.ts            # Plugin contracts
│   ├── hooks.ts             # Hook system
│   ├── agent.ts             # Agent interfaces
│   └── index.ts             # Public exports
│
├── core/                     # Core implementation (INTERNAL)
│   ├── orchestrator.ts      # Agent loop
│   ├── context.ts           # Context management
│   ├── hooks.ts             # Hook engine
│   ├── plugins.ts           # Plugin loader
│   └── subagents.ts         # Subagent manager
│
├── services/                 # Common services (INTERNAL)
│   ├── logging.ts
│   ├── config.ts
│   └── file-io.ts
│
└── index.ts                  # Core exports
```

**amplifier-plugins (Rich, Evolving)**:

```
packages/
├── tools/                    # Tool implementations
│   ├── grep/
│   ├── edit/
│   ├── bash/
│   └── web-fetch/
│
├── agents/                   # Specialized agents
│   ├── zen-architect/
│   ├── modular-builder/
│   ├── bug-hunter/
│   ├── security-guardian/
│   └── knowledge-archaeologist/
│
├── processors/               # Data processors
│   ├── knowledge-extraction/
│   ├── concept-extractor/
│   └── transcript-analyzer/
│
├── hooks/                    # Hook implementations
│   ├── formatter/
│   ├── linter/
│   ├── security-validator/
│   └── transcript-backup/
│
└── providers/                # MCP providers
    ├── github/
    ├── filesystem/
    ├── database/
    └── slack/
```

### 4.2 Plugin Composition Examples

**Example 1: Security Validation Plugin**:

```typescript
// packages/hooks/security-validator/src/index.ts

export class SecurityValidatorPlugin implements HookPlugin {
  readonly name = "security-validator";
  readonly version = "1.0.0";
  readonly type = "hook";

  private rules: SecurityRule[];

  async initialize(context: PluginContext) {
    this.rules = await this.loadRules(context.config);
    context.log.info(
      "Security validator initialized with",
      this.rules.length,
      "rules"
    );
  }

  registerHooks(hooks: HookSystem) {
    // Validate bash commands before execution
    hooks.on(LifecycleEvent.PreToolUse, async (data) => {
      if (data.tool !== "Bash") {
        return { action: "continue" };
      }

      const command = data.input.command;
      const violations = this.rules
        .map((rule) => rule.check(command))
        .filter((v) => v !== null);

      if (violations.length > 0) {
        return {
          action: "deny",
          reason: `Security violations: ${violations.join(", ")}`,
        };
      }

      return { action: "continue" };
    });
  }
}
```

**Example 2: Knowledge Extraction Agent**:

```typescript
// packages/agents/knowledge-archaeologist/src/index.ts

export class KnowledgeArchaeologistPlugin implements AgentPlugin {
  readonly name = "knowledge-archaeologist";
  readonly version = "1.0.0";
  readonly type = "agent";

  readonly agent: AgentDefinition = {
    name: "knowledge-archaeologist",
    description: "Traces evolution of ideas through conversation history",
    tools: ["Read", "Grep", "TranscriptSearch"],
    model: "opus-4",
  };

  async execute(task: Task, context: AgentContext): Promise<AgentResult> {
    // 1. Search transcripts for concept mentions
    const transcripts = await context.tools.TranscriptSearch({
      query: task.concept,
      limit: 50,
    });

    // 2. Analyze evolution over time
    const evolution = await this.analyzeEvolution(transcripts);

    // 3. Extract key insights
    const insights = await this.extractInsights(evolution);

    return {
      summary: `Traced ${task.concept} through ${transcripts.length} conversations`,
      insights,
      confidence: 0.85,
    };
  }
}
```

**Example 3: Modular Builder Plugin**:

```typescript
// packages/agents/modular-builder/src/index.ts

export class ModularBuilderPlugin implements AgentPlugin {
  readonly name = "modular-builder";
  readonly version = "1.0.0";
  readonly type = "agent";

  readonly agent: AgentDefinition = {
    name: "modular-builder",
    description:
      "Builds modules following contract-spec-plan-generate-review workflow",
    tools: ["Read", "Write", "Edit", "Bash", "Grep"],
    model: "sonnet-4.5",
  };

  async execute(task: Task, context: AgentContext): Promise<AgentResult> {
    const mode = task.mode || "assist"; // auto | assist | dry-run

    // 1. Contract definition
    const contract = await this.defineContract(task.module, context);
    await context.tools.Write({
      path: `ai_working/${task.module}/contract/CONTRACT.md`,
      content: contract,
    });

    // 2. Spec creation
    const spec = await this.createSpec(contract, context);
    await context.tools.Write({
      path: `ai_working/${task.module}/spec/SPEC.md`,
      content: spec,
    });

    // 3. Implementation plan
    const plan = await this.generatePlan(contract, spec, context);

    if (mode === "dry-run") {
      return { plan, dryRun: true };
    }

    // 4. Code generation
    if (mode === "auto" && plan.confidence >= 0.75) {
      await this.generateCode(plan, context);
    } else {
      // Assist mode - ask clarifying questions
      const answers = await this.askQuestions(plan, context);
      await this.generateCode(plan, context, answers);
    }

    // 5. Review
    const review = await this.reviewCode(contract, spec, context);

    return { plan, review, success: review.passed };
  }
}
```

### 4.3 Dependency Injection Pattern

**Plugin Loader with DI**:

```typescript
/**
 * Plugin loader - handles discovery and initialization
 * @internal
 */
class PluginLoader {
  private plugins = new Map<string, AmplifierPlugin>();
  private context: PluginContext;

  constructor(private core: AmplifierCore) {
    this.context = this.createPluginContext();
  }

  /**
   * Discover and load plugins from directories
   */
  async loadPlugins(directories: string[]) {
    for (const dir of directories) {
      const pluginFiles = await this.discoverPlugins(dir);

      for (const file of pluginFiles) {
        await this.loadPlugin(file);
      }
    }

    // Initialize plugins in dependency order
    await this.initializePlugins();
  }

  /**
   * Load single plugin
   */
  private async loadPlugin(file: string) {
    const module = await import(file);
    const PluginClass = module.default || module;

    if (!this.isValidPlugin(PluginClass)) {
      throw new Error(`Invalid plugin: ${file}`);
    }

    const plugin = new PluginClass();

    // Check dependencies
    if (plugin.dependencies) {
      for (const dep of plugin.dependencies) {
        if (!this.plugins.has(dep)) {
          throw new Error(
            `Plugin ${plugin.name} depends on ${dep} which is not loaded`
          );
        }
      }
    }

    this.plugins.set(plugin.name, plugin);
  }

  /**
   * Initialize plugins (dependency injection happens here)
   */
  private async initializePlugins() {
    for (const plugin of this.plugins.values()) {
      if (plugin.initialize) {
        // Inject core services via context
        await plugin.initialize(this.context);
      }

      // Register plugin with appropriate managers
      if ("registerHooks" in plugin) {
        (plugin as HookPlugin).registerHooks(this.core.hooks);
      }

      if ("agent" in plugin) {
        this.core.agents.registerAgent((plugin as AgentPlugin).agent);
      }

      if ("tool" in plugin) {
        this.core.tools.register((plugin as ToolPlugin).tool);
      }
    }
  }

  /**
   * Create plugin context (DI container)
   */
  private createPluginContext(): PluginContext {
    return {
      emitFile: (options) => this.core.files.emit(options),
      config: this.core.config.readonly(),
      log: this.core.logger,
      services: {
        hooks: this.core.hooks,
        tools: this.core.tools,
        agents: this.core.agents,
        context: this.core.context,
      },
    };
  }
}
```

---

## 5. ENABLING DISTRIBUTED PARALLEL INNOVATION

### 5.1 Clear Boundaries Enable Parallelism

**Module Boundaries = Team Boundaries**:

```
Core Team:
├── Maintains amplifier-core
├── Defines stable APIs
├── Reviews API changes
└── Releases core versions

Agent Team:
├── Develops specialized agents
├── Independent release cycle
├── Uses stable core APIs
└── Proposes new extension points

Tools Team:
├── Implements tools
├── Independent release cycle
├── Uses stable core APIs
└── Coordinates tool namespaces

Hook Team:
├── Creates lifecycle hooks
├── Independent release cycle
├── Uses stable hook APIs
└── Documents hook patterns

Provider Team:
├── Builds MCP providers
├── Independent release cycle
├── Uses stable MCP APIs
└── Maintains provider catalog
```

**Benefits**:

- **Parallel development**: Teams work simultaneously without blocking
- **Independent releases**: Plugins ship on their own schedule
- **Specialization**: Teams develop deep expertise in their domain
- **Reduced coordination**: Clear interfaces minimize dependencies

### 5.2 Stable Interfaces Enable Innovation

**API Stability Contract**:

```typescript
/**
 * Version 1.0.0 - Initial stable release
 *
 * STABLE GUARANTEES:
 * - All interfaces marked @stable never break
 * - Can add optional fields/methods
 * - Cannot remove or change required fields
 * - Must maintain backward compatibility
 *
 * EXPERIMENTAL FEATURES:
 * - Marked with @experimental
 * - Can change in minor versions
 * - Must opt-in explicitly
 *
 * INTERNAL IMPLEMENTATION:
 * - Marked with @internal
 * - Not exported from public API
 * - Free to change anytime
 */

// Example of stability levels
export interface PluginContext {
  /** @stable Since 1.0.0 */
  emitFile(options: EmitFileOptions): string;

  /** @stable Since 1.0.0 */
  readonly config: ReadonlyConfig;

  /** @experimental - May change */
  experimental_parallelExecute?(tasks: Task[]): Promise<Result[]>;

  // @internal methods not exported
}
```

**Semantic Versioning Strategy**:

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes to stable APIs
- **MINOR** (1.0.0 → 1.1.0): New features, backward compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, backward compatible

### 5.3 Plugin Marketplace Model

**Discovery and Distribution**:

```
amplifier-plugins/
├── official/              # Official plugins (core team)
│   └── manifest.json     # Plugin catalog
│
└── community/            # Community plugins
    ├── user1/
    │   ├── plugin-a/
    │   └── manifest.json
    └── user2/
        ├── plugin-b/
        └── manifest.json
```

**Plugin Manifest**:

```json
{
  "name": "zen-architect",
  "version": "1.2.3",
  "description": "Ruthless simplicity in design",
  "author": "Amplifier Team",
  "license": "MIT",
  "amplifierVersion": "^1.0.0",
  "type": "agent",
  "main": "./dist/index.js",
  "dependencies": {
    "amplifier-core": "^1.0.0"
  },
  "keywords": ["agent", "architecture", "design"],
  "repository": "https://github.com/microsoft/amplifier-plugins"
}
```

**Plugin CLI**:

```bash
# Install plugin
amplifier plugin install zen-architect

# List installed plugins
amplifier plugin list

# Update plugin
amplifier plugin update zen-architect

# Create new plugin from template
amplifier plugin create my-agent --type=agent
```

### 5.4 Contribution Model

**Contribution Flow**:

```
1. Developer creates plugin
   ├── Uses amplifier-core APIs
   ├── Follows plugin interface
   └── Writes tests

2. Plugin published to npm/GitHub
   ├── Versioned independently
   ├── Own release cycle
   └── Own documentation

3. Users install plugin
   ├── Via plugin CLI
   ├── Or manual installation
   └── Configured in .amplifier/

4. Core team may promote to official
   ├── High quality
   ├── Well documented
   ├── Actively maintained
   └── Useful to community
```

**RFC Process for Core Changes**:

```
1. Propose API addition/change
   ├── RFC document in GitHub
   ├── Use case justification
   ├── Backward compatibility analysis
   └── Implementation plan

2. Community review
   ├── 2-week comment period
   ├── Address feedback
   └── Reach consensus

3. Core team approval
   ├── API design review
   ├── Stability assessment
   └── Maintenance commitment

4. Implementation
   ├── PR with tests
   ├── Documentation update
   └── Migration guide if needed

5. Release
   ├── Semantic version bump
   ├── Changelog entry
   └── Announcement
```

---

## 6. SCALING FROM SINGLE DEVELOPER TO DISTRIBUTED TEAM

### 6.1 Phase 1: Single Maintainer (Months 1-3)

**Setup**:

```
amplifier/
├── src/
│   ├── core/          # All code here initially
│   └── api/           # Define interfaces from day 1
├── tests/
└── docs/
```

**Focus**:

- ✅ Define stable plugin interface
- ✅ Implement core agent loop
- ✅ Basic hook system
- ✅ 2-3 example plugins inline
- ✅ Comprehensive tests
- ✅ Documentation

**Discipline**:

- Separate public API from implementation from day 1
- Mark everything @stable or @internal
- Write documentation as you code
- Test plugin boundaries

### 6.2 Phase 2: Small Team (Months 4-6)

**Structure**:

```
amplifier/
├── packages/
│   ├── core/          # Core moves to package
│   ├── cli/           # CLI in separate package
│   └── plugins/       # Plugins in separate packages
│       ├── tools/
│       ├── agents/
│       └── hooks/
└── docs/
```

**Team**: 2-5 developers

**Focus**:

- ✅ Monorepo with multiple packages
- ✅ Split plugins into separate packages
- ✅ CI/CD for each package
- ✅ Independent versioning
- ✅ Plugin development guide
- ✅ Contribution guidelines

**Organization**:

- Core team (1-2 people) maintains core
- Plugin developers (2-3 people) build plugins
- Weekly sync meetings
- GitHub for coordination

### 6.3 Phase 3: Growing Team (Months 7-12)

**Structure**:

```
github.com/microsoft/
├── amplifier-core/          # Core in own repo
│   └── Stable APIs only
│
└── amplifier-plugins/       # Plugins in own repo
    ├── packages/
    │   ├── agents/
    │   ├── tools/
    │   └── providers/
    └── Independent releases
```

**Team**: 6-15 developers

**Focus**:

- ✅ Separate repositories
- ✅ Independent release cycles
- ✅ Plugin marketplace
- ✅ Community contributions
- ✅ RFC process for core changes
- ✅ Plugin certification program

**Organization**:

- Core team (2-3 people)
- Agent team (3-4 people)
- Tools team (2-3 people)
- Provider team (2-3 people)
- Monthly architecture reviews
- Slack/Discord for async communication

### 6.4 Phase 4: Distributed Team (Year 2+)

**Structure**:

```
Ecosystem:
├── microsoft/amplifier-core         # Core library
├── microsoft/amplifier-plugins      # Official plugins
├── microsoft/amplifier-cli          # CLI tool
├── community/awesome-amplifier      # Plugin directory
└── Various/community-plugins        # Community plugins
```

**Team**: 15+ developers + community

**Focus**:

- ✅ Mature plugin ecosystem
- ✅ Community-driven innovation
- ✅ Multiple organizations contributing
- ✅ Plugin compatibility matrix
- ✅ Automated testing infrastructure
- ✅ Conference talks and tutorials

**Organization**:

- Core team (3-5 people) maintains APIs
- Multiple plugin teams (distributed)
- Community contributors (open)
- Quarterly roadmap planning
- Annual contributor summit

---

## 7. CONCRETE IMPLEMENTATION EXAMPLES

### 7.1 Minimal Core Example

**Entry Point**:

```typescript
// src/index.ts - Public API entry point

export { AmplifierCore } from "./core/amplifier-core";
export type {
  AmplifierPlugin,
  PluginContext,
  HookPlugin,
  ToolPlugin,
  AgentPlugin,
  ProcessorPlugin,
  ProviderPlugin,
} from "./api/plugin";
export { LifecycleEvent } from "./api/hooks";
export type { Agent, AgentDefinition, Task, AgentResult } from "./api/agent";
```

**Core Implementation**:

```typescript
// src/core/amplifier-core.ts

import { PluginLoader } from "./plugin-loader";
import { HookEngine } from "./hook-engine";
import { AgentOrchestrator } from "./agent-orchestrator";
import { ContextManager } from "./context-manager";

export class AmplifierCore {
  private pluginLoader: PluginLoader;
  private hookEngine: HookEngine;
  private orchestrator: AgentOrchestrator;
  private contextManager: ContextManager;

  constructor(config: AmplifierConfig) {
    this.hookEngine = new HookEngine();
    this.contextManager = new ContextManager(config.context);
    this.orchestrator = new AgentOrchestrator(
      this.hookEngine,
      this.contextManager
    );
    this.pluginLoader = new PluginLoader(this);
  }

  /**
   * Initialize amplifier with plugins
   */
  async initialize() {
    // Load plugins from configured directories
    await this.pluginLoader.loadPlugins([
      "./node_modules/@amplifier/plugins",
      "./.amplifier/plugins",
      "~/.amplifier/plugins",
    ]);

    // Emit SessionStart event
    await this.hookEngine.emit(LifecycleEvent.SessionStart, {
      sessionId: this.contextManager.sessionId,
      source: "initialize",
    });
  }

  /**
   * Execute prompt through agent orchestrator
   */
  async execute(prompt: string): Promise<string> {
    return await this.orchestrator.execute(prompt);
  }

  /**
   * Access to hook system for plugins
   */
  get hooks() {
    return this.hookEngine;
  }
}
```

### 7.2 Example Plugin Implementations

**Tool Plugin Example**:

```typescript
// packages/tools/grep/src/index.ts

import { ToolPlugin, PluginContext } from "@amplifier/core";

export default class GrepPlugin implements ToolPlugin {
  readonly name = "grep";
  readonly version = "1.0.0";
  readonly type = "tool";

  readonly tool = {
    name: "Grep",
    description: "Search for patterns in files using regex",
    inputSchema: {
      type: "object",
      properties: {
        pattern: { type: "string", description: "Regex pattern" },
        paths: { type: "array", items: { type: "string" } },
        flags: { type: "string", description: "Regex flags (optional)" },
      },
      required: ["pattern", "paths"],
    },
  };

  async execute(input: any, context: PluginContext) {
    const { pattern, paths, flags } = input;

    context.log.debug("Grep searching", { pattern, paths });

    // Use ripgrep for actual search
    const results = await this.ripgrep(pattern, paths, flags);

    return {
      matches: results,
      count: results.length,
    };
  }

  private async ripgrep(pattern: string, paths: string[], flags?: string) {
    // Implementation using ripgrep
    // ...
  }
}
```

**Agent Plugin Example**:

```typescript
// packages/agents/bug-hunter/src/index.ts

import { AgentPlugin, Task, AgentContext, AgentResult } from "@amplifier/core";

export default class BugHunterPlugin implements AgentPlugin {
  readonly name = "bug-hunter";
  readonly version = "1.0.0";
  readonly type = "agent";

  readonly agent = {
    name: "bug-hunter",
    description: "Systematic debugging specialist. Use for tracking down bugs.",
    tools: ["Read", "Grep", "Bash", "Edit"],
    model: "sonnet-4.5",
  };

  async execute(task: Task, context: AgentContext): Promise<AgentResult> {
    const { issue, codebase } = task;

    // 1. Understand the bug
    const understanding = await this.understandBug(issue, context);

    // 2. Search for relevant code
    const relevantFiles = await this.findRelevantFiles(
      understanding.keywords,
      codebase,
      context
    );

    // 3. Reproduce the bug
    const reproduction = await this.reproduceBug(issue, relevantFiles, context);

    // 4. Identify root cause
    const rootCause = await this.identifyRootCause(
      reproduction,
      relevantFiles,
      context
    );

    // 5. Propose fix
    const fix = await this.proposeFix(rootCause, context);

    return {
      summary: `Found bug in ${rootCause.file}:${rootCause.line}`,
      rootCause,
      proposedFix: fix,
      confidence: 0.9,
    };
  }

  private async understandBug(issue: string, context: AgentContext) {
    // LLM analysis of bug description
    // ...
  }
}
```

**Hook Plugin Example**:

```typescript
// packages/hooks/transcript-backup/src/index.ts

import { HookPlugin, PluginContext, LifecycleEvent } from "@amplifier/core";

export default class TranscriptBackupPlugin implements HookPlugin {
  readonly name = "transcript-backup";
  readonly version = "1.0.0";
  readonly type = "hook";

  private backupDir: string;

  async initialize(context: PluginContext) {
    this.backupDir = context.config.get(
      "transcriptBackup.directory",
      ".data/transcripts"
    );
    await this.ensureDirectory(this.backupDir);
  }

  registerHooks(hooks: HookSystem) {
    // Backup transcript before compaction
    hooks.on(LifecycleEvent.PreCompact, async (data) => {
      const { sessionId, messages, trigger } = data;

      const timestamp = new Date().toISOString().replace(/:/g, "-");
      const filename = `${timestamp}_${sessionId}_${trigger}.jsonl`;
      const path = `${this.backupDir}/${filename}`;

      // Save transcript
      await this.saveTranscript(path, messages);

      console.log(`Backed up transcript to ${path}`);

      return { action: "continue" };
    });

    // Also backup on session end
    hooks.on(LifecycleEvent.SessionEnd, async (data) => {
      const { sessionId, messages } = data;

      const timestamp = new Date().toISOString().replace(/:/g, "-");
      const filename = `${timestamp}_${sessionId}_final.jsonl`;
      const path = `${this.backupDir}/${filename}`;

      await this.saveTranscript(path, messages);

      return { action: "continue" };
    });
  }

  private async saveTranscript(path: string, messages: any[]) {
    // Write JSONL format
    // ...
  }
}
```

### 7.3 Configuration Example

**Project Configuration** (`.amplifier/config.json`):

```json
{
  "version": "1.0.0",

  "plugins": {
    "directories": [
      "./node_modules/@amplifier/plugins",
      "./.amplifier/plugins",
      "~/.amplifier/plugins"
    ],
    "enabled": [
      "grep",
      "edit",
      "bash",
      "zen-architect",
      "bug-hunter",
      "security-validator",
      "transcript-backup"
    ],
    "disabled": ["experimental-feature"]
  },

  "agents": {
    "defaultModel": "sonnet-4.5",
    "maxSubagents": 5,
    "timeout": 300000
  },

  "context": {
    "maxTokens": 200000,
    "compactThreshold": 0.92,
    "memoryFiles": ["./CLAUDE.md", "./.amplifier/MEMORY.md"]
  },

  "hooks": {
    "parallel": true,
    "timeout": 60000
  },

  "transcriptBackup": {
    "enabled": true,
    "directory": ".data/transcripts"
  }
}
```

---

## 8. KEY DESIGN DECISIONS SUMMARY

### 8.1 What Goes in Core vs. Plugins

**Core (Minimal, Stable)**:

- ✅ Plugin discovery and loading
- ✅ Hook system infrastructure
- ✅ Agent orchestration loop
- ✅ Context management
- ✅ Common services (logging, config, file I/O)
- ✅ Public API definitions

**Plugins (Rich, Evolving)**:

- ✅ All tools (Grep, Edit, Bash, WebFetch, etc.)
- ✅ All agents (zen-architect, bug-hunter, etc.)
- ✅ All hooks (formatters, validators, backups)
- ✅ All providers (GitHub, filesystem, databases)
- ✅ Knowledge extraction
- ✅ UI/presentation layers

### 8.2 Stable Interfaces

**Never Break (1.x.x)**:

- Plugin interface (AmplifierPlugin)
- Hook system (LifecycleEvent, HookHandler)
- Agent interface (Agent, Task, AgentResult)
- Tool interface (Tool, ToolInput, ToolOutput)
- Context interface (PluginContext, AgentContext)
- Configuration format

**Can Evolve (1.x.x → 1.y.y)**:

- Add optional fields
- Add new events
- Add new plugin types
- Add experimental APIs
- Extend capabilities

**Internal (Change Anytime)**:

- Agent loop implementation
- Context compaction algorithm
- Plugin loader internals
- Hook execution strategy
- Performance optimizations

### 8.3 Extension Points

**How Plugins Extend Core**:

1. **Tools**: Register new tools via ToolPlugin
2. **Agents**: Register specialized agents via AgentPlugin
3. **Hooks**: Register lifecycle handlers via HookPlugin
4. **Processors**: Register data transformers via ProcessorPlugin
5. **Providers**: Register MCP servers via ProviderPlugin

**Communication Patterns**:

- Plugins → Core: Via registered interfaces
- Core → Plugins: Via lifecycle events
- Plugin → Plugin: Via core services (discouraged direct communication)

---

## 9. UNIX/LINUX PRINCIPLES APPLIED

### 9.1 How This Architecture Embodies Unix Philosophy

**Do One Thing Well**:

- Core does orchestration, plugins do specific work
- Each plugin has single responsibility
- Clear module boundaries

**Composability**:

- Plugins compose through hook system
- Output of one plugin can trigger another
- Text-based interchange (JSON)

**Text Streams as Universal Interface**:

- JSON for plugin communication
- JSONL for transcripts
- Markdown for documentation and memory

**Separation of Mechanism and Policy**:

- Core provides mechanisms (how to run agents)
- Plugins define policies (what agents do)
- Configuration determines behavior

### 9.2 How This Architecture Embodies Linux Kernel Principles

**Never Break Userspace**:

- Public APIs are sacred contracts
- Semantic versioning enforced
- Deprecation process for changes
- Backward compatibility guaranteed

**Stable External, Flexible Internal**:

- Public API layer is stable
- Internal implementation can change freely
- Refactoring doesn't affect plugins
- Optimization doesn't break contracts

**Code Talks, Bullshit Walks**:

- Working plugins prove architecture
- Test-driven development
- Pragmatic over perfect
- Ship and iterate

**Clear Boundary**:

- amplifier-core vs. amplifier-plugins
- Clear responsibility
- Independent evolution
- No finger-pointing

---

## 10. SUCCESS METRICS

### How to Measure If This Architecture Succeeds

**External Stability**:

- ✅ Old plugins work with new core versions
- ✅ No breaking changes in minor versions
- ✅ Clear upgrade paths for major versions
- ✅ Deprecation warnings before removal

**Internal Flexibility**:

- ✅ Can refactor core without breaking plugins
- ✅ Can optimize without external impact
- ✅ Can fix bugs in isolated modules
- ✅ Can improve without API changes

**Developer Productivity**:

- ✅ New developers can create plugins easily
- ✅ Debugging is straightforward
- ✅ Errors are clear and actionable
- ✅ Documentation is helpful

**Innovation Velocity**:

- ✅ Multiple teams work in parallel
- ✅ Experiments are easy to try
- ✅ Features added without core changes
- ✅ Community contributions flourish

**Maintainability**:

- ✅ Single person can maintain core
- ✅ Code is clear and well-documented
- ✅ Tests provide confidence
- ✅ Technical debt stays manageable

---

## 11. IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Months 1-2)

**Week 1-2: API Design**

- [ ] Define stable plugin interfaces
- [ ] Design hook system
- [ ] Specify agent interfaces
- [ ] Document API contracts

**Week 3-4: Core Implementation**

- [ ] Implement plugin loader
- [ ] Build hook engine
- [ ] Create agent orchestrator
- [ ] Add context manager

**Week 5-6: Example Plugins**

- [ ] Implement 2-3 tool plugins
- [ ] Implement 1-2 agent plugins
- [ ] Implement 1-2 hook plugins
- [ ] Document plugin patterns

**Week 7-8: Testing & Documentation**

- [ ] Comprehensive test suite
- [ ] API reference documentation
- [ ] Plugin development guide
- [ ] Architecture documentation

### Phase 2: Expansion (Months 3-4)

**Week 9-10: Plugin Ecosystem**

- [ ] Move plugins to separate packages
- [ ] Setup monorepo (Lerna/Nx)
- [ ] Independent versioning
- [ ] CI/CD for each package

**Week 11-12: CLI Tool**

- [ ] Plugin installation CLI
- [ ] Plugin management commands
- [ ] Configuration helpers
- [ ] Interactive setup wizard

**Week 13-14: MCP Integration**

- [ ] MCP provider interface
- [ ] Example MCP providers
- [ ] MCP server lifecycle management
- [ ] Documentation and examples

**Week 15-16: Community Prep**

- [ ] Contribution guidelines
- [ ] Plugin certification process
- [ ] Example plugin templates
- [ ] Getting started tutorials

### Phase 3: Maturation (Months 5-6)

**Week 17-20: Ecosystem Growth**

- [ ] Separate repositories
- [ ] Plugin marketplace
- [ ] Community plugins
- [ ] Plugin compatibility matrix

**Week 21-24: Polish & Performance**

- [ ] Performance optimization
- [ ] Error handling improvements
- [ ] Better logging and debugging
- [ ] Production readiness

---

## 12. CONCLUSION

### The Vision

Amplifier-core becomes the **Linux kernel of AI coding assistants**: a thin, stable core that provides essential mechanisms while enabling a rich ecosystem of plugins to flourish. Just as Linux enabled distributed innovation in operating systems, amplifier-core enables distributed innovation in AI-assisted development.

### Core Principles Realized

1. **Thin Stable Core**: Minimal core with well-defined extension points
2. **Never Break Userspace**: Public APIs are sacred contracts
3. **Mechanism vs. Policy**: Core provides mechanisms, plugins define policies
4. **Distributed Innovation**: Clear boundaries enable parallel development
5. **Pragmatic Evolution**: Working code over perfect architecture

### Why This Architecture Scales

**Single Maintainer** (Day 1):

- Simple core, clear boundaries
- Easy to understand and maintain
- Room to evolve

**Small Team** (Months 3-6):

- Module boundaries become team boundaries
- Parallel development without blocking
- Independent release cycles

**Distributed Team** (Year 1+):

- Plugin ecosystem flourishes
- Community contributions
- Multiple organizations collaborating
- Innovation at the edges, stability at the core

### The Unix/Linux Legacy

This architecture stands on the shoulders of giants:

- **Unix philosophy**: Simplicity, composability, text streams
- **Linux kernel**: Stable APIs, flexible implementation, never break userspace
- **Modern plugins**: Babel, Webpack, VSCode show the patterns work

By applying these time-tested principles to AI-assisted development, amplifier-core can achieve the same longevity, stability, and innovation that has made Unix/Linux the foundation of modern computing.

### Next Steps

1. **Validate** this design with stakeholders
2. **Prototype** core interfaces
3. **Implement** minimal viable core
4. **Test** with example plugins
5. **Document** extensively
6. **Iterate** based on feedback
7. **Ship** and enable the ecosystem

The journey of a thousand plugins begins with a single, stable core. Let's build that foundation right.
````

---

Powered by [Claude Exporter](https://www.claudexporter.com)
