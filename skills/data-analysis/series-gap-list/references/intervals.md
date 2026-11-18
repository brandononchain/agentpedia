# Intervals

Accepted intervals are `1d`, `1h`, and `1m`.

A `1d` bucket is the calendar date. A date-only value (`2026-11-10`) and a datetime on that date land in the same day. A `1h` or `1m` bucket requires a time. A date-only value is unparsed for those intervals and counted in `date_only_rejected`.

Accepted shapes are `YYYY-MM-DD`, `YYYY-MM-DDTHH:MM`, `YYYY-MM-DD HH:MM`, and the same with seconds. A trailing `Z` is accepted and is not shifted. An offset such as `+00:00` is unparsed.

Two rows in the same bucket count once as present and once as a duplicate. The walk is inclusive from the earliest bucket to the latest. A missing bucket is printed as `gap=`. At most 40 gaps are printed. `gaps_omitted` is the rest. A span of more than 100000 slots prints `refused=span-too-wide` and no gap lines.

[pandas `Series.asfreq`](https://pandas.pydata.org/docs/reference/api/pandas.Series.asfreq.html) builds a new index from the minimum and maximum timestamps at a chosen frequency and leaves a missing timestep null unless a fill method is set. This script only lists those missing timestamps. It does not fill them.
