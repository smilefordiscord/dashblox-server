import psycopg2
import time
from flask import Flask, request
import json
from json.encoder import JSONEncoder
from flask import Flask, request
import logging
import os
from psycopg2 import sql

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

secret = os.environ.get('secret')
conn = psycopg2.connect(
    host=os.environ.get('host2'),
    port="25060",
    dbname=os.environ.get('dbname2'),
    user=os.environ.get('user2'),
    password=os.environ.get('password2'),
)

def logInfo(address, method, route, status, extra):
    print('"' + method + ' ' + route + '" ' + str(status) + ' - ' + extra)

def logWarn(address, method, route, status, extra):
    print("\033[93m {}\033[00m".format('"' + method + ' ' + route + '" ' + str(status) + ' - ' + extra))

@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return "hello :)", 200
    else:
        return "Invalid method", 403

@app.route('/execute', methods=['POST'])
def execute():
    if request.method == 'POST':
        data = request.get_json()
        if data["secret"] != secret:
            return "Invalid secret", 403
        
        sql = data["request"]

        cursor = conn.cursor()
        try:
            returnLevels = {}
            try:
                cursor.execute(sql)
                returnLevels =  JSONEncoder().encode(cursor.fetchall())
            except:
                returnLevels = ""
            conn.commit()
            cursor.close()
            logInfo(request.remote_addr, "POST", "/execute", 200, sql)
            return returnLevels, 200
        except:
            conn.commit()
            cursor.close()
            logWarn(request.remote_addr, "POST", "/execute", 404, sql)
            return "Request failed", 404
    else:
        logWarn(request.remote_addr, "GET", "/execute", 403)
        return "Invalid method", 403

@app.route('/add-level', methods=['POST'])
def addlevel():
    if request.method == 'POST':
        cursor = conn.cursor()

        data = request.get_json()
        if data["secret"] != secret:
            cursor.close()
            return "Invalid secret", 403
        
        title = data["title"]
        desc = data["desc"]
        lvldata = data["data"]
        owner = data["owner"]
        difficulty = data["difficulty"]
        timestamp = data["timestamp"]
        cursor.execute("INSERT INTO public.levels (title, description, data, owner, difficulty, rating, timestamp) VALUES (%(title)s, %(desc)s, %(data)s, %(owner)s, %(difficulty)s, %(rating)s, %(timestamp)s);", {"title":title,"desc":desc,"data":lvldata,"owner":owner,"difficulty":difficulty,"rating":0,"timestamp":timestamp})
        
        conn.commit()
        cursor.close()
        logInfo(request.remote_addr, "POST", "/add-level", 200)
        return "OK", 200
    else:
        logWarn(request.remote_addr, "GET", "/add-level", 403)
        return "Invalid method", 403

    if request.method == 'POST':
        cursor = conn.cursor()

        data = request.get_json()
        if data["secret"] != secret:
            cursor.close()
            return "Invalid secret", 403
        
        owner = data["owner"]
        cursor.execute("SELECT * FROM public.rsitems WHERE owner = %(owner)s", {"owner":owner})
        conn.commit()
        
        returnedLvls = cursor.fetchall()
        if returnedLvls == None:
            cursor.execute()
            returnedLvls = []
        
        cursor.execute("SELECT * FROM public.rsplayerdata WHERE userId = %(owner)s", {"owner":owner})

        playerData = cursor.fetchone()
        if playerData == None:
            lastTime = time.time()
            cursor.execute("INSERT INTO public.rsplayerdata (userid, money, laston, opened) VALUES (%(userid)s, 0, %(laston)s, 0);", {"userid":owner, "laston":lastTime})
            conn.commit()
            playerData = {"userid":owner, "money": 0, "laston": lastTime, "opened": 0}
        
        returnData = [playerData, returnedLvls]
        
        cursor.close()
        logInfo(request.remote_addr, "POST", "/cs-get-player-data", 200)
        return json.dumps(returnData), 200
    else:
        logWarn(request.remote_addr, "GET", "/cs-get-player-data", 403)
        return "Invalid method", 403

@app.route('/db2-maxlvl', methods=['POST'])
def db2get():
    if request.method != 'POST':
        return "Invalid method", 403
    
    data = request.get_json()
    if data == None:
        return "Invalid", 403
    if data["secret"] != secret:
        return "Invalid secret", 403
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM public.levels ORDER BY id DESC LIMIT 1")
        returnLevels =  JSONEncoder().encode(cursor.fetchone())
        cursor.close()
        return returnLevels, 200
    except:
        cursor.close()
        return "Request failed", 404

