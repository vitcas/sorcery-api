import json

INPUT_FILE = "sorcery.json"
OUTPUT_FILE = "sorcery_final.json"
BASE_URL = "https://card.cards.army/cards/"

def gerar_url(slug):
    """
    Remove prefixo inicial (antes do primeiro "_") e gera a URL final .webp
    Exemplo: "alp_apprentice_wizard_b_s" -> "apprentice_wizard_b_s.webp"
    """
    if "_" in slug:
        slug_sem_prefixo = slug.split("_", 1)[1]
    else:
        slug_sem_prefixo = slug  # fallback, caso não tenha prefixo
    return f"{BASE_URL}{slug_sem_prefixo}.webp"

def processar():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for card in data:
        # Encontrar primeiro slug em variants (em qualquer set)
        slug_encontrado = None
        for set_item in card.get("sets", []):
            variants = set_item.get("variants", [])
            if variants:
                slug_encontrado = variants[0].get("slug")
                if slug_encontrado:
                    break  # achou, sai
        if not slug_encontrado:
            # Caso raro de carta sem slug — pular
            continue

        url = gerar_url(slug_encontrado)

        # Inserir chave images
        card["images"] = {
            "small": url,
            "large": url
        }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Arquivo gerado com sucesso: {OUTPUT_FILE}")

if __name__ == "__main__":
    processar()
