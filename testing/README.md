# Local Testing Setup for Odoo Inventory API

This folder contains everything you need to test the Lambda function locally before deploying to AWS.

## Quick Start

1. **Install dependencies:**
   ```bash
   cd testing
   pip install -r requirements.txt
   ```

2. **Create environment file:**
   ```bash
   cp .env.template .env
   # Edit .env with your actual Odoo credentials
   ```

3. **Start local server:**
   ```bash
   python local_server.py
   ```

4. **Test with Postman or run automated tests:**
   ```bash
   python test_api.py
   ```

## Files Overview

### Configuration Files
- **`.env.template`** - Template for environment variables
- **`.env`** - Your actual credentials (create from example, not tracked in git)
- **`.gitignore`** - Ensures .env file is not committed
- **`requirements.txt`** - Python dependencies for local testing

### Testing Scripts
- **`local_server.py`** - Flask server that runs your Lambda function locally
- **`test_api.py`** - Automated test suite (can run with or without pytest)
- **`postman_collection.json`** - Postman collection for manual testing

## Local Server Usage

The local server runs on `http://localhost:8000` by default (configurable via `LOCAL_PORT` in .env).

### Available Endpoints:
- `GET /` - API documentation
- `GET /health` - Health check and environment validation
- `GET /inventory` - List inventory items (main endpoint)
- `OPTIONS /inventory` - CORS preflight

### Example Requests:

**Basic inventory list:**
```bash
curl http://localhost:8000/inventory
```

**With pagination:**
```bash
curl "http://localhost:8000/inventory?limit=10&offset=0"
```

**Search products:**
```bash
curl "http://localhost:8000/inventory?search=laptop"
```

**With authentication (if enabled):**
```bash
curl -H "x-client-id: your_id" -H "x-client-secret: your_secret" http://localhost:8000/inventory
```

## Automated Testing

Run the test suite:
```bash
# Run with pytest (recommended)
pytest test_api.py -v

# Or run manually
python test_api.py
```

### Test Coverage:
- ✅ CORS preflight requests
- ✅ Basic inventory listing
- ✅ Pagination functionality
- ✅ Search functionality
- ✅ Authentication (if configured)
- ✅ Method validation
- ✅ HTTP server endpoints
- ✅ Error handling

## Postman Testing

1. **Import collection:**
   - Open Postman
   - Import `postman_collection.json`

2. **Configure variables:**
   - Set `base_url` to `http://localhost:8000`
   - Set `client_id` and `client_secret` if using authentication

3. **Test endpoints:**
   - Start with "Health Check"
   - Try "List All Inventory"
   - Test different query parameters

## Sample Responses

### Successful Inventory Response:
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "name": "Laptop Computer",
      "price": 999.99,
      "cost_price": 750.00,
      "currency": {
        "id": 1,
        "name": "USD"
      },
      "tags": [
        {
          "id": 5,
          "name": "Electronics",
          "color": 2
        }
      ]
    }
  ],
  "pagination": {
    "total_count": 150,
    "limit": 100,
    "offset": 0,
    "has_more": true
  },
  "filters_applied": {
    "search_term": "",
    "category_id": ""
  }
}
```

### Health Check Response:
```json
{
  "status": "healthy",
  "service": "Odoo Inventory API Local Server",
  "environment_check": {
    "ODOO_URL": true,
    "ODOO_DB": true,
    "ODOO_USERNAME": true,
    "ODOO_PASSWORD": true,
    "CLIENT_ID": false,
    "CLIENT_SECRET": false
  }
}
```

### Error Response:
```json
{
  "error": "Could not authenticate with Odoo: Authentication failed"
}
```

## Troubleshooting

### Common Issues:

1. **"Missing required environment variables"**
   - Create `.env` file from `.env.template`
   - Fill in your actual Odoo credentials

2. **"Connection refused" or server not starting**
   - Check if port 8000 is available
   - Change `LOCAL_PORT` in `.env` if needed

3. **"Could not authenticate with Odoo"**
   - Verify your Odoo credentials in `.env`
   - Check if your Odoo instance is accessible
   - Ensure XML-RPC is enabled in Odoo

4. **"Odoo API error"**
   - Check Odoo server logs
   - Verify user permissions in Odoo
   - Ensure product.product model is accessible

### Debug Mode:
The Flask server runs in debug mode by default, so you'll see detailed error messages and automatic reloading when you modify code.

## Next Steps

Once local testing passes:
1. Deploy the Lambda function to AWS
2. Set up environment variables in Lambda console
3. Create Function URL
4. Test the deployed endpoint
5. Update your frontend to use the production URL

## Security Notes

- Never commit the `.env` file to version control
- Use strong, unique credentials for production
- Consider using AWS Secrets Manager for production credentials
- Test authentication thoroughly before deploying