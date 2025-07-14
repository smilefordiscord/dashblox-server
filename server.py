import geoip2.database
import psycopg2
import time
from flask import Flask, request
import json
from json.encoder import JSONEncoder
import os
from flask import Flask, request
import time
import geoip2

app = Flask(__name__)

secret = os.environ.get('secret')
conn = psycopg2.connect(
    host=os.environ.get('host'),
    port="5432",
    dbname=os.environ.get('dbname'),
    user=os.environ.get('user'),
    password=secret,
)

ipreader = geoip2.database.Reader("GeoLite2-City.mmdb")


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
        
        cursor = conn.cursor()
        try:
            returnLevels = {}
            try:
                cursor.execute(data["request"])
                returnLevels =  JSONEncoder().encode(cursor.fetchall())
            except:
                returnLevels = ""
            conn.commit()
            cursor.close()
            return returnLevels, 200
        except:
            conn.commit()
            cursor.close()
            return "Request failed", 404
    else:
        return "Invalid method", 403

@app.route('/last-key', methods=['POST'])
def getLastkey():
    if request.method == 'POST':
        data = request.get_json()
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
    else:
        return "Invalid method", 403

@app.route('/get-key', methods=['POST'])
def getkey():
    if request.method == 'POST':
        data = request.get_json()
        if data["secret"] != secret:
            return "Invalid secret", 403
        
        cursor = conn.cursor()
        try:
            id: int = 17
            cursor.execute("SELECT * FROM public.levels WHERE id = %(id)s", {'id':id})
            returnLevels =  JSONEncoder().encode(cursor.fetchone())

            cursor.close()
            return returnLevels, 200
        except:
            cursor.close()
            return "Request failed", 404
    else:
        return "Invalid method", 403

@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        data = request.get_json()
        if data["secret"] != secret:
            return "Invalid secret", 403
        
        cursor = conn.cursor()
        # try:
        col = data["attribute"]
        substring = data["query"]
        rated = data["rated"]
        # print(col)
        # print(substring)
        # print(rated)
        if rated == "true":
            cursor.execute("SELECT * FROM public.levels WHERE %(col)s ILIKE %(sub)s AND difficulty > 0", {"col":col, "sub": '%'+substring+'%'})
        else:
            cursor.execute("SELECT * FROM public.levels WHERE %(col)s ILIKE %(sub)s", {"col":col, "sub": '%'+substring+'%'})
        
        returnLevels = {}
        try:
            cursor.execute(data["request"])
            returnLevels =  JSONEncoder().encode(cursor.fetchall())
        except:
            returnLevels = {}
        # for item in cursor:
        #     returnLevels.append(JSONEncoder().encode(item))

        cursor.close()
        return returnLevels, 200
        # except:
        #     cursor.close()
        #     return "Request failed", 404
    else:
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
        return "OK", 200
    else:
        return "Invalid method", 403

@app.route('/remove-level', methods=['POST'])
def removeLevel():
    if request.method == 'POST':
        data = request.get_json()
        if data["secret"] != secret:
            return "Invalid secret", 403
        
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM public.levels WHERE id = %(id)s;", {"id":data["id"]})
            conn.commit()
            cursor.close()
            return "OK", 200
        except:
            cursor.close()
            return "Request failed", 404
    else:
        return "Invalid method", 403

@app.route('/glro', methods=['POST'])
def glro():
    if request.method == 'POST':
        data = request.get_json()
        
        if data["secret"] != secret:
            return "Invalid secret", 403
        
        cursor = conn.cursor()
        try:
            rated = data["rated"]
            
            if rated == True:
                cursor.execute("SELECT * FROM public.levels WHERE id <= %(id)s AND difficulty > 0 ORDER BY id DESC LIMIT %(length)s", {"id":data["id"],"length":data["length"]})
            else:
                cursor.execute("SELECT * FROM public.levels WHERE id <= %(id)s ORDER BY id DESC LIMIT %(length)s", {"id":data["id"],"length":data["length"]})
            
            returnLevels = []
            for item in cursor:
                returnLevels.append(JSONEncoder().encode(item))
            
            cursor.close()
            return returnLevels, 200
        except:
            cursor.close()
            return "Request failed", 404
    else:
        return "Invalid method", 403

@app.route('/cs-add-item', methods=['POST'])
def csAddItem():
    if request.method == 'POST':
        cursor = conn.cursor()

        data = request.get_json()
        if data["secret"] != secret:
            cursor.close()
            return "Invalid secret", 403
        
        itemid = data["id"]
        owner = data["owner"]
        pattern = data["pattern"]
        stattrak = data["st"]
        wear = data["wear"]
        cursor.execute("INSERT INTO public.rsitems (itemid, owner, pattern, stattrak, wear) VALUES (%(itemid)s, %(owner)s, %(pattern)s, %(stattrak)s, %(wear)s) RETURNING id;", {"itemid":itemid,"owner":owner,"pattern":pattern,"stattrak":stattrak,"wear":wear})
        conn.commit()
        
        returnedLvls = JSONEncoder().encode(cursor.fetchone())
        
        cursor.close()
        return returnedLvls, 200
    else:
        return "Invalid method", 403

