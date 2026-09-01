# Git Mastery — Command Reference (8 Scenarios)

---

## Scenario 1 — Launch Your First Python Service

```bash
# Configure Git identity (once per machine, or use --local for this repo only)
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# Create and enter project folder
mkdir log-inspector && cd log-inspector

# Initialize repository
git init

# Create folder structure
mkdir src tests docs
touch src/.gitkeep tests/.gitkeep docs/.gitkeep

# Create .gitignore (Python-friendly)
cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
env/
.env
.pytest_cache/
.mypy_cache/
dist/
build/
*.log
.DS_Store
.idea/
.vscode/
EOF

# Create README
cat > README.md << 'EOF'
# Log Inspector

A lightweight Python utility for parsing, filtering, and analyzing log files.

## Status
🚧 In active development

## Structure
- `src/` — application source code
- `tests/` — unit tests
- `docs/` — documentation
EOF

# Stage and commit
git add .
git commit -m "Initial commit: project scaffolding for Log Inspector"

# Create GitHub repo (using GitHub CLI)
gh repo create log-inspector --public --source=. --remote=origin

# Push
git branch -M main
git push -u origin main
```

**No GitHub CLI?** Create the repo manually on github.com, then:
```bash
git remote add origin https://github.com/<username>/log-inspector.git
git branch -M main
git push -u origin main
```

---

## Scenario 2 — Build a Feature Without Breaking Production

```bash
# Clone the project
git clone https://github.com/<username>/log-inspector.git
cd log-inspector

# Create a feature branch
git checkout -b feature/email-validation

# Create the module
cat > src/email_validator.py << 'EOF'
import re

EMAIL_REGEX = re.compile(r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$")

def is_valid_email(email: str) -> bool:
    """Return True if the given string is a valid email address."""
    return bool(EMAIL_REGEX.match(email))
EOF

git add src/email_validator.py
git commit -m "Add email validation function"

# Add tests (second meaningful commit)
cat > tests/test_email_validator.py << 'EOF'
from src.email_validator import is_valid_email

def test_valid_email():
    assert is_valid_email("user@example.com") is True

def test_invalid_email():
    assert is_valid_email("not-an-email") is False
EOF

git add tests/test_email_validator.py
git commit -m "Add unit tests for email validator"

# Push the branch
git push -u origin feature/email-validation

# Open a Pull Request
gh pr create --title "Add Email Validation Module" \
  --body "Introduces is_valid_email() with unit tests. Ready for review."
```

**Why avoid committing directly to `main`?**
- `main` should always be deployable — direct commits risk breaking production instantly.
- Pull Requests enable code review, catching bugs and design issues before merge.
- CI checks (tests, linting) typically gate PRs, not direct pushes.
- It creates an audit trail and a rollback point isolated from unreviewed work.

---

## Scenario 3 — Clean Up History with Interactive Rebase

Starting history (oldest → newest): `fix`, `oops`, `another fix`, `testing`, `final`

```bash
# Rebase the last 5 commits interactively
git rebase -i HEAD~5
```

In the editor that opens, you'll see:
```
pick a1b2c3d fix
pick e4f5g6h oops
pick i7j8k9l another fix
pick m1n2o3p testing
pick q4r5s6t final
```

Change it to **squash** everything into the first commit, then reword:
```
pick a1b2c3d fix
squash e4f5g6h oops
squash i7j8k9l another fix
squash m1n2o3p testing
squash q4r5s6t final
```

Save and close — Git will then open a second editor to combine commit messages. Replace all of it with:
```
Add Email Validation Module

Add Unit Tests
```

Or, to produce **two separate clean commits** instead of one:
```
pick a1b2c3d fix
squash e4f5g6h oops
squash i7j8k9l another fix
reword m1n2o3p testing
squash q4r5s6t final
```
Then rename the two resulting commits to `Add Email Validation Module` and `Add Unit Tests` when prompted.

```bash
# Push the rewritten history
git push --force-with-lease origin feature/email-validation
```

**When is force push safe?**
- ✅ Safe on your own feature branch that no one else has pulled/based work on.
- ✅ Use `--force-with-lease` instead of `--force` — it fails safely if someone else pushed new commits you don't have.
- ❌ Never force-push to `main`/shared branches after others have pulled it.
- ❌ Never force-push if teammates have already checked out your branch.

---

## Scenario 4 — Resolve a Merge Conflict

```bash
# Switch to target branch and merge
git checkout main
git pull origin main
git merge feature/email-validation  
```

If there's a conflict, Git marks the file like this:

```python
<<<<<<< HEAD
def is_valid_email(email):
    return "@" in email
=======
def is_valid_email(email):
    return EMAIL_REGEX.match(email) is not None
>>>>>>> feature/email-validation
```

