import random
from models.user_model import UserModel

class GameService:
    # Configuração oficial dos mini-games
    MINIGAME_CONFIG = {
        "easy": {"time": 5.0, "reward": 10.00},
        "medium": {"time": 1.3, "reward": 45.00},
        "hard": {"time": 0.7, "reward": 100.00}
    }

    # Configuração dos símbolos da Slot Machine
    SLOT_SYMBOLS = [
        {"symbol": "❌", "weight": 460},
        {"symbol": "🟢", "weight": 260},
        {"symbol": "🟩", "weight": 150},
        {"symbol": "❇️", "weight": 80},
        {"symbol": "💚", "weight": 35},
        {"symbol": "7️⃣", "weight": 15}
    ]

    @classmethod
    def sell_skin(cls, user_id, item_uid, sell_type="bot"):
        """
        Vende uma skin do inventário do jogador no backend:
        - Bot: 45% do valor da skin (já influenciada pela condição).
        - Player Market: 100% do valor da skin.
        """
        removed_item = UserModel.remove_skin_from_inventory(user_id, item_uid)
        if not removed_item:
            return {"error": "Skin não encontrada no seu inventário.", "code": 404}

        skin_value = float(removed_item.get("price", removed_item.get("basePrice", 0.0)))
        
        if sell_type == "bot":
            payout = round(skin_value * 0.45, 2)
        else:
            payout = round(skin_value * 1.00, 2)

        updated_user = UserModel.add_balance(user_id, payout)

        return {
            "success": True,
            "item": removed_item,
            "payout": payout,
            "sellType": sell_type,
            "novoSaldo": updated_user["dinheiro"] if updated_user else 0.0
        }

    @classmethod
    def sell_batch(cls, user_id, item_uids, sell_type="bot"):
        """Vende um lote de skins (ex: de uma abertura de 2 a 5 caixas)."""
        removed_items = UserModel.remove_skins_from_inventory(user_id, item_uids)
        if not removed_items:
            return {"error": "Nenhuma skin válida encontrada para venda.", "code": 404}

        total_value = sum(float(item.get("price", item.get("basePrice", 0.0))) for item in removed_items)
        rate = 0.45 if sell_type == "bot" else 1.00
        payout = round(total_value * rate, 2)

        updated_user = UserModel.add_balance(user_id, payout)

        return {
            "success": True,
            "count": len(removed_items),
            "payout": payout,
            "novoSaldo": updated_user["dinheiro"] if updated_user else 0.0
        }

    @classmethod
    def claim_minigame_reward(cls, user_id, difficulty):
        """Valida e credita a recompensa do mini-game de reflexo."""
        cfg = cls.MINIGAME_CONFIG.get(difficulty)
        if not cfg:
            return {"error": "Dificuldade de mini-game inválida.", "code": 400}

        reward = cfg["reward"]
        updated_user = UserModel.add_balance(user_id, reward)

        return {
            "success": True,
            "difficulty": difficulty,
            "reward": reward,
            "novoSaldo": updated_user["dinheiro"] if updated_user else 0.0
        }

    @classmethod
    def spin_slots(cls, user_id, bet_amount):
        """
        Executa a roleta de apostas (Slot Machine 3x1) autoritativa no servidor:
        - Valida a aposta contra o saldo real.
        - Sorteia os 3 símbolos.
        - Regra do ❌: se cair qualquer ❌ (1 ou mais), anula todo o ganho.
        - Multiplica até 220x no 777 Jackpot.
        """
        bet_amount = round(float(bet_amount), 2)
        if bet_amount <= 0:
            return {"error": "Valor da aposta inválido.", "code": 400}

        # Deduz o valor da aposta atomicamente
        user = UserModel.deduct_balance(user_id, bet_amount)
        if not user:
            return {"error": "Saldo insuficiente para esta aposta.", "code": 400}

        # Sorteia 3 símbolos
        total_weight = sum(s["weight"] for s in cls.SLOT_SYMBOLS)
        def draw_symbol():
            rand = random.uniform(0, total_weight)
            for item in cls.SLOT_SYMBOLS:
                if rand < item["weight"]:
                    return item["symbol"]
                rand -= item["weight"]
            return "❌"

        symbols = [draw_symbol(), draw_symbol(), draw_symbol()]

        # Contagem
        counts = {}
        for s in symbols:
            counts[s] = counts.get(s, 0) + 1

        x_count = counts.get("❌", 0)

        # Regra do X: se cair qualquer ❌ (1 ou mais), anula todo o bônus
        if x_count >= 1:
            return {
                "success": True,
                "symbols": symbols,
                "multiplier": 0,
                "payout": 0.0,
                "message": f"❌ O símbolo X caiu e você perdeu todo o bônus da rodada! (-R$ {bet_amount:.2f})",
                "novoSaldo": user["dinheiro"]
            }

        multiplier = 0
        reason = ""

        if counts.get("7️⃣", 0) == 3:
            multiplier = 220
            reason = "JACKPOT 777! (220x)"
        elif counts.get("💚", 0) == 3:
            multiplier = 65
            reason = "3 Corações Verdes! (65x)"
        elif counts.get("❇️", 0) >= 2:
            multiplier = 26
            reason = "2+ Brilhos Verdes! (26x)"
        elif counts.get("🟩", 0) >= 2:
            multiplier = 13
            reason = "2+ Quadrados Verdes! (13x)"
        elif counts.get("🟢", 0) >= 2:
            multiplier = 7
            reason = "2+ Círculos Verdes! (7x)"

        payout = 0.0
        final_user = user
        if multiplier > 0:
            payout = round(bet_amount * multiplier, 2)
            final_user = UserModel.add_balance(user_id, payout)
            message = f"🎉 Parabéns! {reason} Ganho: +R$ {payout:.2f}"
        else:
            message = "Nenhuma combinação vencedora. Tente novamente!"

        return {
            "success": True,
            "symbols": symbols,
            "multiplier": multiplier,
            "payout": payout,
            "message": message,
            "novoSaldo": final_user["dinheiro"] if final_user else user["dinheiro"]
        }
