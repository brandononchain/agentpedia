# Step order

`raw` is the number of distinct actors who have that step label at least once.

`ordered` is the number of distinct actors who have that step and every step earlier in the list the user passed. An actor missing an earlier label is not counted, even if a later label is present.

`drop_from_previous` is the previous step's ordered count minus this step's ordered count. The first step's drop is 0.

`of_first` is this step's ordered count over the first step's ordered count, both integers. It is not a rounded percent.

Rows with a blank actor or a blank step are `skipped_rows`. A step label that is not in the ordered list is an unknown label and is not added to the funnel.

This is label presence. The script does not read a timestamp, so it cannot enforce "step B happened after step A".

[PostHog's funnel docs](https://posthog.com/docs/product-analytics/funnels) separate sequential order from any-order completion, where the steps may occur in any sequence. This script is the any-order presence check. It does not apply a conversion window, a breakdown, or a time-to-convert measure.
