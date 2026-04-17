Dashboard Alternance & Stage 🎯
Outil personnel d'automatisation de recherche d'alternance et de stage, développé entièrement en Python.
Collecte les offres en temps réel, les note selon tes critères personnels et affiche un dashboard interactif.

Fonctionnalités

Collecte automatique des offres via l'API officielle France Travail
Scoring intelligent basé sur des mots-clés personnalisables
Dashboard web avec 4 pages interactives (Offres, Suivi, CV, Stats)
Suivi des candidatures avec statuts (Favori, Postulé, Entretien, Accepté...)
Analyse de compatibilité entre ton CV et chaque offre
Filtres avancés : ville, date, score, statut
Barre de progression des candidatures en temps réel
Graphiques de statistiques (répartition par ville, par statut...)
Lancement en un seul double-clic via LANCER.bat


Technologies utilisées

Python 3.12
API France Travail (Offres d'emploi v2)
HTML / CSS / JavaScript (vanilla, sans framework)
CSV pour le stockage des données
Git & GitHub


Structure du projet
dashboard-alternance/
│
├── main.py              ← Lance les 3 scripts en une seule commande
├── collecte.py          ← Collecte les offres via l'API France Travail
├── scoring.py           ← Note et trie les offres selon tes critères
├── dashboard_v2.py      ← Génère les 4 pages HTML du dashboard
├── alertes_email.py     ← Envoie les meilleures offres par email
├── LANCER.bat           ← Lancement Windows en double-clic
├── README.md
└── .gitignore
Les fichiers HTML générés (offres.html, suivi.html, cv.html, stats.html)
ne sont pas inclus dans le repo car ils sont générés automatiquement.

Installation
Prérequis

Python 3.10 ou supérieur
Un compte développeur France Travail (gratuit)

Étapes
1. Clone le projet
bashgit clone https://github.com/voundipaulyvan-art/dashboard-alternance.git
cd dashboard-alternance
2. Installe les dépendances
bashpip install requests beautifulsoup4 pdfminer.six
3. Crée ton compte API France Travail

Va sur https://francetravail.io/inscription
Crée une application
Active l'API "Offres d'emploi v2"
Récupère ton Client ID et Client Secret

4. Configure tes identifiants dans collecte.py
pythonCLIENT_ID     = "TON_CLIENT_ID"
CLIENT_SECRET = "TON_CLIENT_SECRET"
5. Lance le projet
bashpython main.py
Ou double-clique sur LANCER.bat (Windows)

Utilisation au quotidien
bash# Tout lancer en une commande
python main.py

# Ou étape par étape
python collecte.py      # Récupère les nouvelles offres
python scoring.py       # Note et trie les offres
python dashboard_v2.py  # Génère le dashboard
Puis ouvre offres.html dans ton navigateur.

Personnalisation du scoring
Dans scoring.py, tu peux personnaliser :

Les mots-clés positifs pour les titres et descriptions
Les mots-clés négatifs (postes à exclure)
Les villes préférées (bonus de score)
Les types de contrats recherchés

pythonTITRE_FORT = ["data analyst", "chef de projet", "support it", ...]
MOTS_NEGATIFS = ["commercial", "vente", "comptabilité", ...]
VILLES_PREFEREES = ["paris", "lyon", "bordeaux", ...]

Pages du dashboard
PageDescriptionoffres.htmlListe des offres triées par score avec filtres avancéssuivi.htmlTableau de bord de toutes tes candidaturescv.htmlImport et analyse de compatibilité CVstats.htmlGraphiques et statistiques de ta recherche

Alertes email (optionnel)
Dans alertes_email.py, configure ton adresse Gmail et un mot de passe
d'application pour recevoir les meilleures offres par email.
pythonEMAIL_EXPEDITEUR   = "tonemail@gmail.com"
MOT_DE_PASSE       = "ton_mot_de_passe_application"
EMAIL_DESTINATAIRE = "tonemail@gmail.com"
SCORE_MINIMUM      = 10

Auteur
Voundipaul Yvan
Étudiant en informatique - Recherche d'alternance
GitHub : https://github.com/voundipaulyvan-art

Licence
Ce projet est open source. N'hésite pas à le forker et l'adapter à ta recherche d'emploi !
