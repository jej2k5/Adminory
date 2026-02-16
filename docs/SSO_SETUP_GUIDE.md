# SSO Setup Guide

## Overview

Adminory supports enterprise Single Sign-On (SSO) with SAML 2.0 and OAuth 2.0/OIDC protocols. This guide covers setup for major identity providers.

## Prerequisites

- Enterprise plan subscription
- Admin access to your identity provider (IdP)
- Access to Adminory workspace settings

## Supported Identity Providers

- [Okta (SAML)](./sso/OKTA_SAML.md)
- [Azure AD (SAML)](./sso/AZURE_AD_SAML.md)
- [Google Workspace](./sso/GOOGLE_WORKSPACE.md)
- [Generic SAML Provider](./sso/GENERIC_SAML.md)
- OAuth 2.0 / OIDC providers

## SAML 2.0 Setup

### Step 1: Get Service Provider Metadata

1. Navigate to **Workspace Settings > SSO**
2. Click **Configure SAML SSO**
3. Copy the following values:
   - **Entity ID (SP)**: `https://your-domain.com/api/sso/saml/metadata/{workspace_id}`
   - **ACS URL**: `https://your-domain.com/api/sso/saml/acs/{workspace_id}`
   - **Single Logout URL**: `https://your-domain.com/api/sso/saml/logout/{workspace_id}`

Alternatively, download the SP metadata XML:
```bash
curl https://your-domain.com/api/sso/saml/metadata/{workspace_id} > sp-metadata.xml
```

### Step 2: Configure Your IdP

Follow the specific guide for your IdP:
- [Okta SAML Setup](./sso/OKTA_SAML.md)
- [Azure AD SAML Setup](./sso/AZURE_AD_SAML.md)
- [Google Workspace Setup](./sso/GOOGLE_WORKSPACE.md)

### Step 3: Enter IdP Details in Adminory

1. In Adminory, go to **Workspace Settings > SSO > SAML Configuration**
2. Enter the following from your IdP:
   - **IdP Entity ID**: Identity provider entity ID
   - **SSO URL**: SAML 2.0 endpoint (HTTP-POST binding)
   - **SLO URL**: Single logout endpoint (optional)
   - **X.509 Certificate**: Public certificate from IdP

3. Configure attribute mapping:
   ```json
   {
     "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
     "name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
     "first_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
     "last_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname"
   }
   ```

4. Enable JIT (Just-In-Time) provisioning if desired

### Step 4: Test Connection

1. Click **Test SSO Connection**
2. You'll be redirected to your IdP
3. Login with test credentials
4. Verify successful authentication

### Step 5: Configure Domain Mapping (Optional)

Map email domains to auto-discover SSO:

1. Go to **SSO > Domain Mapping**
2. Add domain: `example.com`
3. Users with `@example.com` emails will automatically use SSO

### Step 6: Enable SSO

1. Toggle **Enable SSO**
2. Optionally enable **Enforce SSO** to require SSO for all logins

## OAuth 2.0 / OIDC Setup

### Step 1: Register Application with IdP

Register your application with your OAuth provider (Auth0, Keycloak, etc.):

**Redirect URI**: `https://your-domain.com/api/sso/oauth/callback/{workspace_id}`

### Step 2: Configure OAuth in Adminory

1. Go to **Workspace Settings > SSO > OAuth Configuration**
2. Enter the following:
   - **Client ID**: From your IdP
   - **Client Secret**: From your IdP (encrypted at rest)
   - **Authorization URL**: OAuth authorization endpoint
   - **Token URL**: OAuth token endpoint
   - **Userinfo URL**: OpenID Connect userinfo endpoint (optional)
   - **Scopes**: `openid email profile` (or customize)

### Step 3: Configure Attribute Mapping

Map OAuth/OIDC claims to user attributes:
```json
{
  "email": "email",
  "name": "name",
  "avatar": "picture"
}
```

### Step 4: Test Connection

Click **Test OAuth Connection** to verify configuration.

## Advanced Configuration

### Group/Role Mapping

Map IdP groups to Adminory workspace roles:

```json
{
  "groups": {
    "adminory-admins": "admin",
    "adminory-members": "member",
    "adminory-viewers": "viewer"
  }
}
```

### SAML Settings

Advanced SAML options:

- **Want Assertions Signed**: Require signed SAML assertions (recommended: enabled)
- **Want Messages Signed**: Require signed SAML messages (optional)
- **Allow Unsolicited Responses**: Allow IdP-initiated logins (default: disabled)

### Session Configuration

- **Session Duration**: How long SSO sessions last (default: 8 hours)
- **Force Re-authentication**: Require re-auth after period (optional)

## Troubleshooting

### Common Issues

**Error: "SAML assertion validation failed"**
- Verify X.509 certificate is correct
- Check clock sync between SP and IdP
- Ensure assertion is signed

**Error: "Email not found in assertion"**
- Check attribute mapping configuration
- Verify IdP is sending email attribute
- Review IdP application configuration

**Error: "User not provisioned"**
- Enable JIT provisioning
- Manually create user first
- Check email domain matches

### Debugging

Enable SSO debug logging:
```bash
LOG_LEVEL=DEBUG
```

View SSO audit logs:
```bash
GET /api/internal/audit-logs?action=sso.*
```

### Testing SAML Assertions

Use browser developer tools:
1. Initiate SSO login
2. Intercept POST to ACS endpoint
3. Decode SAMLResponse (base64)
4. Validate XML assertion

## Security Best Practices

1. **Use HTTPS**: Always use HTTPS in production
2. **Certificate Rotation**: Rotate certificates regularly
3. **Validate Assertions**: Enable signature validation
4. **Audit Logging**: Monitor SSO login attempts
5. **Test Regularly**: Test SSO configuration after changes
6. **Backup Credentials**: Maintain emergency access methods
7. **Document Setup**: Keep IdP configuration documented

## Multi-Workspace SSO

For organizations with multiple workspaces:

1. Each workspace can have its own SSO configuration
2. Or share SSO configuration across workspaces (enterprise feature)
3. Use domain mapping to route users to correct workspace

## SSO API Reference

### GET /api/sso/saml/metadata/:workspace_id
Get SP metadata XML

### GET /api/sso/saml/login/:workspace_id
Initiate SAML login

### POST /api/sso/saml/acs/:workspace_id
Assertion Consumer Service (receives SAML response)

### POST /api/sso/saml/logout/:workspace_id
Single Logout endpoint

### GET /api/sso/oauth/authorize/:workspace_id
OAuth authorization redirect

### GET /api/sso/oauth/callback/:workspace_id
OAuth callback endpoint

### POST /api/external/sso/configuration
Create/update SSO configuration (requires workspace admin)

### POST /api/external/sso/test-connection
Test SSO configuration

---

For provider-specific guides, see:
- [Okta SAML Setup](./sso/OKTA_SAML.md)
- [Azure AD SAML Setup](./sso/AZURE_AD_SAML.md)
- [Google Workspace Setup](./sso/GOOGLE_WORKSPACE.md)
- [Generic SAML Setup](./sso/GENERIC_SAML.md)
