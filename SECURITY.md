# Security And Privacy

Do not report private evidence through public issues.

If you discover a privacy leak in this repository, remove the material from your
local copy and report the affected file path and commit reference without
including the private content itself.

## Public Data Rules

Examples must be synthetic. Avoid:

- real names
- handles
- email addresses
- phone numbers
- street addresses
- real web URLs
- real export archive names
- client or case identifiers

The release check is:

```bash
python scripts/verify_public_repo.py .
```
