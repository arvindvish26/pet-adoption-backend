# Pet Adoption System - REST API Documentation

## Overview
This document provides comprehensive documentation for the Pet Adoption System REST API. The API is built using Django REST Framework and provides full CRUD operations for all modules.

## Authentication
The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## Base URL
```
http://localhost:8000/api/
```

## API Endpoints

### 1. Users Module (`/api/users/`)

#### User Management
- **GET** `/users/` - List all users (Admin only)
- **POST** `/users/` - Register new user
- **GET** `/users/{id}/` - Get user details
- **PUT** `/users/{id}/` - Update user (Owner/Admin)
- **PATCH** `/users/{id}/` - Partial update user (Owner/Admin)
- **DELETE** `/users/{id}/` - Delete user (Admin only)

#### Custom User Actions
- **POST** `/users/login/` - User login (returns JWT tokens)
- **GET** `/users/me/` - Get current user profile
- **PUT** `/users/update_profile/` - Update current user profile
- **POST** `/users/{id}/deactivate/` - Deactivate user (Admin)
- **POST** `/users/{id}/activate/` - Activate user (Admin)

#### Admin Management
- **GET** `/admins/` - List all admins (Admin only)
- **POST** `/admins/` - Create admin (Admin only)
- **GET** `/admins/{id}/` - Get admin details
- **PUT** `/admins/{id}/` - Update admin (Admin only)
- **DELETE** `/admins/{id}/` - Delete admin (Admin only)
- **POST** `/admins/{id}/toggle_superadmin/` - Toggle superadmin status

### 2. Pets Module (`/api/pets/`)

#### Pet Management
- **GET** `/pets/` - List all pets (Public)
- **POST** `/pets/` - Create pet (Admin only)
- **GET** `/pets/{id}/` - Get pet details (Public)
- **PUT** `/pets/{id}/` - Update pet (Admin only)
- **PATCH** `/pets/{id}/` - Partial update pet (Admin only)
- **DELETE** `/pets/{id}/` - Delete pet (Admin only)

#### Custom Pet Actions
- **POST** `/pets/{id}/adopt/` - Adopt a pet (Authenticated users)
- **GET** `/pets/available/` - Get all available pets
- **GET** `/pets/adopted/` - Get all adopted pets (Admin only)
- **GET** `/pets/my_pets/` - Get current user's adopted pets
- **POST** `/pets/{id}/make_available/` - Make adopted pet available (Admin only)
- **GET** `/pets/stats/` - Get pet statistics

#### Query Parameters
- `status` - Filter by status (Available/Adopted)
- `category` - Filter by category ID
- `city` - Filter by city
- `vaccinated` - Filter by vaccination status

### 3. Accessories Module (`/api/accessories/`)

#### Category Management
- **GET** `/categories/` - List all categories (Public)
- **POST** `/categories/` - Create category (Admin only)
- **GET** `/categories/{id}/` - Get category details
- **PUT** `/categories/{id}/` - Update category (Admin only)
- **DELETE** `/categories/{id}/` - Delete category (Admin only)
- **GET** `/categories/{id}/accessories/` - Get accessories in category

#### Accessory Management
- **GET** `/accessories/` - List all accessories (Public)
- **POST** `/accessories/` - Create accessory (Admin only)
- **GET** `/accessories/{id}/` - Get accessory details (Public)
- **PUT** `/accessories/{id}/` - Update accessory (Admin only)
- **PATCH** `/accessories/{id}/` - Partial update accessory (Admin only)
- **DELETE** `/accessories/{id}/` - Delete accessory (Admin only)

#### Custom Accessory Actions
- **PATCH** `/accessories/{id}/update_stock/` - Update stock (Admin only)
- **GET** `/accessories/in_stock/` - Get in-stock accessories
- **GET** `/accessories/out_of_stock/` - Get out-of-stock accessories (Admin only)
- **GET** `/accessories/low_stock/` - Get low-stock accessories (Admin only)
- **GET** `/accessories/stats/` - Get accessory statistics

#### Query Parameters
- `category` - Filter by category ID
- `min_price` - Filter by minimum price
- `max_price` - Filter by maximum price
- `in_stock` - Filter by stock availability

### 4. Addresses Module (`/api/addresses/`)

#### Address Management
- **GET** `/addresses/` - List user's addresses
- **POST** `/addresses/` - Create address
- **GET** `/addresses/{id}/` - Get address details
- **PUT** `/addresses/{id}/` - Update address (Owner/Admin)
- **PATCH** `/addresses/{id}/` - Partial update address (Owner/Admin)
- **DELETE** `/addresses/{id}/` - Delete address (Owner/Admin)

#### Custom Address Actions
- **GET** `/addresses/my_addresses/` - Get current user's addresses
- **GET** `/addresses/shipping/` - Get user's shipping addresses
- **GET** `/addresses/billing/` - Get user's billing addresses
- **POST** `/addresses/{id}/set_default/` - Set address as default
- **GET** `/addresses/by_location/` - Filter addresses by location

#### Query Parameters
- `type` - Filter by address type (shipping/billing)
- `city` - Filter by city
- `state` - Filter by state
- `country` - Filter by country

### 5. Carts Module (`/api/carts/`)

#### Cart Management
- **GET** `/carts/` - List user's carts
- **POST** `/carts/` - Create cart
- **GET** `/carts/{id}/` - Get cart details
- **PUT** `/carts/{id}/` - Update cart (Owner/Admin)
- **DELETE** `/carts/{id}/` - Delete cart (Owner/Admin)

