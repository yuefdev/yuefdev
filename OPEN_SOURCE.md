# Open-source contributions

## Verified snapshot

As of **18 October 2026**, GitHub reports **54 merged pull requests across 31 repositories owned by other accounts** during the preceding 12 months. This is a dated snapshot of publicly visible PRs authored by `yuefdev`.

[View the merged PRs on GitHub](https://github.com/search?q=is%3Apr+is%3Amerged+author%3Ayuefdev+-user%3Ayuefdev+merged%3A2025-10-18..2026-10-18&type=pullrequests)

Open PRs and changes merged into my own repositories are excluded. Contribution status does not imply a maintainer or core-team role.

## Selected accepted contributions

| Project | Contribution |
| --- | --- |
| Pylint | [Ignore discard-variable type redefinitions](https://github.com/pylint-dev/pylint/pull/11546) |
| SQLFluff | [Preserve MySQL and MariaDB account quotes](https://github.com/sqlfluff/sqlfluff/pull/8638) |
| LiteLLM | [Accept model instances during end-user validation](https://github.com/BerriAI/litellm/pull/41677) |
| uutils/coreutils | [Keep the final csplit output, including empty splits](https://github.com/uutils/coreutils/pull/14565) |
| Candle | [Correct ONNX LogSoftmax without an axis attribute](https://github.com/huggingface/candle/pull/3975) |
| tract | [Handle per-axis quantisation scales and zero points](https://github.com/sonos/tract/pull/2849) |
| Pydash | [Keep replacement anchors at string boundaries](https://github.com/dgilland/pydash/pull/321) |
| New-Tab | [Complete offline source-unit conversions](https://github.com/404-PF/New-Tab/pull/849) |

## Reproduce the count

The query used for this snapshot is:

```text
is:pr is:merged author:yuefdev -user:yuefdev merged:2025-10-18..2026-10-18
```

With GitHub CLI:

```sh
gh api search/issues --method GET -f 'q=is:pr is:merged author:yuefdev -user:yuefdev merged:2025-10-18..2026-10-18' -f per_page=100 --jq '{total_count, incomplete_results}'
```

The result was `total_count: 54` and `incomplete_results: false`. All results fitted in one page. The repository count is the number of distinct `repository_url` values among those results. For a future rolling-year check, update both dates and paginate if the result exceeds 100 PRs.

## Working approach

My contributions include bug fixes, regression tests, documentation and responses to review feedback. Individual PRs contain the implementation, discussion and verification evidence. I use AI-assisted development tools and disclose their use in contributions according to each project's policy.
