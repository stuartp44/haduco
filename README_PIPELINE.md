# Release Pipeline - Complete Setup

## What Has Been Created

I've created a **comprehensive, production-ready release pipeline** for your Home Assistant Custom Component with:

### 30+ Files Created

#### GitHub Actions Workflows (7 workflows)
1. **tests.yml** - Multi-version testing, linting, type checking, HACS/Hassfest validation
2. **release.yml** - Automated semantic versioning and releases
3. **pr-labeler.yml** - Automatic PR labeling
4. **validate-pr-title.yml** - Validates conventional commit format
5. **dependency-review.yml** - Security scanning for dependencies
6. **codeql.yml** - Weekly security vulnerability scanning
7. **stale.yml** - Manages inactive issues and PRs

#### Documentation (8 files)
- **CONTRIBUTING.md** - Comprehensive contribution guidelines
- **CONTRIBUTORS.md** - Auto-updated contributor list
- **SECURITY.md** - Security policy
- **CHANGELOG.md** - Auto-generated changelog
- **CHECKLIST.md** - Complete setup and maintenance checklists
- **SETUP_SUMMARY.md** - Detailed setup documentation
- **docs/RELEASE_PIPELINE.md** - Full pipeline documentation
- **docs/COMMIT_GUIDE.md** - Quick reference for commit messages
- **docs/DEVELOPMENT.md** - Development guide
- **docs/WORKFLOW_DIAGRAM.md** - Visual workflow guide

#### Templates (4 files)
- Bug report template
- Feature request template
- Documentation template
- Pull request template

#### Configuration (4 files)
- **.releaserc.json** - Semantic release configuration
- **pyproject.toml** - Python project config with Ruff/MyPy rules
- **requirements_test.txt** - Testing dependencies
- **.gitignore** - Updated with pipeline files

#### Testing (3 files)
- **tests/__init__.py**
- **tests/conftest.py** - Pytest fixtures
- **tests/test_init.py** - Sample integration tests

#### Scripts (1 file)
- **scripts/update_version.py** - Automatic version updating

---

## Key Features

### 1. **Semantic Versioning** 
Automatic version bumping based on commit messages:
- `fix:` → Patch (1.2.0 → 1.2.1)
- `feat:` → Minor (1.2.0 → 1.3.0)
- `feat!:` or `BREAKING CHANGE:` → Major (1.2.0 → 2.0.0)

### 2. **Automated Testing**
- Multi-Python version testing (3.11, 3.12)
- Code coverage with Codecov
- Linting with Ruff
- Type checking with MyPy
- HACS validation
- Home Assistant Hassfest validation

### 3. **Automated Releases**
Every push to `main`:
1. Runs all tests
2. Analyzes commits
3. Updates manifest.json
4. Generates CHANGELOG.md
5. Creates Git tag
6. Creates GitHub release
7. Updates contributors

### 4. **Contributor Acknowledgment**
- Automatic CONTRIBUTORS.md updates
- Visual display with avatars
- Thank you messages in releases

### 5. **Security**
- CodeQL security scanning
- Dependency vulnerability checks
- Secret scanning
- Security policy

---

## Next Steps

### 1. **Review the Files**
```bash
# Check what was created
ls -la .github/workflows/
ls -la docs/
ls -la tests/
cat SETUP_SUMMARY.md
```

### 2. **Commit Everything**
```bash
git add .
git commit -m "ci: add comprehensive release pipeline with semantic versioning and testing

- Add GitHub Actions workflows for testing and releases
- Configure semantic-release for automated versioning
- Set up contributor acknowledgment system
- Add comprehensive documentation and templates
- Configure Ruff, MyPy, and pytest
- Add security scanning with CodeQL
- Create contribution guidelines"

git push origin main
```

### 3. **Enable GitHub Features** (Optional but Recommended)

#### In GitHub Repository Settings:
1. **Actions** → Enable workflows
2. **Branches** → Add branch protection for `main`:
   - ✅ Require status checks to pass
   - ✅ Require pull request reviews
   - ✅ Require branches to be up to date
3. **Issues** → Enable issues
4. **Discussions** → Enable (optional)

#### Create Labels:
```bash
# Using GitHub CLI (if installed)
gh label create bug --color "d73a4a" --description "Something isn't working"
gh label create enhancement --color "a2eeef" --description "New feature"
gh label create documentation --color "0075ca" --description "Documentation"
gh label create tests --color "e7e7e7" --description "Tests"
gh label create breaking-change --color "b60205" --description "Breaking change"
```

