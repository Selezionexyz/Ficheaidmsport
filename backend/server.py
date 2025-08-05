from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json
import requests
from openai import OpenAI
import asyncio
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection with OpenSSL 3.0 compatibility
mongo_url = os.environ.get('MONGO_URL')
if not mongo_url:
    raise ValueError("MONGO_URL environment variable is required")

# Add SSL configuration for OpenSSL 3.0 compatibility
if 'mongodb+srv://' in mongo_url:
    # For MongoDB Atlas connections, add specific SSL parameters
    if 'tlsAllowInvalidCertificates=true' not in mongo_url:
        separator = '&' if '?' in mongo_url else '?'
        mongo_url += f"{separator}tlsAllowInvalidCertificates=true&ssl_cert_reqs=0"

print(f"Connecting to MongoDB: {mongo_url[:50]}...")
client = AsyncIOMotorClient(mongo_url)
db_name = os.environ.get('DB_NAME', 'product_db')
db = client[db_name]
print(f"Connected to database: {db_name}")

# API Keys
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'your_openai_key_here')
GOOGLE_SEARCH_API_KEY = os.environ.get('GOOGLE_SEARCH_API_KEY', 'your_google_search_key_here')
GOOGLE_SEARCH_CX = os.environ.get('GOOGLE_SEARCH_CX', 'your_google_cx_here')

# Configure OpenAI client (TEMPORARILY DISABLED for testing)
openai_client = None
# if OPENAI_API_KEY and OPENAI_API_KEY != 'your_openai_key_here':
#     openai_client = OpenAI(api_key=OPENAI_API_KEY)

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
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ean_code: str
    search_query: str
    google_results: Optional[List[Dict]] = []
    extracted_info: Optional[Dict] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProductSearchCreate(BaseModel):
    ean_code: str

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ean_code: str
    title: str
    brand: str
    model: str
    color: str
    category: str
    price: Optional[float] = None
    description: str
    characteristics: Dict[str, str] = {}
    sizes: List[str] = []
    weight_by_type: Dict[str, float] = {
        "baskets": 1.0,
        "ensemble": 0.75,
        "sweat": 0.5,
        "t-shirt": 0.25,
        "maroquinerie": 0.3
    }
    images: List[str] = []
    google_source: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(BaseModel):
    ean_code: str
    title: str
    brand: str
    model: str
    color: str
    category: str
    price: Optional[float] = None
    description: str
    characteristics: Dict[str, str] = {}
    sizes: List[str] = []
    weight_by_type: Dict[str, float] = {}
    images: List[str] = []

class ProductSheet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    title: str
    reference: str
    color_code: str
    price_ttc: float
    description: str
    characteristics: Dict[str, str]
    variants: List[Dict] = []  # Tailles et couleurs
    weight_info: Dict[str, float]
    seo_title: str
    seo_description: str
    associated_products: List[str] = []
    prestashop_ready: bool = True
    export_data: Optional[Dict] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "draft"  # draft, published, exported

class ProductSheetCreate(BaseModel):
    product_id: str
    generate_with_ai: bool = True

class EANGenerateRequest(BaseModel):
    ean_code: str
    generate_sheet: bool = True

# ===== SERVICES =====

