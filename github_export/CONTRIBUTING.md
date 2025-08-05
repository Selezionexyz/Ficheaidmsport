# Guide de Contribution

Merci de votre intérêt pour contribuer au **Générateur de Fiches Produits DM'Sports** ! 🎉

## 🚀 Comment contribuer

### Types de contributions
- 🐛 **Correction de bugs**
- ✨ **Nouvelles fonctionnalités**
- 📚 **Amélioration documentation**
- 🎨 **Améliorations UI/UX**
- ⚡ **Optimisations performances**
- 🧪 **Tests automatisés**

### Processus de contribution

#### 1. Fork et Clone
```bash
# Fork le projet sur GitHub
# Puis cloner votre fork
git clone https://github.com/votre-username/dmsports-product-generator.git
cd dmsports-product-generator
```

#### 2. Créer une branche
```bash
# Créer une branche pour votre fonctionnalité
git checkout -b feature/ma-nouvelle-fonctionnalite
# ou pour un bug
git checkout -b fix/correction-bug-xyz
```

#### 3. Développer
```bash
# Installer les dépendances
./scripts/setup.sh

# Développer votre contribution
# Tester localement
./start.sh
```

#### 4. Tests et qualité
```bash
# Tests backend
cd backend
source venv/bin/activate
python -m pytest

# Tests frontend
cd frontend
yarn test

# Linting
yarn lint
python -m flake8 backend/
```

#### 5. Commit et Push
```bash
# Commits avec messages descriptifs
git add .
git commit -m "✨ Ajouter recherche par nom de produit"
git push origin feature/ma-nouvelle-fonctionnalite
```

#### 6. Pull Request
1. Ouvrir une **Pull Request** sur GitHub
2. Décrire les changements effectués
3. Référencer les issues liées
4. Attendre la review

## 📋 Standards de code

### Backend (Python)
```python
# Style PEP 8
# Docstrings pour toutes les fonctions
def generate_product_info(ean_code: str) -> Dict:
    """
    Génère les informations produit via IA.
    
    Args:
        ean_code: Code EAN du produit (13 chiffres)
        
    Returns:
        Dict contenant les infos produit générées
        
    Raises:
        HTTPException: Si l'EAN est invalide
    """
    pass

# Type hints obligatoires
# Gestion d'erreurs explicite
# Tests unitaires pour nouvelles fonctions
```

### Frontend (React)
```javascript
// Composants fonctionnels avec hooks
// PropTypes ou TypeScript
// Styles Tailwind CSS
// Tests avec Jest/Testing Library

const ProductCard = ({ product, onAction }) => {
  // Hooks en début de composant
  const [loading, setLoading] = useState(false);
  
  // Fonctions de gestion d'événements
  const handleClick = async () => {
    setLoading(true);
    try {
      await onAction(product.id);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // JSX clair et lisible
  return (
    <div className="product-card">
      {/* Contenu */}
    </div>
  );
};
```

### Commits
Format des messages de commit :
```
type(scope): description courte

Corps du message plus détaillé si nécessaire.
Expliquer le "quoi" et le "pourquoi", pas le "comment".

Fixes #123
```

Types de commits :
- `feat`: nouvelle fonctionnalité
- `fix`: correction de bug
- `docs`: documentation
- `style`: formatage, point-virgules manquants, etc.
- `refactor`: refactorisation de code
- `test`: ajout/modification de tests
- `chore`: tâches de maintenance

## 🧪 Tests

### Tests Backend
```python
# tests/test_services.py
import pytest
from backend.services import GoogleSearchService

def test_search_by_ean():
    """Test de recherche par EAN."""
    result = GoogleSearchService.search_by_ean("1234567890123")
    assert "items" in result
    assert len(result["items"]) > 0
```

### Tests Frontend
```javascript
// src/__tests__/ProductCard.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import ProductCard from '../ProductCard';

test('affiche le titre du produit', () => {
  const product = { title: 'Nike Air Max', brand: 'Nike' };
  render(<ProductCard product={product} />);
  
  expect(screen.getByText('Nike Air Max')).toBeInTheDocument();
});
```

