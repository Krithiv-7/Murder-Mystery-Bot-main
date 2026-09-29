import json
import logging
import os
import sqlite3
import time

try:
    import pymongo
except ImportError:  # Mongo is an optional extra, not the default backend.
    pymongo = None

logger = logging.getLogger("mmb.storage")

cache = {}
printCacheHitsAndMisses = False
_repo = None
_backend = "json"

# Module-level globals initialized to safe defaults
localStorage = True
data = {}
collection = None


BASE_DIR = os.path.dirname(__file__)

# Disaster recovery (SQLite mirror) configuration
enableSQLiteBackup = True
_sqlite_conn = None
_sqlite_path = os.path.join(BASE_DIR, "disaster_backup.sqlite")

def _sqlite_init():
    global _sqlite_conn
    if not enableSQLiteBackup:
        return
    try:
        _sqlite_conn = sqlite3.connect(_sqlite_path, check_same_thread=False)
        _sqlite_conn.execute(
            "CREATE TABLE IF NOT EXISTS guild_kv (guild_id TEXT NOT NULL, key TEXT NOT NULL, value_json TEXT, PRIMARY KEY (guild_id, key))"
        )
        _sqlite_conn.execute(
            "CREATE TABLE IF NOT EXISTS member_kv (guild_id TEXT NOT NULL, member_id TEXT NOT NULL, key TEXT NOT NULL, value_json TEXT, PRIMARY KEY (guild_id, member_id, key))"
        )
        _sqlite_conn.execute(
            "CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)"
        )
        _sqlite_conn.commit()
    except Exception as e:
        logger.info(f"[dataStorage] WARNING: Could not initialize SQLite backup: {e}")

def _sqlite_upsert_guild(guild_id: str, key: str, value):
    if not enableSQLiteBackup or _sqlite_conn is None:
        return
    try:
        _sqlite_conn.execute(
            "INSERT INTO guild_kv(guild_id, key, value_json) VALUES(?, ?, ?) ON CONFLICT(guild_id, key) DO UPDATE SET value_json=excluded.value_json",
            (str(guild_id), str(key), json.dumps(value, ensure_ascii=False))
        )
        _sqlite_conn.commit()
    except Exception as e:
        logger.info(f"[dataStorage] WARNING: SQLite upsert guild failed: {e}")

def _sqlite_delete_guild(guild_id: str, key: str):
    if not enableSQLiteBackup or _sqlite_conn is None:
        return
    try:
        _sqlite_conn.execute("DELETE FROM guild_kv WHERE guild_id=? AND key=?", (str(guild_id), str(key)))
        _sqlite_conn.commit()
    except Exception as e:
        logger.info(f"[dataStorage] WARNING: SQLite delete guild failed: {e}")

def _sqlite_upsert_member(guild_id: str, member_id: str, key: str, value):
    if not enableSQLiteBackup or _sqlite_conn is None:
        return
    try:
        _sqlite_conn.execute(
            "INSERT INTO member_kv(guild_id, member_id, key, value_json) VALUES(?, ?, ?, ?) ON CONFLICT(guild_id, member_id, key) DO UPDATE SET value_json=excluded.value_json",
            (str(guild_id), str(member_id), str(key), json.dumps(value, ensure_ascii=False))
        )
        _sqlite_conn.commit()
    except Exception as e:
        logger.info(f"[dataStorage] WARNING: SQLite upsert member failed: {e}")

def _sqlite_delete_member(guild_id: str, member_id: str, key: str):
    if not enableSQLiteBackup or _sqlite_conn is None:
        return
    try:
        _sqlite_conn.execute("DELETE FROM member_kv WHERE guild_id=? AND member_id=? AND key=?", (str(guild_id), str(member_id), str(key)))
        _sqlite_conn.commit()
    except Exception as e:
        logger.info(f"[dataStorage] WARNING: SQLite delete member failed: {e}")


def storage_status() -> str:
    if _repo is not None:
        return "ok" if _repo.ping() else "error"
    if _backend == "mongo":
        return "mongo" if collection is not None else "error"
    return "json"


