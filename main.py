import subprocess
import sys
import os
import webbrowser
from datetime import datetime
 
PYTHON = r"C:\Python312\python.exe"
 
os.chdir(os.path.dirname(os.path.abspath(__file__)))
 
print("=" * 55)
print("   DASHBOARD ALTERNANCE - Lancement automatique")
print(f"   {datetime.now().strftime('%d/%m/%Y a %H:%M')}")
print("=" * 55)
 
def lancer(script, description):
    print(f"\n>>> {description}")
    print(f"    Lancement de {script}...")
    if not os.path.exists(script):
        print(f"    ERREUR : {script} introuvable !")
        return False
    resultat = subprocess.run(
        [PYTHON, script],
        capture_output=False,
        text=True
    )
    if resultat.returncode == 0:
        print(f"    OK - {description} termine !")
        return True
    else:
        print(f"    ERREUR dans {script} (code {resultat.returncode})")
        return False
 
print("\n Demarrage en cours...\n")
 
ok1 = lancer("collecte.py",     "Etape 1/3 - Collecte des offres")
ok2 = lancer("scoring.py",      "Etape 2/3 - Scoring et tri")
ok3 = lancer("dashboard_v2.py", "Etape 3/3 - Generation du dashboard")
 
print("\n" + "=" * 55)
if ok1 and ok2 and ok3:
    print("  SUCCES ! Ouverture du dashboard...")
else:
    print("  Termine avec des erreurs. Verifie ci-dessus.")
print("=" * 55)
 
webbrowser.open("file:///" + os.path.abspath("offres.html"))
 
print("\n  Le dashboard est ouvert dans ton navigateur.")
print("  Appuie sur Entree pour fermer cette fenetre.")
input()