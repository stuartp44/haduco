# Release Pipeline Checklist

## Pre-Push Checklist

Before pushing code to trigger a release:

- [ ] All tests pass locally (`pytest tests/`)
- [ ] Code is properly formatted (`ruff format .`)
- [ ] No linting errors (`ruff check .`)
- [ ] Type checking passes (`mypy custom_components/duco_ventilation_sun_control`)
- [ ] Commits follow conventional format
- [ ] Documentation is updated
- [ ] CHANGELOG notes are clear (if manually editing)

## First-Time Setup Checklist

### Repository Configuration

- [ ] Enable GitHub Actions in repository settings
- [ ] Set up branch protection for `main` branch
  - [ ] Require status checks to pass
  - [ ] Require pull request reviews (recommended)
  - [ ] Require branches to be up to date
- [ ] Enable Issues in repository settings
- [ ] Configure repository to allow squash merging
- [ ] Add repository description and topics

### Optional Integrations

- [ ] Set up Codecov account (optional)
  - Visit https://codecov.io
  - Link repository
  - View coverage reports in PRs
- [ ] Enable GitHub Discussions (optional)
- [ ] Set up GitHub repository insights

### Labels Setup

Create these labels in your repository for better organization:

- [ ] `bug` - Bug reports
- [ ] `enhancement` - Feature requests
- [ ] `documentation` - Documentation updates
- [ ] `tests` - Test-related changes
- [ ] `refactor` - Code refactoring
- [ ] `performance` - Performance improvements
- [ ] `breaking-change` - Breaking changes
- [ ] `dependencies` - Dependency updates
- [ ] `stale` - Stale issues/PRs

Quick create labels:
```bash
# Use GitHub CLI
gh label create bug --color "d73a4a" --description "Something isn't working"
gh label create enhancement --color "a2eeef" --description "New feature or request"
gh label create documentation --color "0075ca" --description "Documentation improvements"
gh label create tests --color "e7e7e7" --description "Test improvements"
gh label create refactor --color "fbca04" --description "Code refactoring"
gh label create performance --color "5319e7" --description "Performance improvements"
gh label create breaking-change --color "b60205" --description "Breaking changes"
gh label create dependencies --color "0366d6" --description "Dependency updates"
gh label create stale --color "ffffff" --description "Stale issue or PR"
```

## Post-Setup Validation

After initial setup:

- [ ] Push a test commit to trigger workflows
- [ ] Verify all GitHub Actions run successfully
- [ ] Check that tests workflow completes
- [ ] Verify semantic-release creates a release (if applicable)
- [ ] Confirm CHANGELOG.md is updated
- [ ] Check CONTRIBUTORS.md is populated
- [ ] Review GitHub release notes

## Development Workflow Checklist

### Creating a Feature

- [ ] Create branch: `git checkout -b feat/feature-name`
- [ ] Make changes with conventional commits
- [ ] Run tests locally
- [ ] Push and create PR
- [ ] Wait for CI checks to pass
- [ ] Get review approval
- [ ] Squash merge to main with conventional commit message

### Fixing a Bug

- [ ] Create branch: `git checkout -b fix/bug-name`
- [ ] Fix the bug
- [ ] Add/update tests
- [ ] Commit with `fix:` prefix
- [ ] Push and create PR
- [ ] Merge after approval

### Updating Documentation

- [ ] Create branch: `git checkout -b docs/update-name`
- [ ] Update documentation
- [ ] Commit with `docs:` prefix
- [ ] Add `[skip ci]` if no release needed
- [ ] Create PR and merge

## Release Checklist

### Automatic Release (Recommended)

- [ ] Ensure all commits follow conventional format
- [ ] Push to `main` branch
- [ ] Wait for tests to pass
- [ ] Verify semantic-release creates release
- [ ] Check GitHub Releases page
- [ ] Verify CHANGELOG.md updated
- [ ] Confirm version in manifest.json updated

### Verify Release

- [ ] GitHub release created
- [ ] Release notes are accurate
- [ ] Version number is correct
- [ ] CHANGELOG.md updated
- [ ] manifest.json version updated
- [ ] Contributors acknowledged

## Maintenance Checklist

### Weekly

- [ ] Review open issues
- [ ] Respond to PRs
- [ ] Check for dependency updates
- [ ] Review security alerts

### Monthly

- [ ] Review stale issues
- [ ] Update documentation
- [ ] Check test coverage
- [ ] Review and update dependencies

### Quarterly

- [ ] Review and update CI/CD workflows
- [ ] Audit security policies
- [ ] Update contributing guidelines
- [ ] Review community health files

## Troubleshooting Checklist

### Tests Failing

- [ ] Run tests locally: `pytest tests/ -v`
- [ ] Check test output for errors
- [ ] Verify dependencies installed: `pip install -r requirements_test.txt`
- [ ] Clear cache: `rm -rf .pytest_cache`
- [ ] Check Python version matches CI

### Linting Errors

- [ ] Run linter: `ruff check .`
- [ ] Auto-fix: `ruff check . --fix`
- [ ] Format code: `ruff format .`
- [ ] Check mypy: `mypy custom_components/duco_ventilation_sun_control`

### Release Not Created

- [ ] Check commit message format
- [ ] Verify tests passed
- [ ] Look for `[skip ci]` in commits
- [ ] Check GitHub Actions logs
- [ ] Ensure GITHUB_TOKEN has permissions
- [ ] Verify semantic-release configuration

### Version Not Updated

- [ ] Check `scripts/update_version.py` is executable
- [ ] Verify manifest.json path is correct
- [ ] Check semantic-release logs
- [ ] Ensure Git config is correct

## Notes

- Always use conventional commits for automatic releases
- Use `[skip ci]` to prevent unnecessary releases
- Squash merge PRs to keep commit history clean
- Review CHANGELOG before each release
- Keep dependencies updated regularly

---

**Last Updated**: December 2025  
**Pipeline Version**: 1.0
