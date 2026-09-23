import os
import json
import uuid
from datetime import datetime, timezone
from bson import ObjectId
from pymongo import MongoClient, ReturnDocument
from config import Config

# ==============================================================================
# CAMADA DE BANCO DE DADOS RESILIENTE (MONGODB + FALLBACK LOCAL)
# ==============================================================================

class Database:
    _client = None
    _db = None
    _use_local_fallback = False
    _fallback_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')

    @classmethod
    def get_db(cls):
        if cls._db is None and not cls._use_local_fallback:
            try:
                # Tenta conectar ao MongoDB com timeout rápido para não travar
                cls._client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=2000)
                cls._client.admin.command('ping')
                cls._db = cls._client.get_database()
                print(f"[OK - MongoDB] Conectado com sucesso ao banco: {cls._db.name}")
                cls._db.users.create_index("githubId", unique=True, sparse=True)
                cls._db.users.create_index("username", unique=True, sparse=True)
            except Exception as e:
                print(f"[AVISO - MongoDB] Servidor MongoDB offline ({type(e).__name__}).")
                print(f"[INFO - Modo Resiliente] Utilizando persistência local em: {cls._fallback_file}")
                cls._use_local_fallback = True
                cls._db = None
        return cls._db

    @classmethod
    def is_fallback(cls):
        cls.get_db()
        return cls._use_local_fallback

    @classmethod
    def _read_fallback(cls):
        os.makedirs(os.path.dirname(cls._fallback_file), exist_ok=True)
        if not os.path.exists(cls._fallback_file):
            return {}
        try:
            with open(cls._fallback_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    @classmethod
    def _write_fallback(cls, data):
        os.makedirs(os.path.dirname(cls._fallback_file), exist_ok=True)
        with open(cls._fallback_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


class UserModel:
    @staticmethod
    def format_user_doc(user):
        if not user:
            return None
        
        user_id = str(user.get("_id") or user.get("id"))
        return {
            "id": user_id,
            "githubId": user.get("githubId"),
            "username": user.get("username", "Jogador"),
            "nome": user.get("nome", user.get("username", "Jogador")),
            "avatar": user.get("avatar", ""),
            "dinheiro": round(float(user.get("dinheiro", 0.0)), 2),
            "inventario": user.get("inventario", []),
            "criadoEm": user.get("criadoEm").isoformat() if isinstance(user.get("criadoEm"), datetime) else str(user.get("criadoEm", "")),
            "atualizadoEm": user.get("atualizadoEm").isoformat() if isinstance(user.get("atualizadoEm"), datetime) else str(user.get("atualizadoEm", ""))
        }

    @classmethod
    def get_or_create_user(cls, github_profile):
        db = Database.get_db()
        github_id = github_profile.get("id")
        username = github_profile.get("login", "Jogador")
        name = github_profile.get("name") or username
        avatar = github_profile.get("avatar_url") or f"https://avatars.githubusercontent.com/{username}"
        now = datetime.now(timezone.utc)

        # 1. MongoDB Ativo
        if db is not None:
            coll = db.users
            query = {"githubId": github_id} if github_id else {"username": username}
            existing = coll.find_one(query)
            
            if existing:
                coll.update_one(
                    {"_id": existing["_id"]},
                    {
                        "$set": {
                            "username": username,
                            "nome": name,
                            "avatar": avatar,
                            "atualizadoEm": now
                        }
                    }
                )
                updated = coll.find_one({"_id": existing["_id"]})
                return cls.format_user_doc(updated)

            new_user = {
                "githubId": github_id,
                "username": username,
                "nome": name,
                "avatar": avatar,
                "dinheiro": round(float(Config.INITIAL_BALANCE), 2),
                "inventario": [],
                "criadoEm": now,
                "atualizadoEm": now
            }
            res = coll.insert_one(new_user)
            new_user["_id"] = res.inserted_id
            return cls.format_user_doc(new_user)

        # 2. Fallback Local
        users = Database._read_fallback()
        found_key = None
        for uid, u in users.items():
            if (github_id and u.get("githubId") == github_id) or (u.get("username") == username):
                found_key = uid
                break

        if found_key:
            users[found_key]["username"] = username
            users[found_key]["nome"] = name
            users[found_key]["avatar"] = avatar
            users[found_key]["atualizadoEm"] = now.isoformat()
            Database._write_fallback(users)
            return cls.format_user_doc(users[found_key])

        new_id = str(uuid.uuid4())
        new_user = {
            "id": new_id,
            "_id": new_id,
            "githubId": github_id,
            "username": username,
            "nome": name,
            "avatar": avatar,
            "dinheiro": round(float(Config.INITIAL_BALANCE), 2),
            "inventario": [],
            "criadoEm": now.isoformat(),
            "atualizadoEm": now.isoformat()
        }
        users[new_id] = new_user
        Database._write_fallback(users)
        return cls.format_user_doc(new_user)

    @classmethod
    def get_by_id(cls, user_id):
        if not user_id:
            return None
        db = Database.get_db()

        if db is not None:
            try:
                doc = db.users.find_one({"_id": ObjectId(user_id)})
                return cls.format_user_doc(doc)
            except Exception:
                doc = db.users.find_one({"_id": user_id})
                return cls.format_user_doc(doc)

        # Fallback
        users = Database._read_fallback()
        user = users.get(str(user_id))
        return cls.format_user_doc(user)

    @classmethod
    def deduct_balance(cls, user_id, amount):
        amount = round(float(amount), 2)
        if amount <= 0:
            return cls.get_by_id(user_id)

        db = Database.get_db()
        now = datetime.now(timezone.utc)

        if db is not None:
            try:
                oid = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
                updated = db.users.find_one_and_update(
                    {"_id": oid, "dinheiro": {"$gte": amount}},
                    {"$inc": {"dinheiro": -amount}, "$set": {"atualizadoEm": now}},
                    return_document=ReturnDocument.AFTER
                )
                return cls.format_user_doc(updated)
            except Exception as e:
                print(f"[Erro deduct_balance MongoDB] {e}")

        # Fallback
        users = Database._read_fallback()
        u = users.get(str(user_id))
        if not u or u.get("dinheiro", 0.0) < amount:
            return None
        u["dinheiro"] = round(u["dinheiro"] - amount, 2)
        u["atualizadoEm"] = now.isoformat()
        Database._write_fallback(users)
        return cls.format_user_doc(u)

    @classmethod
    def add_balance(cls, user_id, amount):
        amount = round(float(amount), 2)
        if amount <= 0:
            return cls.get_by_id(user_id)

        db = Database.get_db()
        now = datetime.now(timezone.utc)

        if db is not None:
            try:
                oid = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
                updated = db.users.find_one_and_update(
                    {"_id": oid},
                    {"$inc": {"dinheiro": amount}, "$set": {"atualizadoEm": now}},
                    return_document=ReturnDocument.AFTER
                )
                return cls.format_user_doc(updated)
            except Exception as e:
                print(f"[Erro add_balance MongoDB] {e}")

        # Fallback
        users = Database._read_fallback()
        u = users.get(str(user_id))
        if not u:
            return None
        u["dinheiro"] = round(u.get("dinheiro", 0.0) + amount, 2)
        u["atualizadoEm"] = now.isoformat()
        Database._write_fallback(users)
        return cls.format_user_doc(u)

    @classmethod
    def add_skins_to_inventory(cls, user_id, items):
        if not items:
            return cls.get_by_id(user_id)

        db = Database.get_db()
        now = datetime.now(timezone.utc)

        if db is not None:
            try:
                oid = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
                updated = db.users.find_one_and_update(
                    {"_id": oid},
                    {"$push": {"inventario": {"$each": items}}, "$set": {"atualizadoEm": now}},
                    return_document=ReturnDocument.AFTER
                )
                return cls.format_user_doc(updated)
            except Exception as e:
                print(f"[Erro add_skins MongoDB] {e}")

        # Fallback
        users = Database._read_fallback()
        u = users.get(str(user_id))
        if not u:
            return None
        if "inventario" not in u:
            u["inventario"] = []
        u["inventario"].extend(items)
        u["atualizadoEm"] = now.isoformat()
        Database._write_fallback(users)
        return cls.format_user_doc(u)

    @classmethod
    def remove_skin_from_inventory(cls, user_id, item_uid):
        db = Database.get_db()
        now = datetime.now(timezone.utc)

        if db is not None:
            try:
                oid = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
                user = db.users.find_one({"_id": oid})
                if not user:
                    return None
                found_item = next((item for item in user.get("inventario", []) if item.get("uid") == item_uid), None)
                if not found_item:
                    return None
                db.users.update_one(
                    {"_id": oid},
                    {"$pull": {"inventario": {"uid": item_uid}}, "$set": {"atualizadoEm": now}}
                )
                return found_item
            except Exception as e:
                print(f"[Erro remove_skin MongoDB] {e}")

        # Fallback
        users = Database._read_fallback()
        u = users.get(str(user_id))
        if not u:
            return None
        inv = u.get("inventario", [])
        found_item = next((item for item in inv if item.get("uid") == item_uid), None)
        if not found_item:
            return None
        u["inventario"] = [item for item in inv if item.get("uid") != item_uid]
        u["atualizadoEm"] = now.isoformat()
        Database._write_fallback(users)
        return found_item

    @classmethod
    def remove_skins_from_inventory(cls, user_id, item_uids):
        db = Database.get_db()
        now = datetime.now(timezone.utc)
        uids_set = set(item_uids)

        if db is not None:
            try:
                oid = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
                user = db.users.find_one({"_id": oid})
                if not user:
                    return []
                found_items = [item for item in user.get("inventario", []) if item.get("uid") in uids_set]
                if not found_items:
                    return []
                db.users.update_one(
                    {"_id": oid},
                    {"$pull": {"inventario": {"uid": {"$in": list(uids_set)}}}, "$set": {"atualizadoEm": now}}
                )
                return found_items
            except Exception as e:
                print(f"[Erro remove_skins MongoDB] {e}")

        # Fallback
        users = Database._read_fallback()
        u = users.get(str(user_id))
        if not u:
            return []
        inv = u.get("inventario", [])
        found_items = [item for item in inv if item.get("uid") in uids_set]
        if not found_items:
            return []
        u["inventario"] = [item for item in inv if item.get("uid") not in uids_set]
        u["atualizadoEm"] = now.isoformat()
        Database._write_fallback(users)
        return found_items
