# ODC Techniques pour JarvisOne

## Objectifs Techniques

* **Fonctionnalité de Base :**
  * Permettre l'interaction en langage naturel via une interface de chat.
  * Intégrer des outils externes pour des fonctionnalités spécifiques (recherche de fichiers, etc.).
  * Afficher la sortie des outils externes via leur interface native quand c'est approprié.
* **Traitement des Requêtes :**
  * Récupérer les requêtes des utilisateurs via une interface de chat Streamlit.
  * Effectuer une recherche rapide dans un cache local des précédentes réponses.
  * Analyser et extraire les informations pertinentes des requêtes.
  * Appliquer des sécurités au niveau de l'entrée en supprimant le PII par exemple.
  * Exécuter des requêtes sur des données persistantes (documents, tables etc).
  * Gérer l'accès à différents LLMs.
  * Générer des réponses à partir du modèle sélectionné.
  * Evaluer la qualité de la réponse générée.
  * Appliquer des sécurités au niveau de la sortie (safe, ethical).
  * Mettre en cache les réponses pour réutilisation future.
* **Gestion de l'Interface**
  * Utiliser un input text pour permettre aux utilisateurs d'envoyer leur requêtes.
  * Afficher le résultat des recherches de fichiers avec l'interface de `everything`
  * Afficher le reste des sorties dans le chat text.
* **Outils Externes :**
  * Capacité d'intégrer et d'exécuter divers outils externes selon les besoins.
  * Utilisation flexible des interfaces natives des outils quand elles existent.
* **Langage et Plateforme :**
  * Développer avec Python 3.12.
  * Utiliser Streamlit 1.31+ pour l'interface utilisateur.
  * Utiliser des agents intelligents pour la gestion des agents.
  * Utiliser des modèles LLM avancés pour le traitement du langage naturel.

## Dépendances Techniques

* **Logiciels et Librairies:**
  * Python 3.12
  * Streamlit 1.31+
  * `Everything` - Pour la recherche de fichiers.
* **Outils Externes :**
  * `C:\Program Files\Everything\es.exe` (Chemin spécifique pour l'exécution de l'outil `everything`).
  * Interface de `everything` pour l'affichage des résultats.

## Contraintes Techniques

* **Performance :**
  * Le temps de réponse à une requête doit être aussi rapide que possible.
* **Sécurité :**
  * Protection contre le PII (Personally Identifiable Information) dans les requêtes.
  * Gestion sécurisée des accès aux LLMs (tokens).
  * Filtrage de la sortie pour s'assurer qu'elle soit "safe" et éthique.
* **Interface Utilisateur :**
  * Utiliser au maximum l'interface des outils externes si elle existe, par exemple celle de `everything`.
  * Pour le reste afficher le résultat dans l'interface de chat.
  * La mise en page de l'interface doit être simple et responsive.
  * Éviter la ré-implémentation de systèmes d'affichage ou d'interaction déjà existants dans les outils externes.
* **Gestion de la Configuration**
  * Configuration de base du projet à travers des fichiers de configuration (YAML).
* **Gestion de la Documentation**
  * La documentation du projet doit être simple, maintenable et mise à jour à chaque action du système