class GoogleSearchService:
    @staticmethod
    async def search_by_ean(ean_code: str) -> Dict:
        """Recherche Google optimisée par code EAN"""
        if GOOGLE_SEARCH_API_KEY == 'your_google_search_key_here' or GOOGLE_SEARCH_CX == 'your_google_cx_here':
            # Mode simulation avec données réalistes
            return {
                "items": [
                    {
                        "title": f"Nike Air Max 97 - EAN {ean_code}",
                        "snippet": f"Découvrez les Nike Air Max 97 avec le code EAN {ean_code}. Chaussures de sport premium avec technologie Air visible. Disponibles en plusieurs coloris et tailles.",
                        "link": f"https://www.nike.com/fr/product/{ean_code}",
                        "pagemap": {
                            "product": [{
                                "name": "Nike Air Max 97",
                                "brand": "Nike",
                                "price": "179.99"
                            }]
                        }
                    },
                    {
                        "title": f"Baskets Nike Air Max - {ean_code} | Zalando",
                        "snippet": f"Nike Air Max disponibles sur Zalando. Code EAN {ean_code}. Livraison gratuite. Retours gratuits pendant 100 jours.",
                        "link": f"https://www.zalando.fr/nike-air-max-{ean_code}",
                        "pagemap": {}
                    },
                    {
                        "title": f"Produit {ean_code} - Specifications",
                        "snippet": f"Caractéristiques détaillées du produit {ean_code}: matériaux, couleurs disponibles, guide des tailles.",
                        "link": f"https://www.produit-specs.com/{ean_code}",
                        "pagemap": {}
                    }
                ],
                "searchInformation": {
                    "totalResults": "3"
                }
            }
        
        try:
            # Requêtes multiples pour plus d'infos
            queries = [
                f"{ean_code} produit caractéristiques prix",
                f"{ean_code} marque modèle couleur",
                f"EAN {ean_code} specifications"
            ]
            
            all_results = []
            
            for query in queries:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': GOOGLE_SEARCH_API_KEY,
                    'cx': GOOGLE_SEARCH_CX,
                    'q': query,
                    'num': 5
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if 'items' in data:
                    all_results.extend(data['items'])
                
                # Petit délai entre requêtes
                await asyncio.sleep(0.1)
            
            return {
                "items": all_results[:10],  # Top 10 résultats
                "searchInformation": {
                    "totalResults": str(len(all_results))
                }
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur Google Search API: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur recherche Google: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue Google Search: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur système: {str(e)}")

    @staticmethod
    def extract_product_info(search_results: Dict) -> Dict:
        """Extrait les informations produit des résultats Google"""
        extracted = {
            "titles": [],
            "brands": [],
            "prices": [],
            "descriptions": [],
            "potential_category": "",
            "urls": []
        }
        
        if 'items' not in search_results:
            return extracted
            
        for item in search_results['items']:
            # Titres
            if 'title' in item:
                extracted["titles"].append(item['title'])
                
            # URLs
            if 'link' in item:
                extracted["urls"].append(item['link'])
                
            # Descriptions
            if 'snippet' in item:
                extracted["descriptions"].append(item['snippet'])
                
            # Informations structurées
            if 'pagemap' in item and 'product' in item['pagemap']:
                products = item['pagemap']['product']
                for product in products:
                    if 'brand' in product:
                        extracted["brands"].append(product['brand'])
                    if 'price' in product:
                        extracted["prices"].append(product['price'])
        
        # Détecter la catégorie
        all_text = " ".join(extracted["titles"] + extracted["descriptions"]).lower()
        if any(word in all_text for word in ['basket', 'chaussure', 'sneaker', 'air max', 'nike', 'adidas']):
            extracted["potential_category"] = "Chaussures"
        elif any(word in all_text for word in ['t-shirt', 'polo', 'sweat', 'hoodie', 'vêtement']):
            extracted["potential_category"] = "Vêtements"
        elif any(word in all_text for word in ['sac', 'portefeuille', 'maroquinerie']):
            extracted["potential_category"] = "Maroquinerie"
        
        return extracted

class AIService:
    @staticmethod
    async def generate_product_info(ean_code: str, search_results: Dict, extracted_info: Dict) -> Dict:
        """Génère les informations produit via OpenAI"""
        
        if not openai_client:
            # Mode simulation avec données intelligentes
            category = extracted_info.get("potential_category", "Chaussures")
            
            # Génération intelligente basée sur le contexte
            titles = extracted_info.get("titles", [])
            descriptions = extracted_info.get("descriptions", [])
            
            brand = "Nike"  # Par défaut
            if any("adidas" in str(t).lower() for t in titles):
                brand = "Adidas"
            elif any("lacoste" in str(t).lower() for t in titles):
                brand = "Lacoste"
            elif any("hugo" in str(t).lower() for t in titles):
                brand = "Hugo Boss"
            
            # Prix simulé
            prices = extracted_info.get("prices", [])
            price = 99.99
            if prices:
                try:
                    price = float(re.findall(r'\d+\.?\d*', str(prices[0]))[0])
                except:
                    price = 99.99
            
            return {
                "title": f"{category} {brand} Premium - EAN {ean_code}",
                "brand": brand,
                "model": f"Modèle {ean_code[-4:]}",
                "color": "Noir",
                "category": category,
                "price": price,
                "description": f"Découvrez ce magnifique produit {brand} de catégorie {category}. Conçu avec des matériaux de qualité premium, ce produit allie style et performance. Le code EAN {ean_code} garantit l'authenticité. Parfait pour un usage quotidien ou sportif, il s'adapte à toutes les occasions. Design moderne et confortable, disponible en plusieurs tailles.",
                "characteristics": {
                    "marque": brand,
                    "couleur": "Noir",
                    "matière": "Synthétique et textile",
                    "saison": "Toute saison",
                    "style": "Sport/Streetwear",
                    "origine": "Import"
                },
                "sizes": ["36", "37", "38", "39", "40", "41", "42", "43", "44", "45"] if category == "Chaussures" else ["XS", "S", "M", "L", "XL", "XXL"],
                "weight_by_type": {
                    "baskets": 1.0,
                    "ensemble": 0.75,
                    "sweat": 0.5,
                    "t-shirt": 0.25,
                    "maroquinerie": 0.3
                }
            }
        
        try:
            # Préparer le contexte
            context_titles = "\n".join(extracted_info.get("titles", [])[:5])
            context_descriptions = "\n".join(extracted_info.get("descriptions", [])[:3])
            context_brands = ", ".join(set(extracted_info.get("brands", [])))
            context_urls = "\n".join(extracted_info.get("urls", [])[:3])
            
            prompt = f"""
Tu es un expert en e-commerce spécialisé dans la création de fiches produits pour une boutique de sport style DM'Sports.

CODE EAN À ANALYSER: {ean_code}

INFORMATIONS TROUVÉES SUR GOOGLE:

Titres des résultats:
{context_titles}

Descriptions:
{context_descriptions}

Marques détectées: {context_brands}

URLs sources:
{context_urls}

CATÉGORIE POTENTIELLE: {extracted_info.get('potential_category', 'Non déterminée')}

MISSION:
Génère un produit e-commerce complet au format JSON stricte avec ces champs OBLIGATOIRES:

{{
  "title": "Titre produit structuré: [Catégorie] [Marque] [Modèle] - [Couleur]",
  "brand": "Marque principale du produit",
  "model": "Nom/modèle précis du produit",
  "color": "Couleur principale",
  "category": "Catégorie principale (Chaussures/Vêtements/Accessoires/Maroquinerie)",
  "price": prix_numérique_sans_devise,
  "description": "Description vendeuse de 250-400 mots, optimisée pour la vente en ligne, mettant en avant les bénéfices client",
  "characteristics": {{
    "marque": "nom_marque",
    "couleur": "couleur_principale",
    "matière": "matériaux_utilisés",
    "saison": "saison_appropriée",
    "style": "style_vestimentaire",
    "origine": "pays_origine_ou_import"
  }},
  "sizes": ["liste", "des", "tailles", "disponibles"],
  "weight_by_type": {{
    "baskets": 1.0,
    "ensemble": 0.75,
    "sweat": 0.5,
    "t-shirt": 0.25,
    "maroquinerie": 0.3
  }}
}}

RÈGLES IMPORTANTES:
- Utilise UNIQUEMENT les informations des résultats Google
- Si une info manque, déduis intelligemment du contexte
- Prix réaliste pour le marché français
- Description vendeuse et engageante
- Tailles adaptées au type de produit
- Style DM'Sports: moderne, sport, streetwear

RÉPONDS UNIQUEMENT EN JSON VALIDE, SANS AUTRE TEXTE.
"""

            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Nettoyer le JSON si nécessaire
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON OpenAI: {e}")
            raise HTTPException(status_code=500, detail="Erreur format réponse IA")
        except Exception as e:
            logger.error(f"Erreur OpenAI API: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur génération IA: {str(e)}")
    
    @staticmethod
    async def generate_product_sheet(product: Product) -> Dict:
        """Génère une fiche produit PrestaShop optimisée"""
        
        if not openai_client:
            # Mode simulation
            return {
                "title": product.title,
                "reference": f"REF-{product.ean_code[-8:]}",
                "color_code": product.color[:3].upper(),
                "price_ttc": product.price or 99.99,
                "description": f"""
<div class="product-description">
    <h3>🏷️ {product.title}</h3>
    <p><strong>Marque:</strong> {product.brand}</p>
    <p><strong>Modèle:</strong> {product.model}</p>
    <p><strong>Couleur:</strong> {product.color}</p>
    
    <h4>📋 Description</h4>
    <p>{product.description}</p>
    
    <h4>✨ Caractéristiques</h4>
    <ul>
        {"".join([f"<li><strong>{k.title()}:</strong> {v}</li>" for k, v in product.characteristics.items()])}
    </ul>
    
    <h4>📏 Tailles disponibles</h4>
    <p>{" • ".join(product.sizes)}</p>
    
    <p class="highlight">Code EAN: {product.ean_code}</p>
</div>
                """,
                "characteristics": product.characteristics,
                "seo_title": f"{product.title} - {product.brand} | DM'Sports - Livraison Gratuite",
                "seo_description": f"Achetez {product.title} de {product.brand} sur DM'Sports. {product.description[:120]}... Livraison gratuite et retour sous 30 jours.",
                "export_data": {
                    "prestashop_format": {
                        "name": product.title,
                        "reference": f"REF-{product.ean_code[-8:]}",
                        "price": product.price or 99.99,
                        "description": product.description,
                        "meta_title": f"{product.title} - {product.brand} | DM'Sports",
                        "meta_description": product.description[:155],
                        "categories": [product.category],
                        "brand": product.brand,
                        "ean13": product.ean_code
                    }
                }
            }
        
        try:
            prompt = f"""
Tu es un expert PrestaShop pour DM'Sports. Génère une fiche produit complète.

PRODUIT:
- Titre: {product.title}
- Marque: {product.brand}
- EAN: {product.ean_code}
- Catégorie: {product.category}
- Prix: {product.price}€
- Description: {product.description}
- Caractéristiques: {product.characteristics}
- Tailles: {product.sizes}

Génère au format JSON:

{{
  "title": "titre_optimisé_prestashop",
  "reference": "REF-code_unique",
  "color_code": "code_couleur_court",
  "price_ttc": prix_numérique,
  "description": "description_html_prestashop_formatée",
  "characteristics": {product.characteristics},
  "seo_title": "titre_seo_optimisé_max_70_caractères",
  "seo_description": "meta_description_max_155_caractères",
  "export_data": {{
    "prestashop_format": {{
      "name": "nom_produit",
      "reference": "référence_unique",
      "price": prix,
      "description": "description_produit",
      "meta_title": "titre_meta",
      "meta_description": "description_meta",
      "categories": ["catégorie_principale"],
      "brand": "marque",
      "ean13": "{product.ean_code}"
    }}
  }}
}}

RÈGLES:
- Description HTML avec balises <h3>, <p>, <ul>, <li>
- SEO optimisé pour Google
- Format PrestaShop standard
- Style DM'Sports moderne

JSON UNIQUEMENT:
"""

            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=1200
            )
            
            content = response.choices[0].message.content.strip()
            
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
                
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Erreur génération fiche: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur génération fiche: {str(e)}")

