# API Documentation

**Base URL:** `https://sentiment-api-vpmz.onrender.com`
**API Version:** v1
**OpenAPI Spec:** Available at `/docs` (Swagger UI)
**Alternative Docs:** Available at `/redoc` (ReDoc UI)

---

## 🚀 Quick Start

### 1. Health Check

```bash
curl https://sentiment-api-vpmz.onrender.com/health
```

**Response:**

```json
{
  "status": "ok",
  "app_name": "Student Sentiment Analysis API"
}
```

---

### 2. Submit Feedback

```bash
curl -X POST https://sentiment-api-vpmz.onrender.com/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "roll_number": "CS2024001",
    "gender": "Male",
    "age": 20,
    "study_hours_per_day": 6,
    "attendance_percentage": 85,
    "active_backlogs": 0,
    "academic_feedback": "Good",
    "emotional_feedback": "Happy"
  }'
```

**Response (201 Created):**

```json
{
  "id": 1,
  "roll_number": "CS2024001",
  "gender": "Male",
  "age": 20,
  "study_hours_per_day": 6,
  "attendance_percentage": 85.0,
  "active_backlogs": 0,
  "academic_feedback": "Good",
  "emotional_feedback": "Happy",
  "sentiment_label": "Positive",
  "created_at": "2026-05-02T10:30:00Z",
  "updated_at": "2026-05-02T10:30:00Z"
}
```

---

### 3. Get Analytics

```bash
curl https://sentiment-api-vpmz.onrender.com/api/v1/analytics/summary
```

**Response:**

```json
{
  "sentiment_distribution": {
    "total": 500,
    "positive": 180,
    "neutral": 165,
    "negative": 155,
    "positive_percentage": 36.0,
    "neutral_percentage": 33.0,
    "negative_percentage": 31.0
  },
  "average_metrics": {
    "avg_study_hours": 6.2,
    "avg_attendance": 78.5,
    "avg_backlogs": 0.8
  }
}
```

---

## 📚 Endpoints Overview

| Method | Endpoint                                            | Description                   | Auth |
| ------ | --------------------------------------------------- | ----------------------------- | ---- |
| GET    | `/health`                                         | Health check                  | No   |
| POST   | `/api/v1/feedback`                                | Submit feedback               | No   |
| GET    | `/api/v1/feedback`                                | List all feedback (paginated) | No   |
| GET    | `/api/v1/feedback/{id}`                           | Get feedback by ID            | No   |
| PATCH  | `/api/v1/feedback/{id}`                           | Update feedback               | No   |
| DELETE | `/api/v1/feedback/{id}`                           | Delete feedback               | No   |
| GET    | `/api/v1/analytics/summary`                       | Get sentiment summary         | No   |
| GET    | `/api/v1/analytics/by-sentiment`                  | Filter by sentiment           | No   |
| GET    | `/api/v1/analytics/trends`                        | Get trend analysis            | No   |
| GET    | `/api/v1/analytics/at-risk`                       | Get at-risk students          | No   |
| GET    | `/api/v1/visualisations/sentiment-bar`            | Sentiment bar chart (PNG)     | No   |
| GET    | `/api/v1/visualisations/sentiment-pie`            | Sentiment pie chart (PNG)     | No   |
| GET    | `/api/v1/visualisations/attendance-vs-sentiment`  | Attendance scatter plot (PNG) | No   |
| GET    | `/api/v1/visualisations/backlogs-by-sentiment`    | Backlogs box plot (PNG)       | No   |
| GET    | `/api/v1/visualisations/gender-sentiment`         | Gender distribution (PNG)     | No   |
| GET    | `/api/v1/visualisations/study-hours-distribution` | Study hours histogram (PNG)   | No   |

---

## 🔐 Authentication

**Current:** None (demo API, public access)

**For Production:**

- Add API key authentication
- Implement rate limiting per key
- Add role-based access control (admin vs student)

---

## 📊 Data Models

### StudentFeedbackCreate (Request Body)

```json
{
  "roll_number": "string (required, unique, max 50 chars)",
  "gender": "Male | Female | Other (required)",
  "age": "integer (required, 17-35)",
  "study_hours_per_day": "integer (required, 1-12)",
  "attendance_percentage": "float (required, 0.0-100.0)",
  "active_backlogs": "integer (required, >= 0)",
  "academic_feedback": "Excellent | Good | Satisfactory | Bad (required)",
  "emotional_feedback": "Happy | Glad | Neutral | Sad | Angry (required)"
}
```

### StudentFeedbackResponse (Response Body)

```json
{
  "id": "integer (auto-generated)",
  "roll_number": "string",
  "gender": "string",
  "age": "integer",
  "study_hours_per_day": "integer",
  "attendance_percentage": "float",
  "active_backlogs": "integer",
  "academic_feedback": "string",
  "emotional_feedback": "string",
  "sentiment_label": "Positive | Neutral | Negative (ML-predicted)",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp"
}
```