def flush():
    if _repo is not None:
        _repo.flush()
        return
    if localStorage:
        updateData()


def initializeDataStorage(local):
    global localStorage, data, collection, _repo, _backend
    from core.config import json_data_path, sqlite_path, storage_backend

    localStorage = local
    _backend = storage_backend()
    if _backend != "sqlite":
        localStorage = _backend != "mongo"
    if _backend == "sqlite":
        localStorage = False
        _repo = _open_sqlite(sqlite_path(), json_data_path())
        logger.info("Connected to SQLite at %s", sqlite_path())
        return
    # Initialize SQLite disaster-recovery mirror for the legacy backends.
    _sqlite_init()
    if not localStorage:
        logger.info("Connecting to MongoDB")
        if pymongo is None:
            raise RuntimeError(
                "MongoDB storage was requested but pymongo is not installed. "
                "Install the mongo extra or set MMB_STORAGE=sqlite."
            )
        try:
            mongoLoginInfoFile = open(os.path.join(BASE_DIR, "mongoDBLoginInfo.txt"), "r", encoding="utf-8")
        except FileNotFoundError:
            logger.error("mongoDBLoginInfo.txt was not found")
            raise
        try:
            cluster = pymongo.MongoClient(mongoLoginInfoFile.read())
        except Exception:
            logger.exception("Failed to connect to MongoDB")
            raise

        mongoLoginInfoFile.close()
        db = cluster["discord"]
        collection = db["murder-mystery"]
        logger.info("[dataStorage] Connected to mongoDB, fetching cache...")

        cursor = collection.find({})
        for document in cursor:
            finalDic = document.copy()
            for key in document:
                if key == "_id":
                    finalDic.pop("_id")
                    break
            cache[document["_id"]] = finalDic
        # logger.info(cache)
        logger.info("[dataStorage] Successfully fetched cache!")

    if localStorage:
        logger.info("[dataStorage] LocalStorage is on, mongoDB will not be used.")
        # Ensure data file exists and load it
        try:
            with open(os.path.join(BASE_DIR, "data.json"), "r", encoding="utf-8") as dataFile:
                data = json.load(dataFile)
            logger.info("[dataStorage] Data loaded, making backup...")
        except FileNotFoundError:
            data = {}
            with open(os.path.join(BASE_DIR, "data.json"), "w", encoding="utf-8") as dataFile:
                json.dump(data, dataFile, ensure_ascii=False, indent=2)
            logger.info("[dataStorage] data.json not found; created a new one.")
        except json.JSONDecodeError:
            # Handle corrupted JSON by backing it up and starting fresh
            corrupted_path = os.path.join(BASE_DIR, "data.json.corrupt")
            try:
                os.replace(os.path.join(BASE_DIR, "data.json"), corrupted_path)
                logger.info(f"[dataStorage] WARNING: data.json corrupt; backed up to {corrupted_path} and recreated.")
            except Exception:
                logger.info("[dataStorage] WARNING: data.json corrupt and could not be backed up; recreating.")
            data = {}
            with open(os.path.join(BASE_DIR, "data.json"), "w", encoding="utf-8") as dataFile:
                json.dump(data, dataFile, ensure_ascii=False, indent=2)

        # Make backup folder if missing
        try:
            os.makedirs(os.path.join(BASE_DIR, "dataBackup"), exist_ok=True)
        except Exception as e:
            logger.info(f"[dataStorage] WARNING: Could not ensure backup folder: {e}")

        # Read backup number safely
        num = 0
        try:
            with open(os.path.join(BASE_DIR, "backupNum"), "r", encoding="utf-8") as f:
                num = int(f.read().strip() or "0")
        except (FileNotFoundError, ValueError):
            try:
                with open(os.path.join(BASE_DIR, "backupNum"), "w", encoding="utf-8") as f:
                    f.write("0")
                num = 0
            except Exception as e:
                logger.info(f"[dataStorage] WARNING: Could not initialize backupNum: {e}")

        # Write backup file
        try:
            with open(os.path.join(BASE_DIR, "dataBackup", f"backup{num}.json"), "w", encoding="utf-8") as backupFile:
                json.dump(data, backupFile, ensure_ascii=False, indent=2)
            with open(os.path.join(BASE_DIR, "backupNum"), "w", encoding="utf-8") as f:
                f.write(str(num + 1))
            logger.info(f"[dataStorage] A data backup has been made to dataBackup/backup{num}.json!")
        except Exception as e:
            logger.info(f"[dataStorage] WARNING: Failed to write backup: {e}")


