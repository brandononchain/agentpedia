# How a line becomes a bump

Each kept line is one commit that is already classified. The word `breaking` as the second token means the commit has a `!` or a `BREAKING CHANGE` footer. A type named on its own is not breaking. `Feat` and `feat` are the same type. One commit gets one class: breaking is major, even when the type is `feat` or `fix`.

The correlation is the one in the [Conventional Commits FAQ](https://www.conventionalcommits.org/en/v1.0.0/#how-does-this-relate-to-semver):

- `fix` is patch.
- `feat` is minor.
- A breaking commit is major, whatever the type.
- Any other type is none, unless it is breaking.

The highest class in the file is `bump`. Counts do not add a second class for the same line.

When `--current` is set, the value has to match the [SemVer 2.0.0](https://semver.org/#summary) form. A leading `v` is rejected, because the SemVer FAQ says `v1.2.3` is not a semantic version. For a major greater than zero, and no pre-release identifier:

- major becomes `X+1.0.0`
- minor becomes `X.Y+1.0`
- patch becomes `X.Y.Z+1`
- none stays `next=unchanged`

Those resets are SemVer items 6, 7, and 8, which apply when the major is greater than zero. Major zero prints `initial_development=yes` and `next=not-computed`, because item 4 says anything may change. A pre-release identifier also prints `next=not-computed`. Build metadata is ignored for the decision and is not copied onto a next number. The script does not invent a pre-release bump.
