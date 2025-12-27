# Data Model

## Table layout
- Table: single-table with `PK` (HASH), `SK` (RANGE)
- GSI1: `GSI1PK` (HASH), `GSI1SK` (RANGE) for device-centric queries

## Item shapes
### Event item
- PK: `TENANT#{tenantId}#USER#{userId}`
- SK: `EVENT#{yyyy-mm-dd}#{ts_epoch_ms}#{eventId}`
- GSI1PK: `DEVICE#{deviceId}`
- GSI1SK: `TS#{ts_epoch_ms}#USER#{userId}`
- Attributes: `eventType`, `deviceId`, `ts`, `payload`, `createdAt`

### Rollup item (daily)
- PK: `TENANT#{tenantId}#USER#{userId}`
- SK: `ROLLUP#DAY#{yyyy-mm-dd}`
- Attributes: `counters` map keyed by eventType plus `total`, `updatedAt`

## Access patterns
1. **Ingest event**: `TransactWriteItems` with conditional put to prevent duplicates; update rollup with atomic `ADD` counters.
2. **Query rollups by date range**: `Query` on PK with `SK BETWEEN ROLLUP#DAY#start AND ROLLUP#DAY#end`.
3. **Query events by device (GSI path)**: `Query` GSI1 with `GSI1PK = DEVICE#{deviceId}`, ordered by `GSI1SK` for recency.

## Idempotency
- Event deduplication uses conditional put on PK/SK; idempotency key comes from `Idempotency-Key` header or `eventId` in body.
- Duplicate events return `duplicate_ignored=true` and do not increment rollups.
