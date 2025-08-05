from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json
import requests
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# SIMPLE JSON STORAGE
PRODUCTS_FILE = ROOT_DIR / 'products.json'
SHEETS_FILE = ROOT_DIR / 'sheets.json'

def load_json_file(file_path):
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_json_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# API Keys
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'your_openai_key_here')
GOOGLE_SEARCH_API_KEY = os.environ.get('GOOGLE_SEARCH_API_KEY', 'your_google_search_key_here')
GOOGLE_SEARCH_CX = os.environ.get('GOOGLE_SEARCH_CX', 'your_google_cx_here')

# Create the main app
app = FastAPI(
    title="🏷️ Générateur de Fiches Produits DM'Sports", 
    description="Outil intelligent de création automatique de fiches produits avec IA + recherche EAN",
    version="2.0.0"
)

# Create API router
api_router = APIRouter(prefix="/api")

# ===== MODELS =====

class ProductSearch(BaseModel):
    ean: str = Field(..., description="Code EAN du produit (13 chiffres)")
    auto_generate: bool = Field(default=True, description="Générer automatiquement la fiche produit")

class ProductSheet(BaseModel):
    id: Optional[str] = None
    ean: str
    name: str
    brand: Optional[str] = None
    type: Optional[str] = None
    reference: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    characteristics: Optional[Dict[str, Any]] = None
    variations: Optional[List[Dict[str, Any]]] = None
    weight: Optional[float] = None
    photos: Optional[List[str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# ===== API ENDPOINTS =====

@api_router.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

@api_router.get("/products")
def get_products():
    """Get all products"""
    products = load_json_file(PRODUCTS_FILE)
    return {"products": products, "total": len(products)}

@api_router.get("/sheets")
def get_sheets():
    """Get all product sheets"""
    sheets = load_json_file(SHEETS_FILE)
    return {"sheets": sheets, "total": len(sheets)}

@api_router.post("/search")
def search_ean(product_search: ProductSearch):
    """Search EAN and optionally generate product sheet"""
    ean = product_search.ean.strip()
    
    if len(ean) != 13 or not ean.isdigit():
        raise HTTPException(status_code=400, detail="EAN doit contenir exactement 13 chiffres")
    
    # Mock Google Search (replace with real API when ready)
    mock_search_result = {
        "name": f"Produit EAN {ean}",
        "brand": "Nike" if ean.startswith("36") else "Adidas" if ean.startswith("40") else "Autre",
        "type": "Chaussures de sport",
        "description": f"Produit trouvé pour le code EAN {ean}",
        "estimated_price": 89.99
    }
    
    # Create product
    product = {
        "id": str(uuid.uuid4()),
        "ean": ean,
        "name": mock_search_result["name"],
        "brand": mock_search_result["brand"],
        "type": mock_search_result["type"],
        "description": mock_search_result["description"],
        "price": mock_search_result["estimated_price"],
        "created_at": datetime.now().isoformat(),
        "status": "found"
    }
    
    # Save to products
    products = load_json_file(PRODUCTS_FILE)
    products.append(product)
    save_json_file(PRODUCTS_FILE, products)
    
    # Generate sheet if requested
    if product_search.auto_generate:
        sheet = generate_product_sheet(product)
        sheets = load_json_file(SHEETS_FILE)
        sheets.append(sheet)
        save_json_file(SHEETS_FILE, sheets)
        return {"success": True, "product": product, "sheet": sheet}
    
    return {"success": True, "product": product}

@api_router.post("/generate")
def generate_sheet(product_data: dict):
    """Generate product sheet from product data"""
    sheet = generate_product_sheet(product_data)
    sheets = load_json_file(SHEETS_FILE)
    sheets.append(sheet)
    save_json_file(SHEETS_FILE, sheets)
    return {"success": True, "sheet": sheet}

def generate_product_sheet(product_data):
    """Generate a complete product sheet"""
    return {
        "id": str(uuid.uuid4()),
        "ean": product_data.get("ean"),
        "name": product_data.get("name", ""),
        "brand": product_data.get("brand", ""),
        "type": product_data.get("type", ""),
        "reference": f"REF-{product_data.get('ean', '')[:8]}",
        "price": product_data.get("price", 0),
        "description": product_data.get("description", ""),
        "characteristics": {
            "color": "Noir/Blanc",
            "material": "Textile synthétique",
            "season": "Toute saison",
            "gender": "Mixte"
        },
        "variations": [
            {"size": "36", "stock": 10},
            {"size": "37", "stock": 15},
            {"size": "38", "stock": 20},
            {"size": "39", "stock": 25},
            {"size": "40", "stock": 30},
            {"size": "41", "stock": 25},
            {"size": "42", "stock": 20},
            {"size": "43", "stock": 15},
            {"size": "44", "stock": 10}
        ],
        "weight": 0.8,
        "photos": [
            "https://via.placeholder.com/400x400/000000/FFFFFF?text=Photo1",
            "https://via.placeholder.com/400x400/333333/FFFFFF?text=Photo2",
            "https://via.placeholder.com/400x400/666666/FFFFFF?text=Photo3"
        ],
        "created_at": datetime.now().isoformat(),
        "status": "generated"
    }

@api_router.delete("/products/{product_id}")
def delete_product(product_id: str):
    """Delete a product"""
    products = load_json_file(PRODUCTS_FILE)
    products = [p for p in products if p.get("id") != product_id]
    save_json_file(PRODUCTS_FILE, products)
    return {"success": True, "message": "Produit supprimé"}

@api_router.delete("/sheets/{sheet_id}")
def delete_sheet(sheet_id: str):
    """Delete a product sheet"""
    sheets = load_json_file(SHEETS_FILE)
    sheets = [s for s in sheets if s.get("id") != sheet_id]
    save_json_file(SHEETS_FILE, sheets)
    return {"success": True, "message": "Fiche supprimée"}

# ===== SETUP =====

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

# Serve React frontend
frontend_dir = Path(__file__).parent.parent / "frontend" / "build"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=frontend_dir / "static"), name="static")
    
    @app.get("/{path:path}")
    def serve_frontend(path: str = ""):
        if path.startswith("api/"):
            raise HTTPException(status_code=404)
        return FileResponse(frontend_dir / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)