---
name: subtitle-cue-sheet
description: >-
  Builds an SRT or WebVTT cue sheet from timed lines the user supplies, and
  checks order, overlap, and a character budget they set. Use when the user
  asks for captions or subtitles from a transcript they already timed.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/subtitle_cues.py. No network and no extra
  packages.
metadata:
  category: media-content
  subshelf: captions
  tags: subtitles, captions
  added: "2026-11-12"
  featured: false
---

# Subtitle cue sheet

Write captions from timed lines the user already has. The format notes are in [references/cue-formats.md](references/cue-formats.md). Do not transcribe audio, and do not burn the captions into a picture.

## Steps

1. Take a CSV with `start`, `end`, and `text`. Ask for `srt` or `vtt`. Apply a character budget only when the user names one. Do not invent a reading speed, and do not split a line to meet a budget.
2. Run `python3 scripts/subtitle_cues.py` on that file with `--format` and, when they set a budget, `--max-chars`. The fixture is [assets/sample.csv](assets/sample.csv).
3. Read `end_after_start`, `ordered`, `overlap`, `arrow_in_text`, `over_budget`, and `ready`. Overlap is reported and left in the file. WebVTT allows it. Say so when `overlap=yes`, and do not delete a cue to hide it.
4. If `ready=no`, show the failing row and do not hand the cue file off as finished captions. Do not shorten the words, and do not drop a cue that contains an arrow. Ask the user to change the source line.
5. If `ready=yes`, show the cue file. Cue text must match the CSV, including the words and not a paraphrase. Do not mux the file into a video.

## Example

User: Build WebVTT from `assets/sample.csv` with a budget of 80 characters. Do not transcribe anything else.

Agent: The script prints `cues=2`, `format=vtt`, `ordered=yes`, `overlap=no`, `over_budget=0`, `char_budget=80`, `longest_chars=36`, `ready=yes`. The cue file starts with `WEBVTT`. The first cue text is `We lint every skill before it ships.` No line is shortened.

## Boundaries

Do not fetch a video, translate a cue, or invent a millisecond the file did not have. A finished cue sheet is not a burned-in subtitle and it is not a publish.