#### Cart Items Management
- **GET** `/cart-items/` - List cart items
- **POST** `/cart-items/` - Create cart item
- **GET** `/cart-items/{id}/` - Get cart item details
- **PUT** `/cart-items/{id}/` - Update cart item (Owner/Admin)
- **PATCH** `/cart-items/{id}/` - Partial update cart item (Owner/Admin)
- **DELETE** `/cart-items/{id}/` - Delete cart item (Owner/Admin)

#### Custom Cart Actions
- **GET** `/carts/my_cart/` - Get or create current user's cart
- **POST** `/carts/{id}/add_item/` - Add item to cart
- **PATCH** `/carts/{id}/update_item/` - Update cart item quantity
- **DELETE** `/carts/{id}/remove_item/` - Remove item from cart
- **DELETE** `/carts/{id}/clear_cart/` - Clear all items from cart
- **GET** `/carts/empty_carts/` - Get empty carts (Admin only)
- **GET** `/carts/stats/` - Get cart statistics (Admin only)

### 6. Orders Module (`/api/orders/`)

#### Order Management
- **GET** `/orders/` - List user's orders
- **POST** `/orders/` - Create order
- **GET** `/orders/{id}/` - Get order details
- **PUT** `/orders/{id}/` - Update order (Admin only)
- **PATCH** `/orders/{id}/` - Partial update order (Admin only)
- **DELETE** `/orders/{id}/` - Delete order (Admin only)

#### Custom Order Actions
- **GET** `/orders/my_orders/` - Get current user's orders
- **GET** `/orders/by_status/` - Get orders by status
- **PATCH** `/orders/{id}/update_status/` - Update order status (Admin only)
- **POST** `/orders/{id}/cancel_order/` - Cancel order
- **GET** `/orders/{id}/tracking/` - Get order tracking info
- **GET** `/orders/processing/` - Get processing orders (Admin only)
- **GET** `/orders/shipped/` - Get shipped orders (Admin only)
- **GET** `/orders/delivered/` - Get delivered orders (Admin only)
- **GET** `/orders/stats/` - Get order statistics (Admin only)

#### Query Parameters
- `status` - Filter by status (Processing/Shipped/Delivered/Cancelled)

### 7. Payments Module (`/api/payments/`)

#### Payment Management
- **GET** `/payments/` - List user's payments
- **POST** `/payments/` - Create payment
- **GET** `/payments/{id}/` - Get payment details
- **PUT** `/payments/{id}/` - Update payment (Admin only)
- **PATCH** `/payments/{id}/` - Partial update payment (Admin only)
- **DELETE** `/payments/{id}/` - Delete payment (Admin only)

#### Custom Payment Actions
- **GET** `/payments/my_payments/` - Get current user's payments
- **GET** `/payments/by_status/` - Get payments by status
- **PATCH** `/payments/{id}/update_status/` - Update payment status (Admin only)
- **POST** `/payments/{id}/process_payment/` - Process payment
- **POST** `/payments/{id}/refund_payment/` - Refund payment (Admin only)
- **GET** `/payments/pending/` - Get pending payments (Admin only)
- **GET** `/payments/completed/` - Get completed payments (Admin only)
- **GET** `/payments/failed/` - Get failed payments (Admin only)
- **GET** `/payments/stats/` - Get payment statistics (Admin only)

#### Query Parameters
- `status` - Filter by status (Pending/Completed/Refunded/Failed)
- `payment_method` - Filter by payment method (UPI/Card/Cash)

## Response Format

### Success Response
```json
{
    "data": [...],
    "message": "Operation successful"
}
```

### Error Response
```json
{
    "error": "Error message",
    "details": {...}
}
```

### Pagination
List endpoints support pagination:
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/pets/?page=2",
    "previous": null,
    "results": [...]
}
```

## Authentication Endpoints

### Login
```http
POST /api/users/login/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

### Token Refresh
```http
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "your_refresh_token"
}
```

## Example Usage

### 1. User Registration
```http
POST /api/users/
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password",
    "password_confirm": "secure_password",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890"
}
```

### 2. Adopt a Pet
```http
POST /api/pets/1/adopt/
Authorization: Bearer <your_token>
```

### 3. Add Item to Cart
```http
POST /api/carts/1/add_item/
Authorization: Bearer <your_token>
Content-Type: application/json

{
    "accessory_id": 5,
    "quantity": 2
}
```

### 4. Create Order
```http
POST /api/orders/
Authorization: Bearer <your_token>
Content-Type: application/json

{
    "cart": 1,
    "shipping_address": 2,
    "billing_address": 3
}
```

### 5. Process Payment
```http
POST /api/payments/1/process_payment/
Authorization: Bearer <your_token>
```

## Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Permissions

- **Public** - No authentication required
- **Authenticated** - Valid JWT token required
- **Owner** - User can only access their own resources
- **Admin** - Staff/admin users only

## Filtering and Search

Most list endpoints support:
- **Filtering** - Use query parameters to filter results
- **Search** - Use `search` parameter for text search
- **Ordering** - Use `ordering` parameter to sort results
- **Pagination** - Use `page` parameter for pagination

## Rate Limiting

API endpoints are rate-limited to prevent abuse. Default limits:
- 1000 requests per hour for authenticated users
- 100 requests per hour for anonymous users