@app.route('/db2-search', methods=['POST'])
def db2search():
    if request.method != 'POST':
        return "Invalid method", 403
    
    data = request.get_json()
    if data is None:
        return "Invalid", 403
    if data.get("secret") != secret:
        return "Invalid secret", 403
    
    searchText = f"%{data['searchText']}%"
    sortType = data["sortType"]
    max = data["max"]

    cursor = conn.cursor()
    try:
        if max > 0:
            query = sql.SQL("""
                SELECT * FROM public.levels 
                WHERE {0} < %s AND title ILIKE %s 
                ORDER BY {0} DESC 
                LIMIT 10
            """).format(sql.Identifier(sortType))
            
            cursor.execute(query, (max, searchText))
        else:
            query = sql.SQL("""
                SELECT * FROM public.levels 
                WHERE title ILIKE %s 
                ORDER BY {} DESC 
                LIMIT 10
            """).format(sql.Identifier(sortType))
            
            cursor.execute(query, (searchText,))

        returnLevels = JSONEncoder().encode(cursor.fetchall())
        cursor.close()
        print("DB2 Search: " + searchText)
        return returnLevels, 200
    except:
        cursor.close()
        return "Request failed", 404

print("Starting server")

app.run(host='0.0.0.0', port=8080)

# @app.route('/cs-add-item', methods=['POST'])
# def csAddItem():
#     if request.method == 'POST':
#         cursor = conn.cursor()

#         data = request.get_json()
#         if data["secret"] != secret:
#             cursor.close()
#             return "Invalid secret", 403
        
#         itemid = data["id"]
#         owner = data["owner"]
#         pattern = data["pattern"]
#         stattrak = data["st"]
#         wear = data["wear"]
#         cursor.execute("INSERT INTO public.rsitems (itemid, owner, pattern, stattrak, wear) VALUES (%(itemid)s, %(owner)s, %(pattern)s, %(stattrak)s, %(wear)s) RETURNING id;", {"itemid":itemid,"owner":owner,"pattern":pattern,"stattrak":stattrak,"wear":wear})
#         conn.commit()
        
#         returnedLvls = JSONEncoder().encode(cursor.fetchone())
        
#         cursor.close()
#         logInfo(request.remote_addr, "POST", "/cs-add-item", 200)
#         return returnedLvls, 200
#     else:
#         logWarn(request.remote_addr, "GET", "/cs-add-item", 403)
#         return "Invalid method", 403

# @app.route('/cs-add-items', methods=['POST'])
# def csAddItems():
#     if request.method == 'POST':
#         cursor = conn.cursor()

#         data = request.get_json()
#         if data["secret"] != secret:
#             cursor.close()
#             return "Invalid secret", 403
        
#         returnedLvls = []
        
#         amtOpened = 0

#         for item in data["items"]:
#             amtOpened += 1
#             itemid = item["id"]
#             owner = item["owner"]
#             pattern = item["pattern"]
#             stattrak = item["st"]
#             wear = item["wear"]
#             cursor.execute("INSERT INTO public.rsitems (itemid, owner, pattern, stattrak, wear) VALUES (%(itemid)s, %(owner)s, %(pattern)s, %(stattrak)s, %(wear)s) RETURNING id;", {"itemid":itemid,"owner":owner,"pattern":pattern,"stattrak":stattrak,"wear":wear})
#             conn.commit()
#             returnedLvls.append(cursor.fetchone()[0])
        
#         cursor.execute("UPDATE public.rsplayerdata SET money = money + %(money)s WHERE userid = %(userid)s", {"money": data["cost"], "userid": data["userid"]})
#         cursor.execute("UPDATE public.rsplayerdata SET opened = opened + %(opened)s WHERE userid = %(userid)s", {"opened": amtOpened, "userid": data["userid"]})
#         conn.commit()
        
#         cursor.close()
#         logInfo(request.remote_addr, "POST", "/cs-add-items", 200)
#         return returnedLvls, 200
#     else:
#         logWarn(request.remote_addr, "GET", "/cs-add-items", 403)
#         return "Invalid method", 403

# @app.route('/cs-delete-items', methods=['POST'])
# def csDeleteItems():
#     if request.method == 'POST':
#         cursor = conn.cursor()

