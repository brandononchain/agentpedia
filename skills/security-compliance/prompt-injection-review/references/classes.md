# Instruction classes

These names are this shelf's wording for the failure OWASP documents as LLM01, prompt injection, in the [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/). The descriptions below are not a copy of that entry.

- Direct override. The user-visible text tells the agent to ignore earlier instructions, reveal a hidden prompt, or change its job.
- Hidden text. Text is present for a machine and easy for a person to miss: same-color text, a comment, a zero-width character, or an HTML tag that is not shown.
- Untrusted tool output. A page, a file, an email, or a tool result contains instructions aimed at the agent rather than facts aimed at the user.
- Exfiltration ask. The text tells the agent to send data onward, including to a URL, a webhook, or another tool.

A hit on a class is a reason to stop and ask. It is not a working exploit, and this file does not include payloads.
