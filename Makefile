# Workspace Makefile - Orchestrates modular components

#==============================================================================
# CRITICAL: Include order matters
#
# 1. core.mk (foundation - MUST be first)
# 2. delegation.mk (depends on core - MUST be second)
# 3. All others (depend on core, some on delegation - any order)
#
# DO NOT change include order without reviewing dependencies
#==============================================================================

include tools/makefiles/core.mk
include tools/makefiles/delegation.mk
include tools/makefiles/install.mk
include tools/makefiles/quality.mk
include tools/makefiles/knowledge-extraction.mk
include tools/makefiles/knowledge-synthesis.mk
include tools/makefiles/worktree.mk
include tools/makefiles/content-generation.mk
include tools/makefiles/sync.mk
include tools/makefiles/utilities.mk

.DEFAULT_GOAL := default

.PHONY: default help verify-modules

default: ## Show essential commands
	@echo ""
	@echo "Quick Start:"
	@echo "  make install         Install parent dependencies"
	@echo "  make install-all     Install parent + all submodules"
	@echo ""
	@echo "Knowledge Base:"
	@echo "  make knowledge-update        Full pipeline: extract & synthesize"
	@echo "  make knowledge-query Q=\"...\" Query your knowledge base"
	@echo "  make knowledge-graph-viz     Create interactive visualization"
	@echo "  make knowledge-stats         Show knowledge base statistics"
	@echo ""
	@echo "Development (Pure Delegation Architecture):"
	@echo "  make check          Format, lint, and type-check parent workspace"
	@echo "  make test           Run parent workspace tests with coverage"
	@echo "  make check-all      Check parent + all submodules recursively"
	@echo "  make test-all       Test parent + all submodules recursively"
	@echo "  make smoke-test     Run quick smoke tests (< 2 minutes)"
	@echo "  make worktree NAME   Create git worktree with .data copy"
	@echo "  make worktree-list   List all git worktrees"
	@echo "  make worktree-stash NAME  Hide worktree (keeps directory)"
	@echo "  make worktree-adopt BRANCH  Create worktree from remote"
	@echo "  make worktree-rm NAME  Remove worktree and delete branch"
	@echo ""
	@echo "AI Context:"
	@echo "  make ai-context-files Build AI context documentation"
	@echo ""
	@echo "Blog Writing:"
	@echo "  make blog-write      Create a blog post from your ideas"
	@echo ""
	@echo "Transcription:"
	@echo "  make transcribe      Transcribe audio/video files or YouTube URLs"
	@echo "  make transcribe-index Generate index of all transcripts"
	@echo ""
	@echo "Article Illustration:"
	@echo "  make illustrate      Generate AI illustrations for article"
	@echo ""
	@echo "Web to Markdown:"
	@echo "  make web-to-md       Convert web pages to markdown"
	@echo ""
	@echo "Sync (Optional):"
	@echo "  make sync-setup      Setup bidirectional sync"
	@echo "  make sync-status     Show sync configuration"
	@echo "  make sync-pull       Pull from remote (remote wins)"
	@echo "  make sync-push       Push to remote"
	@echo ""
	@echo "Other:"
	@echo "  make clean           Clean build artifacts"
	@echo "  make help            Show ALL available commands"
	@echo ""

