# JarvisOne

JarvisOne est un assistant conversationnel modulaire et évolutif qui intègre des capacités avancées de recherche de fichiers.

## Fonctionnalités

- 🔍 Recherche de fichiers intégrée avec Everything
- 🤖 Support de multiples modèles LLM (OpenAI, Ollama)
- 💬 Interface de chat intuitive avec Streamlit
- ⚙️ Configuration flexible des fournisseurs LLM

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
- Ajouter vos clés API si nécessaire

4. Installer Everything :
- Télécharger et installer [Everything](https://www.voidtools.com/)
- Assurez-vous que Everything est en cours d'exécution

## Utilisation

1. Lancer l'application :
```bash
streamlit run src/main.py
```

2. Dans l'interface :
- Sélectionnez votre fournisseur LLM préféré
- Utilisez le chat pour interagir avec JarvisOne
- Effectuez des recherches de fichiers en langage naturel

## Exemples de recherche

- "Trouve les fichiers PDF modifiés aujourd'hui"
- "Cherche les documents Word contenant 'rapport'"
- "Liste les images dans le dossier Documents"

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.
