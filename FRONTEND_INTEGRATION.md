# Frontend Integration Guide (BMS v1.0)

This guide provides frontend developers (React/Vue/Angular) with the essential information required to connect to the BMS API.

## 1. API Documentation (Swagger)
All available endpoints, request bodies, and response schemas are automatically documented and testable at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 2. Authentication Flow (JWT)
We use a standard OAuth2 with Bearer Tokens (Access & Refresh tokens).

1. **Login:** Send `username` (email) and `password` as `application/x-www-form-urlencoded` to `POST /auth/login`.
2. **Response:** You will receive `access_token` and `refresh_token`.
3. **Usage:** Attach the access token to the headers of all protected requests:
   ```http
   Authorization: Bearer <your_access_token>
   ```
4. **Refresh Token:** When the access token expires (401 error), send the `refresh_token` to `POST /auth/refresh` to get a new access token.
5. **Logout:** Call `POST /auth/logout` and clear your local storage/cookies.

## 3. Standard Response Formats
### Success (Paginated Data)
Pagination endpoints (e.g., `GET /products`) return a standard structure:
```json
{
  "items": [{...}, {...}],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

### Errors
API errors are consistently formatted as:
```json
{
  "success": false,
  "error": "Human readable error message"
}
```

## 4. Key Endpoints
* **`GET /me`**: Fetch current logged-in user profile, role (`ADMIN` or `SALESPERSON`), and branch_id.
* **`GET /analytics/dashboard`**: Primary endpoint for the main admin dashboard (contains metrics, trends, and top products).
* **`GET /alerts`**: Check for background system alerts (like Out of Stock notifications).

## 5. File Uploads (Data Import)
When importing sales data via `POST /import/sales`, you must send a `multipart/form-data` request with a `file` field containing the CSV or XLSX document.

## 6. Rate Limiting
Security rate limiting is active on critical routes:
* `/auth/login`: Maximum 5 attempts per minute.
* `/analytics/*`: Usually capped at 20 requests per minute per IP.
(Exceeding these limits will return a `429 Too Many Requests` error).