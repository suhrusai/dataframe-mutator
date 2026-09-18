# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in dataframe-mutator, please email **security@dataframe-mutator.dev** instead of using the public issue tracker.

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

We will acknowledge receipt within 48 hours and provide updates on our progress.

## Supported Versions

We provide security updates for the following versions:

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Yes    |
| < 0.1   | ❌ No     |

## Security Considerations

### Code Execution

dataframe-mutator uses `ast` and `exec()` for mutation testing. It should **only be run on trusted code** in a development or CI environment.

⚠️ **Do not use in production environments or with untrusted code.**

### Dependencies

We regularly:
- Update dependencies to patch vulnerabilities
- Monitor security advisories
- Run dependency checks in CI/CD

See [CHANGELOG.md](CHANGELOG.md) for dependency updates.

### Data Handling

- dataframe-mutator does **not** collect or transmit any data
- All analysis happens locally
- No external API calls for core functionality
- Test data remains on your machine

## Best Practices

1. **Run in isolated environments** - Use virtual environments or containers
2. **Keep dependencies updated** - Regularly update Polars and other packages
3. **Review mutated code** - Understand what mutations are being applied
4. **Don't use in production** - Only for development and testing
5. **Secure your test data** - If using sensitive data, ensure proper access controls

## GitHub Security Features

We use:
- ✅ Branch protection for main branch
- ✅ Require PR reviews
- ✅ Required status checks
- ✅ Dependency vulnerability scanning
- ✅ Secret scanning

## Changelog

For security-related updates, see [CHANGELOG.md](CHANGELOG.md) marked with **[SECURITY]**.

## Contact

- **Security Issues:** security@dataframe-mutator.dev
- **General Questions:** Open an Issue on GitHub
- **Discussion:** Start a Discussion on GitHub

## Credits

We thank all security researchers who responsibly disclose vulnerabilities.
