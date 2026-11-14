---
name: paper-edit-list
description: >-
  Selects transcript spans the user marked and keeps the total inside a runtime
  they set. Use when the user asks for a paper edit or a cut list before an
  episode is trimmed. It does not rewrite a quote.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/paper_edit.py. No network and no extra
  packages.
metadata:
  category: media-content
  subshelf: scripts
  tags: editing, podcasts
  added: "2026-11-12"
  featured: false
---

# Paper edit list

Pick spans that fit a runtime from a transcript the user already marked. The keep rules are in [references/keep-rules.md](references/keep-rules.md). This is a paper edit. It does not trim the recording.

## Steps

1. Take a CSV with `start`, `end`, `text`, and `must`. Set `must` to yes only for a span the user said has to survive. Ask for the target in whole seconds. Do not invent a span or a boundary.
2. Run `python3 scripts/paper_edit.py` on that file with `--target-seconds`. The fixture is [assets/sample.csv](assets/sample.csv) with target `30`, and it is not a finished cut.
3. Required spans are reserved first. Optional spans then fill what is left, in file order. A short later span can still fit after a longer one is skipped. If the script stops on an overlap, show that message and do not move a timestamp.
4. Check `must_keep_over_target`, `kept_seconds`, `ready`, and both line lists. If `must_keep_over_target=yes`, the required spans already pass the target. Say how far over, leave those spans in, and do not drop one to force a fit. A negative `remaining_seconds` is that overage.
5. If `ready=yes`, show the kept lines and the skipped lines. Every quote must match the file. Do not export, trim, or publish the episode.

## Example

User: Paper-edit `assets/sample.csv` to 30 seconds. The two `must=yes` rows have to stay. Do not trim the file.

Agent: The script prints `spans=5`, `must_keep_seconds=24`, `must_keep_over_target=no`, `kept=3`, `kept_seconds=28`, `remaining_seconds=2`, `ready=yes`. Kept text includes `A warning costs eight points.` and `The score starts at 100.` The office story and the lunch span are skipped. No quote is rewritten, and the recording is not trimmed.

## Boundaries

Do not mark a span required because it sounds better. Do not rewrite a quote to save seconds. Do not open an editor or upload the episode.
