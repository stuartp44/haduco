# Quick Reference: Commit Message Guide

## Format
```
<type>(<scope>): <subject>
```

## Common Examples

### Features (Minor Release - 0.x.0)
```bash
git commit -m "feat: add temperature sensor support"
git commit -m "feat(sensor): add humidity readings"
git commit -m "feat(config): add auto-discovery option"
```

### Bug Fixes (Patch Release - 0.0.x)
```bash
git commit -m "fix: resolve sensor timeout issue"
git commit -m "fix(coordinator): handle connection errors"
git commit -m "fix(select): correct entity state updates"
```

### Breaking Changes (Major Release - x.0.0)
```bash
git commit -m "feat!: redesign configuration structure"

# OR with footer
git commit -m "feat: change sensor naming convention

BREAKING CHANGE: Sensor entity IDs have changed. Users must reconfigure."
```

### Documentation
```bash
git commit -m "docs: update README with examples"
git commit -m "docs(api): add sensor documentation"
```

### Code Improvements (No version bump)
```bash
git commit -m "chore: update dependencies"
git commit -m "ci: improve test workflow"
git commit -m "test: add sensor unit tests"
git commit -m "refactor: simplify coordinator logic"
```

## Multi-line Commits
```bash
git commit -m "feat: add new ventilation modes

- Add auto mode
- Add sleep mode
- Add boost mode

This enhances user control over ventilation settings."
```

## Quick Workflow

1. **Make changes**
2. **Stage files**: `git add .`
3. **Commit with conventional format**: `git commit -m "feat: your feature"`
4. **Push**: `git push`
5. **Release happens automatically!** 🎉

## What NOT to Do

❌ `git commit -m "updated files"`
❌ `git commit -m "fixes"`
❌ `git commit -m "WIP"`
❌ `git commit -m "changes"`

✅ `git commit -m "feat: add new sensor type"`
✅ `git commit -m "fix: resolve update delay"`
✅ `git commit -m "docs: improve installation guide"`

## Scopes (Optional)

Use scopes to specify what part was modified:
- `sensor` - Sensor platform
- `select` - Select platform
- `config` - Configuration flow
- `coordinator` - Data coordinator
- `api` - API client
- `docs` - Documentation

Example: `git commit -m "fix(sensor): correct temperature conversion"`
