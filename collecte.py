import requests
import csv

# -----------------------------------------------
# ⚙️  CONFIGURATION
# -----------------------------------------------
CLIENT_ID     = "PAR_projetalternance_758f843bf891929f322e487faf4f153d554dce13d87a07b5557b1118ac148ad5"
CLIENT_SECRET = "c164896375bd87fc5752fbcf4daeacd7b22b6377cce106d7ad8602253ed7b27c"

MOTS_CLES = [
    # Développement
    "alternance developpeur python",
    "alternance developpeur web",
    "stage developpeur",
    "stage informatique",

    # Data
    "alternance data analyst",
    "stage data analyst",
    "alternance data",
    "charge qualite data",

    # Gestion IT / Projet
    "alternance chef de projet it",
    "alternance assistant chef de projet it",
    "alternance gestion it",
    "alternance coordinateur systeme information",
    "alternance charge exploitation informatique",
    "stage chef de projet it",

    # Support IT
    "alternance technicien support it",
    "alternance support applicatif",
    "alternance support fonctionnel",
    "alternance support informatique",
    "stage support it",

    # Systèmes / Réseaux
    "alternance administrateur systeme",
    "alternance administrateur reseau",
    "stage administrateur systeme",

    # ERP
    "alternance consultant erp",
    "alternance support erp",
    "alternance integrateur erp",
    "stage consultant erp",

    # SI
    "alternance assistant responsable SI",
    "alternance product manager",
    "alternance coordinateur SI",
]
# -----------------------------------------------
# FONCTION : obtenir le token
# -----------------------------------------------
def get_token():
    url    = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
    params = {"realm": "/partenaire"}
    data   = {
        "grant_type":    "client_credentials",
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope":         "api_offresdemploiv2 o2dsoffre",
    }
    r = requests.post(url, params=params, data=data)
    r.raise_for_status()
    print("✅ Connexion réussie")
    return r.json()["access_token"]

# -----------------------------------------------
# FONCTION : chercher les offres
# -----------------------------------------------
def chercher_offres(token, mot_cle, nb_max=149):
    url     = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept":        "application/json",
    }
    params  = {
        "motsCles": mot_cle,
        "range":    f"0-{nb_max - 1}",
    }

    print(f"  → '{mot_cle}'...", end=" ")
    r = requests.get(url, headers=headers, params=params)

    if r.status_code not in [200, 206]:
        print(f"⚠️ Erreur {r.status_code}")
        return []

    resultats = r.json().get("resultats", [])
    print(f"✅ {len(resultats)} offres")
    return resultats

# -----------------------------------------------
# FONCTION : extraire les infos utiles
# -----------------------------------------------
def extraire_offre(o):
    return {
        "id":          o.get("id", ""),
        "titre":       o.get("intitule", ""),
        "entreprise":  o.get("entreprise", {}).get("nom", "Non précisé"),
        "lieu":        o.get("lieuTravail", {}).get("libelle", ""),
        "contrat":     o.get("typeContratLibelle", ""),
        "description": o.get("description", "")[:400],
        "lien":        o.get("origineOffre", {}).get("urlOrigine", ""),
        "date":        o.get("dateCreation", "")[:10],
        "salaire":     o.get("salaire", {}).get("libelle", "Non précisé"),
    }

# -----------------------------------------------
# FONCTION : sauvegarder en CSV
# -----------------------------------------------
def sauvegarder_csv(offres, nom="offres.csv"):
    if not offres:
        print("\n❌ Aucune offre à sauvegarder.")
        return
    champs = ["id", "titre", "entreprise", "lieu", "contrat", "description", "lien", "date", "salaire"]
    with open(nom, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=champs)
        writer.writeheader()
        writer.writerows(offres)
    print(f"\n💾 {len(offres)} offres sauvegardées dans '{nom}'")

# -----------------------------------------------
# PROGRAMME PRINCIPAL
# -----------------------------------------------
print("=" * 50)
print("  Collecte via API France Travail")
print("=" * 50)

token  = get_token()
toutes = []

for mot in MOTS_CLES:
    resultats = chercher_offres(token, mot)
    for r in resultats:
        toutes.append(extraire_offre(r))

# Supprimer les doublons par ID
seen    = set()
uniques = []
for o in toutes:
    cle = o["titre"] + o["entreprise"]   # doublon si même titre + même entreprise
    if cle not in seen:
        seen.add(cle)
        uniques.append(o)

print(f"\n📊 {len(toutes)} offres brutes → {len(uniques)} offres uniques après déduplication")
sauvegarder_csv(uniques)