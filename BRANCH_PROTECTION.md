# Branch Protection Rules

**Required Settings for Production-Grade CI/CD**

This document outlines the branch protection rules that MUST be configured in GitHub to ensure quality and prevent accidental merges.

## GitHub Settings Required

### Location
Settings → Branches → Branch protection rules

### Rule Configuration for `main` branch

#### 1. Require a pull request before merging
- ✅ **Require pull request reviews before merging**: YES
- Number of required reviews: **1**
- ✅ **Dismiss stale pull request approvals when new commits are pushed**: YES
- ✅ **Require review from code owners**: YES (if CODEOWNERS exists)

#### 2. Require status checks to pass before merging
- ✅ **Require branches to be up to date before merging**: YES
- ✅ **Require status checks to pass**: YES

**Required checks (MUST ALL PASS before merge):**

```
Tests (Ubuntu Latest, Python 3.8)
Tests (Ubuntu Latest, Python 3.9)
Tests (Ubuntu Latest, Python 3.10)
Tests (Ubuntu Latest, Python 3.11)
Tests (Ubuntu Latest, Python 3.12)
Tests (Ubuntu Latest, Python 3.13)
Tests (Ubuntu Latest, Python 3.14)
Tests (macOS 15 Intel, Python 3.14)
Tests (Windows Latest, Python 3.14)
Tests (Ubuntu 24.04 ARM, Python 3.14)
Benchmarks (ubuntu-latest, x64)
Benchmarks (macos-15-intel, x64)
Benchmarks (windows-latest, x64)
Benchmarks (ubuntu-24.04-arm, arm64)
Comment PR Results
Test with mutmut Public Suite
Plugin Integration Test
```

