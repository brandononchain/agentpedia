# Which pattern wins

GitHub loads one CODEOWNERS file, searching `.github/`, the repository root, then `docs/`, and it uses the first of those that exists. Later lines in that file win. The syntax section of [About code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) is the source for the rules below. Patterns follow most of [gitignore pattern format](https://git-scm.com/docs/gitignore#_pattern_format).

The script keeps a line when the pattern compiles and every owner is a `@user`, a `@org/team`, or an email. A line with a pattern and no owners is kept. That is how a later line clears owners. A ` #` starts an inline comment. A skipped line is reported and does not match.

GitHub says these gitignore forms do not work here, so the script skips them instead of guessing:

- a pattern that starts with `!`
- a `[` or `]` character range
- a `\#` that tries to make a leading hash into a pattern

What the script matches, in the same sense as the documented examples:

- `*` matches every path. `*.js` matches that basename in any directory, and it does not cover a child of a directory whose name happens to end in `.js`.
- A pattern with no slash matches in any directory. A trailing slash, or a last segment with no `*` or `?`, also covers files inside that directory. `apps/` covers `src/apps/sub/main.ts`.
- A slash anchors the pattern at the repository root, except a leading `**/`. `/build/logs/` does not match `other/build/logs/a.txt`. `docs/*` matches `docs/getting-started.md` and does not match `docs/build-app/troubleshooting.md`.
- `**/logs` matches a `logs` directory at any depth, and files inside it.
- `**` as a whole segment matches zero or more segments. `?` matches one character other than a slash. Matching is case sensitive.

The last matching line is the only one printed. `/docs/` later in the file beats an earlier `docs/*` on a file that both match. The script stops at 3000000 bytes. GitHub says a file of 3 MB or over is not loaded. The script does not guess a byte count past that sentence, and it does not check that an owner has write access.
