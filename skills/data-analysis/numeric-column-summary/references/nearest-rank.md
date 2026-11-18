# Nearest rank

Sort the numeric values ascending. For a percentile P, the rank is `ceil(P / 100 * N)`, with N the numeric count. The reported value is the value at that 1-based rank. Rank is clamped to the closed range 1 through N.

Mean is the exact sum of the numeric values divided by N, printed as an integer when it divides evenly and as a reduced fraction otherwise. The script does not round the mean to a decimal.

Blank cells are counted and skipped. A cell that is not a finite decimal, including a thousands separator such as `1,200`, is non-numeric. The script does not delete those characters to force a parse.

A column with zero numeric values prints `percentiles=not-computed` and no min, max, or mean.
