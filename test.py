# Mon premier test
offres = [
    {"titre": "Alternance Dev Web", "ville": "Paris", "score": 8},
    {"titre": "Stage Data Analyst", "ville": "Lyon", "score": 6},
    {"titre": "Alternance Python", "ville": "Paris", "score": 9},
]

# Trier par score décroissant
offres_triees = sorted(offres, key=lambda x: x["score"], reverse=True)

for offre in offres_triees:
    print(f"[{offre['score']}/10] {offre['titre']} — {offre['ville']}")