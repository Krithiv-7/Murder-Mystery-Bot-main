import pymongo
import json
import os

cache = {}
printCacheHitsAndMisses = False


BASE_DIR = os.path.dirname(__file__)


def initializeDataStorage(local):
    global localStorage, data, cluser, collection
    localStorage = local
    if not localStorage:
        print("[dataStorage] Connecting to mongoDB...")
        try:
            mongoLoginInfoFile = open(os.path.join(BASE_DIR, "mongoDBLoginInfo.txt"), "r", encoding="utf-8")
        except FileNotFoundError:
            print(
                "[dataStorage] File mongoDBLoginInfo.txt was not found! If you don't want to use mongoDB for data storage, set localStorage to True in bot.py to use json instead.")
        try:
            cluster = pymongo.MongoClient(mongoLoginInfoFile.read())
        except:
            print(
                "[dataStorage] Failed to connect to the mongoDB database. Consider changing localStorage to True in bot.py to use json instead. Saving functions will not work and errors will probably occur")

        mongoLoginInfoFile.close()
        db = cluster["discord"]
        collection = db["murder-mystery"]
        print("[dataStorage] Connected to mongoDB, fetching cache...")

        cursor = collection.find({})
        for document in cursor:
            finalDic = document.copy()
            for key in document:
                if key == "_id":
                    finalDic.pop("_id")
                    break
            cache[document["_id"]] = finalDic
        # print(cache)
        print("[dataStorage] Successfully fetched cache!")

    if localStorage:
        print("[dataStorage] LocalStorage is on, mongoDB will not be used.")
        # Ensure data file exists and load it
        try:
            with open(os.path.join(BASE_DIR, "data.json"), "r", encoding="utf-8") as dataFile:
                data = json.load(dataFile)
            print("[dataStorage] Data loaded, making backup...")
        except FileNotFoundError:
            data = {}
            with open(os.path.join(BASE_DIR, "data.json"), "w", encoding="utf-8") as dataFile:
                json.dump(data, dataFile, ensure_ascii=False, indent=2)
            print("[dataStorage] data.json not found; created a new one.")
        except json.JSONDecodeError:
            # Handle corrupted JSON by backing it up and starting fresh
            corrupted_path = os.path.join(BASE_DIR, "data.json.corrupt")
            try:
                os.replace(os.path.join(BASE_DIR, "data.json"), corrupted_path)
                print(f"[dataStorage] WARNING: data.json corrupt; backed up to {corrupted_path} and recreated.")
            except Exception:
                print("[dataStorage] WARNING: data.json corrupt and could not be backed up; recreating.")
            data = {}
            with open(os.path.join(BASE_DIR, "data.json"), "w", encoding="utf-8") as dataFile:
                json.dump(data, dataFile, ensure_ascii=False, indent=2)

        # Make backup folder if missing
        try:
            os.makedirs(os.path.join(BASE_DIR, "dataBackup"), exist_ok=True)
        except Exception as e:
            print(f"[dataStorage] WARNING: Could not ensure backup folder: {e}")

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
                print(f"[dataStorage] WARNING: Could not initialize backupNum: {e}")

        # Write backup file
        try:
            with open(os.path.join(BASE_DIR, "dataBackup", f"backup{num}.json"), "w", encoding="utf-8") as backupFile:
                json.dump(data, backupFile, ensure_ascii=False, indent=2)
            with open(os.path.join(BASE_DIR, "backupNum"), "w", encoding="utf-8") as f:
                f.write(str(num + 1))
            print(f"[dataStorage] A data backup has been made to dataBackup/backup{num}.json!")
        except Exception as e:
            print(f"[dataStorage] WARNING: Failed to write backup: {e}")


def reloadCache():
    print("[dataStorage] Reloading cache...")
    cursor = collection.find({})
    for document in cursor:
        finalDic = document.copy()
        for key in document:
            if key == "_id":
                finalDic.pop("_id")
                break
        cache[document["_id"]] = finalDic
    # print(cache)
    print("[dataStorage] Successfully fetched cache!")


def setPlayerData(member, key, **kwargs):
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


def getPlayerData(member, key, **kwargs):
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
                        print("[dataStorage] Cache hit!")
                    return cache[member.guild.id]["members"][f"{member.id}"][key]

        # data not found in cache, so accessing database
        if printCacheHitsAndMisses:
            print("[dataStorage] Cache miss :(")
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
    if localStorage:
        if f"{member.guild.id}" not in data:
            data[f"{member.guild.id}"] = {"members": {}}
        if f"{member.id}" not in data[f"{member.guild.id}"]["members"]:
            data[f"{member.guild.id}"]["members"][f"{member.id}"] = {}

        if key in data[f"{member.guild.id}"]["members"][f"{member.id}"]:
            d = data[f"{member.guild.id}"]["members"][f"{member.id}"].pop(key)
            updateData()
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
            return d
        else:
            return None


def setGuildData(guild, key, **kwargs):
    if localStorage:
        if f"{guild.id}" not in data:
            data[f"{guild.id}"] = {"members": {}}

        if "increase" in kwargs:
            if key in data[f"{guild.id}"]:
                data[f"{guild.id}"][key] = data[f"{guild.id}"][key] + kwargs["increase"]
            else:
                data[f"{guild.id}"][key] = kwargs["increase"]
            updateData()

        if "value" in kwargs:
            data[f"{guild.id}"][key] = kwargs["value"]
            updateData()

    else:
        if getLen(collection.find({"_id": guild.id})) == 0:
            collection.insert_one({"_id": guild.id, "members": {}})
            cache[guild.id] = {"members": {}}

        if "increase" in kwargs:
            collection.update_one({"_id": guild.id}, {"$inc": {key: kwargs["increase"]}})
            cache[guild.id][key] += kwargs["increase"]

        if "value" in kwargs:
            collection.update_one({"_id": guild.id}, {"$set": {key: kwargs["value"]}})
            cache[guild.id][key] = kwargs["value"]


def getGuildData(guild, key, **kwargs):
    if localStorage:
        # try finding data in cache before accessing database
        if guild.id in cache:
            if key in cache[guild.id]:
                if printCacheHitsAndMisses:
                    print("[dataStorage] Cache hit!")
                return cache[guild.id][key]

        # data not found in cache, so accessing database
        if printCacheHitsAndMisses:
            print("[dataStorage] Cache miss :(")
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
    if localStorage:
        if f"{guild.id}" not in data:
            data[f"{guild.id}"] = {"members": {}}

        if key in data[f"{guild.id}"]:
            d = data[f"{guild.id}"].pop(key)
            updateData()
            return d
        else:
            return None

    else:
        d = collection.find_one({"_id": f"{guild.id}"})[key]
        collection.update_one({"_id": f"{guild.id}"}, {"$unset": {key: ""}})
        if key in cache[guild.id]:
            cache[guild.id].pop(key)
        return d


def getAllGuilds():
    return collection.find({})


def updateData():
    if localStorage:
        # Atomic write to avoid corrupting data.json
        temp_path = os.path.join(BASE_DIR, "data.json.tmp")
        final_path = os.path.join(BASE_DIR, "data.json")
        with open(temp_path, "w", encoding="utf-8") as dataFile:
            json.dump(data, dataFile, ensure_ascii=False, indent=2)
        os.replace(temp_path, final_path)


def getLen(x):
    l = 0
    for v in x:
        l += 1
    return l
