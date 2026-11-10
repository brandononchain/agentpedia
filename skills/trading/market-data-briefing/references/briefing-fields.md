# Briefing fields

Include only fields you can fill from supplied data.

- Session name and timezone
- As-of timestamp
- For each symbol: last, reference price, source
- Headlines with source, or "none supplied"
- Levels the user said they care about
- Unknowns

Do not compute a change when the reference price was not supplied. Do not add a symbol the user did not ask about.
