# Security

## Authentication
- Cognito User Pool with Hosted UI domain (parameterized).
- App Client uses OAuth2 Authorization Code flow with scopes `openid email profile`.
- Federated providers: Google (native) and Apple (OIDC). Provider secrets are resolved at deploy time via SSM parameters; no secrets are stored in git.

## Authorization & RBAC
- Cognito groups: `user` and `admin` created via IaC.
- API Gateway uses a Cognito authorizer; verified JWT claims are forwarded in `requestContext.authorizer.claims`.
- Lambda enforces group membership (`admin` required for `/v1/admin/ping`). Claims consumed: `sub`, `email`, `cognito:groups`, optional `custom:tenant`.

## Input validation & limits
- JSON Schema enforced at API Gateway via Model + RequestValidator for POST `/v1/events`.
- Defense-in-depth validation in Lambda with `jsonschema`.
- Payload size control: API Gateway documented limit plus Lambda check using `MAX_BODY_BYTES` (returns 413).

## Least privilege & secrets
- Lambda execution roles receive DynamoDB CRUD on the app table and CloudWatch logging; no blanket permissions.
- Provider client IDs/secrets are pulled from SSM parameters using CloudFormation dynamic references at deploy time.

## Observability & guardrails
- Structured JSON logging, correlation IDs, metrics, and tracing powered by AWS Lambda Powertools.
- CloudWatch alarms: Lambda errors, Lambda p95 duration, API 5XX, API throttles.
- Log retention set to 14 days; tracing enabled for API Gateway and Lambda.
