# Release Pipeline Documentation

## Overview

This project uses a comprehensive automated release pipeline that handles testing, versioning, and contributor acknowledgment.

## Features

### 1. **Automated Testing** (`tests.yml`)
- **Multi-Python Version Testing**: Tests run on Python 3.11 and 3.12
- **Code Coverage**: Automatically uploads coverage to Codecov
- **Linting**: Uses Ruff for code quality and formatting
- **Type Checking**: MyPy ensures type safety
- **HACS Validation**: Validates Home Assistant Custom Component standards
- **Hassfest**: Official Home Assistant integration validation

### 2. **Semantic Releases** (`release.yml`)
- **Automatic Versioning**: Based on commit messages following [Conventional Commits](https://www.conventionalcommits.org/)
- **Changelog Generation**: Automatically generates and updates CHANGELOG.md
- **GitHub Releases**: Creates releases with detailed notes
- **Version Bumping**: Updates manifest.json automatically
 - **Preview Channel**: PRs labeled `preview` publish pre-releases with `-preview.N` tag suffix

### 3. **Contributor Acknowledgment**
- **Automatic Updates**: Contributors list updated on each release
- **Visual Display**: Contributors shown with avatars in CONTRIBUTORS.md
- **Release Comments**: Thanks contributors in release notes

### 4. **Additional Workflows**
- **PR Labeling**: Automatic labels based on conventional commit types
- **Dependency Review**: Security scanning for dependencies
- **CodeQL Analysis**: Security vulnerability scanning
- **Stale Issue Management**: Automatically manages inactive issues/PRs

## 📝 Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>: <description>

[optional body]

[optional footer]
```

### Types

| Type | Description | Version Bump | Changelog Section |
|------|-------------|--------------|-------------------|
| `feat:` | New feature | Minor (0.x.0) | Features |
| `fix:` | Bug fix | Patch (0.0.x) | Bug Fixes |
| `perf:` | Performance improvement | Patch | Performance |
| `docs:` | Documentation only | Patch | Documentation |
| `refactor:` | Code refactoring | Patch | Refactoring |
| `test:` | Adding tests | None | Tests |
| `build:` | Build system changes | None | Build |
| `ci:` | CI/CD changes | None | CI/CD |
| `chore:` | Maintenance | None | (hidden) |

### Breaking Changes

Add `!` after type or use `BREAKING CHANGE:` footer for major version bump:

```
feat!: change configuration structure

BREAKING CHANGE: Configuration format has changed
```

## Release Process

### Automatic (Recommended)

1. **Create commits** using conventional format:
   ```bash
   git commit -m "feat: add new sensor type"
   git commit -m "fix: resolve sensor update issue"
   ```

2. **Push to main**:
   ```bash
   git push origin main
   ```

3. **Automated actions**:
   - Tests run automatically
   - If tests pass, semantic-release analyzes commits
   - Version is determined automatically
   - Changelog is generated
   - manifest.json is updated
   - GitHub release is created
   - Contributors are acknowledged

### Preview Releases

To publish a preview version for early testing, add the `preview` label to your PR.
This publishes a **GitHub pre-release** tagged like `v1.2.3-preview.1`.

### Version Examples

Starting version: `1.2.0`

| Commits | New Version | Reason |
|---------|-------------|--------|
| `fix: bug fix` | `1.2.1` | Patch release |
| `feat: new feature` | `1.3.0` | Minor release |
| `feat!: breaking change` | `2.0.0` | Major release |
| `docs: update readme` | `1.2.1` | Patch release |
| `fix: bug` + `feat: feature` | `1.3.0` | Highest bump wins |

## Testing Locally

### Run tests
```bash
pytest tests/ --cov=custom_components/duco_ventilation_sun_control
```

### Run linting
```bash
ruff check .
ruff format --check .
mypy custom_components/duco_ventilation_sun_control
```

### Run all checks
```bash
# Run linting
ruff check .
ruff format .

# Run type checking
mypy custom_components/duco_ventilation_sun_control

# Run tests
pytest tests/ -v
```

## Pull Request Workflow

1. **Create feature branch**:
   ```bash
   git checkout -b feat/my-new-feature
   ```

2. **Make changes** with conventional commits

3. **Push and create PR**:
   - PR template will guide you
   - PR will be auto-labeled based on title
   - All tests must pass

4. **Merge to main**:
   - Squash merge recommended
   - Ensure merge commit follows conventional format

## Required Secrets

The workflows use `GITHUB_TOKEN` which is automatically provided by GitHub Actions. No additional secrets needed!

## Badges

Add these to your README.md:

```markdown
[![Tests](https://github.com/stuartp44/haduco/actions/workflows/tests.yml/badge.svg)](https://github.com/stuartp44/haduco/actions/workflows/tests.yml)
[![Release](https://github.com/stuartp44/haduco/actions/workflows/release.yml/badge.svg)](https://github.com/stuartp44/haduco/actions/workflows/release.yml)
[![codecov](https://codecov.io/gh/stuartp44/haduco/branch/main/graph/badge.svg)](https://codecov.io/gh/stuartp44/haduco)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
```

## Maintenance

### Disable Automatic Releases

Add `[skip ci]` to commit message:
```bash
git commit -m "chore: update docs [skip ci]"
```

### Manual Release

Releases are triggered automatically on push to main, but you can also trigger manually from the Actions tab.

## Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Semantic Release](https://semantic-release.gitbook.io/)
- [GitHub Actions](https://docs.github.com/en/actions)
