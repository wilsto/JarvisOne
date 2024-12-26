<!-- markdownlint-disable MD029 -->
# JarvisOne

JarvisOne est un assistant conversationnel modulaire et évolutif qui intègre des capacités d'interaction avec des outils externes, notamment pour la recherche de fichiers.

## Fonctionnalités

- 🔧 Architecture modulaire pour l'intégration d'outils externes
- 🔍 Recherche de fichiers via Everything (exemple d'intégration)
- 🤖 Support de multiples modèles LLM (OpenAI, Ollama)
- 💬 Interface de chat intuitive avec Streamlit
- ⚙️ Configuration flexible des fournisseurs LLM et outils externes

## Installation

1. Cloner le dépôt :

```bash
git clone https://github.com/votre-username/JarvisOne.git
cd JarvisOne
```

2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

3. Configurer l'environnement :

- Copier `.env.example` vers `.env`
- Ajouter vos clés API et chemins des outils externes si nécessaire

4. Installer les outils externes requis :

- Pour la recherche de fichiers : Télécharger et installer [Everything](https://www.voidtools.com/)
- Assurez-vous que les outils externes sont correctement configurés et en cours d'exécution

## Utilisation

1. Lancer l'application :

```bash
streamlit run src/main.py
```

2. Dans l'interface :

- Sélectionnez votre fournisseur LLM préféré
- Utilisez le chat pour interagir avec JarvisOne
- Accédez aux fonctionnalités des outils externes via le chat

## Exemples d'utilisation

- "Trouve les fichiers PDF modifiés aujourd'hui" (via Everything)
- "Cherche les documents Word contenant 'rapport'" (via Everything)
- "Liste les images dans le dossier Documents" (via Everything)

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.
