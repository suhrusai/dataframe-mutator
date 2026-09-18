# PyPI Publishing Setup Guide

This document outlines the steps to finalize PyPI publishing setup for dataframe-mutator using GitHub Actions and OpenID Connect (OIDC).

## What's Been Done

✅ Updated `pyproject.toml` with author email  
✅ Created GitHub Actions workflow (`.github/workflows/publish.yml`)  

## Next Steps to Complete Setup

### 1. Configure PyPI Publishers (OIDC)

This is the secure, modern way to publish without storing API tokens.

#### For TestPyPI:

1. Go to https://test.pypi.org/account/register/ (create account if needed)
2. Navigate to **Account settings** → **Publishing**
3. Click **"Add a new pending publisher"**
4. Fill in these fields:
   - **PyPI Project Name:** `dataframe-mutator`
   - **Owner:** `suhrusai` (your GitHub username)
   - **Repository name:** `dataframe-mutator`
   - **Workflow name:** `publish.yml`
   - **Environment name:** `testpypi`

#### For PyPI (Production):

1. Go to https://pypi.org/account/register/ (create account if needed)
2. Navigate to **Account settings** → **Publishing**
3. Click **"Add a new pending publisher"**
4. Fill in these fields:
   - **PyPI Project Name:** `dataframe-mutator`
   - **Owner:** `suhrusai`
   - **Repository name:** `dataframe-mutator`
   - **Workflow name:** `publish.yml`
   - **Environment name:** `pypi`

### 2. Create GitHub Environments (Optional but Recommended)

For better control, set up GitHub Actions environments:

1. Go to your repo **Settings** → **Environments**
2. Create two environments:
   - **Name:** `testpypi`
   - **Name:** `pypi` (restrict to main branch for safety)

### 3. Test the Setup

#### Option A: Create a test release

```bash
git tag -a v0.1.0 -m "Test release"
git push origin v0.1.0
```

Then go to your repo → **Releases** and publish it.

#### Option B: Manually test packaging

```bash
pip install build
python -m build
ls dist/  # Should see .whl and .tar.gz files
```

### 4. Publish Your First Release

When ready to release:

```bash
# Ensure you're on main branch with clean state
git checkout main
git pull origin main

# Create a git tag (semantic versioning recommended)
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# Go to GitHub and create a release from the tag
# The workflow will automatically trigger
```

## How It Works

1. **You create a GitHub release** with a git tag
2. **Workflow triggers** on `release: published` event
3. **Build step** creates `.whl` and `.tar.gz` files
4. **Publish step** uses OIDC to authenticate (no API token needed!)
5. **PyPI receives** your package

## Benefits of OIDC

✅ **No API tokens to manage** - GitHub generates temporary credentials  
✅ **Automatic token rotation** - Each publish gets a fresh token  
✅ **More secure** - Tokens never stored in GitHub secrets  
✅ **Fine-grained permissions** - Only allows publishing this package  
✅ **Audit trail** - PyPI can trace publishes back to your workflow  

## Troubleshooting

### Publisher Not Found
**Error:** "No PyPI publisher trusted this workflow"

**Solution:** Ensure the publisher fields exactly match:
- Environment name matches your workflow
- Owner/repository match your GitHub repo
- Workflow name is `publish.yml`

### Build Failures
**Error:** "No module named 'build'"

**Solution:** The workflow installs this automatically, but verify:
```bash
pip install build
python -m build
```

### Test Push to TestPyPI
Before publishing to production, test with TestPyPI:
```bash
python -m twine upload --repository testpypi dist/*
```

## Next Release Flow

Once set up:

```bash
# 1. Update version in pyproject.toml
# 2. Commit changes
# 3. Create tag
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin v0.1.1
# 4. Create release on GitHub (auto-publishes)
```

## Documentation

- [PyPI Publishing Docs](https://packaging.python.org/guides/publishing-package-distribution-releases-to-pypi/)
- [OIDC for PyPI](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish)
