# Open-source contributions

<!-- OSS:START -->
## Accepted upstream · 2026-10-30

**191 merged PRs across 82 external projects**, out of **209 total public merged PRs** including my own repositories.

## Featured accepted contributions

Projects are ordered by GitHub stars. Each link below is an actual merged PR; stars describe the project, not the size of my contribution.

| Project | Stars | Merged PRs | Latest accepted change |
| --- | ---: | ---: | --- |
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | 293,284 | 1 | [fix: resolve OpenCode source imports and installed skills paths (#3115)](https://github.com/affaan-m/ECC/pull/3115) |
| [rust-lang/rust](https://github.com/rust-lang/rust) | 120,847 | 1 | [Fix typo in riscv64a23-unknown-linux-gnu platform docs (#162722)](https://github.com/rust-lang/rust/pull/162722) |
| [BerriAI/litellm](https://github.com/BerriAI/litellm) | 62,397 | 1 | [fix(proxy): allow model instances in LiteLLM_EndUserTable validation (#41677)](https://github.com/BerriAI/litellm/pull/41677) |
| [jgm/pandoc](https://github.com/jgm/pandoc) | 46,758 | 1 | [TEI writer: use rend, not rendition, on milestone (#11873)](https://github.com/jgm/pandoc/pull/11873) |
| [immerjs/immer](https://github.com/immerjs/immer) | 28,999 | 1 | [fix: snapshot the iteration range of optimised array searches (#1334)](https://github.com/immerjs/immer/pull/1334) |
| [uutils/coreutils](https://github.com/uutils/coreutils) | 24,313 | 1 | [csplit: always create the final split, even when empty (#14565)](https://github.com/uutils/coreutils/pull/14565) |

## Latest upstream merges

- **2026-10-28** · [tox-dev/platformdirs #630](https://github.com/tox-dev/platformdirs/pull/630) — ✅ test(unix): use host strerror in warning tests
- **2026-10-27** · [go-faker/faker #103](https://github.com/go-faker/faker/pull/103) — fix: tagged fixed-size array generation
- **2026-10-27** · [olekukonko/tablewriter #345](https://github.com/olekukonko/tablewriter/pull/345) — Keep text after OSC string terminators
- **2026-10-27** · [go-ozzo/ozzo-validation #232](https://github.com/go-ozzo/ozzo-validation/pull/232) — fix: return an error for nil EnsureString input
- **2026-10-26** · [Terry-Kao/Autonomous-Research-Agent-Protocol #7](https://github.com/Terry-Kao/Autonomous-Research-Agent-Protocol/pull/7) — Document CLI exit codes and expected failures
<!-- OSS:END -->

## Automatic updates and verification

The [hourly GitHub Action](./.github/workflows/oss-contributions.yml) collects every page of merged PRs authored by `yuefdev` through GitHub's GraphQL API. Only public repositories are published. Upstream counts exclude repositories owned by `yuefdev`; the separate total includes them. Open and closed-but-unmerged PRs are excluded.

The six featured projects are selected by current GitHub star count, with a link to the latest accepted contribution in each. The latest-merges list is ordered by the actual merge timestamp. Contribution status does not imply a maintainer or core-team role.

[View the collected public data](./assets/generated/oss-data.json) · [Verify upstream merges on GitHub](https://github.com/pulls?q=is%3Apr+is%3Amerged+is%3Apublic+author%3Ayuefdev+-user%3Ayuefdev)

The existing snapshot is retained if GitHub fails to return complete data. Refreshes commit only changed files; image URLs include a content hash to refresh cached profile images. To refresh locally with a GitHub token:

```sh
python3 .github/scripts/update_oss.py
```

The script uses `GH_TOKEN`; the workflow uses GitHub's built-in token and needs no additional secrets or services.

## Working approach

My contributions include bug fixes, regression tests, documentation and responses to review feedback. Individual PRs contain the implementation, discussion and verification evidence. I use AI-assisted development tools and disclose their use in contributions according to each project's policy.
