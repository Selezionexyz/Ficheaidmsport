#!/usr/bin/env python3
import os
import asyncio
import sys
sys.path.append('/app/backend')

from server import GoogleCustomSearchService

async def test_google_search():
    print("🔍 TEST GOOGLE CUSTOM SEARCH")
    print("=" * 50)
    
    try:
        service = GoogleCustomSearchService()
        print(f"✅ Service initialisé")
        print(f"   - API Key: {'✅ Configurée' if service.api_key else '❌ Manquante'}")
        print(f"   - Engine ID: {'✅ Configurée' if service.search_engine_id else '❌ Manquante'}")
        
        # Test avec EAN Polo Lacoste
        ean = "3608077027028"
        print(f"\n🔍 Recherche EAN: {ean}")
        
        result = await service.search_product_by_ean_sku(ean)
        
        print(f"\n📊 RÉSULTATS:")
        print(f"   - Nom: {result['name']}")
        print(f"   - Marque: {result['brand']}")
        print(f"   - Prix: {result['price']}€")
        print(f"   - Type: {result['type']}")
        print(f"   - Confiance: {result.get('confidence', 0):.0f}%")
        print(f"   - Description: {result['description'][:100]}...")
        
        # Test avec SKU Lacoste
        sku = "49SMA0006-02H"
        print(f"\n🔍 Recherche SKU: {sku}")
        
        result2 = await service.search_product_by_ean_sku(sku)
        
        print(f"\n📊 RÉSULTATS:")
        print(f"   - Nom: {result2['name']}")
        print(f"   - Marque: {result2['brand']}")
        print(f"   - Prix: {result2['price']}€")
        print(f"   - Type: {result2['type']}")
        print(f"   - Confiance: {result2.get('confidence', 0):.0f}%")
        
        print(f"\n✅ GOOGLE CUSTOM SEARCH FONCTIONNE !")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(test_google_search())