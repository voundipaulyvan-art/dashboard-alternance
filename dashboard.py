import csv, json, os, webbrowser
from datetime import datetime
 
print("=" * 50)
print("  Generation du dashboard")
print("=" * 50)
 
# Lire les offres scorees
offres = []
with open("offres_scored.csv", "r", encoding="utf-8") as f:
    for ligne in csv.DictReader(f):
        offres.append(ligne)
 
offres_filtrees = [o for o in offres if int(o["score"]) > 0]
nb_excellent    = sum(1 for o in offres_filtrees if int(o["score"]) >= 10)
nb_bon          = sum(1 for o in offres_filtrees if 5 <= int(o["score"]) < 10)
nb_correct      = sum(1 for o in offres_filtrees if 0 < int(o["score"]) < 5)
date_gen        = datetime.now().strftime("%d/%m/%Y a %H:%M")
 
print(f"  {len(offres_filtrees)} offres pertinentes sur {len(offres)} total")
 
# Nettoyer les donnees pour JSON
def clean(s, maxlen=200):
    if not s: return ""
    s = s[:maxlen]
    for c in ["\r\n","\r","\n","\\","`","'","<",">",'"',"&"]:
        s = s.replace(c, " ")
    return " ".join(s.split())
 
data = []
for o in offres_filtrees:
    oid = o.get("id", o["titre"][:15])
    for c in [" ","/","\\","(",")",'"',"'",".",",",":","!","?","+","-"]:
        oid = oid.replace(c, "_")
    data.append({
        "id":    oid[:30],
        "score": int(o["score"]),
        "titre": clean(o["titre"], 80),
        "ent":   clean(o["entreprise"], 50),
        "lieu":  clean(o["lieu"], 50),
        "date":  o["date"][:10],
        "lien":  o["lien"],
        "desc":  clean(o["description"], 200),
        "rais":  clean(o["raisons"], 80)
    })
 
json_data = json.dumps(data, ensure_ascii=True, separators=(",",":"))
json_data = json_data.replace("</script>", "<\\/script>")
assert "'" not in json_data, "Apostrophe trouvee dans JSON!"
 
