---
name: chapter-marker-list
description: >-
  Checks a chapter list the user already timed and prints YouTube description
  lines. Use when the user asks for video chapters from timestamps they marked.
  It does not invent a start time.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/chapter_check.py. No network and no extra
  packages.
metadata:
  category: media-content
  subshelf: captions
  tags: chapters, youtube
  added: "2026-11-12"
  featured: false
---

# Chapter marker list

Turn timestamps the user already marked into description lines YouTube can read as chapters. The rules that are checked are in [references/youtube-chapters.md](references/youtube-chapters.md). Do not detect chapters from silence, and do not upload the video.

## Steps

1. Take a CSV with `start` and `title`. If the runtime is missing, ask for it. Do not infer a chapter from a transcript that has no timestamps, and do not move a time to make a gap longer.
2. Run `python3 scripts/chapter_check.py` on that file with `--runtime`. The fixture is [assets/sample.csv](assets/sample.csv) with runtime `01:20`, and it is not a live video.
3. Read `chapters`, `first_is_zero`, `ascending`, `short_chapters`, `last_length`, and `ready`. A chapter is short when the gap to the next timestamp is under 10 seconds. The last chapter uses the runtime. `last_length=not-checked` means the runtime was not supplied.
4. If `ready=no`, name the failed check and show the description lines as a draft. Do not paste them into a video description as finished chapters. Do not edit a title so the list looks cleaner.
5. If `ready=yes`, show the description lines. Each title must match the file. Stop there. Do not upload, and do not change the automatic-chapters setting.

## Example

User: Check `assets/sample.csv` with runtime `01:20`. Do not upload.

Agent: The script prints `chapters=4`, `first_is_zero=yes`, `ascending=yes`, `short_chapters=0`, `last_length=15`, `runtime=80`, `ready=yes`. The first line is `00:00 Cold open`. The titles are the four titles from the file. Nothing is uploaded.

## Boundaries

Do not invent a start time, a title, or a runtime. Do not pull a transcript from a URL. A `ready=yes` line list is not a claim that the channel has access to chapters.
