---
name: clip-cutdown
description: >-
  Turns a transcript the user pastes into podcast notes and short clip
  suggestions, each tied to a timestamp or a quote. Use when the user asks for
  show notes or social clips from a recording they already transcribed.
license: Apache-2.0
metadata:
  category: media-content
  tags: podcasts, clips
  added: "2026-11-10"
  featured: false
---

# Clip cutdown

Cut a transcript into notes and clip candidates. A clip is a quote they can verify, not a new sentence.

## Steps

1. If the transcript has timestamps, keep them. If it does not, number the paragraphs and say there are no timestamps.
2. Write show notes as three to seven bullets. Each bullet paraphrases a stretch of the transcript and points at its timestamp or paragraph number.
3. Suggest at most three clips. Each clip is a quote of no more than the words in the transcript, plus the timestamp or paragraph, and one line on why it stands alone.
4. Check every quote against the transcript. A word that is not there is removed. Do not clean up grammar inside a quote.
5. Do not write a title that claims a result the speaker did not say.

## Example

User: Paragraph 1: "We lint every skill before it ships." Paragraph 2: "A warning costs eight points." No timestamps.

Agent: Notes point at paragraph 1 and paragraph 2. One clip quotes "We lint every skill before it ships." from paragraph 1, because it states the rule without the rest of the episode. The quote is not rewritten. No timestamps are invented.

## Boundaries

Do not invent a guest, a sponsor read, or a number of downloads. Do not publish the clips.
