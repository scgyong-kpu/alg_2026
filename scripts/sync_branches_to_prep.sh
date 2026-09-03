#!/usr/bin/env bash
set -euo pipefail

source_branch="prep"
target_branches=(a01 a02 a03)
apply=0
push=0

usage() {
    cat <<USAGE
Usage: $0 [--apply] [--push] [source_branch]

Fast-forward a01, a02, and a03 to source_branch.

Default source_branch: prep

Without --apply, this script only prints what would happen.
--push implies --apply and pushes updated branches to origin.
It refuses non-fast-forward updates.
USAGE
}

for arg in "$@"; do
    case "$arg" in
        --apply)
            apply=1
            ;;
        --push)
            apply=1
            push=1
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            source_branch="$arg"
            ;;
    esac
done

git rev-parse --verify --quiet "$source_branch" >/dev/null || {
    echo "error: source branch '$source_branch' does not exist" >&2
    exit 1
}

for branch in "${target_branches[@]}"; do
    git rev-parse --verify --quiet "$branch" >/dev/null || {
        echo "error: target branch '$branch' does not exist" >&2
        exit 1
    }
done

if [[ "$apply" -eq 1 ]] && (! git diff --quiet || ! git diff --cached --quiet); then
    echo "error: tracked files have uncommitted changes" >&2
    echo "Commit, stash, or discard tracked changes before syncing branches." >&2
    exit 1
fi

source_sha="$(git rev-parse --short "$source_branch")"
current_branch="$(git branch --show-current)"

echo "source: $source_branch ($source_sha)"

for branch in "${target_branches[@]}"; do
    branch_sha="$(git rev-parse --short "$branch")"

    if [[ "$branch_sha" == "$source_sha" ]]; then
        echo "$branch: already at $source_branch ($source_sha)"
        continue
    fi

    if ! git merge-base --is-ancestor "$branch" "$source_branch"; then
        echo "error: $branch cannot fast-forward to $source_branch" >&2
        exit 1
    fi

    if [[ "$apply" -eq 0 ]]; then
        echo "$branch: would fast-forward $branch_sha -> $source_sha"
        continue
    fi

    echo "$branch: fast-forward $branch_sha -> $source_sha"
    git switch --quiet "$branch"
    git merge --ff-only --quiet "$source_branch"
done

if [[ "$apply" -eq 1 && -n "$current_branch" ]]; then
    git switch --quiet "$current_branch"
fi

if [[ "$apply" -eq 0 ]]; then
    echo
    echo "Dry run only. Run with --apply to update branches, or --push to update and push."
    exit 0
fi

if [[ "$push" -eq 1 ]]; then
    echo
    echo "pushing branches to origin"
    git push origin "${target_branches[@]}"
fi
