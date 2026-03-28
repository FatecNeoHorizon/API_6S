# 📚 Documentation Guide: Commits, Branches and Issues

> Centralized index of project standards documentation with a clear description of each document.

---

[Back to main README](../README.md#date-sprint-backlog)

---

## 📄 Main Documents

### 1. **[CONTRIBUTING.md](CONTRIBUTING.md)**

**Who is it for?** Everyone involved (Devs, Scrum, DevOps)

**What is it?** Complete commit and branch standards for the project

**Contains:**
- ✅ Conventional Commits standard (types, format, validation)
- ✅ Branch standard (type/number-description)
- ✅ Automations (all hooks and workflows)
- ✅ Full visual flow (issue → branch → commit → PR → closure)
- ✅ Practical examples (Feature, Bugfix, Hotfix)
- ✅ Best practices by role (Devs, Scrum, DevOps)
- ✅ Troubleshooting

**When to read?**
- 🆕 First day on the project
- 📖 General standards reference
- 🔧 When you need to remember commit syntax

---

### 2. **[ISSUE-TRACKING.md](ISSUE-TRACKING.md)**

**Who is it for?** Mainly Scrum Masters and DevOps (tracking visualizations)

**What is it?** How to trace the relationship between Issues, Branches and PRs

**Contains:**
- ✅ Branch naming (type/number-description)
- ✅ How GitHub links issue → branch → PR
- ✅ Automation flow (workflows)
- ✅ How to find issues by branch
- ✅ Commit and PR linking
- ✅ Available labels
- ✅ Practical end-to-end tracking example

**When to read?**
- 👀 Checking the status of an issue
- 📊 Scrum Master tracking progress
- 🔍 Finding which branch is linked to which issue
- 📈 DevOps understanding traceability

---

## 🔄 Quick Differences

| Aspect | CONTRIBUTING.md | ISSUE-TRACKING.md |
|--------|----------------|-------------------|
| **Main Focus** | Commit and branch standards | Issue tracking |
| **Audience** | Everyone | Scrum + DevOps |
| **Commit Detail** | ✅ Complete (types, validation, examples) | ❌ Reference only |
| **Branch Detail** | ✅ Complete | ✅ Complete |
| **Automations** | ✅ Design and operation | ✅ Operation |
| **Labels** | ✅ List | ✅ List |
| **Examples** | ✅ 3 detailed examples | ✅ 1 tracking example |

---

## 🎯 Flow by Persona

### 👨‍💻 Developer

**Read first:**
1. [CONTRIBUTING.md](CONTRIBUTING.md) — Understand the standards
2. [ISSUE-TRACKING.md](ISSUE-TRACKING.md) — Understand the workflow

**Quick reference:**
```bash
# Commit standard (footer is REQUIRED)
feat(scope): description

#123          # shorthand reference
Ref: #123     # reference without closing
Closes #123   # closes the issue automatically on merge

# Branch standard
feature/123-kebab-case-description
bugfix/456-fix-error
hotfix/789-crash

# Close issue in PR
Closes #456
```

---

### 👨‍💼 Scrum Master

**Read first:**
1. [ISSUE-TRACKING.md](ISSUE-TRACKING.md) — Progress tracking
2. [CONTRIBUTING.md](CONTRIBUTING.md) — Understand the full flow

**What to monitor:**
- ✅ Does issue #123 have a branch created?
- ✅ Does the branch have commits with `#123`, `Ref: #123`, or `Closes #123`? (REQUIRED)
- ✅ Does the PR have `Closes #123`?
- ✅ Was the PR merged? (Issue closes automatically)

**Where to find:**
- GitHub Issue → "Development" tab → see branch and PR
- GitHub Branch → shows which issue is linked

---

### 🔧 DevOps / Release Manager

**Read first:**
1. [CONTRIBUTING.md](CONTRIBUTING.md) — Automations and workflows
2. [ISSUE-TRACKING.md](ISSUE-TRACKING.md) — Tracking for reports

**Responsibilities:**
- ✅ Validate commit standard (hook validates automatically, including footer)
- ✅ Ensure branches follow the standard
- ✅ Monitor workflows (auto-create-branch, auto-fill-pr)
- ✅ Generate progress reports by change type

**Useful commands:**
```bash
# View commits by type
git log --oneline | grep "^feat"
git log --oneline | grep "^fix"

# View commits for an issue
git log --grep "#123"

# View branch history
git log feature/123-description
```

---

## 🔗 Cross-Reference

**If you are in CONTRIBUTING.md and want to understand tracking:**
→ See the "🔄 Full Flow" section or go to [ISSUE-TRACKING.md](ISSUE-TRACKING.md)

**If you are in ISSUE-TRACKING.md and want commit details:**
→ See the "📌 Linking in Commits and Pull Requests" section or go to [CONTRIBUTING.md](CONTRIBUTING.md)

---

## ✅ Quick Validation

**Is everything correct?** Check:

```bash
# 1. Commit validated by hook
✅ git commit works
❌ Message "ERROR: Invalid commit!" = wrong format

# 2. Commit has issue reference in footer (REQUIRED)
✅ feat(auth): implement login

   #42
✅ feat(auth): implement login

   Ref: #42
✅ feat(auth): implement login

   Closes #42
❌ feat(auth): implement login  (no footer = REJECTED by hook)

# 3. Branch is correct
✅ feature/123-description  (type/number-description)
❌ my-feature, my_feature, Feature/123 = wrong format

# 4. PR has Closes
✅ Description contains "Closes #123"
❌ No reference = issue does not close automatically

# 5. GitHub linked
✅ On the issue, "Development" tab shows branch and PR
❌ Nothing appears = standard not followed
```

---

## 📞 Questions?

| Question | Document |
|----------|----------|
| "How do I write a commit?" | [CONTRIBUTING.md](CONTRIBUTING.md#-commit-standards) |
| "How do I name a branch?" | [CONTRIBUTING.md](CONTRIBUTING.md#-branch-standards) |
| "How do I track issues?" | [ISSUE-TRACKING.md](ISSUE-TRACKING.md) |
| "Why does merging close the issue?" | [ISSUE-TRACKING.md](ISSUE-TRACKING.md) |
| "What are the commit types?" | [CONTRIBUTING.md](CONTRIBUTING.md#accepted-types) |
| "How do I link an issue in a commit?" | [CONTRIBUTING.md](CONTRIBUTING.md#5️⃣-footer-required) |

---

**Last updated:** February 28, 2026
**Consistency:** ✅ Validated