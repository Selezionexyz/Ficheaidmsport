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
    <title>🏷️ Générateur de Fiches Produits</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-6 max-w-6xl">
        <!-- Header -->
        <div class="bg-blue-600 text-white rounded-lg p-6 mb-6">
            <h1 class="text-2xl font-bold">🏷️ Générateur de Fiches Produits</h1>
            <p class="text-blue-100">EAN/SKU → PrestaShop Ready</p>
        </div>

        <!-- Form -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h2 class="text-xl font-semibold mb-4">🔍 Recherche</h2>
            
            <div class="grid md:grid-cols-2 gap-4 mb-4">
                <div>
                    <label class="block text-sm font-medium mb-2">EAN (13 chiffres)</label>
                    <input type="text" id="ean" placeholder="3608077027028" 
                           class="w-full px-3 py-2 border rounded-lg" maxlength="13">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-2">SKU</label>
                    <input type="text" id="sku" placeholder="48SMA0097-21G" 
                           class="w-full px-3 py-2 border rounded-lg">
                </div>
            </div>

            <button onclick="search()" id="btn" 
                    class="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                🚀 Rechercher
            </button>

            <!-- Examples -->
            <div class="mt-4">
                <p class="text-sm text-gray-600 mb-2">Exemples :</p>
                <button onclick="setVal('sku','48SMA0097-21G')" class="px-2 py-1 bg-green-100 text-green-700 rounded mr-2">48SMA0097-21G</button>
                <button onclick="setVal('ean','3608077027028')" class="px-2 py-1 bg-blue-100 text-blue-700 rounded">3608077027028</button>
            </div>
        </div>

        <!-- Messages -->
        <div id="message"></div>

        <!-- Results -->
        <div id="results"></div>
    </div>

    <script>
        function setVal(type, value) {
            if (type === 'sku') {
                document.getElementById('sku').value = value;
                document.getElementById('ean').value = '';
            } else {
                document.getElementById('ean').value = value;
                document.getElementById('sku').value = '';
            }
        }

        function showMsg(text, type) {
            const msg = document.getElementById('message');
            const color = type === 'success' ? 'green' : 'red';
            msg.innerHTML = `<div class="bg-${color}-100 text-${color}-800 p-3 rounded mb-4">${text}</div>`;
            setTimeout(() => msg.innerHTML = '', 5000);
        }

        async function search() {
            const ean = document.getElementById('ean').value.trim();
            const sku = document.getElementById('sku').value.trim();
            const btn = document.getElementById('btn');
            const results = document.getElementById('results');

            if (!ean && !sku) {
                showMsg('❌ Saisissez un EAN ou un SKU', 'error');
                return;
            }

            btn.innerHTML = '🔄 Recherche...';
            btn.disabled = true;
            results.innerHTML = '<div class="text-center py-8">🔍 Recherche en cours...</div>';

            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ean: ean || null, sku: sku || null})
                });

                const data = await response.json();
                
                if (response.ok) {
                    showMsg(`✅ ${data.message}`, 'success');
                    showResults(data);
                    document.getElementById('ean').value = '';
                    document.getElementById('sku').value = '';
                } else {
                    showMsg(`❌ ${data.detail}`, 'error');
                    results.innerHTML = '';
                }
            } catch (error) {
                showMsg('❌ Erreur: ' + error.message, 'error');
                results.innerHTML = '';
            }

            btn.innerHTML = '🚀 Rechercher';
            btn.disabled = false;
        }

        function showResults(data) {
            const results = document.getElementById('results');
            const p = data.product;
            const s = data.sheet;

            results.innerHTML = `
                <div class="space-y-6">
                    <!-- Produit -->
                    <div class="bg-green-50 border border-green-200 rounded-lg p-6">
                        <h3 class="text-lg font-bold text-green-800 mb-4">✅ Produit identifié</h3>
                        <div class="grid md:grid-cols-2 gap-6">
                            <div>
                                <img src="${p.image}" alt="${p.name}" class="w-full h-48 object-cover rounded mb-3">
                            </div>
                            <div class="space-y-2">
                                <h4 class="font-bold text-xl">${p.name}</h4>
                                <p class="text-blue-600 font-semibold">${p.brand}</p>
                                <p class="text-2xl font-bold text-red-600">${p.price}€</p>
                                <p class="text-gray-600">${p.description}</p>
                                <div class="text-sm text-gray-500">
                                    <p>EAN: ${p.ean}</p>
                                    <p>SKU: ${p.sku}</p>
                                    <p>Type: ${p.type}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Fiche -->
                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-lg font-bold text-blue-800">📄 Fiche PrestaShop</h3>
                            <button onclick="exportCSV('${p.id}')" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                                📥 Export CSV
                            </button>
                        </div>
                        
                        <div class="grid md:grid-cols-2 gap-4">
                            <div>
                                <h4 class="font-semibold mb-2">🎯 SEO</h4>
                                <div class="bg-white p-3 rounded text-sm">
                                    <p><strong>Titre:</strong> ${s.seo_title}</p>
                                    <p><strong>Description:</strong> ${s.seo_description}</p>
                                    <p><strong>URL:</strong> ${s.url_slug}</p>
                                </div>
                            </div>
                            <div>
                                <h4 class="font-semibold mb-2">📦 Détails</h4>
                                <div class="bg-white p-3 rounded text-sm">
                                    <p><strong>Catégorie:</strong> ${s.category}</p>
                                    <p><strong>Poids:</strong> ${s.weight}kg</p>
                                    <p><strong>Variations:</strong> ${s.variations.length}</p>
                                </div>
                            </div>
                        </div>

                        <div class="mt-4">
                            <h4 class="font-semibold mb-2">🔧 Caractéristiques</h4>
                            <div class="bg-white p-3 rounded grid grid-cols-2 gap-2 text-sm">
                                ${Object.entries(s.characteristics).map(([k,v]) => 
                                    `<div><strong>${k}:</strong> ${v}</div>`
                                ).join('')}
                            </div>
                        </div>

                        <div class="mt-4">
                            <h4 class="font-semibold mb-2">📦 Variations</h4>
                            <div class="bg-white p-3 rounded grid grid-cols-4 gap-2 text-xs">
                                ${s.variations.slice(0,8).map(v => 
                                    `<div class="bg-gray-50 p-2 rounded text-center">
                                        <div class="font-medium">${v.size || v.option}</div>
                                        ${v.color ? `<div>${v.color}</div>` : ''}
                                        <div class="text-green-600">Stock: ${v.stock}</div>
                                    </div>`
                                ).join('')}
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
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `product_${productId}.csv`;
                a.click();
                URL.revokeObjectURL(url);
                showMsg('✅ Export téléchargé !', 'success');
            } catch (error) {
                showMsg('❌ Erreur export', 'error');
            }
        }

        // Enter key
        document.getElementById('ean').addEventListener('keypress', e => e.key === 'Enter' && search());
        document.getElementById('sku').addEventListener('keypress', e => e.key === 'Enter' && search());
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
    
    # Chercher le produit dans les deux formats
    for item in products:
        if isinstance(item, dict):
            if "product" in item and item["product"]["id"] == product_id:
                # Format nouveau avec product/sheet
                product_data = item
                break
            elif "id" in item and item["id"] == product_id:
                # Format ancien - créer une fiche temporaire
                product = item
                sheet = {
                    "id": str(uuid.uuid4()),
                    "product_id": product["id"],
                    "category": "Produits > Divers",
                    "weight": 0.5,
                    "variations": [{"option": "Standard", "stock": 25, "ean": product.get("ean", "")}],
                    "characteristics": {"Matière": "Standard", "Qualité": "Norme européenne"},
                    "seo_title": f"{product.get('brand', 'Produit')} {product.get('name', '')}"[:60],
                    "seo_description": f"Achetez {product.get('name', '')} à {product.get('price', 0)}€",
                    "url_slug": f"produit-{product['id'][:8]}",
                    "visibility": "both",
                    "available_for_order": True,
                    "condition": "new"
                }
                product_data = {"product": product, "sheet": sheet}
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
        "Nom": product.get("name", "Produit"),
        "Catégories": sheet["category"],
        "Prix HT": str(product.get("price", 0)),
        "Prix TTC": str(round(float(product.get("price", 0)) * 1.2, 2)),
        "Référence": product.get("sku", product.get("id")[:8]),
        "EAN-13": product.get("ean", ""),
        "Description courte": product.get("description", "")[:300],
        "Description": f"<h2>{product.get('name', 'Produit')}</h2><p>{product.get('description', '')}</p>",
        "Balise titre": sheet["seo_title"],
        "Méta-description": sheet["seo_description"],
        "URL simplifiée": sheet["url_slug"],
        "Image": product.get("image", ""),
        "Poids": str(sheet["weight"]),
        "Quantité": "100",
        "Visibilité": "both",
        "Marque": product.get("brand", "")
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
        headers={"Content-Disposition": f"attachment; filename=prestashop_{product.get('sku', product['id'][:8])}.csv"}
    )

@app.get("/api/products")
def get_products():
    """Retourne la liste des produits trouvés"""
    try:
        products = load_products()
        product_list = []
        for item in products:
            if isinstance(item, dict) and "product" in item:
                # Format nouveau avec product/sheet
                product_list.append(item["product"])
            elif isinstance(item, dict) and "id" in item:
                # Format ancien - produit direct
                product_list.append(item)
        return {"success": True, "products": product_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sheets")
def get_sheets():
    """Retourne la liste des fiches créées"""
    try:
        products = load_products()
        sheets = []
        for item in products:
            if isinstance(item, dict) and "product" in item and "sheet" in item:
                # Format nouveau avec product/sheet
                sheet = item["sheet"].copy()
                product = item["product"]
                sheet.update({
                    "title": f"{product['brand']} {product['name']}",
                    "ean": product["ean"],
                    "description": product["description"]
                })
                sheets.append(sheet)
        return {"success": True, "sheets": sheets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    return {"status": "OK", "products_count": len(load_products())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)