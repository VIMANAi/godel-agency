# GitHub Quality Setup (Manual Steps)

This repository now includes CI, security, release workflows, templates, Dependabot, and Codespaces config.

## 1) Branch protection rules (GitHub UI)
Create a branch protection rule for `main` with:
- Require a pull request before merging
- Require approvals: at least 1 (recommended 2)
- Require status checks to pass before merging:
  - `quality`
  - `codeql`
  - `secrets-scan`
- Require conversation resolution before merging

## 2) Protected environment for releases
Create environment `production` and require reviewers before deployment approval.

## 3) GitHub Projects board
Create a project board with these columns:
- Backlog
- Ready
- In Progress
- Review
- Done

Then add built-in automations:
- New issue -> Backlog
- PR opened -> In Progress
- PR merged -> Done

## 4) Quality gate policy
Use this policy for all changes:
- All meaningful changes go through PR
- CI + Security checks must pass
- Security findings must be triaged before merge
