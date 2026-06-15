# API Testing Scenarios

This document describes the API test cases executed using Postman.

## Product Endpoints

### 1. Create Product

Request:

```http
POST /products
```

Expected Result:

* Status Code: 200
* Product created successfully
* Product ID returned

---

### 2. Get All Products

Request:

```http
GET /products
```

Expected Result:

* Status Code: 200
* List of products returned

---

### 3. Get Product By ID

Request:

```http
GET /products/{product_id}
```

Expected Result:

* Status Code: 200
* Product information returned

---

### 4. Get Nonexistent Product

Request:

```http
GET /products/999
```

Expected Result:

* Status Code: 404
* Error message returned

---

### 5. Update Product

Request:

```http
PUT /products/{product_id}
```

Expected Result:

* Status Code: 200
* Product updated successfully

---

### 6. Delete Product

Request:

```http
DELETE /products/{product_id}
```

Expected Result:

* Status Code: 200
* Product deleted successfully

---

### 7. Create Product With Invalid Price

Request:

```http
POST /products
```

Expected Result:

* Status Code: 422
* Validation error returned

---

### 8. Create Product With Missing Fields

Request:

```http
POST /products
```

Expected Result:

* Status Code: 422
* Validation error returned

---

## Sales Endpoints

### 9. Create Sale

Request:

```http
POST /sales
```

Expected Result:

* Status Code: 200
* Sale created successfully
* Product stock reduced

---

### 10. Get All Sales

Request:

```http
GET /sales
```

Expected Result:

* Status Code: 200
* List of sales returned

---

### 11. Get Sales By Date

Request:

```http
GET /sales?date=YYYY-MM-DD
```

Expected Result:

* Status Code: 200
* Only sales matching the specified date returned

---

### 12. Create Sale With Insufficient Stock

Request:

```http
POST /sales
```

Expected Result:

* Status Code: 400
* "Not enough stock" error returned

---

### 13. Create Sale For Nonexistent Product

Request:

```http
POST /sales
```

Expected Result:

* Status Code: 404
* "Product not found" error returned

---

## Test Environment

* FastAPI
* Uvicorn
* Postman
* Python 3.x

All test cases completed successfully.
