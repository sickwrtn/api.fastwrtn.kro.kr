from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from functools import wraps
import datetime
import json
import ssl

app = Flask(__name__)
cors = CORS(app,resources={r"*": {"origins":"*"}})
bannedIp = []
adminIp = []
db = []
reportDB = []
c = 0

def as_json(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    res = f(*args, **kwargs)
    res = json.dumps(res, ensure_ascii=False).encode('utf8')
    return Response(res, content_type='application/json; charset=utf-8')
  return decorated_function
@app.get("/")
async def read_root():
    return "Fast wrtn api!"
    
@app.route('/server',methods=['GET'])
@as_json
def server():
    try:
        sum = 0;
        for i in db[len(db)-10:]:
            sum += i['star']
        sum = sum / 10
        data = {"result":"SUSSES","data":sum}
        return data
    except Exception as e:
        return {"result":"FAIL","data":str(e)}
    
@app.route('/history',methods=['GET'])
@as_json
def history():
    try:
        data = []
        if (request.args.get('limit') == None):
            for i in db:
                data.append({"id":i['id'],
                  "ip":f"{i['ip'].split('.')[0]}.{i['ip'].split('.')[1]}",
                  "star":i['star'],
                  "comment" : i['comment'],
                  "name" : i['name'],
                  "date" : i['date'],
                  "likeCount" : i['likeCount'],
                })
            return {"result":"SUSSES","data":data}
        else:
            for i in db[len(db) - int(request.args.get('limit')):]:
                data.append({"id":i['id'],
                  "ip":f"{i['ip'].split('.')[0]}.{i['ip'].split('.')[1]}",
                  "star":i['star'],
                  "comment" : i['comment'],
                  "name" : i['name'],
                  "date" : i['date'],
                  "likeCount" : i['likeCount'],
                })
            return {"result":"SUSSES","data":data}
    except Exception as e:
        return {"result":"FAIL","data":str(e)}
    
@app.route('/comment',methods=['POST'])
@as_json
def comment():
    try:
        if request.remote_addr in bannedIp:
            raise Exception("youe ip banned")
        global c
        data = request.json
        if (type(data['name']) != str or type(data['comment']) != str or type(data['star']) != int):
            raise Exception("type error")
        if (len(data['comment']) > 25):
            raise Exception("comment must be small than 10")
        if (data['star'] > 5 or data['star'] < 0):
            raise Exception("star must be 0 =< star < 5")
        if (len(data['name']) > 15):
            raise Exception("comment must be small than 15")
        db.append({
          "id" : c,
          "ip" : request.remote_addr,
          "star" : data['star'],
          "comment" : data['comment'],
          "name" : data['name'],
          "date" : str(datetime.datetime.now()),
          "likeCount" : 0,
          "likedUsers" : []
        })
        c += 1
        response = {
          "result":"SUSSES",
          "data" : data
        }
        return response
    except Exception as e:
        return {"result":"FAIL","data":str(e)}

@app.route('/comment/action',methods=['POST'])
@as_json
def action():
    try:
        data = request.json
        if (type(data['id']) != int or type(data['type']) != str):
          raise Exception("type error")
        elif (data['type'] == "like"):
          k = 0
          for i in db:
              if (data['id'] == i['id']):
                  if request.remote_addr in i['likedUsers']:
                      raise Exception("already liked.")
                  else:
                      db[k]['likeCount'] += 1
                      db[k]['likedUsers'].append(request.remote_addr)
              k += 1
          return {"result":"SUCCESS"}
    except Exception as e:
        return {"result":"FAIL","data":str(e)}

@app.route('/admin/sickwrtn/cutDB',methods=['GET'])
@as_json
def cutDB():
    try:
        global db,adminIp
        if request.remote_addr in adminIp:
            pass
        else:
            raise Exception("frorbidden")
        if (request.args.get('limit') == None):
          db = []
          return {"result":"SUCCESS"}
        else:
          db = db[len(db) - int(request.args.get('limit')):]
          return {"result":"SUCCESS"}
    except Exception as e:
        return {"result":"FAIL","data":str(e)}

@app.route('/admin/sickwrtn/cutID',methods=['GET'])
@as_json
def cutID():
    try:
        global db,adminIp
        if request.remote_addr in adminIp:
            pass
        else:
            raise Exception("frorbidden")
        if (request.args.get('id') == None):
          raise Exception("plz set id")
        else:
          k = 0
          for i in db:
              if (int(request.args.get('id')) == i['id']):
                  del db[k]
              k += 1
          return {"result":"SUCCESS"}
    except Exception as e:
        return {"result":"FAIL","data":str(e)}
        
@app.route('/admin/sickwrtn/ban',methods=['GET'])
@as_json
def ban():
    try:
        global bannedIp,adminIp
        if request.remote_addr in adminIp:
            pass
        else:
            raise Exception("frorbidden")
        if (request.args.get('ip') == None):
          raise Exception("plz set ip")
        else:
          bannedIp.append(request.args.get('ip'))
          return {"result":"SUCCESS","data":request.args.get('ip')}
    except Exception as e:
        return {"result":"FAIL","data":str(e)}
        
@app.route('/admin/sickwrtn/unban',methods=['GET'])
@as_json
def unban():
    try:
        global bannedIp,adminIp
        if request.remote_addr in adminIp:
            pass
        else:
            raise Exception("frorbidden")
        if (request.args.get('ip') == None):
          raise Exception("plz set ip")
        else:
          k=0
          for i in bannedIp:
            if (i == request.args.get('ip')):
              del bannedIp[k]
            k += 1
          return {"result":"SUCCESS","data":request.args.get('ip')}
    except Exception as e:
        return {"result":"FAIL","data":str(e)}
        
@app.route('/admin/sickwrtn/ban/history',methods=['GET'])
@as_json
def banHistory():
    try:
        global bannedIp,adminIp
        if request.remote_addr in adminIp:
            pass
        else:
            raise Exception("frorbidden")
        return {"result":"SUCCESS","data":bannedIp}
    except Exception as e:
        return {"result":"FAIL","data":str(e)}

@app.route('/admin/sickwrtn/history',methods=['GET'])
@as_json
def adminHistory():
    try:
        global bannedIp,adminIp
        if request.remote_addr in adminIp:
            pass
        else:
            raise Exception("frorbidden")
        if (request.args.get('limit') == None):
            return {"result":"SUSSES","data":db}
        else:
            return {"result":"SUSSES","data":db[len(db) - int(request.args.get('limit')):]}
    except Exception as e:
        return {"result":"FAIL","data":str(e)}
        
@app.route('/admin/sickwrtn/report',methods=['GET'])
@as_json
def adminReport():
    try:
        global reportDB,adminIp
        if request.remote_addr in adminIp:
            pass
        else:
            raise Exception("frorbidden")
        if (request.args.get('limit') == None):
            return {"result":"SUSSES","data":reportDB[::-1]}
        else:
            return {"result":"SUSSES","data":reportDB[len(reportDB) - int(request.args.get('limit')):][::-1]}
    except Exception as e:
        return {"result":"FAIL","data":str(e)}
        
@app.route('/report',methods=['GET'])
@as_json
def report():
    try:
        global bannedIp,reportDB
        if (request.args.get('id') == None):
            raise Exception("plz set id")
        k = 0
        for i in db:
            if (int(request.args.get('id')) == i['id']):
                reportDB.append({"reporter":request.remote_addr,"reportedReview":db[k],"date":str(datetime.datetime.now())})
            k += 1
        return {"result":"SUSSES"}
    except Exception as e:
        return {"result":"FAIL","data":str(e)}
app.run('0.0.0.0',port=80,debug=False)