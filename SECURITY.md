# Security Guidelines

## 🔒 Sensitive Information

This repository contains template files and example code. **Never commit sensitive information** such as:

- Database credentials
- API keys and secrets
- SSL certificates and private keys
- Production URLs and endpoints
- Personal access tokens

## 📁 Protected Files

The following files are protected by `.gitignore` and should contain your actual credentials:

- `testing/.env` - Local testing environment variables
- `docker/.env` - Docker environment variables (if using Docker setup)
- `ssl-certs/` - SSL certificates directory
- `nginx/certs/` - Nginx SSL certificates

## 🛠️ Setup Instructions

### 1. Environment Files

Copy template files and add your credentials:

```bash
# For local testing
cp testing/.env.template testing/.env
# Edit testing/.env with your actual Odoo credentials

# For Docker deployment (if applicable)
cp docker/.env.example docker/.env
# Edit docker/.env with your actual credentials
```

### 2. Required Environment Variables

**Odoo Connection:**
- `ODOO_URL` - Your Odoo instance domain
- `ODOO_DB` - Database name
- `ODOO_USERNAME` - Odoo username
- `ODOO_PASSWORD` - Odoo password

**API Authentication:**
- `CLIENT_ID` - Your API client ID
- `CLIENT_SECRET` - Your API client secret

**SSL Configuration:**
- `VERIFY_SSL` - Set to `true` for production, `false` for testing

### 3. AWS Lambda Environment Variables

When deploying to AWS Lambda, set these environment variables in the Lambda console:

```
ODOO_URL=your-actual-odoo-domain.com
ODOO_DB=your_actual_database_name
ODOO_USERNAME=your_actual_username
ODOO_PASSWORD=your_actual_password
CLIENT_ID=your_actual_client_id
CLIENT_SECRET=your_actual_client_secret
VERIFY_SSL=true
```

## 🚨 Security Best Practices

### For Development:
1. Use `.env` files for local development (never commit these)
2. Use different credentials for development and production
3. Regularly rotate API keys and passwords
4. Use SSL/TLS for all connections

### For Production:
1. Use AWS Secrets Manager or Systems Manager Parameter Store
2. Enable SSL certificate verification (`VERIFY_SSL=true`)
3. Use VPC endpoints for private network access
4. Implement rate limiting and monitoring
5. Use least-privilege IAM roles

### For Team Collaboration:
1. Share template files, not actual credentials
2. Use secure channels for credential sharing
3. Document which credentials are needed
4. Use different credentials for each team member

## 🔍 Checking for Sensitive Data

Before committing, always check:

```bash
# Check what files will be committed
git status

# Check file contents before adding
git diff

# Ensure .env files are ignored
git check-ignore testing/.env
```

## 📞 Reporting Security Issues

If you find sensitive information accidentally committed:

1. **DO NOT** create a public issue
2. Contact the repository maintainer privately
3. We will address the issue immediately
4. Consider the commit history compromised and rotate affected credentials

## 🛡️ Additional Security Measures

- Enable 2FA on all accounts
- Use strong, unique passwords
- Monitor access logs regularly
- Keep dependencies updated
- Use security scanning tools