# CSS commun a toutes les pages
CSS = """<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Segoe UI,sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}
nav{background:#1e293b;padding:12px 24px;border-bottom:1px solid #334155;display:flex;gap:4px;align-items:center}
nav .logo{color:#64748b;font-size:12px;margin-right:12px;font-weight:600}
nav a{padding:7px 14px;border-radius:8px;font-size:13px;text-decoration:none;color:#94a3b8;border:1px solid #334155;transition:all .2s}
nav a:hover{background:#334155;color:#e2e8f0}
nav a.actif{background:#3b82f6;border-color:#3b82f6;color:#fff}
.header{background:#1e293b;padding:16px 24px;border-bottom:1px solid #334155}
.header h1{font-size:18px;font-weight:600;color:#f1f5f9}
.header p{font-size:12px;color:#94a3b8;margin-top:3px}
.stats{display:flex;gap:12px;padding:16px 24px;flex-wrap:wrap}
.stat{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:12px 20px;text-align:center;min-width:110px}
.stat .nb{font-size:24px;font-weight:700}
.stat .lb{font-size:11px;color:#94a3b8;margin-top:3px}
.filtres{padding:0 24px 14px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.filtres input{background:#1e293b;border:1px solid #334155;border-radius:8px;padding:7px 12px;color:#e2e8f0;font-size:13px;width:240px;outline:none}
.filtres input:focus{border-color:#3b82f6}
.btn{background:#1e293b;border:1px solid #334155;border-radius:8px;padding:6px 12px;color:#94a3b8;font-size:12px;cursor:pointer;transition:all .2s}
.btn:hover,.btn.actif{background:#3b82f6;border-color:#3b82f6;color:#fff}
.cpt{color:#94a3b8;font-size:12px;padding:0 24px 8px}
.liste{padding:0 24px 32px;display:flex;flex-direction:column;gap:8px}
.carte{background:#1e293b;border:1px solid #334155;border-radius:10px;overflow:hidden}
.carte:hover{border-color:#475569}
.ch{display:flex;align-items:center;gap:12px;padding:12px 16px}
.sc{font-size:18px;font-weight:700;min-width:44px;text-align:center}
.inf{flex:1}
.inf h3{font-size:13px;font-weight:600;color:#f1f5f9;margin-bottom:4px}
.meta{font-size:11px;color:#64748b}
.bdg{font-size:11px;font-weight:600;padding:3px 8px;border-radius:16px;white-space:nowrap}
.cb{padding:10px 16px 12px;border-top:1px solid #334155}
.desc{font-size:12px;color:#94a3b8;line-height:1.5;margin-bottom:8px}
.strow{display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap}
.stsel{background:#0f172a;border:1px solid #334155;border-radius:6px;padding:4px 8px;color:#e2e8f0;font-size:12px;cursor:pointer;outline:none}
.dtrel{background:#0f172a;border:1px solid #334155;border-radius:6px;padding:4px 8px;color:#e2e8f0;font-size:12px;outline:none;display:none}
.noteinp{width:100%;background:#0f172a;border:1px solid #334155;border-radius:6px;padding:6px 8px;color:#e2e8f0;font-size:12px;resize:none;outline:none;font-family:inherit;margin-bottom:8px}
.noteinp:focus{border-color:#3b82f6}
.ft{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}
.rais{font-size:11px;color:#475569;font-style:italic}
.lienoffre a{color:#3b82f6;font-size:12px;text-decoration:none}
.lienoffre a:hover{text-decoration:underline}
.btncv{background:#1e3a5f;border:1px solid #3b82f6;border-radius:6px;padding:4px 10px;color:#93c5fd;font-size:12px;cursor:pointer}
.btncv:hover{background:#3b82f6;color:#fff}
.acv{background:#0f172a;border:1px solid #334155;border-radius:6px;padding:10px;margin-top:8px;font-size:12px;line-height:1.6;display:none}
.page{padding:20px 24px}
.card{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:16px;margin-bottom:12px}
.card h2{font-size:14px;font-weight:600;color:#f1f5f9;margin-bottom:12px}
table{width:100%;border-collapse:collapse;font-size:13px}
th{background:#334155;padding:8px 12px;text-align:left;color:#94a3b8;font-size:11px;text-transform:uppercase}
td{padding:8px 12px;border-bottom:1px solid #0f172a;color:#e2e8f0}
tr:hover td{background:#243044}
.pill{display:inline-block;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600}
.drop{border:2px dashed #334155;border-radius:10px;padding:32px;text-align:center;cursor:pointer;transition:all .2s}
.drop:hover{border-color:#3b82f6;background:#1a2744}
.drop p{color:#94a3b8;font-size:13px;margin-top:8px}
.cvtxt{background:#0f172a;border:1px solid #334155;border-radius:8px;padding:12px;margin-top:12px;font-size:12px;line-height:1.7;color:#e2e8f0;white-space:pre-wrap;max-height:350px;overflow-y:auto}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.bar-r{display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:12px}
.bar-l{width:80px;color:#94a3b8;font-size:11px}
.bar-bg{flex:1;background:#0f172a;border-radius:3px;height:7px;overflow:hidden}
.bar-f{height:100%;border-radius:3px;transition:width .4s}
.bar-v{width:24px;text-align:right;color:#e2e8f0;font-size:11px;font-weight:600}
.rrow{display:flex;justify-content:space-between;font-size:13px;padding:5px 0;border-bottom:1px solid #334155}
.rrow:last-child{border:none}
</style>"""
 
# Navigation commune
NAV = """<nav>
  <span class="logo">Dashboard</span>
  <a href="offres.html" id="n-offres">Offres (NB_OFFRES)</a>
  <a href="suivi.html" id="n-suivi">Suivi candidatures</a>
  <a href="cv.html" id="n-cv">Mon CV</a>
  <a href="stats.html" id="n-stats">Statistiques</a>
</nav>""".replace("NB_OFFRES", str(len(offres_filtrees)))
 
# JS commun (donnees + sauvegarde)
DATA_JS = """
<script>
var OFFRES = """ + json_data + """;
var C = JSON.parse(localStorage.getItem("cands") || "{}");
var CV = localStorage.getItem("cv") || "";
function save() { localStorage.setItem("cands", JSON.stringify(C)); }
function cpts() {
    var p = Object.values(C).filter(function(d) { return ["postule","entretien","accepte"].includes(d.st); }).length;
    var e = Object.values(C).filter(function(d) { return d.st == "entretien"; }).length;
    var sp = document.getElementById("sp"); var se = document.getElementById("se");
    if (sp) sp.textContent = p;
    if (se) se.textContent = e;
}
var CL = {favori:"#f59e0b",a_postuler:"#3b82f6",postule:"#6366f1",relance:"#f97316",entretien:"#a78bfa",accepte:"#22c55e",refuse:"#ef4444"};
var LB = {favori:"Favori",a_postuler:"A postuler",postule:"Postule",relance:"A relancer",entretien:"Entretien",accepte:"Accepte",refuse:"Refuse"};
</script>"""
 