### 4. **Optional: Set Up Codecov**
1. Visit https://codecov.io
2. Sign in with GitHub
3. Add your repository
4. Coverage reports will appear in PRs automatically

### 5. **Watch the Magic Happen!**
After pushing:
1. Go to **Actions** tab on GitHub
2. Watch workflows run
3. Check **Releases** for new release
4. View updated CHANGELOG.md

---

## Quick Reference

### Commit Message Examples
```bash
# Feature (minor version bump)
git commit -m "feat: add new sensor type"

# Bug fix (patch version bump)
git commit -m "fix: resolve connection timeout"

# Breaking change (major version bump)
git commit -m "feat!: redesign configuration structure"

# Documentation (patch version bump)
git commit -m "docs: update README examples"

# No release
git commit -m "chore: update dependencies"
git commit -m "test: add unit tests"
```

### Testing Locally
```bash
# Run all tests
pytest tests/ --cov=custom_components/duco_ventilation_sun_control

# Linting
ruff check .
ruff format .

# Type checking
mypy custom_components/duco_ventilation_sun_control
```

### Creating a Pull Request
```bash
git checkout -b feat/my-feature
# Make changes
git commit -m "feat: add my feature"
git push origin feat/my-feature
# Open PR on GitHub
```

---

## Documentation

All documentation is available in these files:

| File | Description |
|------|-------------|
| [SETUP_SUMMARY.md](SETUP_SUMMARY.md) | Complete setup summary |
| [CHECKLIST.md](CHECKLIST.md) | Setup and maintenance checklists |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |
| [docs/RELEASE_PIPELINE.md](docs/RELEASE_PIPELINE.md) | Pipeline details |
| [docs/COMMIT_GUIDE.md](docs/COMMIT_GUIDE.md) | Commit message guide |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Development guide |
| [docs/WORKFLOW_DIAGRAM.md](docs/WORKFLOW_DIAGRAM.md) | Visual workflows |

---

## What Happens Next

### First Push to Main
```
1. Tests run (Python 3.11 & 3.12)
2. Linting checks (Ruff, MyPy)
3. HACS & Hassfest validation
4. Semantic-release analyzes commits
5. Creates new version (e.g., 1.3.0)
6. Updates manifest.json
7. Generates CHANGELOG.md
8. Creates GitHub release
9. Updates CONTRIBUTORS.md
```

### Subsequent Commits
Each push to main will:
- Run all quality checks
- Automatically determine version
- Create release if needed
- Keep changelog current
- Acknowledge contributors

---

## Pro Tips

1. **Always use conventional commits** - Required for automatic releases
2. **Run tests locally first** - Saves CI time
3. **Small, focused commits** - Easier to review and track
4. **Squash merge PRs** - Keeps main branch clean
5. **Use [skip ci]** for docs-only changes that don't need a release

---

## Troubleshooting

### Tests Fail
```bash
pytest tests/ -v  # See detailed output
pip install -r requirements_test.txt --force-reinstall
```

### Linting Errors
```bash
ruff check . --fix  # Auto-fix
ruff format .       # Format code
```

### Release Doesn't Trigger
- Check commit message format
- Verify tests passed
- Look for `[skip ci]` in message
- Check GitHub Actions logs

---

## You're All Set!

Your repository now has:
- Automated testing
- Semantic versioning
- Auto-generated changelogs
- Contributor acknowledgment
- Security scanning
- Quality gates
- Comprehensive documentation

**Just commit and push to see it in action!**

---

## Pipeline Stats

After setup, you can add these badges to your README:

```markdown
[![Tests](https://github.com/stuartp44/haduco/actions/workflows/tests.yml/badge.svg)](https://github.com/stuartp44/haduco/actions/workflows/tests.yml)
[![Release](https://github.com/stuartp44/haduco/actions/workflows/release.yml/badge.svg)](https://github.com/stuartp44/haduco/actions/workflows/release.yml)
[![codecov](https://codecov.io/gh/stuartp44/haduco/branch/main/graph/badge.svg)](https://codecov.io/gh/stuartp44/haduco)
```

---

**Questions?** Check the documentation or open an issue!

**Happy coding!**
