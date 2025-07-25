# Seraface AI Server

**Seraface AI Server** is the backend API for the Seraface AI skincare application. It provides endpoints for managing skincare product data and will support AI-powered skin analysis features.

## ✨ Features

- � **Product Management** - CRUD operations for skincare products
- 📊 **Product Caching** - Efficient storage and retrieval of product information
- 🌐 **RESTful API** - Clean, well-documented API endpoints
- � **Async Operations** - High-performance async MongoDB operations
- � **Professional Structure** - Modular, maintainable codebase

## ⚙️ Tech Stack

- **Backend**: FastAPI
- **Database**: MongoDB with Motor (async driver)
- **Validation**: Pydantic v2
- **Environment**: Python-dotenv

## 🚀 Getting Started

## 📁 Project Structure

```
Seraface-AI-Server/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   └── database.py          # Database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product_schemas.py   # Product Pydantic models
│   │   └── skincare/            # Skincare AI schemas
│   │       ├── __init__.py
│   │       ├── form_schemas.py
│   │       ├── analysis_schemas.py
│   │       └── recommendation_schemas.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── products.py          # Product API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── product_service.py   # Business logic
│   ├── data/                    # JSON storage for phase data
│   ├── ai_router.py             # AI pipeline endpoints
│   ├── connection_logic.py      # Phase connection logic
│   ├── phase1.py                # Form processing
│   ├── phase2.py                # Image analysis
│   ├── phase3.py                # Product recommendation
│   ├── phase4.py                # Routine creation
│   ├── __init__.py
│   └── main.py                  # FastAPI application
├── .env                         # Environment variables
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
└── README.md
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- MongoDB (local or cloud)

### Setup

1. Clone the repository
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create environment file:

   ```bash
   cp .env.example .env
   ```

4. Update `.env` with your MongoDB URI:

   ```
   MONGO_URI=mongodb://localhost:27017
   ```

5. Run the server:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## � API Documentation

Once the server is running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔗 API Endpoints

### Products

- `GET /api/v1/products/` - Get all products
- `GET /api/v1/products/{key}` - Get product by key
- `POST /api/v1/products/` - Create new product
- `PUT /api/v1/products/{key}` - Update product
- `DELETE /api/v1/products/{key}` - Delete product

## 🧑‍💻 Authors

**Dandee Galang** – [@dandee77](https://github.com/dandee77)

## 📄 License

This project is licensed under the MIT License.
