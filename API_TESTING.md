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

### 2. Get All Products
Request:
```http
GET /products
```
Expected Result:
* Status Code: 200
* List of products returned

## Sales Endpoints

### 3. Create Sale
Request:
```http
POST /sales
```
Expected Result:
* Status Code: 200
* Sale created successfully
* Product stock reduced

## Data Import Endpoints

### 4. Import Sales CSV/Excel
Request:
```http
POST /import/sales
Content-Type: multipart/form-data
```
Expected Result:
* Status Code: 200
* `imported_rows` and `cleaning_report` returned
* Audit Log successfully recorded

### 5. Import With Invalid File Type
Request:
```http
POST /import/sales
```
(Attach a `.txt` file)
Expected Result:
* Status Code: 400
* "Only CSV and XLSX files are supported" error returned

## Analytics Endpoints

### 6. Get Dashboard Metrics
Request:
```http
GET /analytics/dashboard
```
Expected Result:
* Status Code: 200
* Summary metrics, sales trends, and top products returned

### 7. Export Dashboard (Multi-Sheet Excel)
Request:
```http
GET /analytics/dashboard/export
```
Expected Result:
* Status Code: 200
* A `.xlsx` file attachment with multiple sheets downloaded

### 8. Get Sales Visualizations
Request:
```http
GET /analytics/visualizations/sales-distribution
```
Expected Result:
* Status Code: 200
* Formatted `labels` and `datasets` for frontend charts returned

---
## Test Environment
* FastAPI
* Uvicorn
* Postman
* Python 3.x

All test cases and end-to-end flows completed successfully.