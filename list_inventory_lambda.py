import xmlrpc.client
import json
import os
import ssl

# --- Odoo Connection Configuration ---
ODOO_URL = os.environ.get('ODOO_URL')
ODOO_DB = os.environ.get('ODOO_DB')
ODOO_USERNAME = os.environ.get('ODOO_USERNAME')
ODOO_PASSWORD = os.environ.get('ODOO_PASSWORD')

# --- Client Authentication Configuration ---
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

# --- SSL Configuration ---
VERIFY_SSL = os.environ.get('VERIFY_SSL', 'false').lower() == 'true'

def lambda_handler(event, context):
    """
    Main handler function for AWS Lambda.
    Handles multiple endpoints for Odoo inventory and tag management.
    Compatible with Lambda Function URLs.
    """
    
    # Handle CORS preflight requests
    request_context = event.get('requestContext', {})
    http_method = request_context.get('http', {}).get('method')
    
    if http_method == 'OPTIONS':
        return {
            'statusCode': 204,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, x-client-id, x-client-secret'
            }
        }
    
    if http_method not in ['GET', 'POST', 'PUT', 'DELETE']:
        return {
            'statusCode': 405, 
            'body': json.dumps({'error': 'Method Not Allowed'})
        }
    
    # Parse the path to determine the endpoint
    raw_path = event.get('rawPath', '/')
    path_parts = [part for part in raw_path.split('/') if part]
    
    # Route to appropriate handler based on path and method
    try:
        if not path_parts:  # Root path "/"
            if http_method in ['GET', 'POST']:
                return handle_list_inventory(event, context)
            else:
                return {'statusCode': 405, 'body': json.dumps({'error': 'Method Not Allowed for inventory listing'})}
        
        elif path_parts[0] == 'tags':
            if http_method == 'GET':
                return handle_list_tags(event, context)
            elif http_method == 'POST':
                # Check if this is a search or create request based on the body
                try:
                    if event.get('body'):
                        data = json.loads(event['body'])
                        if 'tag_name' in data or 'search' in data:
                            # This is a search request
                            return handle_list_tags(event, context)
                        elif 'name' in data:
                            # This is a create request
                            return handle_create_tag(event, context)
                        else:
                            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid request body. For search: use "tag_name" or "search". For create: use "name"'})}
                    else:
                        return {'statusCode': 400, 'body': json.dumps({'error': 'Request body is required for POST requests'})}
                except json.JSONDecodeError:
                    return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid JSON in request body'})}
            else:
                return {'statusCode': 405, 'body': json.dumps({'error': 'Method Not Allowed for tags'})}
        
        elif path_parts[0] == 'search':
            if http_method == 'POST':
                return handle_list_inventory(event, context)  # Use same handler with POST method
            else:
                return {'statusCode': 405, 'body': json.dumps({'error': 'Search endpoint only supports POST method'})}
        
        elif path_parts[0] == 'products':
            if http_method == 'POST':
                # Check if this is a create or update request based on the body
                try:
                    if event.get('body'):
                        data = json.loads(event['body'])
                        if 'product_name' in data and 'price' in data:
                            # This is an update request
                            return handle_update_product(event, context)
                        elif 'name' in data and ('cost' in data or 'price' in data):
                            # This is a create request
                            return handle_create_product(event, context)
                        else:
                            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid request body. For create: use "name" and "price" (or legacy "cost"). For update: use "product_name" and "price"'})}
                    else:
                        return {'statusCode': 400, 'body': json.dumps({'error': 'Request body is required'})}
                except json.JSONDecodeError:
                    return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid JSON in request body'})}
            elif http_method == 'PUT':
                return handle_update_product(event, context)
            else:
                return {'statusCode': 405, 'body': json.dumps({'error': 'Method Not Allowed for products'})}
        
        else:
            return {'statusCode': 404, 'body': json.dumps({'error': 'Endpoint not found'})}
            
    except Exception as e:
        print(f"Routing error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

def authenticate_request(event):
    """Authenticate the client request and return Odoo connection objects."""
    
    # --- Step 0: Authenticate the client request ---
    if CLIENT_ID and CLIENT_SECRET:
        request_headers = event.get('headers', {})
        
        # Handle case-insensitive header lookup (HTTP headers can be case-insensitive)
        received_client_id = None
        received_client_secret = None
        
        for key, value in request_headers.items():
            if key.lower() == 'x-client-id':
                received_client_id = value
            elif key.lower() == 'x-client-secret':
                received_client_secret = value
        
        if not (received_client_id == CLIENT_ID and received_client_secret == CLIENT_SECRET):
            print("Authentication failed: Invalid client ID or secret.")
            return None, None, {
                'statusCode': 401,
                'body': json.dumps({'error': 'Unauthorized'})
            }
    
    # --- Step 1: Authenticate with Odoo ---
    try:
        # Create SSL context based on VERIFY_SSL setting
        ssl_context = ssl.create_default_context()
        if not VERIFY_SSL:
            # Disable SSL verification for local testing or self-signed certificates
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            print("⚠️  SSL verification disabled - not recommended for production")
        
        common = xmlrpc.client.ServerProxy(
            f'https://{ODOO_URL}/xmlrpc/2/common',
            context=ssl_context
        )
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            raise Exception("Authentication failed. Please check credentials.")
        
        models = xmlrpc.client.ServerProxy(
            f'https://{ODOO_URL}/xmlrpc/2/object',
            context=ssl_context
        )
        
        return uid, models, None
            
    except Exception as e:
        print(f"Odoo Authentication Error: {e}")
        return None, None, {
            'statusCode': 500, 
            'body': json.dumps({'error': f'Could not authenticate with Odoo: {e}'})
        }

def handle_list_inventory(event, context):
    """Handle GET / and POST / - List inventory items with query params or JSON body."""
    
    # Authenticate
    uid, models, auth_error = authenticate_request(event)
    if auth_error:
        return auth_error
    
    # Determine if this is GET (query params) or POST (JSON body)
    http_method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    
    if http_method == 'POST':
        # Parse JSON body for POST requests
        try:
            if not event.get('body'):
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Request body is required for POST search'})
                }
            
            search_data = json.loads(event['body'])
            
            # Extract search parameters from JSON (only product_name is used for search)
            search_term = search_data.get('product_name', '')
            limit = int(search_data.get('limit', 100))
            offset = int(search_data.get('offset', 0))
            category_id = search_data.get('category_id', '')
            
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON in request body'})
            }
    else:
        # Parse query parameters for GET requests (backward compatibility)
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 100))  # Default limit of 100 items
        offset = int(query_params.get('offset', 0))   # Default offset of 0
        search_term = query_params.get('search', '')  # Optional search term
        category_id = query_params.get('category_id', '')  # Optional category filter
    
    # --- Step 2: Retrieve inventory items from Odoo ---
    try:
        
        # Build search domain - only search by product name
        domain = [('type', '=', 'product')]  # Only get stockable products
        
        if search_term:
            domain.append('|')
            domain.append(('name', 'ilike', search_term))
            domain.append(('default_code', 'ilike', search_term))
        
        if category_id:
            domain.append(('categ_id', '=', int(category_id)))
        
        # Fields to retrieve - focused on name, price, and tags
        fields = [
            'id',
            'name',
            'list_price',
            'standard_price',  # Cost price
            'currency_id',
            'product_tag_ids'  # Product tags
        ]
        
        # Get product IDs first
        product_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'search',
            [domain],
            {'limit': limit, 'offset': offset, 'order': 'name'}
        )
        
        if not product_ids:
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'success': True,
                    'found': False,
                    'data': [],
                    'total_count': 0,
                    'limit': limit,
                    'offset': offset,
                    'message': f'No products found matching: {search_term}' if search_term else 'No products found'
                })
            }
        
        # Get detailed product information
        products = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'read',
            [product_ids, fields]
        )
        
        # Get total count for pagination
        total_count = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'search_count',
            [domain]
        )
        
        # Get tag details if products have tags
        all_tag_ids = []
        for product in products:
            if product['product_tag_ids']:
                all_tag_ids.extend(product['product_tag_ids'])
        
        # Remove duplicates and get tag details
        unique_tag_ids = list(set(all_tag_ids))
        tag_details = {}
        
        if unique_tag_ids:
            tags = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'product.tag', 'read',
                [unique_tag_ids, ['id', 'name', 'color']]
            )
            tag_details = {tag['id']: tag for tag in tags}
        
        # Format the response data - simplified to focus on name, price, and tags
        formatted_products = []
        for product in products:
            # Get tags for this product
            product_tags = []
            if product['product_tag_ids']:
                for tag_id in product['product_tag_ids']:
                    if tag_id in tag_details:
                        tag_info = tag_details[tag_id]
                        product_tags.append({
                            'id': tag_info['id'],
                            'name': tag_info['name'],
                            'color': tag_info['color']
                        })
            
            formatted_product = {
                'id': product['id'],
                'name': product['name'],
                'price': product['list_price'],
                'cost_price': product['standard_price'],
                'currency': {
                    'id': product['currency_id'][0] if product['currency_id'] else None,
                    'name': product['currency_id'][1] if product['currency_id'] else ''
                },
                'tags': product_tags
            }
            formatted_products.append(formatted_product)
        
        print(f"Successfully retrieved {len(formatted_products)} products from Odoo")
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': True,
                'found': len(formatted_products) > 0,
                'data': formatted_products,
                'pagination': {
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': (offset + limit) < total_count
                },
                'filters_applied': {
                    'search_term': search_term,
                    'category_id': category_id,
                    'search_method': http_method
                },
                'message': f'Found {len(formatted_products)} product(s)' if len(formatted_products) > 0 else f'No products found matching: {search_term}' if search_term else 'No products found'
            })
        }
        
    except xmlrpc.client.Fault as e:
        print(f"Odoo API Error during product retrieval: {e}")
        return {
            'statusCode': 500, 
            'body': json.dumps({'error': f'Odoo API error: {e.faultString}'})
        }
    except Exception as e:
        print(f"An unexpected error occurred during product retrieval: {e}")
        return {
            'statusCode': 500, 
            'body': json.dumps({'error': 'An unexpected server error occurred.'})
        }