Resolve manually:
```bash
# Edit the file, keep the correct logic, remove markers
nano src/email_validator.py
```

```python
def is_valid_email(email):
    return EMAIL_REGEX.match(email) is not None
```

```bash
# Verify the code works
python -m pytest tests/

# Mark as resolved
git add src/email_validator.py

# Complete the merge
git commit -m "Merge feature/email-validation: resolve validator conflict"

# Push
git push origin main
```

**What do the conflict markers mean?**
- `<<<<<<< HEAD` — start of **your current branch's** version.
- `=======` — divider between the two conflicting versions.
- `>>>>>>> feature/email-validation` — end marker, labeled with the **incoming branch's** version.

---

## Scenario 5 — "Oops!" Recovery Challenge

**1. Modified a file accidentally (unstaged changes)**
```bash
git restore src/email_validator.py
# Older Git: git checkout -- src/email_validator.py
```
→ Discards uncommitted changes, restores file to last commit. Use when you *don't* want the edit at all.

**2. Staged the wrong file**
```bash
git restore --staged src/email_validator.py
# Older Git: git reset src/email_validator.py
```
→ Unstages the file but **keeps your edits** in the working directory.

**3. Committed something by mistake**

*If not pushed yet, and you want to undo the commit but keep the changes:*
```bash
git reset --soft HEAD~1
```

*If you want to undo the commit and discard the changes entirely:*
```bash
git reset --hard HEAD~1
```

*If already pushed and shared with others (safe, non-destructive):*
```bash
git revert HEAD
```
→ Creates a new commit that undoes the previous one, preserving history — the correct choice for shared branches.

| Situation | Command | Data Loss? |
|---|---|---|
| Unstaged edit | `git restore <file>` | Yes, intentional |
| Wrong file staged | `git restore --staged <file>` | No |
| Bad commit (local, unpushed) | `git reset --soft HEAD~1` | No |
| Bad commit (want to discard) | `git reset --hard HEAD~1` | Yes, intentional |
| Bad commit (already pushed) | `git revert HEAD` | No |

---

## Scenario 6 — Ship Version 1.0

```bash
# Verify project status
git status
git log --oneline -5

# Create an annotated tag
git tag -a v1.0.0 -m "Release v1.0.0: initial stable version of Log Inspector"

# Push the tag
git push origin v1.0.0

# Create a GitHub Release (via CLI)
gh release create v1.0.0 \
  --title "v1.0.0 — First Stable Release" \
  --notes "## What's New
- Core log parsing engine
- Email validation module
- Full unit test coverage
- CLI entry point for log inspection

This is the first production-ready release of Log Inspector."
```

**No GitHub CLI?** Go to your repo → Releases → "Draft a new release" → select tag `v1.0.0` → add notes → Publish.

---

## Scenario 7 — Become a Git Detective

```bash
# Who last modified config.py (and when)
git log -p -- config.py
git log --follow -- config.py

# Line-by-line blame: who changed each line, and when
git blame config.py

# Which commit changed a particular line (e.g. line 42)
git blame -L 42,42 config.py

# Difference between two commits
git diff <commit1> <commit2>
git diff <commit1> <commit2> -- config.py   # scoped to one file

# Files modified in a specific commit
git show --stat <commit-hash>
git show --name-only <commit-hash>

# Visual branch history
git log --oneline --graph --all --decorate
```

**Bonus — the command every team lead loves during debugging:**
```bash
git bisect start
git bisect bad                # current commit is broken
git bisect good <old-commit>  # known-good commit
# Git checks out a midpoint — test it, then:
git bisect good   # or
git bisect bad
# repeat until Git identifies the exact commit that introduced the bug
git bisect reset
```
`git bisect` binary-searches history automatically to pinpoint the exact commit that introduced a bug — far faster than manually checking commits one by one.

---

## Scenario 8 — Emergency Production Fix

```bash
# 1. Save unfinished work
git stash push -m "WIP: half-finished feature work"

# Bonus: list saved stashes before restoring
git stash list

# 2. Switch branches to fix production
git checkout main
git pull origin main
git checkout -b hotfix/login-issue

# 3. Fix the production issue
nano src/auth.py
git add src/auth.py

# 4. Commit the fix
git commit -m "Fix: resolve login failure caused by token expiry bug"
git push -u origin hotfix/login-issue
# (open PR, merge, deploy as per team process)

# 5. Return to your feature branch
git checkout feature/email-validation

# 6. Restore your unfinished work
git stash pop
# (use 'git stash apply' instead if you want to keep the stash entry as backup)

# 7. Continue development
git status   # confirm your WIP changes are back
```

**Why `stash` here?** It lets you cleanly park uncommitted work without a throwaway commit, switch context immediately for the emergency, and restore your exact working state afterward — nothing lost, nothing mixed together.
