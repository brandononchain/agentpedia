# What this audit looks at

The names below are this skill's words for a review of one MCP connector. The injection surface follows the failure OWASP documents as LLM01 in the [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/). This note does not copy that entry and does not include a payload.

- Scope. The tool's name and the one job its description states.
- Write. The tool creates or changes something outside the chat.
- Destructive. The tool deletes, overwrites, pays, sends, or cannot be undone.
- Egress. Arguments or results can leave the machine, including a URL the description names.
- Auth. The tool needs a credential, a session, or an account the user did not already accept.
- Injection surface. A tool description, schema, or result can carry instructions aimed at the agent rather than data aimed at the user.

A recommendation is keep, trim, or block for that tool. It is not a claim that the connector is safe.
