import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from http.server import BaseHTTPRequestHandler

ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js":   "application/javascript",
    ".css":  "text/css",
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".ico":  "image/x-icon",
    ".svg":  "image/svg+xml",
}
import json
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from db import get_offres as _db_get, db_exists as _db_exists
    _HAS_DB = True
except ImportError:
    _HAS_DB = False

CLIENT_ID     = os.environ.get("FRANCE_TRAVAIL_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("FRANCE_TRAVAIL_CLIENT_SECRET", "")

MOTS_CLES = [
    "alternance developpeur python",
    "alternance developpeur web",
    "alternance data analyst",
    "alternance chef de projet it",
    "alternance support informatique",
    "alternance technicien support it",
    "alternance administrateur systeme",
    "alternance consultant erp",
    "alternance assistant responsable SI",
    "alternance coordinateur systeme information",
    "alternance product manager",
    "stage developpeur",
    "stage data analyst",
    "stage informatique",
    "stage chef de projet it",
]

MOTS_POSITIFS = [
    "python", "javascript", "web", "developpeur", "developpement",
    "api", "sql", "git", "django", "flask",
    "data analyst", "data", "excel", "power bi", "tableau",
    "analyse", "reporting", "indicateurs", "kpi",
    "chef de projet", "gestion de projet", "product manager",
    "product owner", "agile", "scrum", "jira", "confluence",
    "cahier des charges", "moa", "amoa",
    "support", "helpdesk", "ticketing", "itil",
    "support applicatif", "support fonctionnel",
    "technicien", "assistance utilisateurs",
    "administrateur", "systeme", "reseau", "infrastructure",
    "windows server", "active directory", "linux", "vmware",
    "erp", "sap", "salesforce", "dynamics", "odoo",
    "integration", "parametrage", "fonctionnel",
    "systeme information", "si", "responsable si",
    "coordinateur", "exploitation", "qualite", "processus",
]

MOTS_NEGATIFS = [
    "commercial", "vente", "comptabilite",
    "ressources humaines", "juridique",
    "chauffeur", "magasinier", "macon",
    "electricien", "plombier", "cuisinier",
    "infirmier", "aide-soignant", "caissier",
]

VILLES_PREFEREES = ["paris", "lyon", "bordeaux", "clermont-ferrand", "nice"]


def get_token():
    r = requests.post(
        "https://entreprise.francetravail.fr/connexion/oauth2/access_token",
        params={"realm": "/partenaire"},
        data={
            "grant_type":    "client_credentials",
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope":         "api_offresdemploiv2 o2dsoffre",
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def chercher_offres(token, mot_cle, nb_max=99, jours=30):
    now = datetime.now()
    date_min = (now - timedelta(days=jours)).strftime("%Y-%m-%dT00:00:00Z")
    date_max = now.strftime("%Y-%m-%dT23:59:59Z")
    r = requests.get(
        "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        params={
            "motsCles": mot_cle,
            "range": f"0-{nb_max - 1}",
            "minCreationDate": date_min,
            "maxCreationDate": date_max,
        },
        timeout=10,
    )
    if r.status_code not in [200, 206]:
        return []
    return r.json().get("resultats", [])


def clean_str(s, maxlen=300):
    if not s:
        return ""
    s = str(s)[:maxlen]
    for c in ["\r\n", "\r", "\n", "\\", "<", ">", '"', "'"]:
        s = s.replace(c, " ")
    return " ".join(s.split())


def extraire_offre(o):
    return {
        "id":          o.get("id", ""),
        "titre":       clean_str(o.get("intitule", ""), 80),
        "entreprise":  clean_str(o.get("entreprise", {}).get("nom", "Non precise"), 50),
        "lieu":        clean_str(o.get("lieuTravail", {}).get("libelle", ""), 50),
        "contrat":     o.get("typeContratLibelle", ""),
        "description": clean_str(o.get("description", ""), 300),
        "lien":        o.get("origineOffre", {}).get("urlOrigine", ""),
        "date":        o.get("dateCreation", "")[:10],
        "salaire":     o.get("salaire", {}).get("libelle", "Non precise"),
    }


def calculer_score(offre):
    score = 0
    raisons = []
    titre       = offre["titre"].lower()
    description = offre["description"].lower()
    lieu        = offre["lieu"].lower()

    for mot in MOTS_POSITIFS:
        if mot in titre:
            score += 3
            raisons.append(f"+3 {mot}")
    for mot in MOTS_POSITIFS:
        if mot in description:
            score += 1
            raisons.append(f"+1 {mot}")
    for mot in MOTS_NEGATIFS:
        if mot in titre + " " + description:
            score -= 5
            raisons.append(f"-5 {mot}")
    for ville in VILLES_PREFEREES:
        if ville in lieu:
            score += 2
            raisons.append(f"+2 {ville}")
            break

    try:
        date_offre = datetime.strptime(offre["date"], "%Y-%m-%d")
        anciennete = (datetime.now() - date_offre).days
        if anciennete <= 7:
            score += 2
            raisons.append("+2 recente")
        elif anciennete <= 30:
            score += 1
            raisons.append("+1 recente")
    except (ValueError, TypeError):
        pass

    return score, " | ".join(raisons[:6])


def get_all_offers():
    token = get_token()

    def fetch_one(mot):
        return [extraire_offre(r) for r in chercher_offres(token, mot)]

    toutes = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_one, mot) for mot in MOTS_CLES]
        for future in as_completed(futures):
            try:
                toutes.extend(future.result())
            except Exception:
                pass

    # Deduplication
    seen = set()
    uniques = []
    for o in toutes:
        cle = o["titre"].lower() + "|" + o["entreprise"].lower()
        if cle not in seen:
            seen.add(cle)
            uniques.append(o)

    # Score + filter + sort
    result = []
    for o in uniques:
        score, raisons = calculer_score(o)
        if score <= 0:
            continue
        oid = o["id"] or o["titre"][:15]
        for c in ' /\\()"\'.,:!?+-':
            oid = oid.replace(c, "_")
        result.append({
            "id":    oid[:30],
            "score": score,
            "titre": o["titre"],
            "ent":   o["entreprise"],
            "lieu":  o["lieu"],
            "date":  o["date"],
            "lien":  o["lien"],
            "desc":  o["description"],
            "rais":  raisons,
        })

    result.sort(key=lambda x: x["score"], reverse=True)
    return result


def get_all_offers_cached() -> list:
    """Lit depuis SQLite si disponible, sinon fetch live."""
    if _HAS_DB and _db_exists():
        return _db_get()
    return get_all_offers()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]

        if path in ("/api/offres", "/api/offres.py"):
            try:
                data = get_all_offers_cached()
                body = json.dumps(data, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                body = json.dumps({"error": str(e)}).encode()
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        else:
            rel = path.lstrip("/") or "index.html"
            file_path = os.path.join(ROOT_DIR, rel)
            ext = os.path.splitext(file_path)[1].lower()
            ctype = CONTENT_TYPES.get(ext, "text/html; charset=utf-8")
            try:
                with open(file_path, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception:
                try:
                    with open(os.path.join(ROOT_DIR, "index.html"), "rb") as f:
                        body = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                except Exception:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        pass
