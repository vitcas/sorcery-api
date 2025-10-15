from flask import Flask, request, jsonify, make_response, render_template
from flask_cors import CORS
import json
import math
import os
import requests

app = Flask(__name__)
CORS(app)  # habilita CORS para todas as rotas

# garante que o arquivo JSON seja lido mesmo no ambiente serverless
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "..", "sorcery_cards.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    GAME_CARDS = json.load(f)

@app.route("/")
def root():
    base_url = request.host_url.rstrip("/")
    endpoints = [
    {"name": "Buscar por nome Wizard", "url": f"{base_url}/cards?name=Wizard"},
    {"name": "Cartas Elemento Air", "url": f"{base_url}/cards?element=Air"},
    {"name": "Cartas Raridade Elite", "url": f"{base_url}/cards?rarity=Elite"},
    {"name": "Cartas Raridade Unique", "url": f"{base_url}/cards?rarity=Unique"},
    {"name": "Cartas Tipo Minion", "url": f"{base_url}/cards?type=Minion"},
    {"name": "Cartas com Subtipo Mortal", "url": f"{base_url}/cards?subtype=Mortal"},
    {"name": "Cartas com Subtipo Beast", "url": f"{base_url}/cards?subtype=Beast"},
    {"name": "Cartas com custo <= 3", "url": f"{base_url}/cards?costMax=3"},
    {"name": "Cartas com custo >= 5", "url": f"{base_url}/cards?costMin=5"},
    {"name": "Cartas do set Alpha", "url": f"{base_url}/cards?set=Alpha"},
    {"name": "Cartas do set Beta", "url": f"{base_url}/cards?set=Beta"},
    {"name": "Cartas com variante Foil", "url": f"{base_url}/cards?finish=Foil"},
    {"name": "Apenas cartas que possuem Foil", "url": f"{base_url}/cards?hasFoil=true"},
    {"name": "Cartas Booster apenas", "url": f"{base_url}/cards?product=Booster"},
    {"name": "Cartas de Deck Preconstruído", "url": f"{base_url}/cards?product=Preconstructed_Deck"},
    {"name": "Minions Elite do elemento Air", "url": f"{base_url}/cards?type=Minion&rarity=Elite&element=Air"},
    {"name": "Minions Ordinary até custo 2", "url": f"{base_url}/cards?type=Minion&rarity=Ordinary&costMax=2"},
    {"name": "Cartas Unique com custo <= 3", "url": f"{base_url}/cards?rarity=Unique&costMax=3"},
    {"name": "Cartas Beast com Foil", "url": f"{base_url}/cards?subtype=Beast&finish=Foil"},
    {"name": "Cartas do set Alpha com Foil", "url": f"{base_url}/cards?set=Alpha&finish=Foil"},
    ]
    return render_template("home.html", endpoints=endpoints)

@app.route("/cards")
def get_cards():
    filters = {
        "name": request.args.get("name"),
        "element": request.args.get("element"),
        "rarity": request.args.get("rarity"),
        "type": request.args.get("type"),
        "subtype": request.args.get("subtype"),
        "costMin": request.args.get("costMin"),
        "costMax": request.args.get("costMax"),
        "set": request.args.get("set"),
        "finish": request.args.get("finish"),
        "product": request.args.get("product"),
        "hasFoil": request.args.get("hasFoil")
    }

    filtered = []
    for card in GAME_CARDS:
        match = True

        # Name (contains)
        if filters["name"]:
            if filters["name"].lower() not in card.get("name", "").lower():
                match = False

        # Element
        if filters["element"]:
            if str(card.get("elements", "")).lower() != filters["element"].lower():
                match = False

        # Rarity
        if filters["rarity"]:
            if card.get("guardian", {}).get("rarity", "").lower() != filters["rarity"].lower():
                match = False

        # Type
        if filters["type"]:
            if card.get("guardian", {}).get("type", "").lower() != filters["type"].lower():
                match = False

        # Subtype (contains)
        if filters["subtype"]:
            if filters["subtype"].lower() not in str(card.get("subTypes", "")).lower():
                match = False

        # Cost range
        cost = card.get("guardian", {}).get("cost", None)
        if cost is not None:
            if filters["costMin"] and cost < int(filters["costMin"]):
                match = False
            if filters["costMax"] and cost > int(filters["costMax"]):
                match = False

        # Set filter (ANY set match)
        if filters["set"]:
            if not any(s.get("name", "").lower() == filters["set"].lower() for s in card.get("sets", [])):
                match = False

        # Finish filter (check variants across all sets)
        if filters["finish"]:
            found_finish = False
            for s in card.get("sets", []):
                for v in s.get("variants", []):
                    if v.get("finish", "").lower() == filters["finish"].lower():
                        found_finish = True
                        break
            if not found_finish:
                match = False

        # Product filter
        if filters["product"]:
            found_product = False
            for s in card.get("sets", []):
                for v in s.get("variants", []):
                    if v.get("product", "").lower() == filters["product"].lower():
                        found_product = True
                        break
            if not found_product:
                match = False

        # hasFoil=true (only include cards with ANY foil variant)
        if filters["hasFoil"] and filters["hasFoil"].lower() == "true":
            has_foil = False
            for s in card.get("sets", []):
                for v in s.get("variants", []):
                    if v.get("finish", "").lower() == "foil":
                        has_foil = True
                        break
            if not has_foil:
                match = False

        if match:
            filtered.append(card)

    # Pagination (same as before)
    try:
        limit = min(int(request.args.get("limit", 25)), 100)
    except ValueError:
        limit = 25
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except ValueError:
        page = 1

    total = len(filtered)
    total_pages = math.ceil(total / limit) if limit > 0 else 1
    start = (page - 1) * limit
    end = start + limit
    paginated = filtered[start:end]

    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages,
        "data": paginated
    })


@app.after_request
def add_cache_headers(resp):
    resp.headers["Cache-Control"] = "s-maxage=300, stale-while-revalidate=600"
    return resp
    
# não precisa de app.run() – o Vercel já usa a variável app
if __name__ == "__main__":
    #app.run(debug=True)
    app.run(port=5001, debug=True)