@app.route('/cs-add-items', methods=['POST'])
def csAddItems():
    if request.method == 'POST':
        cursor = conn.cursor()

        data = request.get_json()
        if data["secret"] != secret:
            cursor.close()
            return "Invalid secret", 403
        
        returnedLvls = []
        
        amtOpened = 0

        for item in data["items"]:
            amtOpened += 1
            itemid = item["id"]
            owner = item["owner"]
            pattern = item["pattern"]
            stattrak = item["st"]
            wear = item["wear"]
            cursor.execute("INSERT INTO public.rsitems (itemid, owner, pattern, stattrak, wear) VALUES (%(itemid)s, %(owner)s, %(pattern)s, %(stattrak)s, %(wear)s) RETURNING id;", {"itemid":itemid,"owner":owner,"pattern":pattern,"stattrak":stattrak,"wear":wear})
            conn.commit()
            returnedLvls.append(cursor.fetchone()[0])
        
        cursor.execute("UPDATE public.rsplayerdata SET money = money + %(money)s WHERE userid = %(userid)s", {"money": data["cost"], "userid": data["userid"]})
        cursor.execute("UPDATE public.rsplayerdata SET opened = opened + %(opened)s WHERE userid = %(userid)s", {"opened": amtOpened, "userid": data["userid"]})
        conn.commit()
        
        cursor.close()
        return returnedLvls, 200
    else:
        return "Invalid method", 403

@app.route('/cs-delete-items', methods=['POST'])
def csDeleteItems():
    if request.method == 'POST':
        cursor = conn.cursor()

        data = request.get_json()
        if data["secret"] != secret:
            cursor.close()
            return "Invalid secret", 403
        
        idList = ""
        for id in data["ids"]:
            if idList == "":
                idList = str(id)
            else:
                idList = idList + ", " + str(id)
        
        idList = "DELETE FROM public.rsitems WHERE id IN (" + idList + ")"
        cursor.execute(idList)
        cursor.execute("UPDATE public.rsplayerdata SET money = money + %(money)s WHERE userid = %(userid)s", {"money": data["money"], "userid": data["userid"]})
        conn.commit()

        cursor.close()
        return "OK", 200
    else:
        return "Invalid method", 403

@app.route('/cs-trade-up', methods=['POST'])
def csTradeUp():
    if request.method == 'POST':
        cursor = conn.cursor()

        data = request.get_json()
        if data["secret"] != secret:
            cursor.close()
            return "Invalid secret", 403
        
        idList = ""
        for id in data["take"]:
            if idList == "":
                idList = str(id)
            else:
                idList = idList + ", " + str(id)
        
        idList = "DELETE FROM public.rsitems WHERE id IN (" + idList + ")"
        cursor.execute(idList)
        conn.commit()
        
        returnedLvls = []

        for item in data["add"]:
            itemid = item["id"]
            owner = item["owner"]
            pattern = item["pattern"]
            stattrak = item["st"]
            wear = item["wear"]
            cursor.execute("INSERT INTO public.rsitems (itemid, owner, pattern, stattrak, wear) VALUES (%(itemid)s, %(owner)s, %(pattern)s, %(stattrak)s, %(wear)s) RETURNING id;", {"itemid":itemid,"owner":owner,"pattern":pattern,"stattrak":stattrak,"wear":wear})
            conn.commit()
            returnedLvls.append(cursor.fetchone()[0])
        
        cursor.close()
        return returnedLvls, 200
    else:
        return "Invalid method", 403

@app.route('/cs-get-inv', methods=['POST'])
def csGetInv():
    if request.method == 'POST':
        cursor = conn.cursor()

        data = request.get_json()
        if data["secret"] != secret:
            cursor.close()
            return "Invalid secret", 403
        
        owner = data["owner"]
        cursor.execute("SELECT * FROM public.rsitems WHERE owner = %(owner)s", {"owner":owner})
        conn.commit()
        
        returnedLvls = JSONEncoder().encode(cursor.fetchall())
        
        cursor.close()
        return returnedLvls, 200
    else:
        return "Invalid method", 403

@app.route('/cs-leaderboard', methods=['POST'])
def csLeaderboard():
    if request.method == 'POST':
        cursor = conn.cursor()

        data = request.get_json()
        if data["secret"] != secret:
            cursor.close()
            return "Invalid secret", 403
        
        cursor.execute("SELECT * FROM public.rsplayerdata ORDER BY money DESC LIMIT 100")
        top100 = cursor.fetchall()
        cursor.execute("SELECT * FROM public.rsplayerdata ORDER BY money ASC LIMIT 100")
        bot100 = cursor.fetchall()
        cursor.execute("SELECT * FROM public.rsplayerdata ORDER BY opened DESC LIMIT 100")
        topUnboxers = cursor.fetchall()
        
        arr = [top100, bot100, topUnboxers]

        returnedLvls = JSONEncoder().encode(arr)
        
        cursor.close()
        return returnedLvls, 200
    else:
        return "Invalid method", 403

@app.route('/cs-get-player-data', methods=['POST'])
def csGetPlayerData():
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
        return json.dumps(returnData), 200
    else:
        return "Invalid method", 403

@app.route('/ipjson', methods=['GET', 'POST'])
def ipjson():
    if request.method == 'POST' or request.method == 'GET':
        try:
            response = ipreader.city(request.remote_addr)
            returnData = {
                "iso": response.country.iso_code,
                "city": response.city.name
            }
            return json.dumps(returnData), 200
        except:
            return "", 200
    else:
        return "Invalid method", 403

print("Starting server")

app.run(host='0.0.0.0', port=8080)