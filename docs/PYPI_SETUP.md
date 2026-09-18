# PyPI Publishing Setup Guide

This document outlines the steps to finalize PyPI publishing setup for dataframe-mutator using GitHub Actions and OpenID Connect (OIDC).

## What's Been Done

✅ Updated `pyproject.toml` with author email  
✅ Created GitHub Actions workflow (`.github/workflows/publish.yml`)  
✅ Configured to use `PYPI_TOKEN` from GitHub environment secrets  

## How It Works

The workflow uses your existing `PYPI_TOKEN` from GitHub secrets to authenticate with PyPI. When you create a release, the workflow automatically:

1. Checks out your code
2. Builds the distribution (`.whl` and `.tar.gz`)
3. Publishes to PyPI using your token

No additional setup needed beyond what you've already done!

## Publish Your First Release

When ready to release:

```bash
# 1. Update version in pyproject.toml if needed
# 2. Create a git tag (semantic versioning recommended)
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# 3. Go to GitHub repo → "Create a new release"
#    Select the tag and publish the release
```

The workflow will automatically trigger and publish to PyPI!

## Testing Your Setup

### Manually test packaging:

```bash
pip install build
python -m build
ls dist/  # Should see .tar.gz and .whl files
```

### Verify on PyPI

After publishing, check:
- https://pypi.org/project/dataframe-mutator/

## Release Flow (Going Forward)

```bash
# Update version in pyproject.toml
# Make your changes and commit

# Create release tag
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0

# Create GitHub release (auto-publishes)
```

## Troubleshooting

### Build Failures
Check the workflow logs in your GitHub repo → **Actions** tab

### Token Issues
Verify `PYPI_TOKEN` is set in your environment secrets:
- Go to repo **Settings** → **Secrets and variables** → **Actions**
- Check that `PYPI_TOKEN` exists

## Documentation

- [PyPI Publishing Docs](https://packaging.python.org/guides/publishing-package-distribution-releases-to-pypi/)
- [OIDC for PyPI](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish)