help: ## Show ALL available commands
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "                ALL AVAILABLE COMMANDS"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "QUICK START:"
	@echo "  make install         Install parent dependencies"
	@echo "  make install-all     Install parent + all submodules"
	@echo ""
	@echo "KNOWLEDGE BASE:"
	@echo "  make knowledge-update        Full pipeline: extract & synthesize"
	@echo "  make knowledge-sync          Extract knowledge from content"
	@echo "  make knowledge-sync-batch N=5  Process next N articles"
	@echo "  make knowledge-synthesize    Find patterns across knowledge"
	@echo "  make knowledge-query Q=\"...\" Query your knowledge base"
	@echo "  make knowledge-search Q=\"...\" Search extracted knowledge"
	@echo "  make knowledge-stats         Show knowledge statistics"
	@echo "  make knowledge-export FORMAT=json|text  Export knowledge"
	@echo ""
	@echo "KNOWLEDGE GRAPH:"
	@echo "  make knowledge-graph-build   Build graph from extractions"
	@echo "  make knowledge-graph-update  Incremental graph update"
	@echo "  make knowledge-graph-stats   Show graph statistics"
	@echo "  make knowledge-graph-viz NODES=50  Create visualization"
	@echo "  make knowledge-graph-search Q=\"...\"  Semantic search"
	@echo "  make knowledge-graph-path FROM=\"...\" TO=\"...\"  Find paths"
	@echo "  make knowledge-graph-neighbors CONCEPT=\"...\" HOPS=2"
	@echo "  make knowledge-graph-tensions TOP=10  Find contradictions"
	@echo "  make knowledge-graph-export FORMAT=gexf|graphml"
	@echo "  make knowledge-graph-top-predicates N=15"
	@echo ""
	@echo "KNOWLEDGE EVENTS:"
	@echo "  make knowledge-events N=50   Show recent pipeline events"
	@echo "  make knowledge-events-tail N=20  Follow events (Ctrl+C stop)"
	@echo "  make knowledge-events-summary SCOPE=last|all"
	@echo ""
	@echo "CONTENT:"
	@echo "  make content-scan    Scan configured content directories"
	@echo "  make content-search q=\"...\"  Search content"
	@echo "  make content-status  Show content statistics"
	@echo ""
	@echo "DEVELOPMENT:"
	@echo "  make install         Install parent dependencies"
	@echo "  make install-all     Install parent + all submodules"
	@echo "  make check           Format, lint, and type-check code"
	@echo "  make test            Run all tests with coverage"
	@echo "  make smoke-test      Run quick smoke tests (< 2 minutes)"
	@echo "  make worktree NAME   Create git worktree with .data copy"
	@echo "  make worktree-list   List all git worktrees"
	@echo "  make worktree-stash NAME  Hide worktree (keeps directory)"
	@echo "  make worktree-adopt BRANCH  Create worktree from remote"
	@echo "  make worktree-rm NAME  Remove worktree and delete branch"
	@echo "  make worktree-rm-force NAME  Force remove (with changes)"
	@echo "  make worktree-unstash NAME  Restore hidden worktree"
	@echo "  make worktree-list-stashed  List all hidden worktrees"
	@echo ""
	@echo "SYNTHESIS:"
	@echo "  make synthesize query=\"...\" files=\"...\"  Run synthesis"
	@echo "  make triage query=\"...\" files=\"...\"  Run triage only"
	@echo ""
	@echo "AI CONTEXT:"
	@echo "  make ai-context-files  Build AI context documentation"
	@echo ""
	@echo "BLOG WRITING:"
	@echo "  make blog-write IDEA=<file> WRITINGS=<dir> [INSTRUCTIONS=\"...\"]  Create blog"
	@echo "  make blog-resume       Resume most recent blog writing session"
	@echo ""
	@echo "ARTICLE ILLUSTRATION:"
	@echo "  make illustrate INPUT=<file> [OUTPUT=<path>] [STYLE=\"...\"] [APIS=\"...\"] [RESUME=true]  Generate illustrations"
	@echo "  make illustrate-example  Run illustrator with example article"
	@echo "  make illustrate-prompts-only INPUT=<file>  Preview prompts without generating"
	@echo ""
	@echo "WEB TO MARKDOWN:"
	@echo "  make web-to-md URL=<url> [URL2=<url>] [OUTPUT=<path>]  Convert web pages to markdown (saves to content_dirs[0]/sites/)"
	@echo ""
	@echo "SYNC (OPTIONAL):"
	@echo "  make sync-setup      Setup bidirectional sync with remote server"
	@echo "  make sync-status     Show sync configuration and status"
	@echo "  make sync-pull       Pull from remote (remote wins on conflicts)"
	@echo "  make sync-push       Push to remote server"
	@echo "  make sync-pull-dry   Preview pull operation (no changes)"
	@echo "  make sync-push-dry   Preview push operation (no changes)"
	@echo ""
	@echo "UTILITIES:"
	@echo "  make clean           Clean build artifacts"
	@echo "  make clean-wsl-files Clean WSL-related files"
	@echo "  make workspace-info  Show workspace information"
	@echo "  make dot-to-mermaid INPUT=\"path\"  Convert DOT files to Mermaid"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""

verify-modules: ## Verify all modules loaded correctly
	@echo "✓ Modular Makefile system loaded (10 modules)"
	@echo ""
	@echo "Modules:"
	@echo "  • core.mk (foundation)"
	@echo "  • delegation.mk (recursion patterns)"
	@echo "  • install.mk (dependency installation)"
	@echo "  • quality.mk (check/test targets)"
	@echo "  • knowledge-extraction.mk (document processing)"
	@echo "  • knowledge-synthesis.mk (pipeline & visualization)"
	@echo "  • worktree.mk (git worktree utilities)"
	@echo "  • content-generation.mk (blog/transcribe/illustrate/web-to-md)"
	@echo "  • sync.mk (bidirectional sync with remote)"
	@echo "  • utilities.mk (cleanup, misc)"
	@echo ""
	@echo "Run 'make help' to see all available targets"

# Catch-all for worktree branch names and dynamic targets
%:
	@if echo "$(MAKECMDGOALS)" | grep -qE '^(worktree|worktree-rm|worktree-rm-force|worktree-stash|worktree-unstash|worktree-adopt|sync-)\b'; then \
		: ; \
	else \
		echo "Error: Unknown command '$@'. Run 'make help' to see available commands."; \
		exit 1; \
	fi
