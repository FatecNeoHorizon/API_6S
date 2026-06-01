# 📋 Tracking Standard: Issues and Branches

> Guide on how to trace the relationship between GitHub Issues and development branches.
>
> 📖 **Related:** [CONTRIBUTING.md](CONTRIBUTING.md) — Complete commit and branch standards
---

[Back to main README](../README.md#date-sprint-backlog)

---
## 🔗 Naming Convention

### Branch Format
```
type/number-kebab-case-description
```

### Examples
| Type | Branch | Issue | Description |
|------|--------|-------|-------------|
| Feature | `feature/123-add-authentication` | #123 | New feature |
| Bugfix | `bugfix/456-fix-login-error` | #456 | Bug fix |
| Hotfix | `hotfix/789-production-crash` | #789 | Critical production fix |
| Docs | `docs/234-setup-guide` | #234 | Documentation |

## 🤖 Automation with GitHub Actions

When you **create an issue**, the `auto-create-branch.yml` workflow automatically:

1. ✅ Reads the type from the label (`type:feature`, `type:bug`, etc.)
2. ✅ Extracts the issue number (#123)
3. ✅ Converts the title to kebab-case
4. ✅ Creates the branch: `type/123-your-description`
5. ✅ Posts a comment on the issue with the checkout command

## 📊 Full Flow

```
┌─────────────────┐
│  Create Issue   │
│  (with label)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  GitHub Action Triggers         │
│  - Reads labels and title       │
│  - Extracts issue number        │
│  - Converts to kebab-case       │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Branch Created Automatically   │
│  feature/123-your-description   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Checkout command posted        │
│  as a comment on the issue      │
└─────────────────────────────────┘
```

## 🎯 How to Checkout the Issue Branch

When you read an issue and want to work on it:

```bash
# GitHub Actions automatically posts:
git checkout feature/123-your-description

# Or clone from scratch:
git clone https://github.com/FatecNeoHorizon/API_6S.git
cd API_6S
git checkout feature/123-your-description
```

## 📌 Linking in Commits and Pull Requests

### ✅ In the Commit — Issue reference (REQUIRED)

Every commit **must** include an issue reference in the footer. All three formats are accepted:

```bash
# Shorthand reference
git commit -m "feat(auth): implement JWT

- Add JWT for authentication
- Validate token in middlewares
- Implement refresh token

#123"

# Reference without closing
git commit -m "feat(auth): implement JWT

- Add JWT for authentication
- Validate token in middlewares
- Implement refresh token

Ref: #123"

# Closes the issue automatically on merge
git commit -m "feat(auth): implement JWT

- Add JWT for authentication
- Validate token in middlewares
- Implement refresh token

Closes #123"
```

> ⚠️ Commits without an issue reference in the footer will be **rejected by the Git Hook**.

### ✅ In the Pull Request — Close the issue

```markdown
## Description
JWT authentication implementation

Closes #123

## Type of Change
- [x] New feature
- [ ] Bug fix
- [ ] Breaking change

## Checklist
- [x] Tests implemented
- [x] Documentation updated
```

**`Closes #123` in the PR:**
- ✅ Links the PR to the issue
- ✅ Shows the branch in Development
- ✅ **CLOSES the issue automatically on merge**

## 🔍 Finding Issues by Branch

On GitHub:

1. **By issue number in the branch name:**
   - `feature/123-*` → Issue #123
   - It's right there in the name! 🎯

2. **Via GitHub UI:**
   - Click on the issue
   - See the "Development" tab
   - Track the associated branch and PR

3. **Via local Git:**
   ```bash
   # View all branches with a number
   git branch -a | grep -E "feature/[0-9]+"

   # Check which issue each branch represents
   git branch -a | sed 's/.*\/\([0-9]*\)-.*/Issue #\1/'
   ```

## 📝 Checklist When Working on an Issue

- [ ] Issue created with label (`type:feature`, `type:bug`, etc.)
- [ ] Branch created automatically
- [ ] Checked out the correct branch
- [ ] Commits follow Conventional Commits standard: `feat(scope): description`
- [ ] Commits include issue reference in the footer (`#123`, `Ref: #123`, or `Closes #123`) — **REQUIRED**
- [ ] PR created with `Closes #123` in the description
- [ ] PR merged into `main` or `develop`
- [ ] Issue **closes automatically** on PR merge ✅

## 🏷️ Available Labels

### Types (one required)
- `type:feature` — New feature
- `type:bug` — Bug fix
- `type:hotfix` — Critical production fix
- `type:documentation` — Documentation
- `type:story` — User Story (Scrum)

### Priority (optional)
- `priority:low` — Low
- `priority:medium` — Medium
- `priority:high` — High
- `priority:critical` — Critical

### Status (automatic)
- `status:in-progress` — In development
- `status:review` — Awaiting review
- `status:done` — Done

## 💡 Tips

1. **Always use the number in the branch name** — Makes tracking easier
2. **Commits must reference the issue** — Footer with `#123`, `Ref: #123`, or `Closes #123` is required
3. **Squash only if needed** — Don't squash commits that reference the issue
4. **PR description** — Add `Closes #123` for automatic linking
5. **Branch protection** — Require review before merge

## 🚀 Practical Example

**Issue created:**
```
Title: [FEATURE] - Implement email validation
Number: #42
Label: type:feature
```

**GitHub Action:**
```
✅ Branch created: feature/42-implement-email-validation
📝 Comment added with checkout command
```

**Locally:**
```bash
git checkout feature/42-implement-email-validation

# Work and commit (footer is REQUIRED)
git commit -m "feat(validation): add email validation

- Add email format validation
- Add domain validation

Ref: #42"

# Push
git push origin feature/42-implement-email-validation

# Open Pull Request with 'Closes #42'
```

**In the Pull Request (description):**
```markdown
## Description
Email validation implementation for user registration

Closes #42

## Type of Change
- [x] New feature

## Checklist
- [x] Tests implemented
- [x] Documentation updated
```

**GitHub automatically:**
- ✅ Links commits to issue #42
- ✅ Shows branch in Development
- ✅ **CLOSES the issue on PR merge**

---

**Result:** Complete traceability from issue to production! 🎯