## 📚 Documentation

### API Documentation
```python
@api_router.post("/generate/product")
async def generate_product_from_ean(request: EANGenerateRequest):
    """
    Pipeline complet : EAN → Recherche → Génération IA → Fiche.
    
    **Paramètres:**
    - `ean_code`: Code EAN du produit (13 chiffres)
    - `generate_sheet`: Générer automatiquement la fiche (défaut: true)
    
    **Retourne:**
    - Produit généré avec informations complètes
    - Fiche PrestaShop si demandée
    - Résumé de la recherche Google
    
    **Erreurs:**
    - `400`: Code EAN invalide
    - `500`: Erreur API externe (OpenAI/Google)
    """
```

### README et guides
- Documentation claire et exemples
- Captures d'écran pour l'interface
- Instructions d'installation pas-à-pas
- FAQ pour problèmes courants

## 🐛 Signalement de bugs

### Template d'issue bug
```markdown
**Description du bug**
Description claire et concise du problème.

**Étapes de reproduction**
1. Aller à '...'
2. Cliquer sur '...'
3. Faire défiler vers '...'
4. Voir l'erreur

**Comportement attendu**
Description de ce qui devrait se passer.

**Captures d'écran**
Si applicable, ajouter des captures d'écran.

**Environnement:**
 - OS: [e.g. Ubuntu 20.04]
 - Python: [e.g. 3.9.5]
 - Node.js: [e.g. 18.16.0]
 - Navigateur: [e.g. Chrome 91]

**Logs**
```
Coller les logs d'erreur ici
```

**Informations additionnelles**
Autres détails utiles pour reproduire le problème.
```

## ✨ Demandes de fonctionnalités

### Template d'issue feature
```markdown
**La fonctionnalité demandée résout-elle un problème ?**
Description claire du problème. Ex: Je suis toujours frustré quand [...]

**Solution proposée**
Description claire de ce que vous aimeriez qui se passe.

**Alternatives considérées**
Description des solutions alternatives que vous avez considérées.

**Contexte additionnel**
Tout autre contexte ou captures d'écran sur la demande de fonctionnalité.
```

## 🎯 Bonnes pratiques

### Code Review
- ✅ Code clair et bien commenté
- ✅ Tests couvrant les nouveaux changements
- ✅ Documentation mise à jour
- ✅ Pas de régression fonctionnelle
- ✅ Performance acceptable
- ✅ Sécurité vérifiée

### Performance
- ⚡ Optimiser les requêtes base de données
- ⚡ Minimiser les appels API externes
- ⚡ Utiliser la mise en cache intelligemment
- ⚡ Compresser les assets frontend
- ⚡ Lazy loading pour gros composants

### Sécurité
- 🔒 Ne jamais committer de clés API
- 🔒 Valider toutes les entrées utilisateur
- 🔒 Échapper les données avant affichage
- 🔒 Utiliser HTTPS en production
- 🔒 Principe du moindre privilège

## 🏆 Reconnaissance

Tous les contributeurs seront listés dans le README du projet. Les contributions majeures seront mentionnées dans le CHANGELOG.

### Types de reconnaissance
- 🏅 **Contributeur actif** : 5+ PRs acceptées
- 🌟 **Expert domaine** : Contributions spécialisées
- 🚀 **Mainteneur** : Contributions régulières et reviews
- 🎯 **Champion communauté** : Aide autres contributeurs

## 📞 Support

### Canaux de communication
- **Issues GitHub** : Pour bugs et features
- **Discussions GitHub** : Pour questions générales
- **Email** : dm-sports-dev@example.com

### Code de conduite
- 🤝 Être respectueux et inclusif
- 🎯 Rester constructif dans les critiques
- 🚀 Encourager les nouveaux contributeurs
- 📚 Partager les connaissances

---

## 🎉 Merci !

Chaque contribution, petite ou grande, nous aide à améliorer ce projet. Merci de faire partie de la communauté DM'Sports ! 🏷️✨