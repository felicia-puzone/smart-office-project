# sample10
# request types

from flask import Flask
from config import Config
from flask import render_template, request, jsonify

appname = "BOT TEST"
app = Flask(appname)
myconfig = Config
app.config.from_object(myconfig)


@app.route('/botAuth', methods=['POST'])
def auth():
    key = request.json['key']
    if key == 'RIGHT-KEY': return jsonify( {'status':'AUTHENTICATED'})
    else: return jsonify( {'status':'NOT-AUTHENTICATED'})
    
@app.route('/botReport', methods=['GET'])
def report():
    return jsonify( {'report':'REPORT'})



if __name__ == '__main__':
    port = 80
    interface = '0.0.0.0'
    app.run(host=interface,port=port)