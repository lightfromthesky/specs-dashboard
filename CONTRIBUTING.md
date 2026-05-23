# Contributing

Thanks for taking a look — contributions are welcome.

## Issues

Open an issue for:

- Bugs (please include Python version, OS, and a minimal repro)
- Feature requests (please explain the use case before suggesting code)
- Questions about the spec convention or AI-agent integration

## Pull requests

Small fixes (typos, doc clarifications, obvious bug fixes) — open a PR directly.

Larger changes (new features, refactors, status-vocabulary additions) — please open an issue first so we can agree on the approach before you write code.

## Scope

specs-dashboard is intentionally minimal: one Python file, stdlib only, no build pipeline. PRs that add dependencies, build steps, or significantly grow the surface area are unlikely to be accepted unless they unlock something genuinely valuable.

The bar for inclusion: does this make the tool more useful for the *common case* of browsing a folder of markdown spec files in a repo?

## Code style

Match the existing style. No formatter or linter is enforced — readability and consistency with what's already there matter more.

## Development

Clone, edit `specs_dashboard.py`, then run the example to test changes:

```
cd example
./rebuild.sh
open specs_dashboard.html
```

## Support level

This is a side project. I'll respond to issues and PRs as I can, but response times may be slow. Don't take silence as rejection — ping the issue if it's been quiet for a while.

## License

By contributing, you agree your contributions are released under the MIT License (see [LICENSE](LICENSE)).
