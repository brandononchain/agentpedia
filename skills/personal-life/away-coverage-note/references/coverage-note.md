# What the note may contain

A finished note repeats items, owners, date windows, and instructions from the CSV. The away dates come from the command. Every window has to sit inside those dates, including the first and last day. A window that starts before the trip or ends after it is `outside`.

The owner column is someone the user already named. The script does not email that person and does not book travel.

These stay out of the file:

- a door code, alarm code, gate code, PIN, password, or passphrase written with four or more digits after it
- a pet, a plant, a bill, or a task the user did not type
- a dose, a diagnosis, or any change to an instruction about medicine

If an instruction mentions medicine, copy the words and do not add a time they did not write. That line is informational only. It is not medical advice.

When `secretish` is not zero, the note is not finished. The user shares that secret in person and deletes it from the file. The script does not keep a copy, and it does not print a replacement code.
