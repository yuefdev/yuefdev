# Open-source contributions

<!-- OSS:START -->
## Accepted upstream · 2026-10-20

**116 merged PRs across 60 external projects**, out of **134 total public merged PRs** including my own repositories.

## Featured accepted contributions

Projects are ordered by GitHub stars. Each link below is an actual merged PR; stars describe the project, not the size of my contribution.

| Project | Stars | Merged PRs | Latest accepted change |
| --- | ---: | ---: | --- |
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | 284,523 | 1 | [fix: resolve OpenCode source imports and installed skills paths (#3115)](https://github.com/affaan-m/ECC/pull/3115) |
| [rust-lang/rust](https://github.com/rust-lang/rust) | 120,651 | 1 | [Fix typo in riscv64a23-unknown-linux-gnu platform docs (#162722)](https://github.com/rust-lang/rust/pull/162722) |
| [BerriAI/litellm](https://github.com/BerriAI/litellm) | 61,651 | 1 | [fix(proxy): allow model instances in LiteLLM_EndUserTable validation (#41677)](https://github.com/BerriAI/litellm/pull/41677) |
| [jgm/pandoc](https://github.com/jgm/pandoc) | 46,648 | 1 | [TEI writer: use rend, not rendition, on milestone (#11873)](https://github.com/jgm/pandoc/pull/11873) |
| [uutils/coreutils](https://github.com/uutils/coreutils) | 24,274 | 1 | [csplit: always create the final split, even when empty (#14565)](https://github.com/uutils/coreutils/pull/14565) |
| [Tencent/ncnn](https://github.com/Tencent/ncnn) | 23,982 | 1 | [cmake: fix CMAKE_EXE_LINKER_FLAGS typo in emscripten flags (#7000)](https://github.com/Tencent/ncnn/pull/7000) |

## Latest upstream merges

- **2026-10-20** · [antchfx/xpath #164](https://github.com/antchfx/xpath/pull/164) — Treat empty node sets as empty strings in predicates
- **2026-10-20** · [antchfx/xpath #163](https://github.com/antchfx/xpath/pull/163) — Preserve infinity when number strings overflow
- **2026-10-20** · [huandu/xstrings #74](https://github.com/huandu/xstrings/pull/74) — Preserve untouched bytes when expanding tabs
- **2026-10-20** · [huandu/xstrings #73](https://github.com/huandu/xstrings/pull/73) — Preserve untouched bytes when squeezing strings
- **2026-10-19** · [dlclark/regexp2 #134](https://github.com/dlclark/regexp2/pull/134) — Reject invalid numeric group names
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
