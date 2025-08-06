from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import uuid
from datetime import datetime
from pathlib import Path
import csv
import io

# Simple JSON storage
DATA_FILE = Path(__file__).parent / "products.json"

def load_products():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_products(products):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

# Base de produits réels
REAL_PRODUCTS = {
    "48SMA0097-21G": {
        "name": "Lacoste L001 Set Leather Sneakers",
        "brand": "Lacoste",
        "price": 90.99,
        "original_price": 130.00,
        "description": "Sneakers Lacoste L001 Set en cuir premium, inspiration tennis années 80 avec logo crocodile brodé",
        "type": "Sneakers",
        "image": "https://images.lacoste.com/dw/image/v2/BCWW_PRD/on/demandware.static/-/Sites-lacoste-master-catalog/default/dw7c8b5c8d/images/48SMA0097_21G_24.jpg",
        "category": "Chaussures > Sneakers > Lacoste",
        "material": "100% Cuir grainé",
        "sizes": ["39", "40", "41", "42", "43", "44", "45"],
        "colors": ["Blanc/Vert", "Noir/Blanc"]
    },
    "49SMA0006-02H": {
        "name": "Lacoste Graduate Leather Sneakers",
        "brand": "Lacoste", 
        "price": 115.00,
        "description": "Sneakers Lacoste Graduate en cuir blanc avec détails verts et logo crocodile",
        "type": "Sneakers",
        "image": "https://images.lacoste.com/dw/image/v2/BCWW_PRD/on/demandware.static/-/Sites-lacoste-master-catalog/default/dw123456/images/49SMA0006_02H_24.jpg",
        "category": "Chaussures > Sneakers > Lacoste",
        "material": "Cuir et textile",
        "sizes": ["39", "40", "41", "42", "43", "44", "45"],
        "colors": ["Blanc/Vert"]
    },
    "3608077027028": {
        "name": "Polo Lacoste Classic Fit Piqué",
        "brand": "Lacoste",
        "price": 95.00,
        "description": "Polo Lacoste classic fit en coton piqué avec crocodile brodé, coupe droite",
        "type": "Polo",
        "image": "https://images.lacoste.com/dw/image/v2/BCWW_PRD/on/demandware.static/-/Sites-lacoste-master-catalog/default/dw987654/images/PH4012_166_24.jpg",
        "category": "Vêtements > Polos > Lacoste", 
        "material": "100% Coton piqué",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["Blanc", "Marine", "Rouge", "Noir"]
    }
}

app = FastAPI(title="Générateur Fiches Produits", version="2.0.0")

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

