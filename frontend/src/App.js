import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ===== COMPONENTS =====

const Header = ({ stats }) => (
  <header className="bg-white shadow-sm border-b">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center h-16">
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-gray-900">🏷️ Générateur de Fiches Produits</h1>
            <span className="ml-3 px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
              IA + EAN
            </span>
          </div>
          {stats && (
            <div className="hidden md:flex space-x-3 text-sm text-gray-600">
              <span>📦 {stats.total_products} produits</span>
              <span>📋 {stats.total_sheets} fiches</span>
              <span>🔍 {stats.total_searches} recherches</span>
            </div>
          )}
        </div>
        <div className="flex items-center space-x-2 text-sm">
          <span className="text-gray-500">Style DM'Sports</span>
          {stats?.api_status && (
            <div className="flex space-x-1">
              <span className={`w-2 h-2 rounded-full ${stats.api_status.openai_configured ? 'bg-green-400' : 'bg-red-400'}`} title="OpenAI"></span>
              <span className={`w-2 h-2 rounded-full ${stats.api_status.google_configured ? 'bg-green-400' : 'bg-red-400'}`} title="Google"></span>
            </div>
          )}
        </div>
      </div>
    </div>
  </header>
);

const EANSearchForm = ({ onSearch, loading }) => {
  const [eanCode, setEanCode] = useState('');
  const [generateSheet, setGenerateSheet] = useState(true);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (eanCode.trim()) {
      onSearch(eanCode.trim(), generateSheet);
    }
  };
  
  // Exemples de codes EAN réels
  const exampleEans = [
    { code: "3614270357637", desc: "Nike Air Max (exemple)" },
    { code: "4064037884942", desc: "Adidas Originals" },
    { code: "1234567890123", desc: "Code test" }
  ];
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-800">🔍 Recherche par Code EAN</h2>
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="generate-sheet"
            checked={generateSheet}
            onChange={(e) => setGenerateSheet(e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
          />
          <label htmlFor="generate-sheet" className="text-sm text-gray-600">
            Générer la fiche automatiquement
          </label>
        </div>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex gap-4">
          <div className="flex-1">
            <input
              type="text"
              value={eanCode}
              onChange={(e) => setEanCode(e.target.value)}
              placeholder="Entrez le code EAN du produit (13 chiffres)..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
              disabled={loading}
              pattern="[0-9]*"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !eanCode.trim()}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-medium rounded-lg hover:from-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all duration-200 shadow-md"
          >
            {loading ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
                <span>Analyse en cours...</span>
              </div>
            ) : (
              '🚀 Rechercher & Générer'
            )}
          </button>
        </div>
        
        {/* Exemples de codes EAN */}
        <div className="border-t pt-4">
          <p className="text-sm text-gray-600 mb-2">💡 Exemples de codes EAN :</p>
          <div className="flex flex-wrap gap-2">
            {exampleEans.map((example, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setEanCode(example.code)}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
                disabled={loading}
              >
                {example.code} <span className="text-gray-500">({example.desc})</span>
              </button>
            ))}
          </div>
        </div>
      </form>
    </div>
  );
};

