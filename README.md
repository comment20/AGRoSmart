# 🌍 AGRIcultSmart - Intelligence Artificielle Agricole

**AGRIcultSmart** est une plateforme web innovante et premium conçue pour accompagner les agriculteurs dans la prise de décision stratégique grâce à l'intelligence artificielle avancée et l'analyse de données de précision.

## 🚀 Fonctionnalités Clés

- **Classification Intelligente des Sols** : Identifiez instantanément le type de sol (Noir, Argileux, Sableux, etc.) à partir d'une simple photo grâce à notre modèle de Computer Vision (SVM).
- **Recommandation de Cultures de Précision** : Recevez des suggestions personnalisées de cultures optimisées en fonction des paramètres physico-chimiques (N, P, K, pH, température, humidité et précipitations).
- **Intelligence des Marchés** : Visualisez l'historique et accédez à des prévisions de prix fiables pour les produits agricoles par région et département au Cameroun, basées sur des modèles de séries temporelles (SARIMA).
- **AGRIcultSmart IA** : Un assistant agronomique conversationnel de pointe (propulsé par Google Gemini Flash 1.5) disponible 24/7 pour répondre à toutes vos problématiques agricoles.
- **Exports Professionnels** : Générez des rapports d'analyse complets au format PDF et CSV pour votre suivi personnel ou vos dossiers de financement.

## 💎 Design & UX Premium

L'application arbore une interface **"Executive Premium"** entièrement responsive, utilisant des technologies modernes telles que le **Glassmorphism**, la police **Plus Jakarta Sans**, et des graphiques interactifs (Chart.js) pour une expérience utilisateur fluide sur ordinateur comme sur mobile.

## 🛠️ Stack Technique

- **Backend** : Django 3.0.5 (Python)
- **Frontend** : HTML5, CSS3 (Premium Responsive Design), JavaScript (ES6+)
- **IA/ML** : Modèles SVM et SARIMA hébergés via Hugging Face Inference API
- **LLM** : Google Gemini API (gemini-1.5-flash)
- **Base de données** : PostgreSQL (Production) / SQLite (Local)
- **Déploiement** : Render (Infrastructure Cloud)

## 📦 Installation (Local)

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/votre-user/soil-predict.git
   cd SoilClassifier
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer les variables d'environnement** :
   Créez un fichier `.env` à la racine et ajoutez vos clés :
   ```env
   SECRET_KEY=votre_cle_django
   GEMINI_API_KEY=votre_cle_google_gemini
   DATABASE_URL=votre_url_postgres (optionnel pour local)
   ```

4. **Lancer le serveur** :
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## 👨‍💻 Auteur
**Boval Germain Tchoupe** - DATA Scientist Junior & Élève Ingénieur.
Maroua Innovation Technologie.
