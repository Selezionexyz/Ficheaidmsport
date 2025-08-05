// Script d'initialisation MongoDB
// Générateur de Fiches Produits DM'Sports

// Sélectionner la base de données
db = db.getSiblingDB('dmsports_products');

// Créer un utilisateur pour l'application (optionnel)
db.createUser({
    user: "dmsports_user",
    pwd: "secure_password_change_in_production",
    roles: [
        {
            role: "readWrite",
            db: "dmsports_products"
        }
    ]
});

// Créer les collections principales
db.createCollection("products", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["id", "ean_code", "title", "brand", "category"],
            properties: {
                id: {
                    bsonType: "string",
                    description: "Identifiant unique du produit (UUID)"
                },
                ean_code: {
                    bsonType: "string",
                    pattern: "^[0-9]{13}$",
                    description: "Code EAN à 13 chiffres"
                },
                title: {
                    bsonType: "string",
                    minLength: 3,
                    maxLength: 200,
                    description: "Titre du produit"
                },
                brand: {
                    bsonType: "string",
                    minLength: 1,
                    maxLength: 100,
                    description: "Marque du produit"
                },
                category: {
                    bsonType: "string",
                    enum: ["Chaussures", "Vêtements", "Accessoires", "Maroquinerie"],
                    description: "Catégorie du produit"
                },
                price: {
                    bsonType: ["double", "null"],
                    minimum: 0,
                    description: "Prix du produit"
                },
                created_at: {
                    bsonType: "date",
                    description: "Date de création"
                }
            }
        }
    }
});

db.createCollection("product_sheets", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["id", "product_id", "title", "reference"],
            properties: {
                id: {
                    bsonType: "string",
                    description: "Identifiant unique de la fiche (UUID)"
                },
                product_id: {
                    bsonType: "string",
                    description: "Référence vers le produit parent (UUID)"
                },
                title: {
                    bsonType: "string",
                    minLength: 3,
                    maxLength: 200,
                    description: "Titre de la fiche produit"
                },
                reference: {
                    bsonType: "string",
                    minLength: 5,
                    maxLength: 50,
                    description: "Référence unique de la fiche"
                },
                status: {
                    bsonType: "string",
                    enum: ["draft", "published", "exported"],
                    description: "Statut de la fiche"
                },
                created_at: {
                    bsonType: "date",
                    description: "Date de création"
                }
            }
        }
    }
});

db.createCollection("product_searches", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["id", "ean_code", "search_query"],
            properties: {
                id: {
                    bsonType: "string",
                    description: "Identifiant unique de la recherche (UUID)"
                },
                ean_code: {
                    bsonType: "string",
                    pattern: "^[0-9]{13}$",
                    description: "Code EAN recherché"
                },
                search_query: {
                    bsonType: "string",
                    description: "Requête de recherche utilisée"
                },
                created_at: {
                    bsonType: "date",
                    description: "Date de la recherche"
                }
            }
        }
    }
});

// Créer des index pour optimiser les performances
db.products.createIndex({ "ean_code": 1 }, { unique: true });
db.products.createIndex({ "brand": 1 });
db.products.createIndex({ "category": 1 });
db.products.createIndex({ "created_at": -1 });

db.product_sheets.createIndex({ "product_id": 1 });
db.product_sheets.createIndex({ "reference": 1 }, { unique: true });
db.product_sheets.createIndex({ "status": 1 });
db.product_sheets.createIndex({ "created_at": -1 });

db.product_searches.createIndex({ "ean_code": 1 });
db.product_searches.createIndex({ "created_at": -1 });

