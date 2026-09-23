import random
import time
from datetime import datetime, timezone
from models.user_model import UserModel

# ==============================================================================
# 1. CATÁLOGO DAS 20 SKINS
# ==============================================================================
SKINS_CATALOG = [
  # 1. COMUM (7 skins)
  { "id": "c1", "weapon": "P250", "skin": "Areia Seca", "rarity": "common", "price": 15.00, "type": "pistol", "color": "#b0c3d9" },
  { "id": "c2", "weapon": "MP9", "skin": "Lama Tóxica", "rarity": "common", "price": 22.00, "type": "smg", "color": "#8898a8" },
  { "id": "c3", "weapon": "Nova", "skin": "Predador", "rarity": "common", "price": 30.00, "type": "shotgun", "color": "#7e8e9f" },
  { "id": "c4", "weapon": "Galil AR", "skin": "Conexão Urbana", "rarity": "common", "price": 40.00, "type": "rifle", "color": "#95a5b5" },
  { "id": "c5", "weapon": "SG 553", "skin": "Onda de Choque", "rarity": "common", "price": 55.00, "type": "rifle", "color": "#7b8d9f" },
  { "id": "c6", "weapon": "UMP-45", "skin": "Carbono", "rarity": "common", "price": 70.00, "type": "smg", "color": "#687787" },
  { "id": "c7", "weapon": "Glock-18", "skin": "Grafite Simples", "rarity": "common", "price": 85.00, "type": "pistol", "color": "#a0b0c0" },

  # 2. INCOMUM (5 skins)
  { "id": "u1", "weapon": "Desert Eagle", "skin": "Corrosão", "rarity": "uncommon", "price": 120.00, "type": "pistol", "color": "#4b69ff" },
  { "id": "u2", "weapon": "FAMAS", "skin": "Olho de Tigre", "rarity": "uncommon", "price": 150.00, "type": "rifle", "color": "#4560ea" },
  { "id": "u3", "weapon": "SSG 08", "skin": "Abismo Azul", "rarity": "uncommon", "price": 190.00, "type": "sniper", "color": "#3d54d4" },
  { "id": "u4", "weapon": "MAC-10", "skin": "Neon Minimal", "rarity": "uncommon", "price": 240.00, "type": "smg", "color": "#5672ff" },
  { "id": "u5", "weapon": "P90", "skin": "Glitch Tecnológico", "rarity": "uncommon", "price": 290.00, "type": "smg", "color": "#405bf0" },

  # 3. RARO (4 skins)
  { "id": "r1", "weapon": "M4A4", "skin": "Magma Infame", "rarity": "rare", "price": 420.00, "type": "rifle", "color": "#8847ff" },
  { "id": "r2", "weapon": "USP-S", "skin": "Fio Cibernético", "rarity": "rare", "price": 580.00, "type": "pistol", "color": "#9658ff" },
  { "id": "r3", "weapon": "AK-47", "skin": "Safira Sintética", "rarity": "rare", "price": 750.00, "type": "rifle", "color": "#7c33f2" },
  { "id": "r4", "weapon": "AWP", "skin": "Hipervelocidade", "rarity": "rare", "price": 980.00, "type": "sniper", "color": "#a26bff" },

  # 4. ÉPICO (3 skins)
  { "id": "e1", "weapon": "M4A1-S", "skin": "Fênix Dourada", "rarity": "epic", "price": 1600.00, "type": "rifle", "color": "#d32ce6" },
  { "id": "e2", "weapon": "AK-47", "skin": "Dragão Vulcânico", "rarity": "epic", "price": 2400.00, "type": "rifle", "color": "#e040f5" },
  { "id": "e3", "weapon": "AWP", "skin": "Lança dos Deuses", "rarity": "epic", "price": 3800.00, "type": "sniper", "color": "#c41bd7" },

  # 5. LENDÁRIA (1 skin)
  { "id": "l1", "weapon": "Karambit", "skin": "Esmeralda Estelar", "rarity": "legendary", "price": 12500.00, "type": "knife", "color": "#ffd700" }
]

# ==============================================================================
# 2. DEFINIÇÃO DAS 3 CAIXAS E PROBABILIDADES
# ==============================================================================
BOXES = {
  "comum": {
    "id": "comum",
    "name": "Caixa Comum",
    "price": 100.00,
    "rarities": ["common", "uncommon"],
    "chances": {
      "common": 75.0,    # 75%
      "uncommon": 25.0   # 25%
    }
  },
  "rara": {
    "id": "rara",
    "name": "Caixa Rara",
    "price": 1000.00,
    "rarities": ["common", "uncommon", "rare", "epic"],
    "chances": {
      "common": 45.0,    # 45%
      "uncommon": 30.0,  # 30%
      "rare": 18.0,      # 18%
      "epic": 7.0        # 7% (abaixo de 8%)
    }
  },
  "lendaria": {
    "id": "lendaria",
    "name": "Caixa Lendária",
    "price": 10000.00,
    "rarities": ["common", "uncommon", "rare", "epic", "legendary"],
    "chances": {
      "common": 30.0,    # 30%
      "uncommon": 27.0,  # 27%
      "rare": 28.0,      # 28%
      "epic": 14.0,      # 14% (entre 12% e 15%)
      "legendary": 1.0   # 1% (abaixo de 2%)
    }
  }
}

