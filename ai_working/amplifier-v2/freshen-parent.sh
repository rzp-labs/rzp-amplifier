#!/bin/bash
# freshen-parent.sh - Update parent repository and amplifier-dev submodule
#
# Usage: ./freshen-parent.sh [OPTIONS]
#
# This script updates the parent amplifier repository and its amplifier-dev
# submodule to their latest versions.
#
# Examples:
#   ./freshen-parent.sh           # Update parent and amplifier-dev
#   ./freshen-parent.sh --dry-run # Preview what would be updated
#
# Exit codes:
#   0 - Success
#   1 - General error
#   3 - Git operation failed

set -euo pipefail

# Color codes
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Flags
DRY_RUN=false
VERBOSE=false
QUIET=false

# Logging functions
log_success() { [[ $QUIET != true ]] && echo -e "${GREEN}✓${NC} $1"; }
log_info() { [[ $QUIET != true ]] && echo -e "${BLUE}→${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1" >&2; }
log_verbose() { [[ $VERBOSE == true ]] && echo -e "  ${BLUE}→${NC} $1"; }

error_exit() {
    log_error "$1"
    exit "${2:-1}"
}

# Show help
show_help() {
    cat <<EOF
Usage: $0 [OPTIONS]

Update parent amplifier repository and amplifier-dev submodule.

OPTIONS:
  -h, --help       Show this help message
  -d, --dry-run    Show what would be done without making changes
  -v, --verbose    Show detailed output
  -q, --quiet      Minimal output (errors only)

Workflow:
  1. Check for uncommitted changes in parent (warn if present)
  2. Fetch and pull latest for parent repository
  3. Enter amplifier-dev submodule
  4. Fetch and pull latest for amplifier-dev (main branch)
  5. Return to parent
  6. Update submodule pointer if amplifier-dev changed

Examples:
  $0                # Update everything
  $0 --dry-run      # Preview changes
  $0 --verbose      # Show detailed output

Exit codes:
  0 - Success
  1 - General error
  3 - Git operation failed
EOF
}

# Parse options
parse_options() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -q|--quiet)
                QUIET=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error_exit "Unknown option: $1\nUse --help for usage information" 2
                ;;
        esac
    done
}

# Check if repo is clean
is_repo_clean() {
    [[ -z $(git status --porcelain) ]]
}

# Get current branch
get_current_branch() {
    git rev-parse --abbrev-ref HEAD
}

# Freshen parent repository
freshen_parent() {
    log_info "Freshening parent repository (microsoft/amplifier)"

    # Check for uncommitted changes
    if ! is_repo_clean; then
        log_warning "Parent repository has uncommitted changes"
        git status --short
        echo
    fi

    local branch
    branch=$(get_current_branch)

    log_verbose "Current branch: $branch"

    # Fetch from remote
    log_verbose "Fetching from origin"
    if [[ $DRY_RUN == true ]]; then
        log_info "[DRY-RUN] Would fetch from origin"
    else
        git fetch origin 2>&1 | grep -v "^From" || true
    fi

    # Pull latest
    log_verbose "Pulling $branch"
    if [[ $DRY_RUN == true ]]; then
        log_info "[DRY-RUN] Would pull origin/$branch"
    else
        if git pull --ff-only origin "$branch" >/dev/null 2>&1; then
            log_success "Parent repository updated"
        else
            log_warning "Could not fast-forward pull (may need merge or rebase)"
            return 1
        fi
    fi

    echo
}

# Freshen amplifier-dev submodule
freshen_submodule() {
    log_info "Freshening amplifier-dev submodule"

    # Check if submodule exists
    if [[ ! -d amplifier-dev ]]; then
        error_exit "amplifier-dev submodule not found" 1
    fi

    # Enter submodule
    pushd amplifier-dev >/dev/null || error_exit "Failed to enter amplifier-dev" 1

    # Check for uncommitted changes
    if ! is_repo_clean; then
        log_warning "amplifier-dev has uncommitted changes"
        git status --short
        echo
    fi

    # Fetch from remote
    log_verbose "Fetching from origin"
    if [[ $DRY_RUN == true ]]; then
        log_info "[DRY-RUN] Would fetch from origin"
    else
        git fetch origin 2>&1 | grep -v "^From" || true
    fi

    # Pull latest (main branch)
    log_verbose "Pulling main"
    if [[ $DRY_RUN == true ]]; then
        log_info "[DRY-RUN] Would pull origin/main"
    else
        if git pull --ff-only origin main >/dev/null 2>&1; then
            log_success "amplifier-dev updated"
        else
            log_warning "Could not fast-forward pull (may need merge or rebase)"
            popd >/dev/null
            return 1
        fi
    fi

    popd >/dev/null
    echo
}

# Update submodule pointer
update_submodule_pointer() {
    log_info "Checking submodule pointer"

    # Check if amplifier-dev submodule has changed
    if git status --porcelain | grep -q "^.M amplifier-dev"; then
        log_info "amplifier-dev submodule has updates"

        if [[ $DRY_RUN == true ]]; then
            log_info "[DRY-RUN] Would commit submodule pointer update"
        else
            log_success "Submodule pointer needs manual commit"
            echo
            log_info "To commit the submodule pointer update:"
            log_info "  git add amplifier-dev"
            log_info "  git commit -m 'chore: update amplifier-dev submodule'"
        fi
    else
        log_verbose "Submodule pointer unchanged"
    fi

    echo
}

# Main
main() {
    # Check we're in a git repository
    git rev-parse --git-dir >/dev/null 2>&1 || error_exit "Not in a git repository" 1

    # Check we're in parent amplifier root
    if [[ ! -f "AMPLIFIER_VISION.md" ]]; then
        error_exit "Must be run from parent amplifier repository root" 1
    fi

    log_info "Freshen Parent - Update parent and amplifier-dev submodule"
    echo

    # Freshen parent
    freshen_parent

    # Freshen amplifier-dev submodule
    freshen_submodule

    # Check submodule pointer
    update_submodule_pointer

    log_success "Freshen completed successfully"

    if [[ $DRY_RUN == true ]]; then
        echo
        log_info "This was a dry-run. No changes were made."
    fi
}

parse_options "$@"
main
