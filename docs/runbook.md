# Runbook

## Deploy
- Update `samconfig.toml` or export parameters, then run `./scripts/deploy.sh` (or `sam deploy --guided`).
- Ensure SSM parameters for Google/Apple client IDs and secrets exist before deployment.
- Outputs: `ApiBaseUrl`, `UserPoolId`, `UserPoolDomain`, `AppClientId`, `TableName`.

## Rollback
- Use CloudFormation to execute a stack rollback or deploy previous template version.
- If Cognito domain changes are involved, deletion may require cleaning up Hosted UI domain first.

## Alarms triage
- **LambdaErrorAlarm**: inspect Lambda CloudWatch Logs for stack traces; redeploy if code issue.
- **LambdaDurationAlarm**: review X-Ray traces; consider increasing memory or optimizing DynamoDB queries.
- **Api5XXAlarm**: check API Gateway execution logs; verify downstream Lambda health.
- **ApiThrottleAlarm**: examine traffic patterns; raise limits or enable Usage Plan/API keys as needed.

## Operational checks
- Verify rate limits: use `aws apigateway get-stage` to confirm burst/rate settings.
- Confirm payload limits: `MAX_BODY_BYTES` environment variable and API Gateway default (10MB) documented.
- Audit RBAC: ensure users are placed into `user` or `admin` Cognito groups; admin-only endpoint returns 403 for non-admins.

## Troubleshooting
- Local: run `scripts/run_local.sh` to start DynamoDB Local and `sam local start-api`.
- JWT acquisition: follow `scripts/get_token_instructions.md` to obtain tokens via Hosted UI.
- DynamoDB: use `aws dynamodb query/scan --table-name <TableName>` to inspect items; rollups are under `ROLLUP#DAY#` sort keys.
