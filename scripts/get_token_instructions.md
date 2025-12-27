# Getting a JWT via Cognito Hosted UI (Authorization Code Flow)

1. Deploy the stack and note the outputs `UserPoolId`, `UserPoolDomain`, and `AppClientId`.
2. Ensure Google and Apple identity providers are configured with valid client IDs and secrets in SSM parameters.
3. Open the Hosted UI authorize URL in a browser, replacing placeholders:
   ```
   https://<UserPoolDomain>.auth.<region>.amazoncognito.com/oauth2/authorize?response_type=code&client_id=<AppClientId>&redirect_uri=<callback_url>&scope=openid+email+profile
   ```
4. Sign in with Cognito or federated Google/Apple. After consent, you will be redirected to `<callback_url>?code=<AUTH_CODE>`.
5. Exchange the code for tokens with a POST:
   ```bash
   curl -X POST \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=authorization_code&client_id=<AppClientId>&code=<AUTH_CODE>&redirect_uri=<callback_url>" \
     https://<UserPoolDomain>.auth.<region>.amazoncognito.com/oauth2/token
   ```
6. The JSON response includes `id_token` and `access_token`. Use the `id_token` as the Bearer token for API calls.
7. Add users to the `admin` group in Cognito to access admin-only routes.
