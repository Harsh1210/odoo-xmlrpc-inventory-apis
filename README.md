# Odoo 17 Inventory Management Lambda APIs

This repository contains AWS Lambda functions for managing Odoo 17 inventory through REST APIs.

## 🚀 API Endpoints Overview

| Endpoint | Method | Description | Link |
|----------|--------|-------------|------|
| `/` | GET | [List all inventory items](#list-inventory-get) | Query-based listing |
| `/` | POST | [Search inventory items](#search-inventory-post) | JSON-based search |
| `/tags` | GET | [List all product tags](#list-tags-get) | Get available tags |
| `/tags` | POST | [Create new product tag](#create-tag-post) | Add new tag |
| `/products` | POST | [Create new product](#create-product-post) | Add new product |
| `/products` | PUT | [Update product price](#update-product-put) | Update pricing |

## 📋 API Documentation

### List Inventory (GET)

**Endpoint**: `GET /`  
**Description**: Retrieves inventory items using query parameters (backward compatibility)

**Query Parameters:**
- `limit` (optional): Number of items to return (default: 100)
- `offset` (optional): Number of items to skip for pagination (default: 0)
- `search` (optional): Search term to filter by product name or SKU
- `category_id` (optional): Filter by product category ID

**Request Example:**
```bash
curl -H "x-client-id: your_client_id" \
     -H "x-client-secret: your_client_secret" \
     "YOUR_FUNCTION_URL?search=CHANA&limit=10"
```

**Response Example:**
```json
{
  "success": true,
  "found": true,
  "data": [
    {
      "id": 123,
      "name": "CHANA AUSTRALIA PREMIUM",
      "price": 299.99,
      "cost_price": 199.99,
      "currency": {"id": 1, "name": "INR"},
      "tags": [
        {"id": 5, "name": "Premium Quality", "color": 3}
      ]
    }
  ],
  "pagination": {
    "total_count": 1,
    "limit": 10,
    "offset": 0,
    "has_more": false
  },
  "message": "Found 1 product(s)"
}
```

---

### Search Inventory (POST)

**Endpoint**: `POST /`  
**Description**: Search inventory items using JSON body for more flexible queries

**Request Body:**
```json
{
  "product_name": "CHANA GOLD",
  "limit": 10,
  "offset": 0,
  "category_id": 5
}
```

**Request Example:**
```bash
curl -X POST \
  -H "x-client-id: your_client_id" \
  -H "x-client-secret: your_client_secret" \
  -H "Content-Type: application/json" \
  -d '{"product_name": "CHANA GOLD"}' \
  YOUR_FUNCTION_URL
```

**Response Example:**
```json
{
  "success": true,
  "found": true,
  "data": [
    {
      "id": 125,
      "name": "CHANA GOLD PREMIUM",
      "price": 7500.0,
      "cost_price": 6000.0,
      "currency": {"id": 1, "name": "INR"},
      "tags": [
        {"id": 3, "name": "Premium Quality", "color": 3}
      ]
    }
  ],
  "pagination": {
    "total_count": 1,
    "limit": 100,
    "offset": 0,
    "has_more": false
  },
  "filters_applied": {
    "search_term": "CHANA GOLD",
    "search_method": "POST"
  },
  "message": "Found 1 product(s)"
}
```

---

### List Tags (GET)

**Endpoint**: `GET /tags`  
**Description**: Retrieve all available product tags with optional search

**Query Parameters:**
- `limit` (optional): Number of tags to return (default: 100)
- `offset` (optional): Number of tags to skip for pagination (default: 0)
- `search` (optional): Search term to filter tags by name

**Request Example:**
```bash
curl -H "x-client-id: your_client_id" \
     -H "x-client-secret: your_client_secret" \
     "YOUR_FUNCTION_URL/tags?search=premium"
```

**Response Example:**
```json
{
  "success": true,
  "data": [
    {
      "id": 5,
      "name": "Premium Quality",
      "color": 3
    },
    {
      "id": 8,
      "name": "Premium Grade",
      "color": 4
    }
  ],
  "pagination": {
    "total_count": 2,
    "limit": 100,
    "offset": 0,
    "has_more": false
  },
  "filters_applied": {
    "search_term": "premium"
  }
}
```

---

### Create Tag (POST)

**Endpoint**: `POST /tags`  
**Description**: Create a new product tag

**Request Body:**
```json
{
  "name": "Premium Quality",
  "color": 3
}
```

**Request Example:**
```bash
curl -X POST \
  -H "x-client-id: your_client_id" \
  -H "x-client-secret: your_client_secret" \
  -H "Content-Type: application/json" \
  -d '{"name": "Premium Quality", "color": 3}' \
  YOUR_FUNCTION_URL/tags
```

**Response Example:**
```json
{
  "success": true,
  "message": "Tag created successfully",
  "data": {
    "id": 5,
    "name": "Premium Quality",
    "color": 3
  }
}
```

---

### Create Product (POST)

**Endpoint**: `POST /products`  
**Description**: Create a new product with specified name, cost, and tags

**Request Body:**
```json
{
  "name": "CHANA PREMIUM GRADE A",
  "cost": 150.75,
  "tag_ids": [1, 2, 3]
}
```

**Request Example:**
```bash
curl -X POST \
  -H "x-client-id: your_client_id" \
  -H "x-client-secret: your_client_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CHANA PREMIUM GRADE A",
    "cost": 150.75,
    "tag_ids": [1, 2]
  }' \
  YOUR_FUNCTION_URL/products
```

**Response Example:**
```json
{
  "success": true,
  "message": "Product created successfully",
  "data": {
    "id": 123,
    "name": "CHANA PREMIUM GRADE A",
    "cost_price": 150.75,
    "sale_price": 150.75,
    "tags": [
      {"id": 1, "name": "Premium Quality", "color": 3},
      {"id": 2, "name": "Organic", "color": 2}
    ],
    "can_be_sold": true,
    "can_be_purchased": false
  }
}
```

---

### Update Product (PUT)

**Endpoint**: `PUT /products`  
**Description**: Update product price by product name

**Request Body:**
```json
{
  "product_name": "CHANA PREMIUM GRADE A",
  "price": 175.50,
  "update_cost_price": false
}
```

**Request Example:**
```bash
curl -X PUT \
  -H "x-client-id: your_client_id" \
  -H "x-client-secret: your_client_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "CHANA PREMIUM GRADE A",
    "price": 175.50
  }' \
  YOUR_FUNCTION_URL/products
```

**Response Example:**
```json
{
  "success": true,
  "message": "Product price updated successfully",
  "data": {
    "id": 123,
    "name": "CHANA PREMIUM GRADE A",
    "previous_price": 150.75,
    "new_price": 175.50,
    "cost_price": 150.75,
    "cost_price_updated": false,
    "tags": [
      {"id": 1, "name": "Premium Quality", "color": 3}
    ]
  }
}
```

## 🔐 Authentication

All endpoints require authentication headers:
```
x-client-id: your_client_id
x-client-secret: your_client_secret
```

## 📝 Environment Variables Required

```
ODOO_URL=your-odoo-domain.com
ODOO_DB=your_database_name
ODOO_USERNAME=your_odoo_username
ODOO_PASSWORD=your_odoo_password
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
VERIFY_SSL=true
```

## 🚀 Deployment Instructions

### Step 1: Create Lambda Function

1. **Go to AWS Lambda Console**
2. **Click "Create function"**
3. **Configure basic settings:**
   - Function name: `odoo-inventory-api`
   - Runtime: `Python 3.9` or higher
   - Architecture: `x86_64`
   - Execution role: Create a new role with basic Lambda permissions

### Step 2: Upload Code

1. **In the Lambda function console, go to "Code" tab**
2. **Delete the default `lambda_function.py` content**
3. **Copy and paste the entire content of `list_inventory_lambda.py`**
4. **Click "Deploy" to save the changes**

### Step 3: Configure Function Settings

1. **Go to "Configuration" tab → "General configuration"**
2. **Edit and set:**
   - Handler: `lambda_function.lambda_handler`
   - Timeout: `30 seconds` (recommended)
   - Memory: `256 MB` (recommended)

### Step 4: Set Environment Variables

1. **Go to "Configuration" tab → "Environment variables"**
2. **Click "Edit" and add the following variables:**

   ```
   ODOO_URL=your-odoo-domain.com
   ODOO_DB=your_database_name
   ODOO_USERNAME=your_odoo_username
   ODOO_PASSWORD=your_odoo_password
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   VERIFY_SSL=true
   ```

   **⚠️ Important:** Replace `your_odoo_username` and `your_odoo_password` with your actual Odoo credentials.

### Step 5: Create Function URL

1. **Go to "Configuration" tab → "Function URL"**
2. **Click "Create function URL"**
3. **Configure:**
   - Auth type: `NONE` (we're using custom authentication)
   - CORS: Enable and configure:
     - Allow origin: `*` (or specify your domain)
     - Allow headers: `x-client-id, x-client-secret, content-type`
     - Allow methods: `GET, POST, PUT, OPTIONS`
4. **Click "Save"**
5. **Copy the Function URL** (you'll need this for testing)

### Step 6: Test the Deployment

Use the Function URL to test your deployment:

```bash
# Replace YOUR_FUNCTION_URL with your actual Function URL
curl -H "x-client-id: your_client_id" -H "x-client-secret: your_client_secret" YOUR_FUNCTION_URL
```

Example with a real Function URL:
```bash
curl -H "x-client-id: your_client_id" -H "x-client-secret: your_client_secret" https://your-lambda-function-url.amazonaws.com/
```

## 🎯 Usage After Deployment

### Authentication
All requests require authentication headers:
```
x-client-id: your_client_id
x-client-secret: your_client_secret
```

### Query Parameters
- `limit` (optional): Number of items to return (default: 100, max recommended: 1000)
- `offset` (optional): Number of items to skip for pagination (default: 0)
- `search` (optional): Search term to filter by product name or SKU
- `category_id` (optional): Filter by product category ID

### Search Examples
```bash
# Search for specific product
curl -H "x-client-id: your_client_id" -H "x-client-secret: your_client_secret" "YOUR_FUNCTION_URL?search=CHANA%20AUSTRALIA"

# Search with partial match
curl -H "x-client-id: your_client_id" -H "x-client-secret: your_client_secret" "YOUR_FUNCTION_URL?search=CHANA"

# Case-insensitive search
curl -H "x-client-id: your_client_id" -H "x-client-secret: your_client_secret" "YOUR_FUNCTION_URL?search=chana%20australia"
```

### Pagination Examples
```bash
# First 10 items
curl -H "x-client-id: your_client_id" -H "x-client-secret: your_client_secret" "YOUR_FUNCTION_URL?limit=10&offset=0"

# Next 10 items
curl -H "x-client-id: your_client_id" -H "x-client-secret: your_client_secret" "YOUR_FUNCTION_URL?limit=10&offset=10"
```

## 🔧 Troubleshooting

### Common Issues and Solutions

**1. "Unauthorized" Error (401)**
- Check that you're including both `x-client-id` and `x-client-secret` headers
- Verify the header values match the environment variables in Lambda
- Ensure headers are case-sensitive: use lowercase `x-client-id`, not `X-Client-Id`

**2. "Could not authenticate with Odoo" Error (500)**
- Verify Odoo credentials in Lambda environment variables
- Check if Odoo instance is accessible from the internet
- Ensure XML-RPC is enabled in your Odoo instance

**3. SSL Certificate Errors**
- Set `VERIFY_SSL=false` for testing with self-signed certificates
- Set `VERIFY_SSL=true` for production with valid SSL certificates

**4. Empty Results**
- Check if your Odoo instance has products with `type='product'`
- Verify user permissions in Odoo for accessing product data
- Try without search/filter parameters first

**5. Timeout Errors**
- Increase Lambda timeout in Configuration → General configuration
- Reduce the `limit` parameter in your requests
- Check Odoo server performance

### Monitoring and Logs
- View Lambda logs in CloudWatch Logs
- Monitor function performance in Lambda console
- Set up CloudWatch alarms for errors and timeouts

## 🔒 Security Notes

- Always use HTTPS endpoints (Lambda Function URLs are HTTPS by default)
- Store sensitive credentials in AWS Systems Manager Parameter Store or AWS Secrets Manager for production
- Consider implementing rate limiting using AWS API Gateway
- Use VPC endpoints if your Odoo instance is in a private network
- Regularly rotate API credentials
- Enable AWS CloudTrail for API access logging
- Consider using AWS WAF for additional protection

## 🎯 n8n Integration

All these APIs are designed to work seamlessly with n8n workflows. Use the HTTP Request node with:

- **Authentication Headers**: Set in the Headers section
- **JSON Body**: For POST/PUT requests
- **Query Parameters**: For GET requests
- **Response Parsing**: Use the `found` field to check if products exist

Example n8n workflow:
```
Webhook → Search Product → Create Product (if not found) → Update Price → Send Notification
```