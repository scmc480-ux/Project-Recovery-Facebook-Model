# Facebook Reader v1

Facebook Reader v1 is the only data source included in the public 1.0 release.

## Supported Inputs

- Extracted Facebook JSON export folders.
- Facebook JSON export zip files.
- Lightweight HTML message pages from Facebook exports.

## Unsupported In v1

- Instagram.
- Marketplace-specific reconstruction beyond generic activity/event capture.
- Device recovery.
- Private workspace jobs/checkpoints.
- Automated Pipecleaner campaigns.

## Output Promise

The reader emits normalized objects with:

- stable object IDs
- truth class
- confidence
- source reference
- source hash
- provenance reference
- stage origin

## Normalized Objects

Facebook Reader v1 can emit:

- `message_object`
- `conversation_object`
- `entity_object`
- `event_object`
- `artifact_object`

## Privacy Promise

The public repo contains only fictional sample data. Real evidence belongs
outside the repository and should be supplied as runtime input only.