# ================================================================
# PAGE 1 : offres.html
# ================================================================
p1 = """<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
<title>Offres - Dashboard</title>""" + CSS + """</head><body>
""" + NAV + """
<script>document.getElementById("n-offres").classList.add("actif");</script>
<div class="header">
  <h1>Offres d alternance et stage</h1>
  <p>Genere le """ + date_gen + """ - """ + str(len(offres_filtrees)) + """ offres pertinentes</p>
</div>
<div class="stats">
  <div class="stat"><div class="nb" style="color:#22c55e">""" + str(nb_excellent) + """</div><div class="lb">Excellentes</div></div>
  <div class="stat"><div class="nb" style="color:#3b82f6">""" + str(nb_bon) + """</div><div class="lb">Bonnes</div></div>
  <div class="stat"><div class="nb" style="color:#94a3b8">""" + str(nb_correct) + """</div><div class="lb">Correctes</div></div>
  <div class="stat"><div class="nb" style="color:#f59e0b" id="sp">0</div><div class="lb">Postulees</div></div>
  <div class="stat"><div class="nb" style="color:#a78bfa" id="se">0</div><div class="lb">Entretiens</div></div>
</div>
<div class="filtres">
  <input type="text" id="rech" placeholder="Filtrer par titre, ville, entreprise...">
  <button class="btn actif" data-min="0" data-tp="sc">Tous</button>
  <button class="btn" data-min="10" data-tp="sc">Score 10+</button>
  <button class="btn" data-min="5" data-tp="sc">Score 5+</button>
  <button class="btn" data-st="favori" data-tp="st">Favoris</button>
  <button class="btn" data-st="a_postuler" data-tp="st">A postuler</button>
  <button class="btn" data-st="relance" data-tp="st">A relancer</button>
</div>
<div class="cpt" id="cpt">""" + str(len(offres_filtrees)) + """ offres</div>
<div class="liste" id="lst"></div>
""" + DATA_JS + """
<script>
var sMin=0, sFlt="";
function render(){
    var q=document.getElementById("rech").value.toLowerCase();
    var html="", n=0;
    OFFRES.forEach(function(o){
        var st=(C[o.id]&&C[o.id].st)||"";
        if(o.score<sMin) return;
        if(sFlt&&st!==sFlt) return;
        if(q&&!(o.titre+" "+o.ent+" "+o.lieu+" "+o.desc).toLowerCase().includes(q)) return;
        n++;
        var col=o.score>=10?"#22c55e":o.score>=5?"#3b82f6":"#94a3b8";
        var bdg=o.score>=10?"Excellent":o.score>=5?"Bon":"Correct";
        var scr=(o.score>=0?"+":"")+o.score;
        var nv=(C[o.id]&&C[o.id].note)||"";
        var dv=(C[o.id]&&C[o.id].dr)||"";
        var ds=st=="relance"?"":"display:none";
        var lnk=o.lien?"<a href=\\""+o.lien+"\\" target=\\"_blank\\">Voir l offre</a>":"";
        var sel="<select class=\\"stsel\\" data-id=\\""+o.id+"\\">";
        [["","Non traite"],["favori","Favori"],["a_postuler","A postuler"],
         ["postule","Postule"],["relance","A relancer"],["entretien","Entretien"],
         ["accepte","Accepte"],["refuse","Refuse"]
        ].forEach(function(x){
            sel+="<option value=\\""+x[0]+"\\""+( st==x[0]?" selected":"")+">"+x[1]+"</option>";
        });
        sel+="</select>";
        html+="<div class=\\"carte\\" data-id=\\""+o.id+"\\">"
            +"<div class=\\"ch\\" style=\\"border-left:4px solid "+col+"\\">"
            +"<div class=\\"sc\\" style=\\"color:"+col+"\\">"+scr+"</div>"
            +"<div class=\\"inf\\"><h3>"+o.titre+"</h3>"
            +"<div class=\\"meta\\">"+o.ent+" | "+o.lieu+" | "+o.date+"</div></div>"
            +"<div class=\\"bdg\\" style=\\"background:"+col+"20;color:"+col+"\\">"+bdg+"</div></div>"
            +"<div class=\\"cb\\"><p class=\\"desc\\">"+o.desc+"</p>"
            +"<div class=\\"strow\\"><span style=\\"font-size:11px;color:#94a3b8\\">Statut:</span>"
            +sel+"<input type=\\"date\\" class=\\"dtrel\\" data-id=\\""+o.id+"\\" value=\\""+dv+"\\" style=\\""+ds+"\\"></div>"
            +"<textarea class=\\"noteinp\\" data-id=\\""+o.id+"\\" rows=\\"2\\">"+nv+"</textarea>"
            +"<div class=\\"ft\\"><span class=\\"rais\\">"+o.rais+"</span>"
            +"<div style=\\"display:flex;gap:8px;align-items:center\\">"
            +"<button class=\\"btncv\\" data-id=\\""+o.id+"\\" data-d=\\""+o.desc+"\\">Analyser vs CV</button>"
            +"<span class=\\"lienoffre\\">"+lnk+"</span></div></div>"
            +"<div class=\\"acv\\" id=\\"a-"+o.id+"\\"></div>"
            +"</div></div>";
    });
    document.getElementById("lst").innerHTML=html||"<div style=\\"text-align:center;padding:30px;color:#64748b\\">Aucun resultat</div>";
    document.getElementById("cpt").textContent=n+" offres";
}
document.getElementById("lst").onclick=function(e){
    var b=e.target.closest(".btncv");
    if(b) analyser(b.dataset.id, b.dataset.d);
};
document.getElementById("lst").onchange=function(e){
    var el=e.target, id=el.dataset.id; if(!id) return;
    if(!C[id]) C[id]={};
    if(el.classList.contains("stsel")){
        C[id].st=el.value;
        C[id].dm=new Date().toLocaleDateString("fr-FR");
        var dr=el.closest(".strow").querySelector(".dtrel");
        if(dr) dr.style.display=el.value=="relance"?"inline-block":"none";
        save(); cpts();
    }
    if(el.classList.contains("dtrel")){ C[id].dr=el.value; save(); }
};
document.getElementById("lst").addEventListener("blur",function(e){
    if(e.target.classList.contains("noteinp")){
        var id=e.target.dataset.id;
        if(!C[id]) C[id]={};
        C[id].note=e.target.value; save();
    }
},true);
document.getElementById("rech").oninput=render;
document.querySelector(".filtres").onclick=function(e){
    var b=e.target.closest(".btn"); if(!b) return;
    document.querySelectorAll(".btn").forEach(function(x){x.classList.remove("actif");});
    b.classList.add("actif");
    if(b.dataset.tp=="sc"){ sMin=parseInt(b.dataset.min); sFlt=""; }
    else { sFlt=b.dataset.st; sMin=0; }
    render();
};
function analyser(id,desc){
    var z=document.getElementById("a-"+id); if(!z) return;
    z.style.display="block";
    if(!CV){ z.innerHTML="Importe ton CV dans la page Mon CV."; return; }
    var cv=CV.toLowerCase(), d=desc.toLowerCase();
    var mots=["python","javascript","sql","excel","git","linux","windows","sap","erp",
              "jira","agile","scrum","api","data","azure","docker","html","css","php","java","node","react"];
    var ok=mots.filter(function(m){return d.includes(m)&&cv.includes(m);});
    var ko=mots.filter(function(m){return d.includes(m)&&!cv.includes(m);});
    z.innerHTML="<strong style=\\"color:#f1f5f9\\">Analyse CV</strong><br>"
        +(ok.length?"<span style=\\"color:#22c55e\\">Presents: "+ok.join(", ")+"</span><br>":"")
        +(ko.length?"<span style=\\"color:#f59e0b\\">Manquants: "+ko.join(", ")+"</span>":"<span style=\\"color:#22c55e\\">CV compatible !</span>");
}
render(); cpts();
</script></body></html>"""
 