#         data = request.get_json()
#         if data["secret"] != secret:
#             cursor.close()
#             return "Invalid secret", 403
        
#         idList = ""
#         for id in data["ids"]:
#             if idList == "":
#                 idList = str(id)
#             else:
#                 idList = idList + ", " + str(id)
        
#         idList = "DELETE FROM public.rsitems WHERE id IN (" + idList + ")"
#         cursor.execute(idList)
#         cursor.execute("UPDATE public.rsplayerdata SET money = money + %(money)s WHERE userid = %(userid)s", {"money": data["money"], "userid": data["userid"]})
#         conn.commit()

#         cursor.close()
#         logInfo(request.remote_addr, "POST", "/cs-delete-items", 200)
#         return "OK", 200
#     else:
#         logWarn(request.remote_addr, "GET", "/cs-delete-items", 403)
#         return "Invalid method", 403

# @app.route('/cs-trade-up', methods=['POST'])
# def csTradeUp():
#     if request.method == 'POST':
#         cursor = conn.cursor()

#         data = request.get_json()
#         if data["secret"] != secret:
#             cursor.close()
#             return "Invalid secret", 403
        
#         idList = ""
#         for id in data["take"]:
#             if idList == "":
#                 idList = str(id)
#             else:
#                 idList = idList + ", " + str(id)
        
#         idList = "DELETE FROM public.rsitems WHERE id IN (" + idList + ")"
#         cursor.execute(idList)
#         conn.commit()
        
#         returnedLvls = []

#         for item in data["add"]:
#             itemid = item["id"]
#             owner = item["owner"]
#             pattern = item["pattern"]
#             stattrak = item["st"]
#             wear = item["wear"]
#             cursor.execute("INSERT INTO public.rsitems (itemid, owner, pattern, stattrak, wear) VALUES (%(itemid)s, %(owner)s, %(pattern)s, %(stattrak)s, %(wear)s) RETURNING id;", {"itemid":itemid,"owner":owner,"pattern":pattern,"stattrak":stattrak,"wear":wear})
#             conn.commit()
#             returnedLvls.append(cursor.fetchone()[0])
        
#         cursor.close()
#         logInfo(request.remote_addr, "POST", "/cs-trade-up", 200)
#         return returnedLvls, 200
#     else:
#         logWarn(request.remote_addr, "GET", "/cs-trade-up", 403)
#         return "Invalid method", 403

# @app.route('/cs-get-inv', methods=['POST'])
# def csGetInv():
#     if request.method == 'POST':
#         cursor = conn.cursor()

#         data = request.get_json()
#         if data["secret"] != secret:
#             cursor.close()
#             return "Invalid secret", 403
        
#         owner = data["owner"]
#         cursor.execute("SELECT * FROM public.rsitems WHERE owner = %(owner)s", {"owner":owner})
#         conn.commit()
        
#         returnedLvls = JSONEncoder().encode(cursor.fetchall())
        
#         cursor.close()
#         logInfo(request.remote_addr, "POST", "/cs-get-inv", 200)
#         return returnedLvls, 200
#     else:
#         logWarn(request.remote_addr, "GET", "/cs-get-inv", 403)
#         return "Invalid method", 403

# @app.route('/cs-leaderboard', methods=['POST'])
# def csLeaderboard():
#     if request.method == 'POST':
#         cursor = conn.cursor()

#         data = request.get_json()
#         if data["secret"] != secret:
#             cursor.close()
#             return "Invalid secret", 403
        
#         cursor.execute("SELECT * FROM public.rsplayerdata ORDER BY money DESC LIMIT 100")
#         top100 = cursor.fetchall()
#         cursor.execute("SELECT * FROM public.rsplayerdata ORDER BY money ASC LIMIT 100")
#         bot100 = cursor.fetchall()
#         cursor.execute("SELECT * FROM public.rsplayerdata ORDER BY opened DESC LIMIT 100")
#         topUnboxers = cursor.fetchall()
        
#         arr = [top100, bot100, topUnboxers]

#         returnedLvls = JSONEncoder().encode(arr)
        
#         cursor.close()
#         logInfo(request.remote_addr, "POST", "/cs-leaderboard", 200)
#         return returnedLvls, 200
#     else:
#         logWarn(request.remote_addr, "GET", "/cs-leaderboard", 403)
#         return "Invalid method", 403

# @app.route('/cs-get-player-data', methods=['POST'])
# def csGetPlayerData():