const ProductCard = ({ product, onGenerateSheet, onDelete, onViewDetails }) => (
  <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-all duration-200 border border-gray-100">
    <div className="p-6">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">{product.title}</h3>
          <div className="space-y-1 text-sm">
            <p className="text-gray-600">🏷️ EAN: <span className="font-mono">{product.ean_code}</span></p>
            <p className="text-blue-600 font-medium">🏢 {product.brand} • 📂 {product.category}</p>
            {product.google_source && (
              <p className="text-green-600 text-xs">✅ {product.google_source}</p>
            )}
          </div>
        </div>
        <div className="flex flex-col gap-2 ml-4">
          {product.price && (
            <span className="text-lg font-bold text-green-600">{product.price}€</span>
          )}
          <div className="flex gap-1">
            <button
              onClick={() => onGenerateSheet(product.id)}
              className="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full hover:bg-green-200 transition-colors"
              title="Générer fiche PrestaShop"
            >
              📋 Fiche
            </button>
            <button
              onClick={() => onViewDetails(product)}
              className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full hover:bg-blue-200 transition-colors"
              title="Voir détails"
            >
              👁️ Détails
            </button>
            <button
              onClick={() => onDelete(product.id)}
              className="px-3 py-1 bg-red-100 text-red-700 text-xs font-medium rounded-full hover:bg-red-200 transition-colors"
              title="Supprimer"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>
      
      <div className="space-y-3">
        {/* Couleur et modèle */}
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            🎨 {product.color}
          </span>
          <span className="text-sm text-gray-600">📱 {product.model}</span>
        </div>
        
        {/* Tailles */}
        {product.sizes?.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">📏 Tailles:</span>
            <div className="flex gap-1 flex-wrap">
              {product.sizes.slice(0, 8).map((size, idx) => (
                <span key={idx} className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded border">
                  {size}
                </span>
              ))}
              {product.sizes.length > 8 && (
                <span className="text-xs text-gray-400">+{product.sizes.length - 8}</span>
              )}
            </div>
          </div>
        )}
        
        {/* Description */}
        <p className="text-sm text-gray-600 line-clamp-3 leading-relaxed">
          {product.description}
        </p>
        
        {/* Caractéristiques */}
        {Object.keys(product.characteristics || {}).length > 0 && (
          <div className="flex flex-wrap gap-1">
            {Object.entries(product.characteristics || {}).slice(0, 3).map(([key, value]) => (
              <span key={key} className="text-xs bg-purple-50 text-purple-700 px-2 py-1 rounded border">
                {key}: {value}
              </span>
            ))}
            {Object.keys(product.characteristics || {}).length > 3 && (
              <span className="text-xs text-gray-400">+{Object.keys(product.characteristics).length - 3}</span>
            )}
          </div>
        )}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between items-center text-xs text-gray-500">
        <span>📅 {new Date(product.created_at).toLocaleDateString('fr-FR', { 
          year: 'numeric', 
          month: 'short', 
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })}</span>
        <span className="font-mono text-gray-400">#{product.id.slice(-8)}</span>
      </div>
    </div>
  </div>
);