# ================================================================
# PAGE 2 : suivi.html
# ================================================================
p2 = """<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
<title>Suivi - Dashboard</title>""" + CSS + """</head><body>
""" + NAV + """
<script>document.getElementById("n-suivi").classList.add("actif");</script>
<div class="header">
  <h1>Suivi des candidatures</h1>
  <p>Toutes les offres avec un statut enregistre</p>
</div>
<div class="page">
  <div class="card">
    <h2>Mes candidatures</h2>
    <div id="empty" style="text-align:center;padding:30px;color:#64748b">
      Aucune candidature. Allez sur Offres et changez le statut d une offre.
    </div>
    <div style="overflow-x:auto">
      <table id="tbl" style="display:none">
        <thead><tr><th>Poste</th><th>Entreprise</th><th>Ville</th><th>Statut</th><th>Date</th><th>Note</th><th>Lien</th></tr></thead>
        <tbody id="tbody"></tbody>
      </table>
    </div>
  </div>
  <div class="card">
    <h2>Compteurs par statut</h2>
    <div class="stats" id="cpt-grid" style="padding:0"></div>
  </div>
</div>
""" + DATA_JS + """
<script>
var rows=Object.entries(C).filter(function(x){return x[1].st&&x[1].st!="";});
if(!rows.length){
    document.getElementById("empty").style.display="block";
} else {
    document.getElementById("empty").style.display="none";
    document.getElementById("tbl").style.display="table";
    document.getElementById("tbody").innerHTML=rows.map(function(r){
        var id=r[0], d=r[1];
        var o=OFFRES.find(function(x){return x.id==id;})||{};
        var c=CL[d.st]||"#94a3b8", l=LB[d.st]||d.st;
        var lnk=o.lien?"<a href=\\""+o.lien+"\\" target=\\"_blank\\" style=\\"color:#3b82f6;text-decoration:none\\">Voir</a>":"-";
        return "<tr>"
            +"<td><strong style=\\"color:#f1f5f9\\">"+(o.titre||id)+"</strong></td>"
            +"<td>"+(o.ent||"-")+"</td>"
            +"<td>"+(o.lieu||"-")+"</td>"
            +"<td><span class=\\"pill\\" style=\\"background:"+c+"20;color:"+c+"\\">"+l+"</span></td>"
            +"<td style=\\"color:#64748b\\">"+(d.dm||"-")+"</td>"
            +"<td style=\\"color:#64748b\\">"+(d.note?d.note.substring(0,40)+"...":"-")+"</td>"
            +"<td>"+lnk+"</td></tr>";
    }).join("");
}
var stats={};
Object.values(C).forEach(function(d){if(d.st) stats[d.st]=(stats[d.st]||0)+1;});
document.getElementById("cpt-grid").innerHTML=Object.entries(stats).map(function(x){
    var c=CL[x[0]]||"#94a3b8", l=LB[x[0]]||x[0];
    return "<div class=\\"stat\\"><div class=\\"nb\\" style=\\"color:"+c+"\\">"+x[1]+"</div><div class=\\"lb\\">"+l+"</div></div>";
}).join("")||"<div style=\\"color:#64748b;font-size:13px;padding:8px\\">Aucune donnee</div>";
</script></body></html>"""
 
