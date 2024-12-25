# ODC d'Architecture pour JarvisOne

## Objectifs d'Architecture

*   **Modularité :**
    *   Concevoir une architecture modulaire facilitant l'ajout de nouvelles fonctionnalités et l'évolution du système.
    *   L'architecture doit être extensible pour intégrer de nouveaux LLM ou outil externe.
*   **Adaptabilité :**
    *   L'architecture doit permettre de connecter différentes sources de données.
*    **Sécurité :**
    *  L'architecture doit assurer des sécurités d'accès au système et aux données.
*   **Performance :**
    *   Concevoir une architecture qui ne pénalise pas le temps de réponse.
*   **Réutilisabilité :**
    *   Les composants doivent être réutilisables autant que possible.
* **Maintenance**
    * L'architecture doit faciliter la maintenance et la compréhension du système par d'autres développeurs.

## Dépendances d'Architecture

*   **Architecture en Couches :**
    *   L'architecture est organisée en couches pour une meilleure séparation des préoccupations.
*   **Flux de Traitement:**
    *   La requête utilisateur est traitée en respectant le schéma décrit dans la section 'High-Level Flow' du README.
*   **Agents :**
    *   Utilisation d'agents intelligents pour l'analyse des requêtes et la recherche de fichiers.
    *   `query_analyzer_agent.py` pour l'analyse des requêtes.
    *   `file_search_agent.py` pour l'interaction avec l'outil `everything`.
*  **Interface Utilisateur :**
    * Utiliser l'input text de Streamlit pour les inputs.
    * Utiliser l'interface des outils externes pour l'affichage des résultats.

## Contraintes d'Architecture

*   **Modularité :**
    *  La modularité doit être respectée lors de l'implémentation de nouvelles fonctionnalités
*   **Performance :**
    *  L'architecture doit minimiser la latence d'exécution.
*   **Sécurité :**
    *   L'architecture doit minimiser les risques de failles de sécurité (accès aux données, accès aux LLMs).
*   **Utilisation d'outils externes**
    * L'architecture doit utiliser l'interface des outils externes si elle existe pour l'affichage des résultats.
    * L'architecture doit éviter au maximum de ré-implémenter des fonctionnalités déjà existantes.