def reloadCache():
    logger.info("[dataStorage] Reloading cache...")
    cursor = collection.find({})
    for document in cursor:
        finalDic = document.copy()
        for key in document:
            if key == "_id":
                finalDic.pop("_id")
                break
        cache[document["_id"]] = finalDic
    # logger.info(cache)
    logger.info("[dataStorage] Successfully fetched cache!")


def _open_sqlite(path, legacy_json):
    from storage.sqlite_store import SqliteStore

    store = SqliteStore(path)
    store.migrate()
    if store.guild_count() == 0 and legacy_json.exists():
        payload = json.loads(legacy_json.read_text(encoding="utf-8") or "{}")
        if isinstance(payload, dict) and payload:
            count = store.import_legacy_document(payload)
            logger.info("Imported %s guilds from data.json", count)
    return store


def _guild_id(guild):
    return guild.id


def _member_ids(member):
    return member.guild.id, member.id


def setPlayerData(member, key, **kwargs):
    if _repo is not None:
        guild_id, member_id = _member_ids(member)
        _repo.set_player(
            guild_id,
            member_id,
            key,
            value=kwargs.get("value"),
            increase=kwargs.get("increase"),
        )
        return
    if localStorage:
        if f"{member.guild.id}" not in data:
            data[f"{member.guild.id}"] = {"members": {}}
        if f"{member.id}" not in data[f"{member.guild.id}"]["members"]:
            data[f"{member.guild.id}"]["members"][f"{member.id}"] = {}

        if "increase" in kwargs:
            if key in data[f"{member.guild.id}"]["members"][f"{member.id}"]:
                data[f"{member.guild.id}"]["members"][f"{member.id}"][key] += kwargs["increase"]
            else:
                data[f"{member.guild.id}"]["members"][f"{member.id}"][key] = kwargs["increase"]

        if "value" in kwargs:
            data[f"{member.guild.id}"]["members"][f"{member.id}"][key] = kwargs["value"]

        updateData()
        # Mirror to SQLite backup
        try:
            val = data[f"{member.guild.id}"]["members"][f"{member.id}"][key]
            _sqlite_upsert_member(member.guild.id, member.id, key, val)
        except Exception:
            pass

    else:
        if getLen(collection.find({"_id": member.guild.id})) == 0:
            collection.insert_one({"_id": member.guild.id, "members": {}})
            cache[member.guild.id] = {"members": {}}

        members = collection.find_one({"_id": member.guild.id})["members"]
        if f"{member.id}" not in members:
            members[f"{member.id}"] = {}
            collection.update_one({"_id": member.guild.id}, {"$set": {"members": members}})
            cache[member.guild.id]["members"] = members

        if "increase" in kwargs:
            if key in members[f"{member.id}"]:
                members[f"{member.id}"][key] += kwargs["increase"]
            else:
                members[f"{member.id}"][key] = kwargs["increase"]

        if "value" in kwargs:
            members[f"{member.id}"][key] = kwargs["value"]

        collection.update_one({"_id": member.guild.id}, {"$set": {"members": members}})
        cache[member.guild.id]["members"] = members
        # Mirror to SQLite backup
        try:
            val = members[f"{member.id}"][key]
            _sqlite_upsert_member(member.guild.id, member.id, key, val)
        except Exception:
            pass


