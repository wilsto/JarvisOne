# ODC d'Architecture pour JarvisOne

## Objectifs d'Architecture

* **Modularité :**
  * Concevoir une architecture modulaire facilitant l'ajout de nouvelles fonctionnalités et l'évolution du système.
  * L'architecture doit être extensible pour intégrer de nouveaux LLM ou outil externe.
* **Adaptabilité :**
  * L'architecture doit permettre de connecter différentes sources de données.
* **Sécurité :**
  * L'architecture doit assurer des sécurité d'accès au système et aux données.
* **Performance :**
  * Concevoir une architecture qui ne pénalise pas le temps de réponse.
* **Réutilisabilité :**
  * Les composants doivent être réutilisables autant que possible.
* **Maintenance**
  * L'architecture doit faciliter la maintenance et la compréhension du système par d'autres développeurs.

## Dépendances d'Architecture

* **Architecture en Couches :**
  * L'architecture est organisée en couches pour une meilleure séparation des préoccupations.
* **Flux de Traitement:**
  * La requête utilisateur est traitée en respectant le schéma décrit dans la section 'High-Level Flow' du fichier `.windsurfrules`.
* **Agents :**
  * Utilisation d'agents intelligents pour l'analyse des requêtes et l'interaction avec les outils externes.
  * `query_analyzer_agent.py` pour l'analyse des requêtes.
  * `file_search_agent.py` pour l'interaction avec l'outil `everything`.
* **Interface Utilisateur :**
  * Utiliser l'input text de Streamlit pour les inputs.
  * Intégrer les interfaces natives des outils externes pour l'affichage des résultats quand approprié.
  * Interface adaptative selon les outils utilisés.

## Contraintes d'Architecture

* **Modularité :**
  * La modularité doit être respectée lors de l'implémentation de nouvelles fonctionnalités
* **Performance :**
  * L'architecture doit minimiser la latence d'exécution.
* **Sécurité :**
  * L'architecture doit minimiser les risques de failles de sécurité (accès aux données, accès aux LLMs).
* **Utilisation d'outils externes**
  * L'architecture doit utiliser l'interface des outils externes si elle existe pour l'affichage des résultats.
  * L'architecture doit éviter au maximum de ré-implémenter des fonctionnalités déjà existantes.


## Architectural Logic

### High-Level Flow (Target)

The target system follows a specific flow for each user request, starting with a user query and ending with a final response.
This flow includes caching, context construction, input and output safeguards, and access to both internal and external data sources.

1. **User Query:** The process begins with a natural language query from the user via the chat interface.
2. **Initial Cache Lookup:** Before processing the query, the system checks a local cache to see if a similar query has been processed before. If a cached response is available, it is returned immediately.
3. **Context Construction:** If the query is not cached, it goes through a context construction phase. This involves:
    - **RAG (Retrieval-Augmented Generation):** Retrieving relevant information from external sources to enrich the query context. (À conserver pour plus tard)
    - **Agent Interaction:** Using an intelligent agent to analyze the query and determine necessary actions.
    - **Query Rewriting:** Refining or rephrasing the query for better processing.
4. **Input Guardrails:** The enriched query is then passed through input guardrails for security. This includes actions like:
    - **PII Redaction:** Removing or masking personally identifiable information.
5. **Data Access and Retrieval:** Depending on the context, the system can access various data sources:
    - **Read-only Actions:** These allow retrieval of data from various sources:
        - **Vector Search:** Performing semantic searches based on vector representations of data. (À conserver pour plus tard)
        - **SQL Query Execution:** Running SQL queries against databases.
        - **Web Search:** Searching for relevant information on the web.
    - **Databases:** These contain persistent data such as:
        - Documents, tables, chat histories, vector databases, etc.
6. **Model Gateway:** The core of the system, handling:
    - **Model Catalog:** Managing and selecting different language models.
    - **Access Token Management:** Securely managing authentication tokens for the models.
    - **Routing:** Selecting the most appropriate model for the current query.
    - **Generation:** Using the chosen model to generate a response.
    - **Scoring:** Evaluating the quality of the generated response.
7. **Output Guardrails:** Before the response is returned, it is checked by output guardrails. This includes:
    - **Safety/Verification:** Ensuring the response is safe, ethical, and free of errors.
    - **Structured Outputs:** Formatting the response for easy use.
8. **Final Response:** The user receives the final response.
9. **Response Caching:** The final response is stored in the cache for future reuse.
10. **Write Actions (Secondary):** If necessary, after the response is returned, the system may execute write actions to modify the state. This can include:
    - Updating orders, sending emails, etc.