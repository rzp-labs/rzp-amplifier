#!/bin/bash
# push-parent.sh - Push parent repository changes and update submodule pointer
#
# Usage: ./push-parent.sh [OPTIONS]
#
# This script pushes committed changes in the parent repository and automatically
# updates the amplifier-dev submodule pointer if it has changed.
#
# Examples:
#   ./push-parent.sh           # Push parent and update submodule pointer
#   ./push-parent.sh --dry-run # Preview what would be pushed
#
# Exit codes:
#   0 - Success
#   1 - General error
#   3 - Git operation failed
#   5 - Precondition not met (uncommitted changes)

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
NO_SUBMODULE_UPDATE=false

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

Push committed parent repository changes and update submodule pointer.

Prerequisites:
  - All changes in parent must be committed
  - No uncommitted changes

OPTIONS:
  -h, --help               Show this help message
  -d, --dry-run            Show what would be done without making changes
  -v, --verbose            Show detailed output
  -q, --quiet              Minimal output (errors only)
  --no-submodule-update    Skip submodule pointer update

Workflow:
  1. Check that parent repository is clean (all changes committed)
  2. Check if amplifier-dev submodule has changed
  3. If changed, add and commit submodule pointer update
  4. Push parent branch to origin

Examples:
  $0                        # Push everything
  $0 --dry-run              # Preview changes
  $0 --no-submodule-update  # Don't update submodule pointer

Exit codes:
  0 - Success
  1 - General error
  3 - Git operation failed
  5 - Precondition not met (uncommitted changes)
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
            --no-submodule-update)
                NO_SUBMODULE_UPDATE=true
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

# Check if there are unpushed commits
has_unpushed_commits() {
    local branch="${1:-$(get_current_branch)}"
    local ahead
    ahead=$(git rev-list --count "origin/$branch..HEAD" 2>/dev/null || echo "0")
    [[ "$ahead" -gt 0 ]]
}

# Count unpushed commits
count_unpushed_commits() {
    local branch="${1:-$(get_current_branch)}"
    git rev-list --count "origin/$branch..HEAD" 2>/dev/null || echo "0"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking repository status"

    # Check if there are uncommitted changes (excluding submodule pointer)
    local status
    status=$(git status --porcelain | grep -v "^.M amplifier-dev" || true)

    if [[ -n $status ]]; then
        log_error "Parent repository has uncommitted changes"
        log_error "Please commit or stash changes before pushing"
        echo
        git status --short
        exit 5
    fi

    log_success "No uncommitted changes"
    echo
}

# Update submodule pointer
update_submodule_pointer() {
    if [[ $NO_SUBMODULE_UPDATE == true ]]; then
        log_info "Skipping submodule pointer update (--no-submodule-update)"
        return 0
    fi

    log_info "Checking amplifier-dev submodule pointer"

    # Check if amplifier-dev submodule has changed
    if git status --porcelain | grep -q "^.M amplifier-dev"; then
        log_info "amplifier-dev submodule has updates"

        if [[ $DRY_RUN == true ]]; then
            log_info "[DRY-RUN] Would add and commit submodule pointer"
        else
            # Add submodule pointer
            git add amplifier-dev

            # Commit
            if git commit -m "chore: update amplifier-dev submodule" >/dev/null 2>&1; then
                log_success "Committed submodule pointer update"
            else
                log_error "Failed to commit submodule pointer"
                return 1
            fi
        fi
    else
        log_verbose "Submodule pointer unchanged"
    fi

    echo
}

# Push parent repository
push_parent() {
    log_info "Pushing to origin"

    local branch
    branch=$(get_current_branch)

    log_verbose "Current branch: $branch"

    # Check if there are unpushed commits
    if has_unpushed_commits "$branch"; then
        local count
        count=$(count_unpushed_commits "$branch")

        log_info "$count commit(s) to push"

        if [[ $DRY_RUN == true ]]; then
            log_info "[DRY-RUN] Would push to origin/$branch"
        else
            if git push origin "$branch" 2>&1; then
                log_success "Pushed to origin/$branch"
            else
                log_error "Failed to push to origin/$branch"
                return 3
            fi
        fi
    else
        log_info "Already up to date with origin/$branch"
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

    log_info "Push Parent - Push parent changes and update submodule pointer"
    echo

    # Check prerequisites
    check_prerequisites

    # Update submodule pointer if needed
    update_submodule_pointer

    # Push parent repository
    push_parent

    log_success "Push completed successfully"

    if [[ $DRY_RUN == true ]]; then
        echo
        log_info "This was a dry-run. No changes were made."
    fi
}

parse_options "$@"
main