def handle_list_tags(event, context):
    """Handle GET /tags and POST /tags - List all product tags with optional search."""
    
    # Authenticate
    uid, models, auth_error = authenticate_request(event)
    if auth_error:
        return auth_error
    
    # Determine if this is GET (query params) or POST (JSON body)
    http_method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    
    if http_method == 'POST':
        # Parse JSON body for POST requests
        try:
            if not event.get('body'):
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Request body is required for POST search'})
                }
            
            search_data = json.loads(event['body'])
            
            # Extract search parameters from JSON
            search_term = search_data.get('tag_name', search_data.get('search', ''))
            limit = int(search_data.get('limit', 100))
            offset = int(search_data.get('offset', 0))
            
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON in request body'})
            }
    else:
        # Parse query parameters for GET requests (backward compatibility)
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 100))
        offset = int(query_params.get('offset', 0))
        search_term = query_params.get('search', '')
    
    try:
        # Build search domain for tags
        domain = []
        if search_term:
            domain.append(('name', 'ilike', search_term))
        
        # Get tag IDs
        tag_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.tag', 'search',
            [domain],
            {'limit': limit, 'offset': offset, 'order': 'name'}
        )
        
        if not tag_ids:
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'success': True,
                    'data': [],
                    'total_count': 0,
                    'limit': limit,
                    'offset': offset
                })
            }
        
        # Get detailed tag information
        tags = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.tag', 'read',
            [tag_ids, ['id', 'name', 'color']]
        )
        
        # Get total count
        total_count = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.tag', 'search_count',
            [domain]
        )
        
        # Format response
        formatted_tags = []
        for tag in tags:
            formatted_tags.append({
                'id': tag['id'],
                'name': tag['name'],
                'color': tag['color']
            })
        
        print(f"Successfully retrieved {len(formatted_tags)} tags from Odoo")
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': True,
                'data': formatted_tags,
                'pagination': {
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': (offset + limit) < total_count
                },
                'filters_applied': {
                    'search_term': search_term,
                    'search_method': http_method
                }
            })
        }
        
    except Exception as e:
        print(f"Error retrieving tags: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Could not retrieve tags: {e}'})
        }

