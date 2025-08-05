#!/bin/bash
# Script de test pour vérifier les dépendances avant Render

echo "🔍 Test des dépendances Frontend..."
cd frontend
if [ -f "package.json" ] && [ -f "yarn.lock" ]; then
    echo "✅ package.json et yarn.lock trouvés"
    yarn --version
    echo "📦 Installation test des dépendances..."
    yarn install --check-files 2>/dev/null && echo "✅ Dépendances OK" || echo "❌ Problème dépendances"
else
    echo "❌ Fichiers package.json ou yarn.lock manquants"
fi

echo ""
echo "🔍 Test des dépendances Backend..."
cd ../backend
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt trouvé"
    echo "📦 Contenu requirements.txt:"
    head -10 requirements.txt
else
    echo "❌ requirements.txt manquant"
fi

echo ""
echo "🔍 Test de la structure du projet..."
cd ..
echo "📁 Structure du projet:"
ls -la
echo ""
echo "📁 Contenu frontend:"
ls -la frontend/
echo ""
echo "📁 Contenu backend:"
ls -la backend/