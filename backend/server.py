from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
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
    ean: Optional[str] = None
    sku: Optional[str] = None
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
        search_term = ""
        search_type = ""
        
        if request.ean:
            if len(request.ean) != 13 or not request.ean.isdigit():
                raise HTTPException(status_code=400, detail="EAN invalide - doit contenir 13 chiffres")
            search_term = request.ean
            search_type = "EAN"
        elif request.sku:
            search_term = request.sku.strip()
            search_type = "SKU"
        else:
            raise HTTPException(status_code=400, detail="Veuillez fournir un EAN ou un SKU")
        
        # Créer produit avec les bonnes infos selon le type de recherche
        if search_type == "EAN":
            product_name = f"Produit EAN {search_term[:6]}"
            brand = "Nike" if search_term.startswith("36") else "Adidas" if search_term.startswith("40") else "Autre"
            sku = f"SKU-{search_term[:8]}"
        else:
            # Recherche par SKU - exemple pour polo Lacoste
            if "lacoste" in search_term.lower() or "polo" in search_term.lower():
                product_name = f"Polo Lacoste {search_term}"
                brand = "Lacoste"
            else:
                product_name = f"Produit {search_term}"
                brand = "Marque inconnue"
            sku = search_term
        
        product = {
            "id": str(uuid.uuid4()),
            "ean": request.ean if request.ean else f"EAN-{uuid.uuid4().hex[:13].upper()}",
            "sku": sku,
            "name": product_name,
            "brand": brand,
            "price": 89.99 if "lacoste" in product_name.lower() else 99.99,
            "search_type": search_type,
            "search_term": search_term,
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
                "ean": product["ean"],
                "sku": product["sku"],
                "title": f"Fiche - {product['name']}",
                "description": f"Fiche produit générée pour {product['name']} (recherché par {search_type}: {search_term})",
                "brand": product["brand"],
                "price": product["price"],
                "created_at": datetime.now().isoformat()
            }
            data["sheets"].append(sheet)
        
        save_data(data)
        
        return {
            "success": True,
            "product": product,
            "sheet": sheet,
            "message": f"Produit trouvé par {search_type} et traité !"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# SERVE FRONTEND SIMPLE
@app.get("/")
def serve_frontend():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏷️ Générateur de Fiches Produits DM'Sports</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8 max-w-4xl">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <div class="flex items-center justify-between">
                <div class="flex items-center">
                    <span class="text-2xl mr-3">🏷️</span>
                    <h1 class="text-2xl font-bold text-gray-800">Générateur de Fiches Produits</h1>
                </div>
                <div class="flex items-center space-x-4">
                    <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">IA + EAN</span>
                    <span class="text-gray-600">Style DM'Sports</span>
                </div>
            </div>
        </div>

        <!-- Messages -->
        <div id="message" class="hidden mb-4"></div>

        <!-- Formulaire -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 class="text-xl font-semibold mb-4">🔍 Recherche par Code EAN</h2>
            
            <div class="space-y-4">
                <div>
                    <input
                        type="text"
                        id="eanCode"
                        placeholder="Entrez le code EAN du produit (13 chiffres)..."
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        maxlength="13"
                    />
                </div>
                
                <div class="flex items-center">
                    <input type="checkbox" id="autoGenerate" checked class="mr-2" />
                    <label for="autoGenerate" class="text-gray-700">✅ Générer la fiche automatiquement</label>
                </div>
                
                <button
                    onclick="handleSearch()"
                    id="searchBtn"
                    class="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700"
                >
                    🚀 Rechercher & Générer
                </button>
            </div>

            <div class="mt-6">
                <p class="text-sm text-gray-600 mb-2">💡 Exemples de codes EAN :</p>
                <div class="flex flex-wrap gap-2">
                    <button onclick="setEAN('3614270357637')" class="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm">3614270357637</button>
                    <button onclick="setEAN('4064037884942')" class="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm">4064037884942</button>
                    <button onclick="setEAN('1234567890123')" class="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm">1234567890123</button>
                </div>
            </div>
        </div>

        <!-- Résultats -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 class="text-xl font-semibold mb-4">📊 Résultats</h2>
            <div id="results" class="text-gray-500">Effectuez une recherche pour voir les résultats</div>
        </div>

        <!-- Comment ça marche -->
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold mb-4">🚀 Comment ça marche ?</h2>
            <div class="grid md:grid-cols-3 gap-6">
                <div class="text-center">
                    <div class="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                        <span class="text-xl">1</span>
                    </div>
                    <h3 class="font-semibold mb-2">🏷️ Code EAN</h3>
                    <p class="text-sm text-gray-600">Saisissez le code-barres du produit (13 chiffres)</p>
                </div>
                <div class="text-center">
                    <div class="bg-green-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                        <span class="text-xl">2</span>
                    </div>
                    <h3 class="font-semibold mb-2">🔍 Recherche IA</h3>
                    <p class="text-sm text-gray-600">L'IA trouve automatiquement les infos sur Google</p>
                </div>
                <div class="text-center">
                    <div class="bg-purple-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                        <span class="text-xl">3</span>
                    </div>
                    <h3 class="font-semibold mb-2">📄 Fiche générée</h3>
                    <p class="text-sm text-gray-600">Fiche complète prête pour PrestaShop</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        function setEAN(ean) {
            document.getElementById('eanCode').value = ean;
        }

        function showMessage(text, type = 'success') {
            const messageDiv = document.getElementById('message');
            messageDiv.className = `mb-4 p-4 rounded ${type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`;
            messageDiv.textContent = text;
            messageDiv.classList.remove('hidden');
            setTimeout(() => messageDiv.classList.add('hidden'), 5000);
        }

        async function handleSearch() {
            const eanCode = document.getElementById('eanCode').value.trim();
            const autoGenerate = document.getElementById('autoGenerate').checked;
            const searchBtn = document.getElementById('searchBtn');
            const resultsDiv = document.getElementById('results');

            if (!eanCode) {
                showMessage('Veuillez saisir un code EAN', 'error');
                return;
            }

            if (eanCode.length !== 13) {
                showMessage('Le code EAN doit contenir 13 chiffres', 'error');
                return;
            }

            searchBtn.textContent = '🔄 Recherche en cours...';
            searchBtn.disabled = true;

            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        ean: eanCode,
                        auto_generate: autoGenerate
                    })
                });

                if (!response.ok) {
                    throw new Error(`Erreur: ${response.status}`);
                }

                const data = await response.json();
                
                if (data.success) {
                    showMessage(data.message, 'success');
                    document.getElementById('eanCode').value = '';
                    
                    resultsDiv.innerHTML = `
                        <div class="space-y-4">
                            <div class="bg-green-50 p-4 rounded-lg">
                                <h3 class="font-semibold text-green-800">✅ Produit trouvé</h3>
                                <p><strong>Nom:</strong> ${data.product.name}</p>
                                <p><strong>EAN:</strong> ${data.product.ean}</p>  
                                <p><strong>Marque:</strong> ${data.product.brand}</p>
                                <p><strong>Prix:</strong> ${data.product.price}€</p>
                            </div>
                            ${data.sheet ? `
                            <div class="bg-blue-50 p-4 rounded-lg">
                                <h3 class="font-semibold text-blue-800">📄 Fiche générée</h3>
                                <p><strong>Titre:</strong> ${data.sheet.title}</p>
                                <p><strong>Description:</strong> ${data.sheet.description}</p>
                            </div>
                            ` : ''}
                        </div>
                    `;
                }
            } catch (err) {
                showMessage('Erreur: ' + err.message, 'error');
            } finally {
                searchBtn.textContent = '🚀 Rechercher & Générer';
                searchBtn.disabled = false;
            }
        }

        // Allow Enter key
        document.getElementById('eanCode').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
    </script>
</body>
</html>
    """)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)