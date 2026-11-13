# How a span is kept

The file the user supplies is the only source. Each row is one span of the recording they already timed.

- `must` is `yes` only when the user said that span has to survive. The script never changes this flag.
- `must` is `no` when the span may be cut. Those spans are considered in file order.
- A must-keep span stays in the list even when the must-keep total is already over the target. Optional spans are then all skipped, and `ready=no`.
- When the must-keep total fits, an optional span is kept only when adding its duration does not pass the target. A span that does not fit is skipped. A later, shorter span can still fit.
- Spans must not overlap, and each span must end after it starts. The script stops on a row that breaks either rule instead of moving a boundary.
- The text on a kept line is the text from that row. Nothing is rewritten to save time.

The total is whole seconds from the timestamps in the file. This list is a paper edit. It is not an export, a trim, or a publish.