# ================================================================
# PAGE 3 : cv.html
# ================================================================
p3 = """<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
<title>Mon CV - Dashboard</title>""" + CSS + """</head><body>
""" + NAV + """
<script>document.getElementById("n-cv").classList.add("actif");</script>
<div class="header">
  <h1>Mon CV</h1>
  <p>Importe ton CV pour analyser ta compatibilite avec les offres</p>
</div>
<div class="page">
  <div class="card">
    <h2>Importer mon CV</h2>
    <div class="drop" id="drop">
      <div style="font-size:36px">&#128196;</div>
      <p>Clique ou glisse ton CV ici (.txt)</p>
      <p style="font-size:11px;margin-top:6px;color:#475569">Sauvegarde localement dans le navigateur</p>
      <input type="file" id="cv-in" accept=".txt" style="display:none">
    </div>
    <div id="cv-ok" style="display:none;margin-top:12px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <span style="color:#22c55e;font-size:13px;font-weight:600">CV charge</span>
        <button id="cv-del" style="background:#7f1d1d;border:none;border-radius:6px;padding:4px 10px;color:#fca5a5;font-size:12px;cursor:pointer">Supprimer</button>
      </div>
      <div class="cvtxt" id="cv-txt"></div>
    </div>
  </div>
  <div class="card">
    <h2>Comment utiliser l analyse CV</h2>
    <p style="font-size:13px;color:#64748b;line-height:1.9">
      1. Importe ton CV ci-dessus en format .txt<br>
      2. Va sur la page <a href="offres.html" style="color:#3b82f6">Offres</a><br>
      3. Clique sur <strong style="color:#93c5fd">Analyser vs CV</strong> sur n importe quelle offre<br>
      4. Tu verras les competences presentes et manquantes dans ton CV<br>
      5. Adapte ton CV en consequence pour maximiser tes chances
    </p>
  </div>
</div>
<script>
var CV=localStorage.getItem("cv")||"";
function showCV(t){
    document.getElementById("cv-ok").style.display="block";
    document.getElementById("cv-txt").textContent=t;
}
if(CV) showCV(CV);
document.getElementById("drop").onclick=function(){ document.getElementById("cv-in").click(); };
document.getElementById("drop").ondragover=function(e){ e.preventDefault(); this.style.borderColor="#3b82f6"; };
document.getElementById("drop").ondragleave=function(){ this.style.borderColor="#334155"; };
document.getElementById("drop").ondrop=function(e){
    e.preventDefault(); this.style.borderColor="#334155";
    if(e.dataTransfer.files[0]) loadFile(e.dataTransfer.files[0]);
};
document.getElementById("cv-in").onchange=function(){ if(this.files[0]) loadFile(this.files[0]); };
document.getElementById("cv-del").onclick=function(){
    localStorage.removeItem("cv"); CV="";
    document.getElementById("cv-ok").style.display="none";
};
function loadFile(f){
    var r=new FileReader();
    r.onload=function(e){ CV=e.target.result; localStorage.setItem("cv",CV); showCV(CV); };
    r.readAsText(f,"utf-8");
}
</script></body></html>"""
 