def getPlayerData(member, key, **kwargs):
    if _repo is not None:
        guild_id, member_id = _member_ids(member)
        return _repo.get_player(guild_id, member_id, key, **kwargs)
    if localStorage:
        if f"{member.guild.id}" not in data:
            data[f"{member.guild.id}"] = {"members": {}}
        if f"{member.id}" not in data[f"{member.guild.id}"]["members"]:
            data[f"{member.guild.id}"]["members"][f"{member.id}"] = {}

        if key in data[f"{member.guild.id}"]["members"][f"{member.id}"]:
            return data[f"{member.guild.id}"]["members"][f"{member.id}"][key]
        else:
            if "default" in kwargs:
                data[f"{member.guild.id}"]["members"][f"{member.id}"][key] = kwargs["default"]
                updateData()
                return data[f"{member.guild.id}"]["members"][f"{member.id}"][key]
            else:
                return None
    else:
        # try finding data in cache before accessing database
        if member.guild.id in cache:
            if f"{member.id}" in cache[member.guild.id]["members"]:
                if key in cache[member.guild.id]["members"][f"{member.id}"]:
                    if printCacheHitsAndMisses:
                        logger.info("[dataStorage] Cache hit!")
                    return cache[member.guild.id]["members"][f"{member.id}"][key]

        # data not found in cache, so accessing database
        if printCacheHitsAndMisses:
            logger.info("[dataStorage] Cache miss :(")
        if getLen(collection.find({"_id": member.guild.id})) == 0:
            collection.insert_one({"_id": member.guild.id, "members": {}})
            cache[member.guild.id] = {"members": {}}

        members = collection.find_one({"_id": member.guild.id})["members"]
        if f"{member.id}" not in members:
            members[f"{member.id}"] = {}
            collection.update_one({"_id": member.guild.id}, {"$set": {"members": members}})
            cache[member.guild.id]["members"] = members

        if key in members[f"{member.id}"]:
            return members[f"{member.id}"][key]
        else:
            if "default" in kwargs:
                members[f"{member.id}"][key] = kwargs["default"]
                collection.update_one({"_id": member.guild.id}, {"$set": {"members": members}})
                cache[member.guild.id]["members"] = members
                return members[f"{member.id}"][key]
            else:
                return None


def deletePlayerData(member, key):
    if _repo is not None:
        guild_id, member_id = _member_ids(member)
        return _repo.delete_player(guild_id, member_id, key)
    if localStorage:
        if f"{member.guild.id}" not in data:
            data[f"{member.guild.id}"] = {"members": {}}
        if f"{member.id}" not in data[f"{member.guild.id}"]["members"]:
            data[f"{member.guild.id}"]["members"][f"{member.id}"] = {}

        if key in data[f"{member.guild.id}"]["members"][f"{member.id}"]:
            d = data[f"{member.guild.id}"]["members"][f"{member.id}"].pop(key)
            updateData()
            # Mirror delete to SQLite backup
            _sqlite_delete_member(member.guild.id, member.id, key)
            return d
        else:
            return None

    else:
        if getLen(collection.find({"_id": member.guild.id})) == 0:
            collection.insert_one({"_id": member.guild.id, "members": {}})
            cache[member.guild.id] = {"members": {}}

        members = collection.find_one({"_id": member.guild.id})["members"]
        if f"{member.id}" not in members:
            members[f"{member.id}"] = {}
            collection.update_one({"_id": member.guild.id}, {"$set": {"members": members}})
            cache[member.guild.id]["members"] = members

        if key in members[f"{member.id}"]:
            d = members[f"{member.id}"].pop(key)
            collection.update_one({"_id": member.guild.id}, {"$set": {"members": members}})
            cache[member.guild.id]["members"] = members
            _sqlite_delete_member(member.guild.id, member.id, key)
            return d
        else:
            return None


