# Release Please Configuration

## Overview

Release Please is configured for **manual trigger only**. It will no longer run automatically on every push to `main`.

## Required Configuration (ONE-TIME SETUP)

Enable the permission for GitHub Actions to create PRs:

1. Go to https://github.com/soma-smart/le-coffre/settings/actions
2. Scroll down to **"Workflow permissions"**
3. Enable **"Allow GitHub Actions to create and approve pull requests"**
4. Click **Save**

## How to Create a Release

### 1. Prepare a Release PR

1. Go to **Actions** → **Release Please** → **Run workflow**
2. Leave the default option (skip GitHub release)
3. Click **Run workflow**
4. Release Please will create/update a PR with the CHANGELOG

### 2. Merge the Release PR

1. Review the generated CHANGELOG in the PR
2. Merge the PR when ready
3. The CHANGELOG and version will be updated on `main`

### 3. Create the GitHub Release (manually)

1. Go to https://github.com/soma-smart/le-coffre/releases/new
2. Select the tag (e.g., `v0.2.1`)
3. Copy the CHANGELOG content for this version
4. Publish when you're ready

## Commit Convention

For your commits to appear in the CHANGELOG, follow Conventional Commits:

✅ **Correct format**:
- `feat: add user authentication`
- `fix: resolve login bug`
- `chore: update dependencies`

❌ **Incorrect format**:
- `Feat/add user authentication` (won't be parsed)
- `Add user authentication` (won't be parsed)

Changelog sections are defined in `release-please-config.json`
