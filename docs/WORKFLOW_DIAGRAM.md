# Release Pipeline Visual Guide

## Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Developer Workflow                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────┐
                   │  Make Changes    │
                   │  Write Tests     │
                   └──────────────────┘
                              │
                              ▼
                   ┌──────────────────┐
                   │ Commit with      │
                   │ Conventional     │
                   │ Format           │
                   └──────────────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        ┌────────────────┐        ┌───────────────┐
        │  Push to       │        │  Create PR    │
        │  Feature       │        │  to main      │
        │  Branch        │        └───────────────┘
        └────────────────┘                 │
                 │                         │
                 └────────────┬────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CI/CD Pipeline (GitHub Actions)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────┐
                   │  Tests Workflow  │
                   └──────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
    ┌──────────┐      ┌──────────┐     ┌──────────┐
    │ Python   │      │ Linting  │     │  HACS    │
    │ 3.11/12  │      │ Ruff     │     │ Validate │
    │ Tests    │      │ MyPy     │     │ Hassfest │
    └──────────┘      └──────────┘     └──────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              ▼
                        ┌──────────┐
                        │ All Pass?│
                        └──────────┘
                         │       │
                    Yes  │       │  No
                         ▼       ▼
                    ┌────────┐  ┌────────┐
                    │Continue│  │ Stop   │
                    └────────┘  └────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Merge to main       │
              │  (PR or Direct Push) │
              └──────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Release Workflow                                │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Semantic Release    │
              │  Analyzes Commits    │
              └──────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Determine Version    │
              │ feat: → 1.x.0        │
              │ fix:  → 1.2.x        │
              │ feat!:→ x.0.0        │
              └──────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Update Files:        │
              │ • manifest.json      │
              │ • CHANGELOG.md       │
              └──────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Create Git Tag       │
              │ Commit Changes       │
              └──────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Create GitHub        │
              │ Release with Notes   │
              └──────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Update Contributors  │
              │ CONTRIBUTORS.md      │
              └──────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Post Comments on     │
              │ Related Issues/PRs   │
              └──────────────────────┘
                         │
                         ▼
                   ┌──────────┐
                   │ Complete!│
                   └──────────┘
```

## Commit Type → Version Matrix

```
┌─────────────────┬──────────────┬──────────────┬────────────────┐
│ Commit Type     │ Example      │ Version Bump │ Changelog      │
├─────────────────┼──────────────┼──────────────┼────────────────┤
│ fix:            │ fix: timeout │ 1.2.3→1.2.4  │ Bug Fixes      │
│ feat:           │ feat: sensor │ 1.2.3→1.3.0  │ Features       │
│ feat!:          │ feat!: api   │ 1.2.3→2.0.0  │ Breaking       │
│ perf:           │ perf: cache  │ 1.2.3→1.2.4  │ Performance    │
│ docs:           │ docs: readme │ 1.2.3→1.2.4  │ Docs           │
│ refactor:       │ refactor:    │ 1.2.3→1.2.4  │ Refactor       │
│ test:           │ test: add    │ No release   │ Tests          │
│ chore:          │ chore: deps  │ No release   │ (hidden)       │
│ ci:             │ ci: workflow │ No release   │ CI/CD          │
└─────────────────┴──────────────┴──────────────┴────────────────┘
```

## Quality Gates

```
                    Pull Request
                         │
                         ▼
              ┌──────────────────┐
              │ Title Validation │◄─── Must be conventional
              └──────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │ Tests (3.11/12)  │◄─── Must pass
              └──────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │ Ruff Linting     │◄─── Must pass
              └──────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │ MyPy Type Check  │◄─── Must pass
              └──────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │ HACS Validation  │◄─── Must pass
              └──────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │ Hassfest Check   │◄─── Must pass
              └──────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │ Dependency Review│◄─── No vulnerabilities
              └──────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │ CodeQL Scan      │◄─── No issues
              └──────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │ Ready to Merge!  │
              └──────────────────┘
