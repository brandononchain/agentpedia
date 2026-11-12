# Chapter rules this list checks

YouTube's help page for video chapters, [Video chapters](https://support.google.com/youtube/answer/9884579), says a creator adds chapters by putting a list of timestamps and titles in the video description. The page states three requirements:

- The first timestamp starts with 00:00.
- The list has at least three timestamps, in ascending order.
- The minimum length for a video chapter is 10 seconds.

This skill checks those three and does not add a fourth. A chapter's length is the gap until the next timestamp. The last chapter's length is the gap until the runtime the user supplies. Without that runtime the script cannot confirm the last chapter, so it prints `last_length=not-checked` and `ready=no`.

When every timestamp is under one hour, each line is `MM:SS` plus the title, and the first line is `00:00`, the form the help page shows. When any timestamp or the runtime is one hour or longer, lines use `H:MM:SS` because `MM:SS` cannot hold them, and a zero start is written `0:00:00`. `first_is_zero=yes` means the first time is zero seconds either way.

The title on each line is copied from the user's file. The script does not upload the video, and it does not turn automatic chapters on or off.
