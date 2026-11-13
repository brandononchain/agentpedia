# What a device change does not carry

The checklist is the user's own list. `kind` is one of `login`, `authenticator`, `files`, `subscription`, or `other`. `where` is a place they name, such as a password manager or an external drive. It is not the secret itself.

[RFC 6238](https://www.rfc-editor.org/rfc/rfc6238) defines TOTP as HOTP with a time-based moving factor. The shared secret is an input to that algorithm. Copying contacts or photos does not recreate the secret. If an authenticator row is `must_move=yes` and `where` is empty, the script marks `missing-where` and `ready=no`. The user names the place that secret already lives, or changes the row to say the account will be set up again. This skill does not sign in and does not print a one-time code.

Some sign-in methods stay on the old device until the user has already turned on a sync they can name. The script does not decide which products sync. It records only the place the user wrote.

A `where` or `account` value that is only digits, or a password, key, token, or seed written as an assignment, is `secretish`. Remove it. The words "password manager" are a place name, not an assignment, so they stay.

`ready=yes` means every row has a known kind, no secret-shaped value, and every `must_move=yes` row names a place. It does not mean the new device already has those accounts.
