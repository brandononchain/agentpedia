# Cue formats this sheet writes

[WebVTT](https://www.w3.org/TR/webvtt1/) is the W3C caption format. A file this script writes uses only the parts a single subtitle track needs:

- The body starts with the string `WEBVTT`, then a blank line.
- A cue has a start timestamp, the arrow `-->`, an end timestamp, a line break, and the cue text.
- The timestamp uses a full stop before the milliseconds. Minutes and seconds are two digits. Hours are written as two digits, which the timestamp grammar allows.
- The end time is greater than the start time.
- Each cue starts at a time greater than or equal to the start of every cue before it.
- Cue text does not contain `-->`.

The same specification says different cues can overlap, and that cues are listed by start time. This script reports `overlap=yes` when one cue starts before the previous cue ends. It still writes those cues. It does not delete one to hide the overlap.

SRT here means the SubRip layout: a cue number, a timing line that uses a comma before the milliseconds, the cue text, and a blank line before the next cue. It is not a W3C format. The same timing checks apply, and the comma is the only timing difference from the WebVTT line.

`--max-chars` is the user's budget. There is no default reading speed. A cue over that budget is counted and the words are left as written.