def handle_create_tag(event, context):
    """Handle POST /tags - Create a new product tag."""
    
    # Authenticate
    uid, models, auth_error = authenticate_request(event)
    if auth_error:
        return auth_error
    
    # Parse request body
    try:
        if not event.get('body'):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        data = json.loads(event['body'])
        
        # Validate required fields
        if 'name' not in data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Tag name is required'})
            }
        
        tag_name = data['name'].strip()
        if not tag_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Tag name cannot be empty'})
            }
        
        # Optional color (default to 0 if not provided)
        color = data.get('color', 0)
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    
    try:
        # Check if tag already exists
        existing_tags = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.tag', 'search',
            [[('name', '=', tag_name)]]
        )
        
        if existing_tags:
            return {
                'statusCode': 409,
                'body': json.dumps({'error': f'Tag "{tag_name}" already exists'})
            }
        
        # Create the tag
        tag_data = {
            'name': tag_name,
            'color': color
        }
        
        tag_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.tag', 'create',
            [tag_data]
        )
        
        print(f"Successfully created tag '{tag_name}' with ID: {tag_id}")
        
        return {
            'statusCode': 201,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Tag created successfully',
                'data': {
                    'id': tag_id,
                    'name': tag_name,
                    'color': color
                }
            })
        }
        
    except Exception as e:
        print(f"Error creating tag: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Could not create tag: {e}'})
        }