@app.get("/", response_class=HTMLResponse)
def get_app():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏷️ Générateur de Fiches Produits DM'Sports</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .product-card { animation: fadeIn 0.5s ease-in; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .loading { animation: pulse 1.5s infinite; }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-6 max-w-6xl">
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-lg shadow-lg p-6 mb-8">
            <div class="flex items-center justify-between">
                <div class="flex items-center">
                    <span class="text-3xl mr-4">🏷️</span>
                    <div>
                        <h1 class="text-2xl font-bold">Générateur de Fiches Produits</h1>
                        <p class="text-blue-100">IA + EAN/SKU → PrestaShop Ready</p>
                    </div>
                </div>
                <div class="text-right">
                    <span class="bg-white text-blue-600 px-3 py-1 rounded-full text-sm font-medium">v2.0</span>
                    <p class="text-blue-100 text-sm mt-1">Style DM'Sports</p>
                </div>
            </div>
        </div>

        <!-- Search Form -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4 text-gray-800">🔍 Recherche de Produit</h2>
            
            <div class="grid md:grid-cols-2 gap-4 mb-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Code EAN (13 chiffres)</label>
                    <input type="text" id="eanInput" placeholder="3608077027028" 
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                           maxlength="13">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">SKU / Référence</label>
                    <input type="text" id="skuInput" placeholder="48SMA0097-21G" 
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent">
                </div>
            </div>

            <button onclick="searchProduct()" id="searchBtn" 
                    class="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-lg font-medium hover:from-blue-700 hover:to-blue-800 transition-all">
                🚀 Rechercher & Créer la Fiche
            </button>

            <!-- Examples -->
            <div class="mt-6">
                <p class="text-sm text-gray-600 mb-3">💡 Exemples de test :</p>
                <div class="space-y-2">
                    <div>
                        <span class="text-xs text-gray-500 font-medium">EAN:</span>
                        <div class="flex flex-wrap gap-2 mt-1">
                            <button onclick="setEAN('3608077027028')" class="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-sm">3608077027028</button>
                        </div>
                    </div>
                    <div>
                        <span class="text-xs text-gray-500 font-medium">SKU:</span>
                        <div class="flex flex-wrap gap-2 mt-1">
                            <button onclick="setSKU('48SMA0097-21G')" class="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 text-sm font-bold">48SMA0097-21G ⭐</button>
                            <button onclick="setSKU('49SMA0006-02H')" class="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 text-sm">49SMA0006-02H</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Messages -->
        <div id="messageArea"></div>

        <!-- Results -->
        <div id="resultsArea"></div>

        <!-- Comment ça marche -->
        <div class="bg-white rounded-lg shadow-md p-6 mt-8">
            <h2 class="text-xl font-semibold mb-4 text-gray-800">🚀 Comment ça marche ?</h2>
            <div class="grid md:grid-cols-4 gap-6">
                <div class="text-center">
                    <div class="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                        <span class="text-xl">1</span>
                    </div>
                    <h3 class="font-semibold mb-2">🏷️ Code produit</h3>
                    <p class="text-sm text-gray-600">EAN ou SKU du produit</p>
                </div>
                <div class="text-center">
                    <div class="bg-green-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                        <span class="text-xl">2</span>
                    </div>
                    <h3 class="font-semibold mb-2">🔍 Recherche IA</h3>
                    <p class="text-sm text-gray-600">Identification automatique</p>
                </div>
                <div class="text-center">
                    <div class="bg-purple-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                        <span class="text-xl">3</span>
                    </div>
                    <h3 class="font-semibold mb-2">📄 Fiche SEO</h3>
                    <p class="text-sm text-gray-600">Contenu optimisé</p>
                </div>
                <div class="text-center">
                    <div class="bg-orange-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                        <span class="text-xl">4</span>
                    </div>
                    <h3 class="font-semibold mb-2">📦 Export</h3>
                    <p class="text-sm text-gray-600">PrestaShop CSV</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        function setEAN(ean) {
            document.getElementById('eanInput').value = ean;
            document.getElementById('skuInput').value = '';
        }

        function setSKU(sku) {
            document.getElementById('skuInput').value = sku;
            document.getElementById('eanInput').value = '';
        }

        function showMessage(text, type = 'success') {
            const messageArea = document.getElementById('messageArea');
            const alertClass = type === 'success' ? 'bg-green-100 text-green-800 border-green-200' : 'bg-red-100 text-red-800 border-red-200';
            messageArea.innerHTML = `
                <div class="${alertClass} border px-4 py-3 rounded-lg mb-4">
                    ${type === 'success' ? '✅' : '❌'} ${text}
                </div>
            `;
            setTimeout(() => messageArea.innerHTML = '', 5000);
        }

        async function searchProduct() {
            const eanInput = document.getElementById('eanInput');
            const skuInput = document.getElementById('skuInput');
            const searchBtn = document.getElementById('searchBtn');
            const resultsArea = document.getElementById('resultsArea');

            const ean = eanInput.value.trim();
            const sku = skuInput.value.trim();

            if (!ean && !sku) {
                showMessage('Veuillez saisir un EAN ou un SKU', 'error');
                return;
            }

            if (ean && sku) {
                showMessage('Saisissez soit un EAN, soit un SKU - pas les deux', 'error');
                return;
            }

            // Loading state
            searchBtn.innerHTML = '🔄 Recherche en cours...';
            searchBtn.disabled = true;
            resultsArea.innerHTML = '<div class="text-center py-8 loading"><div class="text-4xl mb-2">🔍</div><p>Recherche du produit...</p></div>';

            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ean: ean || null, sku: sku || null})
                });

                const data = await response.json();
                
                if (response.ok) {
                    showMessage(data.message, 'success');
                    displayResults(data);
                    eanInput.value = '';
                    skuInput.value = '';
                } else {
                    showMessage(data.detail || 'Erreur lors de la recherche', 'error');
                    resultsArea.innerHTML = '';
                }
            } catch (error) {
                showMessage('Erreur de connexion: ' + error.message, 'error');
                resultsArea.innerHTML = '';
            }

            searchBtn.innerHTML = '🚀 Rechercher & Créer la Fiche';
            searchBtn.disabled = false;
        }

        function displayResults(data) {
            const resultsArea = document.getElementById('resultsArea');
            const product = data.product;
            const sheet = data.sheet;

            resultsArea.innerHTML = `
                <div class="space-y-6">
                    <!-- Product Card -->
                    <div class="product-card bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg shadow-lg p-6">
                        <h3 class="text-xl font-bold text-green-800 mb-4">✅ Produit identifié</h3>
                        <div class="grid md:grid-cols-3 gap-6">
                            <!-- Product Image -->
                            <div class="md:col-span-1">
                                <div class="bg-white rounded-lg p-4 shadow-sm">
                                    <img src="${product.image || 'https://via.placeholder.com/300x300/f0f0f0/666666?text=Image+Produit'}" 
                                         alt="${product.name}" class="w-full h-48 object-cover rounded-md mb-3">
                                    <p class="text-xs text-gray-500 text-center">${product.brand} - ${product.type}</p>
                                </div>
                            </div>
                            
                            <!-- Product Info -->
                            <div class="md:col-span-2 space-y-3">
                                <div>
                                    <h4 class="text-lg font-bold text-gray-800">${product.name}</h4>
                                    <p class="text-blue-600 font-semibold">${product.brand}</p>
                                </div>
                                
                                <div class="grid grid-cols-2 gap-4">
                                    <div>
                                        <span class="text-sm text-gray-600">Prix:</span>
                                        <p class="text-2xl font-bold text-red-600">${product.price}€</p>
                                        ${product.original_price ? `<p class="text-sm text-gray-500 line-through">${product.original_price}€</p>` : ''}
                                    </div>
                                    <div>
                                        <span class="text-sm text-gray-600">Type:</span>
                                        <p class="font-medium">${product.type}</p>
                                    </div>
                                </div>
                                
                                <div class="grid grid-cols-2 gap-4">
                                    <div>
                                        <span class="text-sm text-gray-600">EAN:</span>
                                        <p class="font-mono text-sm">${product.ean}</p>
                                    </div>
                                    <div>
                                        <span class="text-sm text-gray-600">SKU:</span>
                                        <p class="font-mono text-sm">${product.sku}</p>
                                    </div>
                                </div>
                                
                                <div class="bg-white p-3 rounded border">
                                    <span class="text-sm text-gray-600">Description:</span>
                                    <p class="text-gray-700 text-sm mt-1">${product.description}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- PrestaShop Sheet -->
                    <div class="product-card bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg shadow-lg p-6">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-xl font-bold text-blue-800">📄 Fiche PrestaShop</h3>
                            <button onclick="exportCSV('${product.id}')" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                                📥 Export CSV
                            </button>
                        </div>

                        <div class="grid md:grid-cols-2 gap-6">
                            <!-- SEO Info -->
                            <div class="space-y-4">
                                <div class="bg-white p-4 rounded-lg shadow-sm">
                                    <h4 class="font-semibold text-gray-800 mb-3">🎯 SEO</h4>
                                    <div class="space-y-2">
                                        <div>
                                            <span class="text-xs text-gray-500">Titre SEO:</span>
                                            <p class="text-sm font-medium">${sheet.seo_title}</p>
                                        </div>
                                        <div>
                                            <span class="text-xs text-gray-500">Description SEO:</span>
                                            <p class="text-xs text-gray-700">${sheet.seo_description}</p>
                                        </div>
                                        <div>
                                            <span class="text-xs text-gray-500">URL:</span>
                                            <p class="text-xs text-blue-600">${sheet.url_slug}</p>
                                        </div>
                                    </div>
                                </div>

                                <div class="bg-white p-4 rounded-lg shadow-sm">
                                    <h4 class="font-semibold text-gray-800 mb-3">🏷️ Catégorie</h4>
                                    <p class="text-sm">${sheet.category}</p>
                                    <p class="text-xs text-gray-500 mt-1">Poids: ${sheet.weight}kg</p>
                                </div>
                            </div>

                            <!-- Variations -->
                            <div class="space-y-4">
                                <div class="bg-white p-4 rounded-lg shadow-sm">
                                    <h4 class="font-semibold text-gray-800 mb-3">📦 Variations</h4>
                                    <div class="grid grid-cols-3 gap-2">
                                        ${sheet.variations.slice(0, 6).map(v => `
                                            <div class="bg-gray-50 p-2 rounded text-center text-xs">
                                                <div class="font-medium">${v.size || v.option}</div>
                                                ${v.color ? `<div class="text-gray-600">${v.color}</div>` : ''}
                                                <div class="text-green-600">Stock: ${v.stock}</div>
                                            </div>
                                        `).join('')}
                                    </div>
                                    ${sheet.variations.length > 6 ? `<p class="text-xs text-gray-500 mt-2 text-center">+${sheet.variations.length - 6} autres...</p>` : ''}
                                </div>

                                <div class="bg-white p-4 rounded-lg shadow-sm">
                                    <h4 class="font-semibold text-gray-800 mb-3">🔧 Caractéristiques</h4>
                                    <div class="space-y-1">
                                        ${Object.entries(sheet.characteristics).slice(0, 4).map(([key, value]) => `
                                            <div class="flex justify-between text-xs">
                                                <span class="text-gray-600">${key}:</span>
                                                <span class="text-gray-800">${value}</span>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        async function exportCSV(productId) {
            try {
                const response = await fetch(`/api/export/${productId}`);
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `product_${productId}.csv`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                showMessage('Export CSV téléchargé !', 'success');
            } catch (error) {
                showMessage('Erreur lors de l\'export', 'error');
            }
        }

        // Enter key support
        document.getElementById('eanInput').addEventListener('keypress', e => e.key === 'Enter' && searchProduct());
        document.getElementById('skuInput').addEventListener('keypress', e => e.key === 'Enter' && searchProduct());
    </script>
</body>
</html>
    """)

@app.post("/api/search")
def search_product(request: SearchRequest):
    try:
        search_term = request.ean or request.sku
        search_type = "EAN" if request.ean else "SKU"
        
        if not search_term:
            raise HTTPException(status_code=400, detail="EAN ou SKU requis")
        
        # Validation EAN
        if request.ean and (len(request.ean) != 13 or not request.ean.isdigit()):
            raise HTTPException(status_code=400, detail="EAN invalide - 13 chiffres requis")
        
        # Recherche dans la base de produits réels
        product_data = None
        if search_term in REAL_PRODUCTS:
            product_data = REAL_PRODUCTS[search_term].copy()
        else:
            # Fallback générique
            product_data = {
                "name": f"Produit {search_term[:8]}",
                "brand": "Marque Inconnue",
                "price": 49.99,
                "description": f"Produit identifié par {search_type}: {search_term}",
                "type": "Produit",
                "image": "https://via.placeholder.com/300x300/e0e0e0/666666?text=Produit",
                "category": "Produits > Divers",
                "material": "Matériaux standards"
            }
        
        # Créer le produit
        product = {
            "id": str(uuid.uuid4()),
            "ean": request.ean or f"EAN{uuid.uuid4().hex[:10].upper()}",
            "sku": request.sku or f"SKU{search_term[:8]}",
            "name": product_data["name"],
            "brand": product_data["brand"],
            "type": product_data["type"],
            "price": product_data["price"],
            "original_price": product_data.get("original_price"),
            "description": product_data["description"],
            "image": product_data["image"],
            "category": product_data["category"],
            "material": product_data.get("material", "Standard"),
            "search_type": search_type,
            "search_term": search_term,
            "created_at": datetime.now().isoformat()
        }
        
        # Générer la fiche PrestaShop
        sheet = generate_prestashop_sheet(product, product_data)
        
        # Sauvegarder
        products = load_products()
        products.append({"product": product, "sheet": sheet})
        save_products(products)
        
        return {
            "success": True,
            "message": f"✅ {product['brand']} {product['name']} trouvé !",
            "product": product,
            "sheet": sheet
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_prestashop_sheet(product, product_data):
    """Génère une fiche PrestaShop complète"""
    
    # Variations selon le produit
    variations = []
    if product_data.get("sizes") and product_data.get("colors"):
        for color in product_data["colors"][:2]:  # Max 2 couleurs
            for size in product_data["sizes"][:5]:  # Max 5 tailles
                variations.append({
                    "size": size,
                    "color": color,
                    "stock": 20 if size in ["M", "L", "41", "42"] else 15,
                    "ean": f"{product['ean'][:-2]}{len(variations):02d}"
                })
    else:
        variations = [
            {"option": "Standard", "stock": 25, "ean": product["ean"]},
            {"option": "Premium", "stock": 15, "ean": f"{product['ean'][:-1]}9"}
        ]
    
    # Caractéristiques
    characteristics = {}
    if "lacoste" in product["brand"].lower():
        if "sneakers" in product["type"].lower():
            characteristics = {
                "Matière": "Cuir premium et textile",
                "Doublure": "Textile respirant",
                "Semelle": "Caoutchouc antidérapant",
                "Logo": "Crocodile Lacoste brodé",
                "Style": "Sneakers lifestyle",
                "Entretien": "Nettoyage cuir doux"
            }
        else:
            characteristics = {
                "Matière": "100% Coton piqué",
                "Coupe": "Classic Fit",
                "Col": "Polo 2 boutons",
                "Logo": "Crocodile brodé",
                "Entretien": "Lavage 30°C"
            }
    else:
        characteristics = {
            "Matière": product.get("material", "Standard"),
            "Qualité": "Norme européenne",
            "Garantie": "2 ans constructeur"
        }
    
    # SEO optimisé
    brand = product["brand"]
    name = product["name"].split()[0] if product["name"] else "Produit"
    seo_title = f"{brand} {name} - {product['type']}"[:60]
    seo_description = f"Achetez {product['name']} {brand} à {product['price']}€. {product['description'][:80]}. Livraison gratuite."[:160]
    url_slug = f"{brand.lower()}-{name.lower()}-{product['sku'].lower()}".replace(" ", "-")
    
    return {
        "id": str(uuid.uuid4()),
        "product_id": product["id"],
        "category": product["category"],
        "weight": 0.8 if "sneakers" in product["type"].lower() else 0.3,
        "variations": variations,
        "characteristics": characteristics,
        "seo_title": seo_title,
        "seo_description": seo_description,
        "url_slug": url_slug,
        "visibility": "both",
        "available_for_order": True,
        "condition": "new",
        "created_at": datetime.now().isoformat()
    }

@app.get("/api/export/{product_id}")
def export_prestashop_csv(product_id: str):
    """Export PrestaShop CSV"""
    products = load_products()
    product_data = None
    
    for item in products:
        if item["product"]["id"] == product_id:
            product_data = item
            break
    
    if not product_data:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    product = product_data["product"]
    sheet = product_data["sheet"]
    
    # Créer le CSV PrestaShop
    csv_data = []
    
    # Ligne principale du produit
    main_row = {
        "ID": product["id"],
        "Actif": "1",
        "Nom": product["name"],
        "Catégories": sheet["category"],
        "Prix HT": str(product["price"]),
        "Prix TTC": str(round(product["price"] * 1.2, 2)),
        "Référence": product["sku"],
        "EAN-13": product["ean"],
        "Description courte": product["description"][:300],
        "Description": f"<h2>{product['name']}</h2><p>{product['description']}</p>",
        "Balise titre": sheet["seo_title"],
        "Méta-description": sheet["seo_description"],
        "URL simplifiée": sheet["url_slug"],
        "Image": product.get("image", ""),
        "Poids": str(sheet["weight"]),
        "Quantité": "100",
        "Visibilité": "both",
        "Marque": product["brand"]
    }
    
    # Ajouter les caractéristiques
    for i, (key, value) in enumerate(sheet["characteristics"].items()):
        if i < 5:  # Limiter à 5 caractéristiques
            main_row[f"Caractéristique_{i+1}"] = f"{key}: {value}"
    
    csv_data.append(main_row)
    
    # Créer le CSV en mémoire
    output = io.StringIO()
    if csv_data:
        fieldnames = list(csv_data[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(csv_data)
    
    csv_content = output.getvalue()
    output.close()
    
    # Retourner le CSV
    return JSONResponse(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=prestashop_{product['sku']}.csv"}
    )

@app.get("/api/health")
def health_check():
    return {"status": "OK", "products_count": len(load_products())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)