# ==============================================================================
# 3. ESTADOS DA ARMA (ROLETA INVISÍVEL) & MULTIPLICADORES
# ==============================================================================
CONDITIONS = {
  "arruinada": {
    "key": "arruinada",
    "label": "Arruinada",
    "chance": 15.0,  # 15%
    "mult": 0.40,    # 0.40x
    "color": "#ef5350"
  },
  "danificada": {
    "key": "danificada",
    "label": "Danificada",
    "chance": 25.0,  # 25%
    "mult": 0.60,    # 0.60x
    "color": "#ff7043"
  },
  "arranhada": {
    "key": "arranhada",
    "label": "Arranhada",
    "chance": 25.0,  # 25%
    "mult": 0.75,    # 0.75x
    "color": "#ffa726"
  },
  "normal": {
    "key": "normal",
    "label": "Normal",
    "chance": 20.0,  # 20%
    "mult": 1.00,    # 1.00x
    "color": "#90caf9"
  },
  "bom_estado": {
    "key": "bom_estado",
    "label": "Bom Estado",
    "chance": 12.0,  # 12%
    "mult": 1.25,    # 1.25x
    "color": "#66bb6a"
  },
  "perfeito_estado": {
    "key": "perfeito_estado",
    "label": "Perfeito Estado",
    "chance": 3.0,   # 3%
    "mult": 1.50,    # 1.50x
    "color": "#ffd700"
  }
}

# Validação automática das probabilidades
def validar_probabilidades():
    for key, box in BOXES.items():
        sum_chances = sum(box["chances"].values())
        if abs(sum_chances - 100.0) > 0.001:
            raise ValueError(f"Probabilidades da {box['name']} somam {sum_chances}%, esperado exatamente 100%!")

    sum_cond = sum(c["chance"] for c in CONDITIONS.values())
    if abs(sum_cond - 100.0) > 0.001:
        raise ValueError(f"Probabilidades dos estados da arma somam {sum_cond}%, esperado exatamente 100%!")
    return True

# Executa a validação na importação do módulo
validar_probabilidades()


# ==============================================================================
# 4. FUNÇÕES DE SORTEIO
# ==============================================================================

def sortear_raridade(box):
    rand = random.uniform(0, 100.0)
    for rarity, chance in box["chances"].items():
        if rand < chance:
            return rarity
        rand -= chance
    return box["rarities"][0]

def sortear_skin(rarity):
    pool = [s for s in SKINS_CATALOG if s["rarity"] == rarity]
    if not pool:
        return SKINS_CATALOG[0]
    return random.choice(pool)

def sortear_estado():
    rand = random.uniform(0, 100.0)
    for condition in CONDITIONS.values():
        if rand < condition["chance"]:
            return condition
        rand -= condition["chance"]
    return CONDITIONS["normal"]

def calcular_valor_skin(base_price, condition_key):
    cond = CONDITIONS.get(condition_key, CONDITIONS["normal"])
    return round(base_price * cond["mult"], 2)


# ==============================================================================
# 5. SERVIÇO PRINCIPAL: ABRIR CAIXAS (1 A 5 UNIDADES)
# ==============================================================================

class BoxService:
    @staticmethod
    def abrir_caixas(user_id, box_id, quantity=1):
        """
        Executa a abertura autoritativa de 1 a 5 caixas para o jogador.
        Valida saldo, desconta, sorteia as skins com desgaste e salva no MongoDB.
        """
        validar_probabilidades()

        quantity = int(quantity)
        if quantity < 1 or quantity > 5:
            return {"error": "Quantidade de caixas deve ser entre 1 e 5.", "code": 400}

        box = BOXES.get(box_id)
        if not box:
            return {"error": "Caixa inválida selecionada.", "code": 400}

        total_cost = round(box["price"] * quantity, 2)

        # 1. Deduz o saldo atomicamente no MongoDB
        updated_user = UserModel.deduct_balance(user_id, total_cost)
        if not updated_user:
            user = UserModel.get_by_id(user_id)
            saldo_atual = user.get("dinheiro", 0.0) if user else 0.0
            return {
                "error": f"Saldo insuficiente! Você possui R$ {saldo_atual:.2f}, mas são necessários R$ {total_cost:.2f}.",
                "code": 400
            }

        # 2. Realiza o sorteio para cada caixa
        winning_items = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for i in range(quantity):
            # Sorteio de Raridade
            drawn_rarity = sortear_raridade(box)
            # Sorteio de Skin
            skin = sortear_skin(drawn_rarity)
            # Roleta Invisível de Condição
            condition = sortear_estado()
            # Cálculo final do preço
            final_price = calcular_valor_skin(skin["price"], condition["key"])

            item_uid = f"{int(time.time() * 1000)}_{i}_{random.randint(1000, 9999)}"

            item = {
                "uid": item_uid,
                "boxId": box["id"],
                "boxName": box["name"],
                "skinId": skin["id"],
                "weapon": skin["weapon"],
                "skin": skin["skin"],
                "rarity": skin["rarity"],
                "type": skin["type"],
                "color": skin["color"],
                "basePrice": round(skin["price"], 2),
                "conditionKey": condition["key"],
                "conditionLabel": condition["label"],
                "conditionMult": condition["mult"],
                "conditionColor": condition["color"],
                "price": final_price,
                "adquiridoEm": now_iso
            }
            winning_items.append(item)

        # 3. Salva os itens sorteados no MongoDB
        user_after_push = UserModel.add_skins_to_inventory(user_id, winning_items)

        return {
            "success": True,
            "boxId": box_id,
            "quantity": quantity,
            "totalCost": total_cost,
            "items": winning_items,
            "novoSaldo": user_after_push["dinheiro"] if user_after_push else updated_user["dinheiro"]
        }