---

## ⚠️ Error Responses

### 400 Bad Request

```json
{
  "error_code": "BAD_REQUEST",
  "message": "Invalid request format",
  "timestamp": "2026-05-02T10:30:00Z",
  "path": "/api/v1/feedback"
}
```

### 404 Not Found

```json
{
  "error_code": "RECORD_NOT_FOUND",
  "message": "Feedback record with ID 999 not found",
  "timestamp": "2026-05-02T10:30:00Z",
  "path": "/api/v1/feedback/999"
}
```

### 422 Validation Error

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "errors": [
    {
      "field": "age",
      "error": "value must be at least 17"
    },
    {
      "field": "gender",
      "error": "value must be one of: Male, Female, Other"
    }
  ],
  "timestamp": "2026-05-02T10:30:00Z",
  "path": "/api/v1/feedback"
}
```

### 503 Service Unavailable

```json
{
  "error_code": "MODEL_NOT_READY",
  "message": "ML model is not loaded yet",
  "timestamp": "2026-05-02T10:30:00Z"
}
```

---

## 📈 Rate Limits

**Current (Render Free Tier):**

- **Limit:** ~15 requests/second
- **Burst:** ~30 requests in 2 seconds
- **Response:** 503 Service Unavailable (if exceeded)

**Recommended Client Behavior:**

- Implement exponential backoff on 503 errors
- Maximum 10 concurrent requests
- Respect Retry-After header if present

---

## 🔄 Pagination

**Endpoints with pagination:**

- `GET /api/v1/feedback`
- `GET /api/v1/analytics/by-sentiment`

**Query Parameters:**

- `limit` (integer, default: 50, max: 100) — Number of records per page
- `skip` (integer, default: 0) — Number of records to skip

**Example:**

```bash
# Page 1 (first 50 records)
curl "https://sentiment-api-vpmz.onrender.com/api/v1/feedback?limit=50&skip=0"

# Page 2 (records 51-100)
curl "https://sentiment-api-vpmz.onrender.com/api/v1/feedback?limit=50&skip=50"
```

**Response includes metadata:**

```json
{
  "summary": {
    "total": 500,
    "returned": 50,
    "limit": 50,
    "skip": 0
  },
  "records": [...]
}
```

---

## 🖼️ Visualization Endpoints

All visualization endpoints return PNG images (not JSON).

**Headers:**

Content-Type: image/png
Content-Length: [bytes]

**Usage in HTML:**

```html
<img src="https://sentiment-api-vpmz.onrender.com/api/v1/visualisations/sentiment-bar" 
     alt="Sentiment Distribution Bar Chart">
```

**Error Handling:**

- **404:** No data available (database empty)
- **500:** Chart generation failed

---

## 🧪 Testing the API

### Using Swagger UI (Recommended)

1. Open: https://sentiment-api-vpmz.onrender.com/docs
2. Click any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

### Using cURL

```bash
# Create feedback
curl -X POST https://sentiment-api-vpmz.onrender.com/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d @example_feedback.json

# Get all feedback
curl https://sentiment-api-vpmz.onrender.com/api/v1/feedback

# Get specific feedback
curl https://sentiment-api-vpmz.onrender.com/api/v1/feedback/1

# Delete feedback
curl -X DELETE https://sentiment-api-vpmz.onrender.com/api/v1/feedback/1
```

### Using Python

```python
import requests

# Submit feedback
response = requests.post(
    "https://sentiment-api-vpmz.onrender.com/api/v1/feedback",
    json={
        "roll_number": "CS2024001",
        "gender": "Male",
        "age": 20,
        "study_hours_per_day": 6,
        "attendance_percentage": 85,
        "active_backlogs": 0,
        "academic_feedback": "Good",
        "emotional_feedback": "Happy"
    }
)
print(response.status_code)  # 201
print(response.json())
```

---

## 📖 OpenAPI Specification

**Download OpenAPI JSON:**

```bash
curl https://sentiment-api-vpmz.onrender.com/openapi.json > openapi.json
```

**Import into Postman:**

1. Postman → Import → Raw Text
2. Paste OpenAPI JSON
3. Collection auto-generated with all endpoints

---

## 🌐 CORS

**Allowed Origins:** `*` (all origins, demo configuration)

**Allowed Methods:** GET, POST, PATCH, DELETE, OPTIONS

**For Production:** Restrict to specific domains

---

## 📝 Changelog

| Version | Date     | Changes                 |
| ------- | -------- | ----------------------- |
| v1.0.0  | May 2026 | Initial release         |
| -       | -        | All CRUD endpoints      |
| -       | -        | Analytics endpoints     |
| -       | -        | Visualization endpoints |
| -       | -        | ML sentiment prediction |

---

**Live API:** https://sentiment-api-vpmz.onrender.com/docs
**GitHub:** https://github.com/danyon-satyam/ecp-2024
**Last Updated:** May 4, 2026
