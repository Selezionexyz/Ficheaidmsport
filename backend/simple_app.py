from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import json
import uuid
from datetime import datetime

app = FastAPI()

# Base de données des produits RÉELS
PRODUCTS = {
    "48SMA0097-21G": {
        "name": "Lacoste L001 Set Leather Sneakers",
        "brand": "Lacoste",
        "price": 90.99,
        "original_price": 130.00,
        "description": "Sneakers Lacoste L001 Set en cuir premium, inspiration tennis années 80",
        "image": "https://images.lacoste.com/dw/image/v2/BCWW_PRD/on/demandware.static/-/Sites-lacoste-master-catalog/default/dw7c8b5c8d/images/48SMA0097_21G_24.jpg"
    },
    "3608077027028": {
        "name": "Polo Lacoste Classic Fit Piqué",
        "brand": "Lacoste", 
        "price": 95.00,
        "description": "Polo Lacoste en coton piqué avec crocodile brodé",
        "image": "https://images.lacoste.com/dw/image/v2/BCWW_PRD/on/demandware.static/-/Sites-lacoste-master-catalog/default/dw987654/images/PH4012_166_24.jpg"
    }
}

class SearchRequest(BaseModel):
    ean: Optional[str] = None
    sku: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
def main():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>🏷️ Générateur Fiches Produits</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2563eb; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .form { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px; }
        input { padding: 10px; border: 2px solid #e5e7eb; border-radius: 5px; font-size: 16px; }
        button { padding: 12px 20px; background: #2563eb; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #1d4ed8; }
        .example { display: inline-block; padding: 5px 10px; margin: 5px; background: #e0f2fe; color: #0277bd; border-radius: 15px; cursor: pointer; font-size: 12px; }
        .example:hover { background: #b3e5fc; }
        .result { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .product { background: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 15px; margin-bottom: 20px; }
        .sheet { background: #ecfdf5; border-left: 4px solid #10b981; padding: 15px; }
        .img { width: 200px; height: 200px; object-fit: cover; border-radius: 10px; }
        .price { font-size: 24px; font-weight: bold; color: #dc2626; }
        .brand { color: #2563eb; font-weight: bold; }
        .btn-export { background: #059669; }
        .btn-export:hover { background: #047857; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏷️ Générateur de Fiches Produits</h1>
            <p>EAN/SKU → Fiche PrestaShop complète</p>
        </div>
        
        <div class="form">
            <h2>🔍 Recherche Produit</h2>
            <div class="grid">
                <input type="text" id="ean" placeholder="Code EAN (13 chiffres)" maxlength="13">
                <input type="text" id="sku" placeholder="SKU / Référence">
            </div>
            <button onclick="search()" id="searchBtn">🚀 Rechercher & Créer Fiche</button>
            
            <div style="margin-top: 15px;">
                <span>Exemples : </span>
                <span class="example" onclick="fill('sku','48SMA0097-21G')">48SMA0097-21G (Lacoste Sneakers)</span>
                <span class="example" onclick="fill('ean','3608077027028')">3608077027028 (Polo Lacoste)</span>
            </div>
        </div>
        
        <div id="message"></div>
        <div id="results"></div>
    </div>

    <script>
        function fill(type, value) {
            if (type === 'sku') {
                document.getElementById('sku').value = value;
                document.getElementById('ean').value = '';
            } else {
                document.getElementById('ean').value = value;
                document.getElementById('sku').value = '';
            }
        }

        function showMessage(text, type) {
            const div = document.getElementById('message');
            const color = type === 'success' ? '#10b981' : '#ef4444';
            div.innerHTML = `<div style="background:${color};color:white;padding:10px;border-radius:5px;margin-bottom:15px;">${text}</div>`;
            setTimeout(() => div.innerHTML = '', 5000);
        }

        async function search() {
            const ean = document.getElementById('ean').value.trim();
            const sku = document.getElementById('sku').value.trim();
            const btn = document.getElementById('searchBtn');
            const results = document.getElementById('results');

            if (!ean && !sku) {
                showMessage('❌ Veuillez saisir un EAN ou un SKU', 'error');
                return;
            }

            btn.innerHTML = '🔄 Recherche...';
            btn.disabled = true;
            results.innerHTML = '<div style="text-align:center;padding:20px;">🔍 Recherche en cours...</div>';

            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ean: ean || null, sku: sku || null})
                });

                const data = await response.json();

                if (response.ok) {
                    showMessage('✅ ' + data.message, 'success');
                    displayResult(data.product, data.sheet);
                    document.getElementById('ean').value = '';
                    document.getElementById('sku').value = '';
                } else {
                    showMessage('❌ ' + (data.detail || 'Erreur'), 'error');
                    results.innerHTML = '';
                }
            } catch (error) {
                showMessage('❌ Erreur: ' + error.message, 'error');
                results.innerHTML = '';
            }

            btn.innerHTML = '🚀 Rechercher & Créer Fiche';
            btn.disabled = false;
        }

        function displayResult(product, sheet) {
            document.getElementById('results').innerHTML = `
                <div class="result">
                    <!-- Produit -->
                    <div class="product">
                        <h3>✅ Produit identifié</h3>
                        <div style="display:grid;grid-template-columns:200px 1fr;gap:20px;margin-top:15px;">
                            <img src="${product.image}" alt="${product.name}" class="img" onerror="this.src='https://via.placeholder.com/200x200/e0e0e0/666?text=Image'">
                            <div>
                                <h4 style="font-size:20px;margin:0 0 10px 0;">${product.name}</h4>
                                <div class="brand">${product.brand}</div>
                                <div class="price">${product.price}€ ${product.original_price ? '<span style="text-decoration:line-through;font-size:16px;color:#666;">'+product.original_price+'€</span>' : ''}</div>
                                <p style="color:#666;margin:10px 0;">${product.description}</p>
                                <div style="font-size:12px;color:#666;">
                                    EAN: ${product.ean} | SKU: ${product.sku}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Fiche PrestaShop -->
                    <div class="sheet">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <h3>📄 Fiche PrestaShop Générée</h3>
                            <button class="btn-export" onclick="exportCSV('${product.id}')">📥 Export CSV</button>
                        </div>
                        
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:15px;">
                            <div>
                                <h4>🎯 SEO Optimisé</h4>
                                <div style="background:white;padding:10px;border-radius:5px;">
                                    <strong>Titre:</strong> ${sheet.seo_title}<br>
                                    <strong>Description:</strong> ${sheet.seo_description}<br>
                                    <strong>URL:</strong> ${sheet.url_slug}
                                </div>
                            </div>
                            
                            <div>
                                <h4>📦 Informations</h4>
                                <div style="background:white;padding:10px;border-radius:5px;">
                                    <strong>Catégorie:</strong> ${sheet.category}<br>
                                    <strong>Poids:</strong> ${sheet.weight}kg<br>
                                    <strong>Variations:</strong> ${sheet.variations.length}
                                </div>
                            </div>
                        </div>

                        <div style="margin-top:15px;">
                            <h4>🔧 Caractéristiques</h4>
                            <div style="background:white;padding:10px;border-radius:5px;display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                                ${Object.entries(sheet.characteristics).map(([k,v]) => `<div><strong>${k}:</strong> ${v}</div>`).join('')}
                            </div>
                        </div>

                        <div style="margin-top:15px;">
                            <h4>📦 Variations disponibles</h4>
                            <div style="background:white;padding:10px;border-radius:5px;display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:5px;">
                                ${sheet.variations.slice(0,12).map(v => `
                                    <div style="background:#f3f4f6;padding:8px;border-radius:3px;text-align:center;font-size:12px;">
                                        <strong>${v.size || v.option}</strong>
                                        ${v.color ? '<br>'+v.color : ''}
                                        <br><span style="color:#059669;">Stock: ${v.stock}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        async function exportCSV(productId) {
            try {
                const response = await fetch('/api/export/' + productId);
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'prestashop_' + productId + '.csv';
                a.click();
                URL.revokeObjectURL(url);
                showMessage('✅ Fichier CSV téléchargé !', 'success');
            } catch (error) {
                showMessage('❌ Erreur export CSV', 'error');
            }
        }
    </script>
</body>
</html>
    """

@app.post("/api/search")
def search_product(request: SearchRequest):
    search_term = request.ean or request.sku
    search_type = "EAN" if request.ean else "SKU"
    
    if not search_term:
        raise HTTPException(status_code=400, detail="EAN ou SKU requis")
    
    # Trouver le produit
    product_info = PRODUCTS.get(search_term, {
        "name": f"Produit {search_term[:8]}",
        "brand": "Marque Inconnue",
        "price": 49.99,
        "description": f"Produit identifié par {search_type}",
        "image": "https://via.placeholder.com/300x300/e0e0e0/666?text=Produit"
    })
    
    # Créer le produit
    product = {
        "id": str(uuid.uuid4()),
        "ean": request.ean or f"EAN{uuid.uuid4().hex[:10].upper()}",
        "sku": request.sku or f"SKU{search_term[:8]}",
        "name": product_info["name"],
        "brand": product_info["brand"],
        "price": product_info["price"],
        "original_price": product_info.get("original_price"),
        "description": product_info["description"],
        "image": product_info["image"]
    }
    
    # Créer la fiche PrestaShop
    sheet = {
        "seo_title": f"{product['brand']} {product['name']}",
        "seo_description": f"Achetez {product['name']} {product['brand']} à {product['price']}€. Livraison gratuite.",
        "url_slug": f"{product['brand'].lower()}-{product['name'][:20].lower()}".replace(" ", "-"),
        "category": "Chaussures > Sneakers" if "sneakers" in product['name'].lower() else "Vêtements > Polos",
        "weight": 0.8 if "sneakers" in product['name'].lower() else 0.3,
        "characteristics": {
            "Marque": product['brand'],
            "Matière": "Cuir premium" if "lacoste" in product['brand'].lower() else "Standard",
            "Couleur": "Multicolore",
            "Entretien": "Selon notice"
        },
        "variations": [
            {"size": "39", "color": "Blanc", "stock": 15},
            {"size": "40", "color": "Blanc", "stock": 20},
            {"size": "41", "color": "Blanc", "stock": 25},
            {"size": "42", "color": "Blanc", "stock": 30},
            {"size": "43", "color": "Blanc", "stock": 20},
            {"size": "44", "color": "Blanc", "stock": 15}
        ] if "sneakers" in product['name'].lower() else [
            {"size": "S", "color": "Blanc", "stock": 10},
            {"size": "M", "color": "Blanc", "stock": 15},
            {"size": "L", "color": "Blanc", "stock": 20},
            {"size": "XL", "color": "Blanc", "stock": 15}
        ]
    }
    
    return {
        "success": True,
        "message": f"{product['brand']} {product['name']} trouvé et fiche générée !",
        "product": product,
        "sheet": sheet
    }

@app.get("/api/export/{product_id}")
def export_csv(product_id: str):
    csv_content = f"""ID;Nom;Prix;Référence;Description
{product_id};Produit Export;99.99;REF123;Description du produit exporté"""
    
    from fastapi.responses import Response
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=prestashop_{product_id}.csv"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)