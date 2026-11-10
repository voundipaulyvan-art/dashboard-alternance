import sys, os, json
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Pointe vers api/ pour que "from offres import ..." fonctionne
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "api"))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Charge les credentials depuis collecte.py si les variables d'env ne sont pas definies
if not os.environ.get("FRANCE_TRAVAIL_CLIENT_ID"):
    import re
    try:
        with open("collecte.py", "r", encoding="utf-8") as f:
            src = f.read()
        m = re.search(r'CLIENT_ID\s*=\s*"([^"]+)"', src)
        if m: os.environ["FRANCE_TRAVAIL_CLIENT_ID"] = m.group(1)
        m = re.search(r'CLIENT_SECRET\s*=\s*"([^"]+)"', src)
        if m: os.environ["FRANCE_TRAVAIL_CLIENT_SECRET"] = m.group(1)
    except FileNotFoundError:
        print("  Attention : collecte.py introuvable, definissez les variables d'env manuellement.")


class LocalHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0] == "/api/offres":
            try:
                from offres import get_all_offers_cached
                data = get_all_offers_cached()
                body = json.dumps(data, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                import traceback
                traceback.print_exc()
                msg = str(e)
                body = json.dumps({"error": msg}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        else:
            super().do_GET()

    def log_message(self, format, *args):
        status = args[1]
        color = "\033[32m" if status.startswith("2") else "\033[31m" if status.startswith("5") else "\033[33m"
        print(f"  {color}{args[0]}  {status}\033[0m")


if __name__ == "__main__":
    port = 5000
    print("=" * 45)
    print("  Dashboard Alternance - Serveur local")
    print(f"  http://localhost:{port}")
    print("  Ctrl+C pour arreter")
    print("=" * 45)
    HTTPServer(("", port), LocalHandler).serve_forever()
