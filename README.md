# 🧩 HNG Stage 1 — String Analyzer Service

This project implements the **HNG 13 Backend Stage 1 Task** — a RESTful API that analyzes strings, stores computed properties, and provides multiple filtering and retrieval endpoints.

---

## 📘 Overview

**Goal:**  
Build a Django REST Framework API that analyzes a string, computes its properties, stores them in a database, and allows querying through structured and natural-language filters.

---

## ⚙️ Tech Stack

| Tool | Purpose |
|------|----------|
| **Python 3.10+** | Core language |
| **Django 5+** | Web framework |
| **Django REST Framework (DRF)** | API serialization & views |
| **SQLite** | Lightweight built-in database for simplicity |

---

## 🗂️ Project Structure

```
.
├── api/
│   ├── views.py                # Handles create, list, retrieve, delete, and NL filtering
│   ├── serializers.py          # Serializes StringAnalyzer model
│   ├── models.py               # StringAnalyzer model
│   ├── utils.py                # Helper functions (hashing, analysis, NLP filter logic)
│   └── urls.py
├── stringanalyzer/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run Locally

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Newkoncept/HNG-1-String-Analyzer-Service.git
cd HNG-1-String-Analyzer-Service
```

### 2️⃣ Create and activate a virtual environment
```bash
python -m venv .venv
# Activate
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Apply migrations
```bash
python manage.py migrate
```

### 5️⃣ Start the development server
```bash
python manage.py runserver
```
Server runs at **http://127.0.0.1:8000/**

---

---

## 🔌 API Reference

### 1️⃣ **POST /strings**
Create and analyze a string.

#### Request
```json
{
  "value": "Hello World"
}
```

#### Success Response — 201 Created
```json
{
  "id": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
  "value": "Hello World",
  "properties": {
    "length": 11,
    "is_palindrome": false,
    "unique_characters": 8,
    "word_count": 2,
    "sha256_hash": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
    "character_frequency_map": {
      "H": 1,
      "e": 1,
      "l": 3,
      "o": 2,
      " ": 1,
      "W": 1,
      "r": 1,
      "d": 1
    }
  },
  "created_at": "2025-10-22T20:15:00.000Z"
}
```

#### Error Responses
| Status | Description |
|--------|--------------|
| 400 | Invalid request body or missing `value` field |
| 409 | String already exists in the system |
| 422 | Invalid data type for `value` (must be string) |

---

### 2️⃣ **GET /strings**
Retrieve all analyzed strings, optionally filtered by query parameters.

#### Query Parameters
| Parameter | Type | Description |
|------------|------|-------------|
| `is_palindrome` | boolean | Filter by palindrome status |
| `min_length` | integer | Minimum string length |
| `max_length` | integer | Maximum string length |
| `word_count` | integer | Exact word count |
| `contains_character` | string | Single character to search for |

#### Example Request
```
GET /strings?is_palindrome=true&min_length=5&max_length=20
```

#### Example Response — 200 OK
```json
{
  "data": [
    {
      "id": "7c211433f02071597741e6ff5a8ea34789abbf43...",
      "value": "madam",
      "properties": {
        "length": 5,
        "is_palindrome": true,
        "unique_characters": 3,
        "word_count": 1,
        "sha256_hash": "7c211433f02071597741e6ff5a8ea34789abbf43...",
        "character_frequency_map": {"m": 2, "a": 2, "d": 1}
      },
      "created_at": "2025-10-22T20:15:00.000Z"
    }
  ],
  "count": 1,
  "filters_applied": {
    "is_palindrome": true,
    "min_length": 5,
    "max_length": 20
  }
}
```

#### Error Response — 400 Bad Request
```json
{
  "400": "Invalid query parameter values or types"
}
```

---

### 3️⃣ **GET /strings/{string_value}**
Retrieve a specific analyzed string by its exact value.

#### Example Request
```
GET /strings/Hello%20World
```

#### Example Response — 200 OK
```json
{
  "id": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
  "value": "Hello World",
  "properties": { ... },
  "created_at": "2025-10-22T20:15:00.000Z"
}
```

#### Error Response — 404 Not Found
```json
{
  "404": "String does not exist in the system"
}
```

---

### 4️⃣ **GET /strings/filter-by-natural-language?query=...**
Retrieve strings using natural-language filters.

#### Example
```
GET /strings/filter-by-natural-language?query=all single word palindromic strings
```

#### Response — 200 OK
```json
{
  "data": [
    { ...results... }
  ],
  "count": 3,
  "interpreted_query": {
    "original": "all single word palindromic strings",
    "parsed_filters": {
      "word_count": 1,
      "is_palindrome": true
    }
  }
}
```

#### Error Responses
| Status | Message |
|--------|----------|
| 400 | Unable to parse natural language query |
| 422 | Query parsed but resulted in conflicting filters |

---

### 5️⃣ **DELETE /strings/{string_value}**
Delete a specific analyzed string.

#### Example
```
DELETE /strings/Hello%20World
```

#### Response — 204 No Content

#### Error — 404 Not Found
```json
{
  "404": "String does not exist in the system"
}
```

---

## 🧾 Validation Rules

- `value` must exist and be a **string**.
- Duplicate strings are rejected (**409 Conflict**).
- Query parameters must be of correct type and within valid ranges.
- `contains_character` must be a **single character**.
- Timestamps are returned in **UTC ISO 8601** format (`...Z`).

---

## 🧠 Design Decisions

- Used **SQLite** for light, file-based persistence (no external DB setup).
- Used **SHA-256 hash** as `id` for deterministic uniqueness.
- Used **DRF Class-Based Views** for scalability.
- Filters implemented **in Python** for SQLite compatibility.
- Included **natural-language filter** with simple keyword parsing (rule-based).

---

You can also use `curl` or Postman to test endpoints.

---

## 🌍 Deployment Notes

- Hosted easily on **PythonAnywhere**, **Railway**, or any Django-compatible host.
- Default DB: SQLite (auto-created).
- To deploy elsewhere, set env vars:

```
DJANGO_SECRET_KEY=<your-secret-key>
```

---

## 👨‍💻 Author

**Oluwagbemiga Taiwo (Newkoncept)**  
🔗 [GitHub Repository](https://github.com/Newkoncept/HNG-1-String-Analyzer-Service)

---

## 🪪 License

MIT License © 2025 [Newkoncept](https://github.com/Newkoncept)
