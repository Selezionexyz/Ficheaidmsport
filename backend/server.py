from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
from pathlib import Path
import uuid
from datetime import datetime

# Simple data storage
data_file = Path(__file__).parent / "data.json"

def load_data():
    if data_file.exists():
        with open(data_file, 'r') as f:
            return json.load(f)
    return {"products": [], "sheets": []}

def save_data(data):
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    ean: str
    auto_generate: Optional[bool] = True

@app.get("/api/health")
def health():
    return {"status": "OK", "message": "Backend fonctionne !"}

@app.get("/api/products")
def get_products():
    data = load_data()
    return {"products": data["products"], "total": len(data["products"])}

@app.get("/api/sheets")
def get_sheets():
    data = load_data()
    return {"sheets": data["sheets"], "total": len(data["sheets"])}

@app.post("/api/search")
def search_product(request: SearchRequest):
    try:
        # Validation EAN
        if len(request.ean) != 13 or not request.ean.isdigit():
            raise HTTPException(status_code=400, detail="EAN invalide")
        
        # Créer produit factice
        product = {
            "id": str(uuid.uuid4()),
            "ean": request.ean,
            "name": f"Produit {request.ean[:6]}",
            "brand": "Nike" if request.ean.startswith("36") else "Adidas",
            "price": 99.99,
            "created_at": datetime.now().isoformat()
        }
        
        # Sauvegarder
        data = load_data()
        data["products"].append(product)
        
        # Générer fiche si demandé
        sheet = None
        if request.auto_generate:
            sheet = {
                "id": str(uuid.uuid4()),
                "product_id": product["id"],
                "ean": request.ean,
                "title": f"Fiche - {product['name']}",
                "description": f"Fiche produit générée pour {product['name']}",
                "created_at": datetime.now().isoformat()
            }
            data["sheets"].append(sheet)
        
        save_data(data)
        
        return {
            "success": True,
            "product": product,
            "sheet": sheet,
            "message": "Produit trouvé et traité !"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)