# ===== API ENDPOINTS =====

@api_router.get("/")
async def root():
    """Status de l'API"""
    return {
        "message": "🏷️ API Générateur de Fiches Produits DM'Sports", 
        "version": "2.0.0",
        "features": ["EAN Search", "AI Generation", "PrestaShop Export"],
        "openai_configured": openai_client is not None,
        "google_configured": GOOGLE_SEARCH_API_KEY != 'your_google_search_key_here'
    }

@api_router.post("/search/ean", response_model=ProductSearch)
async def search_by_ean(search_request: ProductSearchCreate):
    """Recherche complète par code EAN"""
    try:
        logger.info(f"Recherche EAN: {search_request.ean_code}")
        
        # Recherche Google
        search_results = await GoogleSearchService.search_by_ean(search_request.ean_code)
        
        # Extraction des infos
        extracted_info = GoogleSearchService.extract_product_info(search_results)
        
        # Sauvegarder la recherche
        search_obj = ProductSearch(
            ean_code=search_request.ean_code,
            search_query=f"{search_request.ean_code} produit caractéristiques",
            google_results=search_results.get('items', []),
            extracted_info=extracted_info
        )
        
        await db.product_searches.insert_one(search_obj.dict())
        logger.info(f"Recherche EAN sauvegardée: {search_obj.id}")
        
        return search_obj
        
    except Exception as e:
        logger.error(f"Erreur recherche EAN: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/generate/product")