#### 3. Require branches to be up to date
- ✅ YES (automatically enforced with #2)

#### 4. Require status checks to pass before merging
- ✅ **Require that branches be up to date before merging**: YES

#### 5. Require conversation resolution before merging
- ✅ **Require all conversations on code to be resolved before merging**: YES

#### 6. Require code reviews
- ✅ **Require code reviews**: YES
- Number of required reviews: **1**
- ✅ **Dismiss stale pull request approvals**: YES

#### 7. Require approved reviews from code owners
- ✅ **Require review from code owners**: YES (if applicable)

#### 8. Require up-to-date branches
- ✅ YES (enforced by #2)

#### 9. No forced pushes
- ✅ **Restrict who can force push to matching branches**: 
  - Allow only administrators

#### 10. No deletions
- ✅ **Allow deletion of the head branch**: NO
- ✅ **Allow force pushes**: NO

---

## Workflow Jobs (GitHub Actions)

These jobs MUST ALL pass before PR can be merged:

### Test Jobs (10 combinations)
```
Tests-Linux-3.8
Tests-Linux-3.9
Tests-Linux-3.10
Tests-Linux-3.11
Tests-Linux-3.12
Tests-Linux-3.13
Tests-Linux-3.14
Tests-macOS-3.14
Tests-Windows-3.14
Tests-ARM64-3.14
```

Each test job validates:
- ✅ Lint (ruff, black)
- ✅ Type checking (mypy)
- ✅ Unit tests (pytest)
- ✅ Coverage reporting

### Benchmark Jobs (4 platforms)
```
Benchmarks-Linux-x64
Benchmarks-macOS-x64
Benchmarks-Windows-x64
Benchmarks-ARM64
```

Each benchmark job validates:
- ✅ TPC-H benchmark (28 tests)
- ✅ Comprehensive operations (63 tests)
- ✅ Mutation filtering

### Result Jobs
```
Comment-PR-Results
```

Final step that comments results on PR.

---

## What This Ensures

✅ **No Merges Without Passing Checks**
- All 10 test combinations must pass (Python 3.8-3.14)
- All 4 benchmark suites must pass
- All 2 integration test suites must pass (mutmut + plugin)
- Results comment must post
- Cannot merge with failing tests

✅ **No Automatic Commits to Master**
- No auto-merge workflows enabled
- All merges require manual action
- Manual review required (1+ approver)
- Conversation resolution required

✅ **Code Quality Enforced**
- Linting standards (ruff, black)
- Type safety (mypy)
- Test coverage maintained
- All platforms validated

✅ **Performance Regression Prevention**
- Benchmarks run on all platforms
- Results visible in PR
- Performance tracked over time

---

## Setup Instructions

### Step 1: Open Repository Settings
1. Go to GitHub repository
2. Click **Settings**
3. Go to **Branches** in sidebar

### Step 2: Create/Edit Rule for `main`
1. Click "Add rule" (or edit existing)
2. Branch name pattern: `main`
3. Enable all settings below

### Step 3: Enable Required Checks
1. ✅ Require pull request before merging
2. ✅ Require status checks to pass
3. ✅ Require conversation resolution
4. ✅ Require code owners review
5. ❌ Allow force pushes: NO
6. ❌ Allow deletions: NO

### Step 4: Configure Status Checks
Click "Require status checks to pass before merging":
- Search and select each job name:
  - `Tests (Ubuntu Latest, Python 3.8)`
  - `Tests (Ubuntu Latest, Python 3.9)`
  - `Tests (Ubuntu Latest, Python 3.10)`
  - `Tests (Ubuntu Latest, Python 3.11)`
  - `Tests (Ubuntu Latest, Python 3.12)`
  - `Tests (Ubuntu Latest, Python 3.13)`
  - `Tests (Ubuntu Latest, Python 3.14)`
  - `Tests (macOS 15 Intel, Python 3.14)`
  - `Tests (Windows Latest, Python 3.14)`
  - `Tests (Ubuntu 24.04 ARM, Python 3.14)`
  - `Benchmarks (ubuntu-latest, x64)`
  - `Benchmarks (macos-15-intel, x64)`
  - `Benchmarks (windows-latest, x64)`
  - `Benchmarks (ubuntu-24.04-arm, arm64)`
  - `Run mutmut Public Test Suite`
  - `Plugin Integration Test`
  - `Comment PR Results`

### Step 5: Save Rule
Click "Create" or "Update"

---

## Testing Branch Protection

### Test 1: Cannot Merge Without Passing Checks
1. Open any PR with failing tests
2. Try to merge
3. **Expected**: Merge button disabled with message "Required status checks have not passed"

### Test 2: Cannot Force Push to Master
1. Try to force push to main
2. **Expected**: Push rejected (only admins can force push)

### Test 3: Cannot Delete Master
1. Try to delete main branch
2. **Expected**: Deletion blocked

### Test 4: Requires Reviews
1. Open PR without approvals
2. Try to merge
3. **Expected**: Merge blocked with message "Requires at least 1 approval"

### Test 5: All Checks Visible in PR
1. Open any PR
2. Scroll to "Checks" section
3. **Expected**: See all 12 status checks listed
4. **Expected**: Cannot merge until all are green

---

## FAQ

**Q: Can admins bypass these rules?**
A: Yes, admins can force push and merge without checks. This is GitHub's default. If you want to prevent even admins, use organization-level rules (GitHub Enterprise feature).

**Q: What if a check fails but I want to merge anyway?**
A: You cannot merge. This is intentional - it ensures quality. Fix the failing test instead.

**Q: How long do checks take?**
A: ~60 minutes for all tests and benchmarks to complete (parallel execution). You must wait for all to finish before merging.

**Q: Can I disable a failing check?**
A: No, all checks are required. If a check is not needed, remove it from the workflow instead.

**Q: What about draft PRs?**
A: Draft PRs still require checks to pass before converting to ready for review.

---

## Monitoring

### Dashboard
GitHub automatically shows:
- ✅ Check status in PR
- ✅ Which checks pass/fail
- ✅ Required vs optional checks
- ✅ Merge button status

### Insights
Analytics → Insights:
- Check success rates
- Common failures
- Performance trends

---

## Maintenance

### Review Quarterly
- Ensure all workflows are up to date
- Verify check names match workflow jobs
- Update if new checks added

### Update When
- Adding new platforms
- Adding new test suites
- Changing required Python versions
- Modifying quality standards

---

## Security

This configuration ensures:
- ✅ No accidental merges
- ✅ No bypassing CI/CD
- ✅ No force pushes (except admins)
- ✅ Code review always required
- ✅ All conversations resolved
- ✅ Production stability

**Result: Enterprise-grade protection on the main branch.** 🔒
