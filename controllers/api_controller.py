from flask import Blueprint, request, jsonify
from controllers.auth_controller import login_required
from services.box_service import BoxService
from services.game_service import GameService

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/inventario', methods=['GET'])
@login_required
def get_inventario(current_user):
    """Retorna o inventário salvo permanentemente no MongoDB."""
    return jsonify({
        "success": True,
        "inventario": current_user.get("inventario", []),
        "saldo": current_user.get("dinheiro", 0.0)
    })


@api_bp.route('/api/caixas/abrir', methods=['POST'])
@login_required
def abrir_caixa(current_user):
    """
    Abertura de caixas autoritativa no backend:
    - Verifica saldo
    - Desconta preço
    - Sorteia raridade e skin
    - Executa a roleta invisível de condição
    - Salva no MongoDB
    - Retorna dados para animação no frontend
    """
    data = request.get_json(silent=True) or {}
    box_id = data.get("boxId", "comum")
    quantity = data.get("quantity", 1)

    result = BoxService.abrir_caixas(current_user["id"], box_id, quantity)
    if "error" in result:
        return jsonify(result), result.get("code", 400)

    return jsonify(result)


@api_bp.route('/api/skins/vender', methods=['POST'])
@login_required
def vender_skin(current_user):
    """
    Venda de skin autoritativa:
    - Valida posse da skin no MongoDB
    - Remove do inventário
    - Credita o valor (45% bot ou 100% player)
    """
    data = request.get_json(silent=True) or {}
    item_uid = data.get("uid")
    sell_type = data.get("sellType", "bot")

    if not item_uid:
        return jsonify({"error": "ID da skin não informado.", "code": 400}), 400

    result = GameService.sell_skin(current_user["id"], item_uid, sell_type)
    if "error" in result:
        return jsonify(result), result.get("code", 400)

    return jsonify(result)


@api_bp.route('/api/skins/vender-lote', methods=['POST'])
@login_required
def vender_lote_skins(current_user):
    """Vende múltiplas skins de uma só vez (ex: modal multi-unbox)."""
    data = request.get_json(silent=True) or {}
    item_uids = data.get("uids", [])
    sell_type = data.get("sellType", "bot")

    if not isinstance(item_uids, list) or len(item_uids) == 0:
        return jsonify({"error": "Lista de skins vazia.", "code": 400}), 400

    result = GameService.sell_batch(current_user["id"], item_uids, sell_type)
    if "error" in result:
        return jsonify(result), result.get("code", 400)

    return jsonify(result)


@api_bp.route('/api/minigame/recompensa', methods=['POST'])
@login_required
def recompensa_minigame(current_user):
    """Valida e credita a recompensa do mini-game de reflexo no saldo do MongoDB."""
    data = request.get_json(silent=True) or {}
    difficulty = data.get("difficulty", "easy")

    result = GameService.claim_minigame_reward(current_user["id"], difficulty)
    if "error" in result:
        return jsonify(result), result.get("code", 400)

    return jsonify(result)


@api_bp.route('/api/slots/apostar', methods=['POST'])
@login_required
def apostar_slots(current_user):
    """Executa aposta na Roleta/Slots no servidor."""
    data = request.get_json(silent=True) or {}
    bet = data.get("bet")

    try:
        bet_amount = float(bet)
    except (TypeError, ValueError):
        return jsonify({"error": "Valor de aposta inválido.", "code": 400}), 400

    result = GameService.spin_slots(current_user["id"], bet_amount)
    if "error" in result:
        return jsonify(result), result.get("code", 400)

    return jsonify(result)