async def generate_product_from_ean(request: EANGenerateRequest):
    """Pipeline complet: EAN → Recherche → Génération IA → Fiche"""
    try:
        logger.info(f"Pipeline complet pour EAN: {request.ean_code}")
        
        # Étape 1: Recherche Google
        search_results = await GoogleSearchService.search_by_ean(request.ean_code)
        extracted_info = GoogleSearchService.extract_product_info(search_results)
        
        # Étape 2: Génération IA du produit
        product_info = await AIService.generate_product_info(
            request.ean_code, 
            search_results, 
            extracted_info
        )
        
        # Étape 3: Créer le produit
        product = Product(
            ean_code=request.ean_code,
            google_source=f"Google Search - {len(search_results.get('items', []))} résultats",
            **product_info
        )
        
        await db.products.insert_one(product.dict())
        logger.info(f"Produit créé: {product.id}")
        
        # Étape 4: Générer la fiche si demandée
        product_sheet = None
        if request.generate_sheet:
            sheet_info = await AIService.generate_product_sheet(product)
            product_sheet = ProductSheet(
                product_id=product.id,
                weight_info=product.weight_by_type,
                **sheet_info
            )
            await db.product_sheets.insert_one(product_sheet.dict())
            logger.info(f"Fiche créée: {product_sheet.id}")
        
        return {
            "success": True,
            "product": product,
            "product_sheet": product_sheet,
            "search_summary": {
                "results_count": len(search_results.get('items', [])),
                "brands_found": extracted_info.get("brands", []),
                "category_detected": extracted_info.get("potential_category", "")
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur pipeline EAN: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/products", response_model=List[Product])
async def get_products(limit: int = 50, offset: int = 0, category: Optional[str] = None):
    """Liste des produits avec filtres"""
    try:
        query = {}
        if category:
            query["category"] = category
            
        cursor = db.products.find(query).sort("created_at", -1).skip(offset).limit(limit)
        products = await cursor.to_list(length=limit)
        return [Product(**product) for product in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Détail d'un produit"""
    try:
        product = await db.products.find_one({"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        return Product(**product)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/sheets", response_model=List[ProductSheet])
async def get_product_sheets(limit: int = 50, offset: int = 0, status: Optional[str] = None):
    """Liste des fiches produits"""
    try:
        query = {}
        if status:
            query["status"] = status
            
        cursor = db.product_sheets.find(query).sort("created_at", -1).skip(offset).limit(limit)
        sheets = await cursor.to_list(length=limit)
        return [ProductSheet(**sheet) for sheet in sheets]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/sheets", response_model=ProductSheet)
async def create_product_sheet(sheet_request: ProductSheetCreate):
    """Génère une fiche produit pour un produit existant"""
    try:
        product_data = await db.products.find_one({"id": sheet_request.product_id})
        if not product_data:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        
        product = Product(**product_data)
        
        if sheet_request.generate_with_ai:
            sheet_info = await AIService.generate_product_sheet(product)
        else:
            sheet_info = {
                "title": product.title,
                "reference": f"REF-{product.ean_code[-8:]}",
                "color_code": product.color[:3].upper(),
                "price_ttc": product.price or 99.99,
                "description": product.description,
                "characteristics": product.characteristics,
                "seo_title": f"{product.title} - {product.brand}",
                "seo_description": product.description[:155] + "..."
            }
        
        product_sheet = ProductSheet(
            product_id=sheet_request.product_id,
            weight_info=product.weight_by_type,
            **sheet_info
        )
        
        await db.product_sheets.insert_one(product_sheet.dict())
        return product_sheet
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/sheets/{sheet_id}/export")
async def export_product_sheet(sheet_id: str, format: str = "prestashop"):
    """Export de fiche produit (PrestaShop, CSV, JSON)"""
    try:
        sheet_data = await db.product_sheets.find_one({"id": sheet_id})
        if not sheet_data:
            raise HTTPException(status_code=404, detail="Fiche non trouvée")
            
        sheet = ProductSheet(**sheet_data)
        
        if format == "prestashop":
            return {
                "format": "prestashop",
                "data": sheet.export_data.get("prestashop_format", {}),
                "instructions": "Importez ces données dans PrestaShop via CSV ou API"
            }
        elif format == "json":
            return {"format": "json", "data": sheet.dict()}
        else:
            raise HTTPException(status_code=400, detail="Format non supporté")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """Supprime un produit et ses fiches"""
    try:
        result = await db.products.delete_one({"id": product_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        
        await db.product_sheets.delete_many({"product_id": product_id})
        
        return {"message": "Produit supprimé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/stats")
async def get_stats():
    """Statistiques de l'application"""
    try:
        total_products = await db.products.count_documents({})
        total_sheets = await db.product_sheets.count_documents({})
        total_searches = await db.product_searches.count_documents({})
        
        # Stats par catégorie
        categories = await db.products.aggregate([
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ]).to_list(length=None)
        
        return {
            "total_products": total_products,
            "total_sheets": total_sheets,
            "total_searches": total_searches,
            "categories": {cat["_id"]: cat["count"] for cat in categories},
            "api_status": {
                "openai_configured": openai_client is not None,
                "google_configured": GOOGLE_SEARCH_API_KEY != 'your_google_search_key_here'
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include router
app.include_router(api_router)

# Servir le frontend React (pour production)
frontend_path = Path(__file__).parent.parent / "frontend" / "build"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse(str(frontend_path / "index.html"))
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Si c'est un fichier statique, le servir
        file_path = frontend_path / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        # Sinon, servir index.html pour le routing SPA
        return FileResponse(str(frontend_path / "index.html"))

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Démarrage API Générateur de Fiches Produits")
    logger.info(f"OpenAI configuré: {openai_client is not None}")
    logger.info(f"Google Search configuré: {GOOGLE_SEARCH_API_KEY != 'your_google_search_key_here'}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()