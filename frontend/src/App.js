import React, { useState, useEffect } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [eanCode, setEanCode] = useState('');
  const [autoGenerate, setAutoGenerate] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [products, setProducts] = useState([]);
  const [sheets, setSheets] = useState([]);
  const [activeTab, setActiveTab] = useState('search');

  // Charger les données au démarrage
  useEffect(() => {
    loadProducts();
    loadSheets();
  }, []);

  const loadProducts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/products`);
      const data = await response.json();
      setProducts(data.products || []);
    } catch (err) {
      console.error('Erreur chargement produits:', err);
    }
  };

  const loadSheets = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/sheets`);
      const data = await response.json();
      setSheets(data.sheets || []);
    } catch (err) {
      console.error('Erreur chargement fiches:', err);
    }
  };

  const handleSearch = async () => {
    if (!eanCode.trim()) {
      setError('Veuillez saisir un code EAN');
      return;
    }

    if (eanCode.length !== 13) {
      setError('Le code EAN doit contenir 13 chiffres');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${BACKEND_URL}/api/search`, {
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
        setSuccess(data.message);
        setEanCode('');
        loadProducts();
        loadSheets();
      }
    } catch (err) {
      setError('Erreur: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <span className="text-2xl mr-3">🏷️</span>
              <h1 className="text-2xl font-bold text-gray-800">
                Générateur de Fiches Produits
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                IA + EAN
              </span>
              <span className="text-gray-600">Style DM'Sports</span>
            </div>
          </div>
        </div>

        {/* Messages */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            ❌ {error}
          </div>
        )}
        
        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            ✅ {success}
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('search')}
              className={`px-6 py-3 font-medium ${
                activeTab === 'search'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              🔍 Recherche EAN
            </button>
            <button
              onClick={() => setActiveTab('products')}
              className={`px-6 py-3 font-medium ${
                activeTab === 'products'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              📦 Produits ({products.length})
            </button>
            <button
              onClick={() => setActiveTab('sheets')}
              className={`px-6 py-3 font-medium ${
                activeTab === 'sheets'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              📄 Fiches Créées ({sheets.length})
            </button>
          </div>

          <div className="p-6">
            {/* Onglet Recherche */}
            {activeTab === 'search' && (
              <div>
                <h2 className="text-xl font-semibold mb-4">🔍 Recherche par Code EAN</h2>
                
                <div className="space-y-4">
                  <div>
                    <input
                      type="text"
                      value={eanCode}
                      onChange={(e) => setEanCode(e.target.value)}
                      placeholder="Entrez le code EAN du produit (13 chiffres)..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      maxLength="13"
                    />
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="autoGenerate"
                      checked={autoGenerate}
                      onChange={(e) => setAutoGenerate(e.target.checked)}
                      className="mr-2"
                    />
                    <label htmlFor="autoGenerate" className="text-gray-700">
                      ✅ Générer la fiche automatiquement
                    </label>
                  </div>
                  
                  <button
                    onClick={handleSearch}
                    disabled={loading}
                    className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    {loading ? '🔄 Recherche en cours...' : '🚀 Rechercher & Générer'}
                  </button>
                </div>

                <div className="mt-6">
                  <p className="text-sm text-gray-600 mb-2">💡 Exemples de codes EAN :</p>
                  <div className="flex flex-wrap gap-2">
                    {['3614270357637', '4064037884942', '1234567890123'].map(code => (
                      <button
                        key={code}
                        onClick={() => setEanCode(code)}
                        className="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm"
                      >
                        {code}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Onglet Produits */}
            {activeTab === 'products' && (
              <div>
                <h2 className="text-xl font-semibold mb-4">📦 Produits trouvés</h2>
                {products.length === 0 ? (
                  <p className="text-gray-500">Aucun produit trouvé. Effectuez une recherche pour commencer.</p>
                ) : (
                  <div className="space-y-3">
                    {products.map(product => (
                      <div key={product.id} className="bg-gray-50 p-4 rounded-lg">
                        <div className="flex justify-between items-start">
                          <div>
                            <h3 className="font-semibold">{product.name}</h3>
                            <p className="text-sm text-gray-600">EAN: {product.ean}</p>
                            <p className="text-sm text-gray-600">Marque: {product.brand}</p>
                            <p className="text-sm text-gray-600">Prix: {product.price}€</p>
                          </div>
                          <span className="text-xs text-gray-400">
                            {new Date(product.created_at).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Onglet Fiches */}
            {activeTab === 'sheets' && (
              <div>
                <h2 className="text-xl font-semibold mb-4">📄 Fiches créées</h2>
                {sheets.length === 0 ? (
                  <p className="text-gray-500">Aucune fiche créée. Activez la génération automatique lors de vos recherches.</p>
                ) : (
                  <div className="space-y-3">
                    {sheets.map(sheet => (
                      <div key={sheet.id} className="bg-green-50 p-4 rounded-lg">
                        <div className="flex justify-between items-start">
                          <div>
                            <h3 className="font-semibold">{sheet.title}</h3>
                            <p className="text-sm text-gray-600">EAN: {sheet.ean}</p>
                            <p className="text-sm text-gray-600">{sheet.description}</p>
                          </div>
                          <span className="text-xs text-gray-400">
                            {new Date(sheet.created_at).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Comment ça marche */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">🚀 Comment ça marche ?</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl">1</span>
              </div>
              <h3 className="font-semibold mb-2">🏷️ Code EAN</h3>
              <p className="text-sm text-gray-600">
                Saisissez le code-barres du produit (13 chiffres)
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl">2</span>
              </div>
              <h3 className="font-semibold mb-2">🔍 Recherche IA</h3>
              <p className="text-sm text-gray-600">
                L'IA trouve automatiquement les infos sur Google
              </p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl">3</span>
              </div>
              <h3 className="font-semibold mb-2">📄 Fiche générée</h3>
              <p className="text-sm text-gray-600">
                Fiche complète prête pour PrestaShop
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;