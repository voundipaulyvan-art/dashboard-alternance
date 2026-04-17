import csv

# -----------------------------------------------
# ⚙️  TES CRITÈRES PERSONNELS — modifie selon toi
# -----------------------------------------------

# Mots-clés qui t'intéressent (dans le titre ou la description)
MOTS_POSITIFS = [
    # Dev
    "python", "javascript", "web", "développeur", "développement",
    "api", "sql", "git", "django", "flask",

    # Data
    "data analyst", "data", "excel", "power bi", "tableau",
    "analyse", "reporting", "indicateurs", "kpi",

    # Gestion de projet / IT
    "chef de projet", "gestion de projet", "product manager",
    "product owner", "agile", "scrum", "jira", "confluence",
    "cahier des charges", "moa", "amoa",

    # Support IT
    "support", "helpdesk", "ticketing", "itil",
    "support applicatif", "support fonctionnel",
    "technicien", "assistance utilisateurs",

    # Systèmes
    "administrateur", "système", "réseau", "infrastructure",
    "windows server", "active directory", "linux", "vmware",

    # ERP
    "erp", "sap", "salesforce", "dynamics", "odoo",
    "intégration", "paramétrage", "fonctionnel",

    # SI
    "système d'information", "si", "responsable si",
    "coordinateur", "exploitation", "mcoa",
    "qualité", "processus",
]

MOTS_NEGATIFS = [
    "commercial", "vente", "comptabilité",
    "ressources humaines", "rh", "juridique",
    "chauffeur", "magasinier", "maçon",
    "électricien", "plombier", "cuisinier",
    "infirmier", "aide-soignant", "caissier",
]

# Villes préférées (bonus si l'offre est dans ces villes)
VILLES_PREFEREES = [
    "paris",
    "lyon",
    "bordeaux",
    "clermont-ferrand",
    "nice",
]

# -----------------------------------------------
# FONCTION : calculer le score d'une offre
# -----------------------------------------------
def calculer_score(offre):
    score = 0
    raisons = []

    # On analyse le titre + description en minuscules
    titre       = offre["titre"].lower()
    description = offre["description"].lower()
    texte       = titre + " " + description
    lieu        = offre["lieu"].lower()

    # +3 points par mot positif dans le TITRE
    for mot in MOTS_POSITIFS:
        if mot in titre:
            score += 3
            raisons.append(f"+3 '{mot}' dans le titre")

    # +1 point par mot positif dans la DESCRIPTION
    for mot in MOTS_POSITIFS:
        if mot in description:
            score += 1
            raisons.append(f"+1 '{mot}' dans description")

    # -5 points par mot négatif
    for mot in MOTS_NEGATIFS:
        if mot in texte:
            score -= 5
            raisons.append(f"-5 '{mot}' indésirable")

    # +2 points si ville préférée
    for ville in VILLES_PREFEREES:
        if ville in lieu:
            score += 2
            raisons.append(f"+2 ville '{ville}'")
            break

    # +1 point si l'offre est récente (commence par 2025 ou 2026)
    if offre["date"].startswith("2025") or offre["date"].startswith("2026"):
        score += 1
        raisons.append("+1 offre récente")

    return score, " | ".join(raisons)

# -----------------------------------------------
# PROGRAMME PRINCIPAL
# -----------------------------------------------
print("=" * 50)
print("  Scoring des offres")
print("=" * 50)

# Lire le CSV collecté
offres = []
with open("offres.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for ligne in reader:
        offres.append(ligne)

print(f"📂 {len(offres)} offres chargées")

# Calculer le score de chaque offre
for offre in offres:
    score, raisons = calculer_score(offre)
    offre["score"]   = score
    offre["raisons"] = raisons

# Trier par score décroissant
offres_triees = sorted(offres, key=lambda x: int(x["score"]), reverse=True)

# Sauvegarder le résultat
champs = ["score", "titre", "entreprise", "lieu", "contrat", "date", "salaire", "lien", "raisons", "description"]
with open("offres_scored.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=champs, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(offres_triees)

# Afficher le top 10
print("\n🏆 TOP 10 des meilleures offres :\n")
for i, offre in enumerate(offres_triees[:10], 1):
    print(f"{i:2}. [{offre['score']:+d}] {offre['titre']}")
    print(f"     📍 {offre['lieu']} | 🏢 {offre['entreprise']}")
    print(f"     💡 {offre['raisons'][:80]}")
    print()

print(f"💾 Résultats complets sauvegardés dans 'offres_scored.csv'")
print(f"   → Offres avec score > 5  : {sum(1 for o in offres_triees if int(o['score']) > 5)}")
print(f"   → Offres avec score > 10 : {sum(1 for o in offres_triees if int(o['score']) > 10)}")