# ================================================================
# PAGE 4 : stats.html
# ================================================================
p4 = """<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
<title>Stats - Dashboard</title>""" + CSS + """</head><body>
""" + NAV + """
<script>document.getElementById("n-stats").classList.add("actif");</script>
<div class="header">
  <h1>Statistiques</h1>
  <p>Vue globale de ta recherche d alternance</p>
</div>
<div class="page">
  <div class="grid">
    <div class="card">
      <h2>Resume des offres</h2>
      <div class="rrow"><span style="color:#94a3b8">Total collectees</span><span style="font-weight:600">""" + str(len(offres)) + """</span></div>
      <div class="rrow"><span style="color:#94a3b8">Pertinentes (score > 0)</span><span style="font-weight:600;color:#22c55e">""" + str(len(offres_filtrees)) + """</span></div>
      <div class="rrow"><span style="color:#94a3b8">Excellentes (score 10+)</span><span style="font-weight:600;color:#22c55e">""" + str(nb_excellent) + """</span></div>
      <div class="rrow"><span style="color:#94a3b8">Bonnes (score 5-9)</span><span style="font-weight:600;color:#3b82f6">""" + str(nb_bon) + """</span></div>
      <div class="rrow"><span style="color:#94a3b8">Postulees</span><span style="font-weight:600;color:#f59e0b" id="nb-p">0</span></div>
      <div class="rrow"><span style="color:#94a3b8">Entretiens obtenus</span><span style="font-weight:600;color:#a78bfa" id="nb-e">0</span></div>
    </div>
    <div class="card">
      <h2>Statuts des candidatures</h2>
      <div id="bars"><div style="color:#64748b;font-size:13px">Aucune candidature enregistree</div></div>
    </div>
  </div>
</div>
""" + DATA_JS + """
<script>
var p=Object.values(C).filter(function(d){return ["postule","entretien","accepte"].includes(d.st);}).length;
var e=Object.values(C).filter(function(d){return d.st=="entretien";}).length;
document.getElementById("nb-p").textContent=p;
document.getElementById("nb-e").textContent=e;
var ST={};
Object.values(C).forEach(function(d){if(d.st) ST[d.st]=(ST[d.st]||0)+1;});
var tot=Object.values(ST).reduce(function(a,b){return a+b;},0)||1;
if(Object.keys(ST).length){
    document.getElementById("bars").innerHTML=Object.entries(ST).map(function(x){
        return "<div class=\\"bar-r\\"><span class=\\"bar-l\\">"+(LB[x[0]]||x[0])+"</span>"
            +"<div class=\\"bar-bg\\"><div class=\\"bar-f\\" style=\\"width:"+Math.round(x[1]/tot*100)+"%;background:"+(CL[x[0]]||"#94a3b8")+"\\"></div></div>"
            +"<span class=\\"bar-v\\">"+x[1]+"</span></div>";
    }).join("");
}
</script></body></html>"""
 
# Sauvegarder les 4 fichiers
pages = {
    "offres.html": p1,
    "suivi.html":  p2,
    "cv.html":     p3,
    "stats.html":  p4,
}
for nom, contenu in pages.items():
    with open(nom, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"  OK : {nom} ({len(contenu)//1000}ko)")
 
print("\nDashboard genere ! Ouvre offres.html dans ton navigateur.")
webbrowser.open("file:///" + os.path.abspath("offres.html"))