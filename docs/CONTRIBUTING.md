# 📋 Commit and Branch Standards

> Official commit and branch naming guide for the 6th Semester API.

**Date:** February 28, 2026
**Version:** 1.1
**Status:** ✅ Approved

---

[Back to main README](../README.md#date-sprint-backlog)

---

## 📑 Table of Contents

1. [Overview](#overview)
2. [Commit Standards](#commit-standards)
3. [Branch Standards](#branch-standards)
4. [Full Flow](#full-flow)
5. [Automations](#automations)
6. [Practical Examples](#practical-examples)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview <a id="overview"></a>

This project uses **Conventional Commits** + **Git Flow** to maintain a clean and traceable code history.

### Objectives

✅ Readable and organized commit history
✅ Changelog automation
✅ Clear traceability: issues → branches → commits → pull requests
✅ Easier code review and onboarding for new developers
✅ DevOps with full workflow visibility

---

## 📝 Commit Standards <a id="commit-standards"></a>

### Convention: Conventional Commits

**Format:**
```
<type>(<scope>): <description> ← REQUIRED

[optional body]

#<issue-number>   ← REQUIRED
```

### Accepted Types

| Type | Emoji | Usage | Example |
|------|-------|-------|---------|
| `feat` | ✨ | New feature | `feat(auth): implement JWT` |
| `fix` | 🐛 | Bug fix | `fix(api): fix 500 error` |
| `docs` | 📚 | Documentation | `docs: update README` |
| `style` | 🎨 | Formatting/style (no logic) | `style: fix indentation` |
| `refactor` | ♻️ | Code refactoring | `refactor(auth): reorganize logic` |
| `perf` | ⚡ | Performance improvements | `perf(api): optimize search` |
| `test` | 🧪 | Tests | `test(auth): add JWT tests` |
| `chore` | 🔧 | Build, CI, dependencies | `chore: update deps` |
| `ci` | 🔄 | Continuous Integration | `ci: configure GitHub Actions` |
| `revert` | ↩️ | Revert commit | `revert: revert 'feat(auth)'` |

### Detailed Structure

#### 1️⃣ **Type** (Required)
Must be one of the types listed above.

```bash
✅ feat(auth): ...
❌ feature(auth): ...
❌ new(auth): ...
```

#### 2️⃣ **Scope** (Optional, but recommended)
The affected area or module.

```bash
✅ feat(auth): implement JWT
✅ feat(users): add validation
✅ fix(api): fix response
❌ feat: implement JWT  (no scope)
```

#### 3️⃣ **Description** (Required)
- Start with lowercase
- Use imperative mood (not past tense)
- No trailing period

```bash
✅ feat(auth): implement JWT login
❌ feat(auth): Implement JWT login
❌ feat(auth): implemented JWT login
❌ feat(auth): implement JWT login.
```

#### 4️⃣ **Body** (Optional — for details)
Separated by a blank line. Use to explain the "why".

```bash
feat(auth): implement JWT

- Add JWT for better security
- Implement refresh token
- Validate token in middlewares

#123
```

#### 5️⃣ **Footer** (REQUIRED)

> ⚠️ The issue reference is **mandatory** in every commit. The Git Hook will **reject** any commit missing it.

All three formats are accepted:

```bash
Closes #123    # automatically closes the issue on merge
Ref: #123      # references without closing
#123           # shorthand reference
```

**Example:**
```bash
fix(auth): fix token expiry

Token now expires correctly.

Ref: #456
```

### Automatic Validation

✅ **Git Hook enabled:** `.githooks/commit-msg`

The hook rejects commits that:
- Have an invalid type
- Have a missing or malformed description
- Are **missing an issue reference** in the footer (`#number`, `Closes #number`, or `Ref: #number`)

```
╔════════════════════════════════════════════════╗
║  ❌ ERROR: Invalid commit!                     ║
╚════════════════════════════════════════════════╝

Your message: "add login feature"

❌ Commit REJECTED. Fix and try again:
   git commit --amend -m "feat(auth): implement login

   #42"
```

---

## 🌳 Branch Standards <a id="branch-standards"></a>

### Convention: Type + Issue Number + Description

**Format:**
```
<type>/<number>-<kebab-case-description>
```

### Branch Types

| Type | Usage | Example |
|------|-------|---------|
| `feature` | New feature | `feature/123-add-jwt-login` |
| `bugfix` | Bug fix | `bugfix/456-fix-auth` |
| `hotfix` | Critical fix in production | `hotfix/789-api-crash` |
| `docs` | Documentation | `docs/234-setup-guide` |
| `refactor` | Refactoring | `refactor/567-reorganize-auth` |
| `perf` | Performance | `perf/890-optimize-queries` |
| `test` | Tests | `test/345-add-jwt-tests` |
| `chore` | Build/Config | `chore/678-update-deps` |

### Rules

✅ **A valid branch MUST contain:**
- A valid type
- The issue number (mandatory for traceability)
- A kebab-case description (lowercase, hyphens)

```bash
✅ feature/123-add-authentication
✅ bugfix/456-fix-login-error
❌ feature/add-authentication       (no number)
❌ feature/123-AddAuthentication    (CamelCase)
❌ feature/123-add_authentication   (underscore)
```

### Automatic Creation

✅ **Workflow enabled:** `auto-create-branch.yml`

When you create an issue:

1. **Add a label** (`type:feature`, `type:bug`, etc.)
2. **GitHub Action triggers automatically**
3. Branch is created: `type/123-description`
4. A comment with the checkout command is posted on the issue

```bash
git checkout feature/123-add-login
```

---

## 🔄 Full Flow <a id="full-flow"></a>

```
┌──────────────────────────────────────────────────────┐
│ 1️⃣  CREATE ISSUE ON GITHUB                          │
│                                                      │
│  Title: Implement email validation                   │
│  Number: #42                                         │
│  Label: type:feature                                 │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│ 2️⃣  AUTO-CREATE-BRANCH WORKFLOW                      │
│                                                      │
│  ✅ Extracts number: 42                              │
│  ✅ Extracts type: feature                           │
│  ✅ Converts to kebab-case                           │
│  ✅ Creates branch: feature/42-implement-validation  │
│  ✅ Posts checkout command as issue comment           │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│ 3️⃣  DEVELOP LOCALLY                                  │
│                                                      │
│  $ git checkout feature/42-implement-validation      │
│  $ # Make changes                                    │
│  $ git add .                                         │
│  $ git commit -m "feat(validation): add email check  │
│                                                      │
│  #42"                                                │
│                                                      │
│  ✅ commit-msg hook validates type + footer          │
│  ✅ If invalid, commit is rejected immediately       │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│ 4️⃣  PUSH                                             │
│                                                      │
│  $ git push origin feature/42-implement-validation   │
│                                                      │
│  ✅ pre-push hook validates branch name              │
│  ✅ pre-push hook validates all commit messages      │
│  ✅ If invalid, push is rejected before reaching     │
│     GitHub                                           │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│ 5️⃣  OPEN PULL REQUEST                                │
│                                                      │
│  Branch: feature/42-implement-validation             │
│  Title:  feat(validation): add email validation      │
│  Body:   Implements email validation on registration │
│                                                      │
│          Closes #42                                  │
│                                                      │
│  ✅ Auto-fill workflow detects issue #42             │
│  ✅ Informative comment added                        │
│  ✅ commitlint GitHub Action validates all commits   │
│  ✅ Ruleset blocks merge if any check fails          │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│ 6️⃣  REVIEW & MERGE                                   │
│                                                      │
│  ✅ Code review                                      │
│  ✅ Tests passing                                    │
│  ✅ Approve PR                                       │
│  ✅ Merge into main/develop                          │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│ 7️⃣  AUTOMATIC CLOSURE                                │
│                                                      │
│  ✅ GitHub detects "Closes #42" in the PR            │
│  ✅ Issue #42 closes automatically                   │
│  ✅ Branch can be deleted                            │
│  ✅ Complete traceable history                       │
└──────────────────────────────────────────────────────┘
```

---

## 🤖 Automations <a id="automations"></a>

### Validation Layers

This project enforces commit standards in two complementary layers:

| Layer | Tool | When | Can be bypassed? |
|-------|------|------|-----------------|
| Local | `commit-msg` hook | On `git commit` | Yes, with `--no-verify` |
| Local | `pre-push` hook | On `git push` | Yes, with `--no-verify` |
| Remote | GitHub Actions + Ruleset | On Pull Request | ❌ No |

> The remote layer is the final guarantee — even if a developer bypasses local hooks, the PR cannot be merged without passing all checks.

---

### 1. `commit-msg` Hook

**File:** `.githooks/commit-msg`

- Validates commit format at the time of `git commit`
- Rejects commits with an invalid type
- Rejects commits **missing an issue reference** in the footer (`#number`, `Closes #`, or `Ref: #`)
- Shows detailed error messages with examples

---

### 2. `post-checkout` Hook

**File:** `.githooks/post-checkout`

- Validates branch name when switching branches
- Warning only — does not block

---

### 3. `pre-push` Hook

**File:** `.githooks/pre-push`

Runs automatically on every `git push` and validates **two things**:

**3.1 Branch name**
- Prevents pushing branches with invalid names
- Shows accepted formats and rename instructions

**3.2 Commit messages**
- Validates **all commits** that haven't been pushed to remote yet
- Rejects pushes if any commit has an invalid type or is missing an issue reference
- Correctly handles first push of a new branch
- Ignores merge commits automatically
- Shows which commit failed and how to fix it with `rebase -i`

```
╔════════════════════════════════════════════════════════════════╗
║     ❌ ERROR: Invalid commit message!                         ║
╚════════════════════════════════════════════════════════════════╝

Commit: a1b2c3d
Message: "add login feature"

💡 Solution:
   git rebase -i a1b2c3d^
   # mark the commit as 'reword' and fix the message
```

---

### 4. `commitlint` GitHub Action

**File:** `.github/workflows/commitlint.yml`

Triggers on every Pull Request (`opened`, `reopened`, `synchronize`).

- Validates all commits in the PR against `.commitlintrc.json`
- Fails the check if any commit is invalid
- Combined with the Branch Ruleset, **blocks merge** until fixed

---

### 5. Branch Ruleset

**Configured on GitHub** → Settings → Rules → Rulesets

Applied to `main` and `sprint-*` branches:

- ✅ Requires PR before merging (no direct push)
- ✅ Requires `commitlint` check to pass
- ✅ Cannot be bypassed, even by admins

---

### 6. `auto-create-branch` Workflow

**File:** `.github/workflows/auto-create-branch.yml`

Triggers: When an issue is created or labeled

```yaml
on:
  issues:
    types: [opened, labeled]
```

**Actions:**
- Extracts issue number and type
- Creates branch automatically
- Posts a comment on the issue
- Uses labels `type:feature`, `type:bug`, etc.

---

### 7. `auto-fill-pr-from-branch` Workflow

**File:** `.github/workflows/auto-fill-pr-from-branch.yml`

Triggers: When a PR is opened

**Actions:**
- Extracts issue number from branch name
- Detects change type
- Pre-fills `Closes #123`
- Adds an informative comment

---

## 💡 Practical Examples

### Example 1: Login Feature

**Issue created:**
```
Title: [FEATURE] - Implement JWT authentication
Number: #42
Label: type:feature
```

**Branch created automatically:**
```
feature/42-implement-jwt-authentication
```

**Locally:**
```bash
# Checkout branch
git checkout feature/42-implement-jwt-authentication

# Make changes...

# Commit following the standard
git commit -m "feat(auth): implement JWT

- Add JWT for authentication
- Implement refresh token
- Validate token in middlewares

Ref: #42"

# Push (pre-push hook validates branch name + commits)
git push origin feature/42-implement-jwt-authentication
```

**Pull Request:**
```markdown
## Description
JWT authentication implementation

## Type
Feature (New functionality)

## Tests
- [x] Unit tests
- [x] Integration tests

Closes #42
```

**Result:**
- PR is merged
- GitHub detects `Closes #42`
- Issue #42 closes automatically ✅

---

### Example 2: API Bugfix

**Issue created:**
```
Title: [BUG] - 500 error on login
Number: #456
Label: type:bug
```

**Branch created:**
```
bugfix/456-500-error-login
```

**Commit:**
```bash
git commit -m "fix(api): fix 500 error on login

Error occurred when email had trailing spaces.
Now we trim() before validating.

Ref: #456"
```

**PR with `Closes #456`** → Issue closed on merge ✅

---

### Example 3: Production Hotfix

**Issue created:**
```
Title: [HOTFIX] - API is down
Number: #789
Label: type:hotfix, urgent
```

**Branch created:**
```
hotfix/789-api-down
```

⚠️ **Maximum priority!** Fast merge after testing.

---

## ✅ Best Practices

### For Developers

#### ✅ DO's

```bash
# ✅ Small, focused commit with required footer
git commit -m "feat(auth): implement JWT

#42"

# ✅ Descriptive message with body and footer
git commit -m "feat(auth): implement JWT

Add stateless authentication with JWT
to improve API security.

Ref: #42"

# ✅ Correctly named branch
git checkout -b feature/123-description

# ✅ One feature per branch
```

#### ❌ DON'Ts

```bash
# ❌ Generic messages
git commit -m "fix stuff"
git commit -m "update"

# ❌ Missing issue reference (will be REJECTED by hook)
git commit -m "feat(auth): implement login"

# ❌ Giant commits (split into smaller ones)

# ❌ Wrong branch names
git checkout -b my-feature
git checkout -b minha_feature
git checkout -b Feature/123

# ❌ Multiple features in a single branch (create separate branches)

# ❌ Bypassing hooks (the remote layer will still block you)
git commit --no-verify -m "bad message"
git push --no-verify
```

### For Scrum Masters

#### 📊 Traceability

- **Issue #123** → Branch `feature/123-*` → PR → Merge
- Every issue has complete tracking
- Clear history on GitHub

#### 📈 Metrics

- **Lead Time:** Time from commit to production
- **Deployment Frequency:** How many times per day/week
- **Change Failure Rate:** Failure rate in production
- **MTTR:** Time to recover from failures

#### 📋 Reports

```bash
# View commits by type
git log --oneline | grep "^feat"
git log --oneline | grep "^fix"

# View closed issues
git log --grep "Closes #"

# View branch history
git log feature/123-description
```

### For DevOps

#### 🔄 CI/CD

- **Trigger:** Commit on branch → CI runs
- **Validations:** Lint, Tests, Build, Security Scan
- **Deploy:** Automatic to staging after merge

#### 📊 Observability

- Commits linked to issues
- PRs thoroughly documented
- Easy rollback via revert

#### 🔐 Security

- Commit validation (local hooks + GitHub Actions)
- Branch protection via Ruleset
- Require PR review before merge

---

## 🆘 Troubleshooting

### Problem 1: Commit Rejected — Invalid Format

```
❌ ERROR: Invalid commit!
Your message: "add login"
```

**Solution:**
```bash
git commit --amend -m "feat(auth): implement login

#42"
```

---

### Problem 2: Commit Rejected — Missing Issue Reference

```
❌ ERROR: Missing issue reference!
Use: #123, Closes #123, or Ref: #123
```

**Solution:**
```bash
git commit --amend -m "feat(auth): implement login

Ref: #42"
```

---

### Problem 3: Push Rejected — Invalid Branch Name

```
❌ ERROR: Push not allowed!
Branch: "my-feature"
```

**Solution:**
```bash
git branch -m feature/123-my-feature
git push -u origin feature/123-my-feature
```

---

### Problem 4: Push Rejected — Invalid Commit in History

```
❌ ERROR: Invalid commit message!
Commit: a1b2c3d
Message: "add login feature"
```

This means a commit in your local history (not yet pushed) has an invalid message.

**Solution:**
```bash
# Interactive rebase to reword the offending commit
git rebase -i a1b2c3d^
# In the editor, mark the commit as 'reword'
# Save and fix the message in the next prompt
```

---

### Problem 5: PR Blocked — commitlint Check Failed

Even after fixing locally, the PR check is red.

**Cause:** The invalid commit was already pushed before the fix.

**Solution:**
```bash
# Fix the commit message locally
git rebase -i <commit-hash>^
# Mark as 'reword', fix the message

# Force push to update the PR branch
git push --force-with-lease origin <your-branch>
```

---

### Problem 6: Issue Does Not Close

**Cause:** PR description does not contain `Closes #123`

**Solution:** Add to the PR description and merge:
```markdown
Closes #123
```

---

### Problem 7: Branch Was Not Created Automatically

**Cause:** Issue has no label

**Solution:**
```bash
1. Add label type:feature to the issue
2. Workflow triggers automatically
3. Or create manually:
   git checkout -b feature/123-description
```

---

### Problem 8: Forgot the Issue Number

**Solution:** Use the branch name — it already contains the number!

```bash
git branch  # See current branch
# feature/123-description → Issue is #123
```

---

## 📚 Related Documentation

- **[ISSUE-TRACKING.md](ISSUE-TRACKING.md)** — How to track issues, branches, and PRs
- **[Conventional Commits](https://www.conventionalcommits.org/)** — Official specification
- **[Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)** — Branching model
- **[DORA Metrics](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-devops-performance)** — DevOps metrics

---

## 🔐 Initial Setup (First Time)

If you are new to the project:

```bash
# 1. Install dependencies
#    This automatically activates the git hooks via the "prepare" script
npm install

# 2. Verify it works
git commit --allow-empty -m "test"
# Should validate the message and reject it

# 3. Cancel the test commit (if it somehow passed)
git reset --soft HEAD~1
```

> ℹ️ The `npm install` command runs `git config core.hooksPath .githooks` automatically via the `prepare` script in `package.json`. You do not need to run it manually.

---

## ❓ Questions?

📖 See: [ISSUE-TRACKING.md](ISSUE-TRACKING.md)

---

**Last updated:** March 27, 2026
**Maintained by:** DevOps + Scrum Team