```

## Security Pipeline

```
    ┌─────────────────────────────────────┐
    │      Security Workflows             │
    └─────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌────────┐  ┌────────┐  ┌────────┐
   │ CodeQL │  │  Dep   │  │ Secret │
   │Weekly  │  │ Review │  │ Scan   │
   └────────┘  └────────┘  └────────┘
        │           │           │
        └───────────┼───────────┘
                    ▼
          ┌──────────────────┐
          │ Security Alert?  │
          └──────────────────┘
                    │
              ┌─────┴─────┐
              ▼           ▼
         ┌────────┐  ┌────────┐
         │ Create │  │  All   │
         │ Issue  │  │  Safe  │
         └────────┘  └────────┘
```

## Development Cycle

```
Week 1-2: Feature Development
├── Create feature branch
├── Write code + tests
├── Commit with feat: prefix
└── Create PR

Week 2: Review & Testing
├── CI runs tests
├── Code review
├── Address feedback
└── Approve

Week 3: Merge & Release
├── Squash merge to main
├── Automatic version bump
├── CHANGELOG updated
├── GitHub release created
└── Contributors acknowledged

Ongoing: Maintenance
├── Bug fixes (fix: commits)
├── Documentation (docs: commits)
├── Dependency updates
└── Security patches
```

## File Organization

```
haduco/
├── .github/
│   ├── workflows/           # 7 automated workflows
│   │   ├── tests.yml       # Quality assurance
│   │   ├── release.yml     # Auto releases
│   │   ├── pr-labeler.yml  # PR management
│   │   ├── validate-pr-title.yml
│   │   ├── dependency-review.yml
│   │   ├── codeql.yml      # Security
│   │   └── stale.yml       # Maintenance
│   ├── ISSUE_TEMPLATE/     # 3 issue templates
│   └── PULL_REQUEST_TEMPLATE.md
├── custom_components/      # Your integration code
├── docs/                   # Documentation
│   ├── RELEASE_PIPELINE.md
│   ├── COMMIT_GUIDE.md
│   └── DEVELOPMENT.md
├── tests/                  # Test suite
│   ├── conftest.py
│   └── test_*.py
├── scripts/
│   └── update_version.py   # Version automation
├── .releaserc.json         # Semantic release config
├── pyproject.toml          # Python project config
├── requirements_test.txt   # Test dependencies
├── CHANGELOG.md            # Auto-generated
├── CONTRIBUTORS.md         # Auto-updated
├── CONTRIBUTING.md         # Guidelines
├── SECURITY.md             # Security policy
├── CHECKLIST.md            # Setup checklist
└── SETUP_SUMMARY.md        # This summary
```

## Status Indicators

After setup, you'll see these in GitHub:

```
All checks passed
   ├── Tests (Python 3.11)
   ├── Tests (Python 3.12)
   ├── Lint (Ruff)
   ├── Type Check (MyPy)
   ├── HACS Validation
   ├── Hassfest
   └── Dependency Review

Release v1.3.0
   ├── Tag: v1.3.0
   ├── Changelog updated
   ├── manifest.json: v1.3.0
   └── Contributors updated

Security
   ├── CodeQL: No issues
   ├── Dependencies: No vulnerabilities
   └── Secrets: None exposed
```

## Tips & Tricks

### Quick Commands
```bash
# Test everything
make test  # (if Makefile updated)
pytest tests/ && ruff check . && mypy custom_components/

# Format and lint
ruff format . && ruff check . --fix

# Create quick feature
git checkout -b feat/new-thing
git commit -m "feat: add new thing"
git push origin feat/new-thing

# Hotfix
git checkout -b fix/critical
git commit -m "fix: critical bug"
git push origin fix/critical
```

### Pro Tips
1. **Use [skip ci]** for docs-only changes
2. **Squash merge PRs** to keep history clean
3. **Review CHANGELOG** before releases
4. **Update tests** with every feature
5. **Keep commits small** and focused

---

**Your pipeline is production-ready!**