def setGuildData(guild, key, **kwargs):
    if _repo is not None:
        _repo.set_guild(
            _guild_id(guild),
            key,
            value=kwargs.get("value"),
            increase=kwargs.get("increase"),
        )
        return
    if localStorage:
        if f"{guild.id}" not in data:
            data[f"{guild.id}"] = {"members": {}}

        if "increase" in kwargs:
            if key in data[f"{guild.id}"]:
                data[f"{guild.id}"][key] = data[f"{guild.id}"][key] + kwargs["increase"]
            else:
                data[f"{guild.id}"][key] = kwargs["increase"]
            updateData()
            _sqlite_upsert_guild(guild.id, key, data[f"{guild.id}"][key])

        if "value" in kwargs:
            data[f"{guild.id}"][key] = kwargs["value"]
            updateData()
            _sqlite_upsert_guild(guild.id, key, data[f"{guild.id}"][key])

    else:
        if getLen(collection.find({"_id": guild.id})) == 0:
            collection.insert_one({"_id": guild.id, "members": {}})
            cache[guild.id] = {"members": {}}

        if "increase" in kwargs:
            collection.update_one({"_id": guild.id}, {"$inc": {key: kwargs["increase"]}})
            cache[guild.id][key] += kwargs["increase"]
            _sqlite_upsert_guild(guild.id, key, cache[guild.id][key])

        if "value" in kwargs:
            collection.update_one({"_id": guild.id}, {"$set": {key: kwargs["value"]}})
            cache[guild.id][key] = kwargs["value"]
            _sqlite_upsert_guild(guild.id, key, kwargs["value"])


def getGuildData(guild, key, **kwargs):
    if _repo is not None:
        return _repo.get_guild(_guild_id(guild), key, **kwargs)
    if localStorage:
        # Access local JSON data directly; do not rely on cache when using localStorage
        if f"{guild.id}" not in data:
            data[f"{guild.id}"] = {"members": {}}

        if key in data[f"{guild.id}"]:
            return data[f"{guild.id}"][key]
        elif "default" in kwargs:
            data[f"{guild.id}"][key] = kwargs["default"]
            updateData()
            return data[f"{guild.id}"][key]
        else:
            return None
    else:
        if getLen(collection.find({"_id": guild.id})) == 0:
            collection.insert_one({"_id": guild.id, "members": {}})
            cache[guild.id] = {"members": {}}

        guildData = collection.find_one({"_id": guild.id})
        if key in guildData:
            return guildData[key]
        elif "default" in kwargs:
            collection.update_one({"_id": guild.id}, {"$set": {key: kwargs["default"]}})
            cache[guild.id][key] = kwargs["default"]
            return kwargs["default"]
        else:
            return None


def deleteGuildData(guild, key):
    if _repo is not None:
        return _repo.delete_guild(_guild_id(guild), key)
    if localStorage:
        if f"{guild.id}" not in data:
            data[f"{guild.id}"] = {"members": {}}

        if key in data[f"{guild.id}"]:
            d = data[f"{guild.id}"].pop(key)
            updateData()
            _sqlite_delete_guild(guild.id, key)
            return d
        else:
            return None

    else:
        d = collection.find_one({"_id": f"{guild.id}"})[key]
        collection.update_one({"_id": f"{guild.id}"}, {"$unset": {key: ""}})
        if key in cache[guild.id]:
            cache[guild.id].pop(key)
        _sqlite_delete_guild(guild.id, key)
        return d


def getAllGuilds():
    if _repo is not None:
        return _repo.all_guilds()
    return collection.find({})


def updateData():
    if localStorage:
        # Atomic write to avoid corrupting data.json
        temp_path = os.path.join(BASE_DIR, "data.json.tmp")
        final_path = os.path.join(BASE_DIR, "data.json")
        with open(temp_path, "w", encoding="utf-8") as dataFile:
            json.dump(data, dataFile, ensure_ascii=False, indent=2)
        os.replace(temp_path, final_path)
        # Record last snapshot time in SQLite meta
        try:
            if enableSQLiteBackup and _sqlite_conn is not None:
                _sqlite_conn.execute("INSERT INTO meta(k, v) VALUES('last_snapshot', ?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (str(int(time.time())),))
                _sqlite_conn.commit()
        except Exception:
            pass


def getLen(x):
    l = 0
    for v in x:
        l += 1
    return l