// Insérer des données de test (optionnel)
db.products.insertMany([
    {
        id: "test-product-1",
        ean_code: "1234567890123",
        title: "Nike Air Max 97 - Test",
        brand: "Nike",
        model: "Air Max 97",
        color: "Noir",
        category: "Chaussures",
        price: 179.99,
        description: "Chaussures de test pour démonstration du système DM'Sports. Modèle iconique avec technologie Air Max visible.",
        characteristics: {
            "marque": "Nike",
            "couleur": "Noir",
            "matière": "Synthétique et textile",
            "saison": "Toute saison",
            "style": "Sport/Streetwear",
            "origine": "Import"
        },
        sizes: ["39", "40", "41", "42", "43", "44"],
        weight_by_type: {
            "baskets": 1.0,
            "ensemble": 0.75,
            "sweat": 0.5,
            "t-shirt": 0.25,
            "maroquinerie": 0.3
        },
        images: [],
        google_source: "Test Data - Manuel",
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        id: "test-product-2", 
        ean_code: "2345678901234",
        title: "Adidas Originals Stan Smith - Blanc",
        brand: "Adidas",
        model: "Stan Smith",
        color: "Blanc",
        category: "Chaussures",
        price: 89.99,
        description: "Baskets emblématiques Adidas Stan Smith en cuir blanc. Design intemporel et confort exceptionnel pour un style casual chic.",
        characteristics: {
            "marque": "Adidas",
            "couleur": "Blanc",
            "matière": "Cuir",
            "saison": "Toute saison",
            "style": "Casual/Streetwear",
            "origine": "Import"
        },
        sizes: ["37", "38", "39", "40", "41", "42", "43"],
        weight_by_type: {
            "baskets": 0.8,
            "ensemble": 0.75,
            "sweat": 0.5,
            "t-shirt": 0.25,
            "maroquinerie": 0.3
        },
        images: [],
        google_source: "Test Data - Manuel",
        created_at: new Date(),
        updated_at: new Date()
    }
]);

// Insérer une fiche de test
db.product_sheets.insertOne({
    id: "test-sheet-1",
    product_id: "test-product-1",
    title: "Nike Air Max 97 - Test",
    reference: "REF-TEST001",
    color_code: "NOI",
    price_ttc: 179.99,
    description: "<div class='product-description'><h3>🏷️ Nike Air Max 97 - Test</h3><p><strong>Marque:</strong> Nike</p><p><strong>Modèle:</strong> Air Max 97</p><p><strong>Couleur:</strong> Noir</p><h4>📋 Description</h4><p>Chaussures de test pour démonstration du système DM'Sports. Modèle iconique avec technologie Air Max visible.</p></div>",
    characteristics: {
        "marque": "Nike",
        "couleur": "Noir",
        "matière": "Synthétique et textile",
        "saison": "Toute saison"
    },
    variants: [],
    weight_info: {
        "baskets": 1.0
    },
    seo_title: "Nike Air Max 97 Test - Nike | DM'Sports - Livraison Gratuite",
    seo_description: "Achetez Nike Air Max 97 Test de Nike sur DM'Sports. Chaussures de test pour démonstration du système DM'Sports...",
    associated_products: [],
    prestashop_ready: true,
    export_data: {
        prestashop_format: {
            name: "Nike Air Max 97 - Test",
            reference: "REF-TEST001",
            price: 179.99,
            description: "Chaussures de test pour démonstration du système DM'Sports.",
            meta_title: "Nike Air Max 97 Test - Nike | DM'Sports",
            meta_description: "Chaussures de test pour démonstration du système DM'Sports. Modèle iconique avec technologie Air Max visible.",
            categories: ["Chaussures"],
            brand: "Nike",
            ean13: "1234567890123"
        }
    },
    created_at: new Date(),
    status: "draft"
});

// Insérer une recherche de test
db.product_searches.insertOne({
    id: "test-search-1",
    ean_code: "1234567890123",
    search_query: "1234567890123 produit caractéristiques",
    google_results: [
        {
            title: "Nike Air Max 97 - Test Product",
            snippet: "Produit de test pour le système DM'Sports",
            link: "https://example.com/test-product"
        }
    ],
    extracted_info: {
        titles: ["Nike Air Max 97 - Test Product"],
        brands: ["Nike"],
        prices: ["179.99"],
        descriptions: ["Produit de test pour le système DM'Sports"],
        potential_category: "Chaussures",
        urls: ["https://example.com/test-product"]
    },
    created_at: new Date()
});

print("✅ Base de données DM'Sports initialisée avec succès !");
print("📊 Collections créées : products, product_sheets, product_searches");
print("📈 Index créés pour optimiser les performances");
print("🧪 Données de test insérées pour développement");
print("");
print("🔍 Commandes utiles :");
print("- db.products.find().pretty()");
print("- db.product_sheets.find().pretty()");
print("- db.product_searches.find().pretty()");
print("- db.stats()");
print("");
print("🎯 Application prête à être utilisée !");