import json

INPUT_FILE = "sorcery_cards.json"
OUTPUT_FILE = "sorcery_cards_final.json"

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        cards = json.load(f)

    updated_cards = []
    for idx, card in enumerate(cards, start=1):
        card_id = f"SORC-{idx:04d}"
        # Garante que ID fica como primeira chave preservando o resto
        new_card = {"id": card_id}
        new_card.update(card)
        updated_cards.append(new_card)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(updated_cards, f, ensure_ascii=False, indent=2)

    print(f"Processado {len(updated_cards)} cartas. Salvo em {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
