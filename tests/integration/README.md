# Tests d'Intégration JarvisOne 🧪

Ce répertoire contient les tests d'intégration pour JarvisOne. Ces tests vérifient que les différents composants du système fonctionnent correctement ensemble dans des scénarios réels d'utilisation.

## 🎯 Objectifs des Tests

Les tests d'intégration vérifient :
- La communication entre les composants
- Les flux de données complets
- La gestion des erreurs système
- L'intégrité des données
- Les interactions avec les services externes

## 📋 Tests Principaux

### Message Flow (`test_message_flow.py`)

Teste le flux complet des messages dans le système :

1. **Conversation Complète** 
   - Vérifie qu'une série de messages est correctement traitée
   - Assure que les réponses sont générées et stockées
   - Valide l'historique des conversations

2. **Contexte Workspace**
   - Teste l'intégration du contexte de l'espace de travail
   - Vérifie que les prompts incluent les informations du workspace
   - Valide la personnalisation par workspace

3. **Gestion des Erreurs**
   - Vérifie la gestion appropriée des erreurs LLM
   - Teste les messages d'erreur utilisateur
   - Assure la stabilité du système en cas d'erreur

4. **Limite Historique Messages** (TODO)
   - Vérifiera la limitation de l'historique des messages
   - Testera la rotation des anciens messages
   - Validera la persistance des messages importants

5. **Assemblage des Prompts**
   - Teste l'intégration de tous les composants du prompt
   - Vérifie la construction correcte des prompts
   - Valide le formatage des entrées/sorties

### Vector DB Integration (`test_vector_db_integration.py`)

Teste l'intégration avec la base de données vectorielle :

1. **Stockage Document**
   - Vérifie l'insertion des documents
   - Teste la mise à jour des embeddings
   - Valide la persistance des données

2. **Recherche Sémantique**
   - Teste la recherche par similarité
   - Vérifie la pertinence des résultats
   - Valide les scores de similarité

## 🛠️ Utilisation

Pour exécuter les tests :

```bash
pytest tests/integration/
```

Pour un test spécifique :

```bash
pytest tests/integration/test_message_flow.py -v
```

## 📝 Notes

- Les tests utilisent des mocks appropriés pour les services externes
- Chaque test est indépendant et peut être exécuté seul
- Les fixtures sont partagées via `conftest.py`
- Les utilitaires communs sont dans `tests/utils.py`

## 🔍 Conventions

1. **Nommage**
   - Fichiers : `test_*.py`
   - Classes : `Test*`
   - Fonctions : `test_*`

2. **Structure**
   - Setup clair des fixtures
   - Actions distinctes
   - Assertions explicites

3. **Documentation**
   - Description du scénario testé
   - Conditions préalables
   - Résultats attendus
