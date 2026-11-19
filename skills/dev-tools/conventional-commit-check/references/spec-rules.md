# What the checker accepts

`scripts/check_commit.py` follows Conventional Commits 1.0.0. The structure and the RFC 2119 rules are in the [specification](https://www.conventionalcommits.org/en/v1.0.0/#specification). The summary that ties `fix`, `feat`, and `BREAKING CHANGE` to SemVer is on the same page, above the numbered rules.

The script treats these as the message:

- A type is one word of letters and digits. `Feat` and `feat` are both accepted. The script prints the type as written. The specification says the parts are not case sensitive, except `BREAKING CHANGE`.
- A scope, when present, is inside one pair of parentheses and contains no spaces. An empty `scope=` means there were no parentheses.
- A `!` immediately before the colon marks a breaking change. So does a footer token `BREAKING CHANGE` or `BREAKING-CHANGE`, each followed by a colon and a space. The script does not treat a lower-case spelling as that token.
- Text after the subject starts on the line after a blank line. The footer block is the last paragraph, and only when that paragraph starts with a footer token. A footer token is `BREAKING CHANGE` or a single hyphenated word, then `: ` or ` #`. A breaking mention that is followed by another paragraph stays in the body, so `breaking=no`.
- Other types are allowed. The specification does not give them a SemVer effect. This script does not choose a version. That is semver-bump-plan.

The script does not require the 50-character subject used by git-commit-writer. That limit is not in this specification.