def handle_create_product(event, context):
    """Handle POST /products - Create a new product."""
    
    # Authenticate
    uid, models, auth_error = authenticate_request(event)
    if auth_error:
        return auth_error
    
    # Parse request body
    try:
        if not event.get('body'):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        data = json.loads(event['body'])
        
        # Validate required fields - support both 'cost' (legacy) and 'price' (preferred)
        if 'name' not in data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'name is required'})
            }
        
        if 'cost' not in data and 'price' not in data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'price is required (or use legacy "cost" field)'})
            }
        
        product_name = data['name'].strip()
        if not product_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Product name cannot be empty'})
            }
        
        # Get sales price (prefer 'price' over legacy 'cost')
        try:
            sales_price = float(data.get('price', data.get('cost', 0)))
            if sales_price < 0:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Price must be a positive number'})
                }
        except (ValueError, TypeError):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Price must be a valid number'})
            }
        
        # Get optional cost price
        cost_price = None
        if 'cost_price' in data:
            try:
                cost_price = float(data['cost_price'])
                if cost_price < 0:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'Cost price must be a positive number'})
                    }
            except (ValueError, TypeError):
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Cost price must be a valid number'})
                }
        
        # Optional tag IDs
        tag_ids = data.get('tag_ids', [])
        if tag_ids and not isinstance(tag_ids, list):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'tag_ids must be an array of tag IDs'})
            }
        
        # Validate tag IDs exist
        if tag_ids:
            existing_tags = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'product.tag', 'search',
                [[('id', 'in', tag_ids)]]
            )
            if len(existing_tags) != len(tag_ids):
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'One or more tag IDs do not exist'})
                }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    
    try:
        # Check if product already exists
        existing_products = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'search',
            [[('name', '=', product_name)]]
        )
        
        if existing_products:
            return {
                'statusCode': 409,
                'body': json.dumps({'error': f'Product "{product_name}" already exists'})
            }
        
        # Create the product
        product_data = {
            'name': product_name,
            'list_price': sales_price,     # Sales price (from 'price' or 'cost' field)
            'type': 'product',             # Stockable product
            'sale_ok': True,               # Can be sold (as requested)
            'purchase_ok': False,          # Cannot be purchased (as requested)
            'product_tag_ids': [(6, 0, tag_ids)] if tag_ids else []  # Link tags
        }
        
        # Only set cost price if explicitly provided
        if cost_price is not None:
            product_data['standard_price'] = cost_price
        
        product_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'create',
            [product_data]
        )
        
        # Get the created product details for response
        created_product_list = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'read',
            [[product_id], ['id', 'name', 'standard_price', 'list_price', 'product_tag_ids']]
        )
        created_product = created_product_list[0]
        
        # Get tag details if any
        product_tags = []
        if created_product['product_tag_ids']:
            tags = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'product.tag', 'read',
                [created_product['product_tag_ids'], ['id', 'name', 'color']]
            )
            product_tags = tags
        
        print(f"Successfully created product '{product_name}' with ID: {product_id}")
        
        return {
            'statusCode': 201,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Product created successfully',
                'data': {
                    'id': product_id,
                    'name': created_product['name'],
                    'cost_price': created_product['standard_price'],
                    'sale_price': created_product['list_price'],
                    'tags': product_tags,
                    'can_be_sold': True,
                    'can_be_purchased': False
                }
            })
        }
        
    except Exception as e:
        print(f"Error creating product: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Could not create product: {e}'})
        }