const ProductSheetCard = ({ sheet, onExport, onViewDetails }) => (
  <div className="bg-white rounded-lg shadow-md overflow-hidden border border-gray-100">
    <div className="p-6">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">{sheet.title}</h3>
          <div className="space-y-1 text-sm">
            <p className="text-gray-600">🏷️ Ref: <span className="font-mono font-medium">{sheet.reference}</span></p>
            <p className="text-blue-600">🎨 {sheet.color_code}</p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-2 ml-4">
          <span className="text-lg font-bold text-green-600">{sheet.price_ttc}€ <span className="text-sm">TTC</span></span>
          <div className="flex items-center gap-2">
            <span className={`px-3 py-1 text-xs font-medium rounded-full ${
              sheet.status === 'published' ? 'bg-green-100 text-green-700' : 
              sheet.status === 'exported' ? 'bg-blue-100 text-blue-700' :
              'bg-yellow-100 text-yellow-700'
            }`}>
              {sheet.status === 'published' ? '🟢 Publié' :
               sheet.status === 'exported' ? '📤 Exporté' : '⚡ Brouillon'}
            </span>
          </div>
        </div>
      </div>
      
      <div className="space-y-3">
        {/* Description */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-1">📝 Description</h4>
          <div className="text-sm text-gray-600 line-clamp-2 bg-gray-50 p-2 rounded text-xs">
            <div dangerouslySetInnerHTML={{ __html: sheet.description.replace(/<[^>]*>/g, ' ').slice(0, 120) + '...' }} />
          </div>
        </div>
        
        {/* Caractéristiques */}
        {Object.keys(sheet.characteristics || {}).length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">✨ Caractéristiques</h4>
            <div className="flex gap-2 flex-wrap">
              {Object.entries(sheet.characteristics || {}).slice(0, 4).map(([key, value]) => (
                <span key={key} className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded border">
                  {key}: {value}
                </span>
              ))}
              {Object.keys(sheet.characteristics || {}).length > 4 && (
                <span className="text-xs text-gray-400">+{Object.keys(sheet.characteristics).length - 4}</span>
              )}
            </div>
          </div>
        )}
        
        {/* SEO */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-1">🔍 SEO</h4>
          <p className="text-xs text-gray-500 line-clamp-1 font-medium">{sheet.seo_title}</p>
          <p className="text-xs text-gray-400 line-clamp-1">{sheet.seo_description}</p>
        </div>
        
        {/* Poids */}
        {sheet.weight_info && Object.keys(sheet.weight_info).length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">⚖️ Poids par type</h4>
            <div className="flex gap-2 flex-wrap">
              {Object.entries(sheet.weight_info).slice(0, 3).map(([type, weight]) => (
                <span key={type} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                  {type}: {weight}kg
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex justify-between items-center">
          <span className="text-xs text-gray-500">
            📅 {new Date(sheet.created_at).toLocaleDateString('fr-FR', { 
              month: 'short', 
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </span>
          <div className="flex gap-2">
            <button 
              onClick={() => onViewDetails(sheet)}
              className="text-xs text-blue-600 hover:text-blue-700 font-medium transition-colors"
            >
              👁️ Détails
            </button>
            <button 
              onClick={() => onExport(sheet.id)}
              className="text-xs text-green-600 hover:text-green-700 font-medium transition-colors"
            >
              📤 Export
            </button>
            <span className="text-xs text-gray-400 font-mono">#{sheet.id.slice(-6)}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const LoadingSpinner = ({ message = "Chargement..." }) => (
  <div className="flex flex-col justify-center items-center py-12 space-y-3">
    <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
    <p className="text-gray-600 text-sm">{message}</p>
  </div>
);

const AlertMessage = ({ type, message, onClose }) => (
  <div className={`p-4 rounded-lg mb-4 border ${
    type === 'success' ? 'bg-green-50 text-green-700 border-green-200' : 
    type === 'error' ? 'bg-red-50 text-red-700 border-red-200' : 
    type === 'warning' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' :
    'bg-blue-50 text-blue-700 border-blue-200'
  }`}>
    <div className="flex justify-between items-start">
      <div className="flex items-start space-x-2">
        <span className="text-lg">
          {type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️'}
        </span>
        <span className="flex-1">{message}</span>
      </div>
      <button 
        onClick={onClose}
        className="text-gray-400 hover:text-gray-600 ml-4 text-xl leading-none"
      >
        ×
      </button>
    </div>
  </div>
);

const ProductModal = ({ product, isOpen, onClose }) => {
  if (!isOpen || !product) return null;
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b">
          <div className="flex justify-between items-start">
            <h3 className="text-xl font-semibold text-gray-900">{product.title}</h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
          </div>
        </div>
        <div className="p-6 space-y-6">
          {/* Informations générales */}
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">📋 Informations générales</h4>
              <div className="space-y-2 text-sm">
                <p><span className="font-medium">EAN:</span> <span className="font-mono">{product.ean_code}</span></p>
                <p><span className="font-medium">Marque:</span> {product.brand}</p>
                <p><span className="font-medium">Modèle:</span> {product.model}</p>
                <p><span className="font-medium">Couleur:</span> {product.color}</p>
                <p><span className="font-medium">Catégorie:</span> {product.category}</p>
                {product.price && <p><span className="font-medium">Prix:</span> {product.price}€</p>}
                {product.google_source && <p><span className="font-medium">Source:</span> {product.google_source}</p>}
              </div>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-3">📏 Tailles disponibles</h4>
              <div className="flex flex-wrap gap-2">
                {product.sizes?.map((size, idx) => (
                  <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                    {size}
                  </span>
                ))}
              </div>
            </div>
          </div>
          
          {/* Description */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3">📝 Description</h4>
            <p className="text-sm text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg">
              {product.description}
            </p>
          </div>
          
          {/* Caractéristiques */}
          {Object.keys(product.characteristics || {}).length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-3">✨ Caractéristiques</h4>
              <div className="grid md:grid-cols-2 gap-4">
                {Object.entries(product.characteristics || {}).map(([key, value]) => (
                  <div key={key} className="flex justify-between py-2 border-b border-gray-100">
                    <span className="font-medium text-gray-600 capitalize">{key}:</span>
                    <span className="text-gray-900">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Poids par type */}
          {Object.keys(product.weight_by_type || {}).length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-3">⚖️ Poids par type de produit</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {Object.entries(product.weight_by_type || {}).map(([type, weight]) => (
                  <div key={type} className="bg-gray-50 p-3 rounded-lg text-center">
                    <div className="font-medium text-gray-900 capitalize">{type}</div>
                    <div className="text-lg font-bold text-blue-600">{weight}kg</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const EmptyState = ({ icon, title, message, actionText, onAction }) => (
  <div className="text-center py-16">
    <div className="text-gray-400 text-8xl mb-4">{icon}</div>
    <h3 className="text-xl font-medium text-gray-900 mb-2">{title}</h3>
    <p className="text-gray-600 mb-6 max-w-md mx-auto">{message}</p>
    {actionText && onAction && (
      <button 
        onClick={onAction}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
      >
        {actionText}
      </button>
    )}
  </div>
);

// ===== MAIN APP =====

function App() {
  const [activeTab, setActiveTab] = useState('search');
  const [products, setProducts] = useState([]);
  const [productSheets, setProductSheets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState(null);
  const [stats, setStats] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showProductModal, setShowProductModal] = useState(false);

  // Charger les données au démarrage
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      await Promise.all([
        loadProducts(),
        loadProductSheets(),
        loadStats()
      ]);
    } catch (error) {
      console.error('Erreur chargement initial:', error);
    }
  };

  const loadProducts = async () => {
    try {
      const response = await axios.get(`${API}/products?limit=50`);
      setProducts(response.data);
    } catch (error) {
      console.error('Erreur chargement produits:', error);
      showAlert('error', 'Erreur lors du chargement des produits');
    }
  };

  const loadProductSheets = async () => {
    try {
      const response = await axios.get(`${API}/sheets?limit=50`);
      setProductSheets(response.data);
    } catch (error) {
      console.error('Erreur chargement fiches:', error);
      showAlert('error', 'Erreur lors du chargement des fiches');
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Erreur chargement stats:', error);
    }
  };

  const showAlert = (type, message) => {
    setAlert({ type, message });
    setTimeout(() => setAlert(null), 5000);
  };

  const handleEANSearch = async (eanCode, generateSheet) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/generate/product`, {
        ean_code: eanCode,
        generate_sheet: generateSheet
      });
      
      if (response.data.success) {
        const summary = response.data.search_summary;
        showAlert('success', 
          `🎉 Produit généré avec succès ! ${summary.results_count} résultats Google trouvés. ` +
          `Marques détectées: ${summary.brands_found.join(', ') || 'Aucune'}. ` +
          `Catégorie: ${summary.category_detected || 'Non déterminée'}.`
        );
        
        // Recharger les données
        await loadInitialData();
        
        // Basculer vers l'onglet approprié
        setActiveTab(generateSheet ? 'sheets' : 'products');
      }
    } catch (error) {
      showAlert('error', `❌ Erreur: ${error.response?.data?.detail || error.message}`);
    }
    setLoading(false);
  };

  const handleGenerateSheet = async (productId) => {
    try {
      await axios.post(`${API}/sheets`, {
        product_id: productId,
        generate_with_ai: true
      });
      
      showAlert('success', '✅ Fiche produit générée avec succès !');
      await loadProductSheets();
      await loadStats();
    } catch (error) {
      showAlert('error', `❌ Erreur génération fiche: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (!window.confirm('⚠️ Êtes-vous sûr de vouloir supprimer ce produit et ses fiches associées ?')) return;
    
    try {
      await axios.delete(`${API}/products/${productId}`);
      showAlert('success', '🗑️ Produit supprimé avec succès !');
      await loadInitialData();
    } catch (error) {
      showAlert('error', `❌ Erreur suppression: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleExportSheet = async (sheetId) => {
    try {
      const response = await axios.get(`${API}/sheets/${sheetId}/export?format=prestashop`);
      console.log('Export PrestaShop:', response.data);
      
      // Créer un fichier JSON téléchargeable
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `fiche-${sheetId.slice(-8)}-prestashop.json`;
      a.click();
      URL.revokeObjectURL(url);
      
      showAlert('success', '📤 Fiche exportée au format PrestaShop !');
    } catch (error) {
      showAlert('error', `❌ Erreur export: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleViewProductDetails = (product) => {
    setSelectedProduct(product);
    setShowProductModal(true);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header stats={stats} />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {alert && (
          <AlertMessage 
            type={alert.type}
            message={alert.message}
            onClose={() => setAlert(null)}
          />
        )}
        
        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <nav className="flex space-x-8 px-6 py-4" aria-label="Tabs">
            {[
              { key: 'search', label: '🔍 Recherche EAN', count: null },
              { key: 'products', label: '📦 Produits', count: products.length },
              { key: 'sheets', label: '📋 Fiches Créées', count: productSheets.length }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-600 bg-blue-50'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-3 px-4 border-b-2 font-medium text-sm transition-all duration-200 rounded-t-lg`}
              >
                {tab.label}
                {tab.count !== null && (
                  <span className={`ml-2 py-1 px-2 rounded-full text-xs ${
                    activeTab === tab.key ? 'bg-blue-200 text-blue-800' : 'bg-gray-100 text-gray-600'
                  }`}>
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* Contenu des Tabs */}
        {activeTab === 'search' && (
          <div>
            <EANSearchForm onSearch={handleEANSearch} loading={loading} />
            
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-800">🚀 Comment ça marche ?</h3>
              <div className="grid md:grid-cols-3 gap-6 text-center">
                <div className="p-4 rounded-lg bg-blue-50 border border-blue-100">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-blue-600 font-bold text-lg">1</span>
                  </div>
                  <h4 className="font-medium mb-2 text-blue-900">🏷️ Code EAN</h4>
                  <p className="text-sm text-blue-700">Saisissez le code-barres du produit (13 chiffres)</p>
                </div>
                <div className="p-4 rounded-lg bg-green-50 border border-green-100">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-green-600 font-bold text-lg">2</span>
                  </div>
                  <h4 className="font-medium mb-2 text-green-900">🔍 Recherche IA</h4>
                  <p className="text-sm text-green-700">L'IA trouve automatiquement les infos sur Google</p>
                </div>
                <div className="p-4 rounded-lg bg-purple-50 border border-purple-100">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-purple-600 font-bold text-lg">3</span>
                  </div>
                  <h4 className="font-medium mb-2 text-purple-900">📋 Fiche générée</h4>
                  <p className="text-sm text-purple-700">Fiche complète prête pour PrestaShop</p>
                </div>
              </div>
              
              {stats && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <div className="bg-gray-50 rounded-lg p-3">
                      <div className="text-2xl font-bold text-blue-600">{stats.total_products}</div>
                      <div className="text-sm text-gray-600">Produits générés</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <div className="text-2xl font-bold text-green-600">{stats.total_sheets}</div>
                      <div className="text-sm text-gray-600">Fiches créées</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <div className="text-2xl font-bold text-purple-600">{stats.total_searches}</div>
                      <div className="text-sm text-gray-600">Recherches EAN</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <div className="text-2xl font-bold text-orange-600">
                        {Object.keys(stats.categories || {}).length}
                      </div>
                      <div className="text-sm text-gray-600">Catégories</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'products' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">📦 Produits Générés ({products.length})</h2>
              <button 
                onClick={loadProducts}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                🔄 Actualiser
              </button>
            </div>
            
            {loading ? (
              <LoadingSpinner message="Chargement des produits..." />
            ) : products.length > 0 ? (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3">
                {products.map((product) => (
                  <ProductCard 
                    key={product.id} 
                    product={product} 
                    onGenerateSheet={handleGenerateSheet}
                    onDelete={handleDeleteProduct}
                    onViewDetails={handleViewProductDetails}
                  />
                ))}
              </div>
            ) : (
              <EmptyState
                icon="📦"
                title="Aucun produit"
                message="Commencez par rechercher un produit avec son code EAN. L'IA trouvera automatiquement toutes les informations nécessaires."
                actionText="🔍 Rechercher un produit"
                onAction={() => setActiveTab('search')}
              />
            )}
          </div>
        )}

        {activeTab === 'sheets' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">📋 Fiches Produits ({productSheets.length})</h2>
              <button 
                onClick={loadProductSheets}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                🔄 Actualiser
              </button>
            </div>
            
            {productSheets.length > 0 ? (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3">
                {productSheets.map((sheet) => (
                  <ProductSheetCard 
                    key={sheet.id} 
                    sheet={sheet}
                    onExport={handleExportSheet}
                    onViewDetails={(sheet) => console.log('Sheet details:', sheet)}
                  />
                ))}
              </div>
            ) : (
              <EmptyState
                icon="📋"
                title="Aucune fiche créée"
                message="Générez des fiches à partir de vos produits existants. Chaque fiche est optimisée pour PrestaShop avec SEO et caractéristiques complètes."
                actionText="📦 Voir les produits"
                onAction={() => setActiveTab('products')}
              />
            )}
          </div>
        )}
      </div>
      
      {/* Modal produit */}
      <ProductModal
        product={selectedProduct}
        isOpen={showProductModal}
        onClose={() => setShowProductModal(false)}
      />
    </div>
  );
}

export default App;