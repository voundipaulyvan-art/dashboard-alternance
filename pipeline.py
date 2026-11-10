import sys, os, re, logging

# --- Logging : fichier + console
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs"), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "pipeline.log"),
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

# --- Credentials : variables d'env ou fallback depuis collecte.py
if not os.environ.get("FRANCE_TRAVAIL_CLIENT_ID"):
    try:
        with open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "collecte.py"),
            encoding="utf-8",
        ) as f:
            src = f.read()
        m = re.search(r'CLIENT_ID\s*=\s*"([^"]+)"', src)
        if m:
            os.environ["FRANCE_TRAVAIL_CLIENT_ID"] = m.group(1)
        m = re.search(r'CLIENT_SECRET\s*=\s*"([^"]+)"', src)
        if m:
            os.environ["FRANCE_TRAVAIL_CLIENT_SECRET"] = m.group(1)
    except FileNotFoundError:
        log.warning("collecte.py introuvable — définissez FRANCE_TRAVAIL_CLIENT_ID/SECRET")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "api"))

from offres import get_all_offers
from db import init_db, upsert_offres, log_run


def run():
    log.info("=" * 55)
    log.info("Pipeline alternance démarré")
    try:
        log.info("Étape 1/3 — Collecte via API France Travail...")
        offres = get_all_offers()
        log.info("  → %d offres collectées et scorées", len(offres))

        log.info("Étape 2/3 — Initialisation de la base de données...")
        init_db()
        log.info("  → offres.db prête")

        log.info("Étape 3/3 — Sauvegarde (upsert idempotent)...")
        upsert_offres(offres)
        log.info("  → %d offres insérées/mises à jour", len(offres))

        log_run(len(offres), "success")
        log.info("Pipeline terminé — %d offres en base", len(offres))
        log.info("=" * 55)
    except Exception as e:
        log.error("Pipeline échoué : %s", e, exc_info=True)
        log_run(0, "error", str(e))
        raise


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run()