def handle_update_product(event, context):
    """Handle PUT /products - Update product price by name."""
    
    # Authenticate
    uid, models, auth_error = authenticate_request(event)
    if auth_error:
        return auth_error
    
    # Parse request body
    try:
        if not event.get('body'):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        data = json.loads(event['body'])
        
        # Validate required fields
        if 'product_name' not in data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'product_name is required'})
            }
        
        if 'price' not in data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'price is required'})
            }
        
        product_name = data['product_name'].strip()
        if not product_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Product name cannot be empty'})
            }
        
        try:
            new_price = float(data['price'])
            if new_price < 0:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Price must be a positive number'})
                }
        except (ValueError, TypeError):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Price must be a valid number'})
            }
        
        # Optional: update cost price as well
        update_cost_price = data.get('update_cost_price', False)
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    
    try:
        # Search for the product by name
        product_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'search',
            [[('name', '=', product_name)]]
        )
        
        if not product_ids:
            # Try partial match if exact match fails
            product_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'product.product', 'search',
                [[('name', 'ilike', product_name)]]
            )
        
        if not product_ids:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': f'Product not found: {product_name}',
                    'suggestion': 'Try using the search API to find the exact product name'
                })
            }
        
        if len(product_ids) > 1:
            # Get product names for multiple matches
            products = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'product.product', 'read',
                [product_ids, ['id', 'name']]
            )
            
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'Multiple products found matching "{product_name}"',
                    'matches': [{'id': p['id'], 'name': p['name']} for p in products],
                    'suggestion': 'Please use the exact product name'
                })
            }
        
        product_id = product_ids[0]
        
        # Get current product details
        current_product_list = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'read',
            [[product_id], ['id', 'name', 'list_price', 'standard_price']]
        )
        current_product = current_product_list[0]
        
        # Prepare update data
        update_data = {
            'list_price': new_price  # Sale price
        }
        
        # Update cost price if requested
        if update_cost_price:
            update_data['standard_price'] = new_price
        
        # Update the product
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'write',
            [[product_id], update_data]
        )
        
        # Get updated product details
        updated_product_list = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'read',
            [[product_id], ['id', 'name', 'list_price', 'standard_price', 'product_tag_ids']]
        )
        updated_product = updated_product_list[0]
        
        # Get tag details if any
        product_tags = []
        if updated_product['product_tag_ids']:
            tags = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'product.tag', 'read',
                [updated_product['product_tag_ids'], ['id', 'name', 'color']]
            )
            product_tags = tags
        
        print(f"Successfully updated product '{product_name}' price from {current_product['list_price']} to {new_price}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Product price updated successfully',
                'data': {
                    'id': updated_product['id'],
                    'name': updated_product['name'],
                    'previous_price': current_product['list_price'],
                    'new_price': updated_product['list_price'],
                    'cost_price': updated_product['standard_price'],
                    'cost_price_updated': update_cost_price,
                    'tags': product_tags
                }
            })
        }
        
    except Exception as e:
        print(f"Error updating product: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Could not update product: {e}'})
        }