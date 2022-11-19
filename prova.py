# sample11
# objects
#pip install flask-sqlalchemy


from flask import Flask
from flask import render_template, request, jsonify
from datetime import datetime

appname = "IOT - sample1"
app = Flask(appname)

@app.errorhandler(404)
def page_not_found(error):
    return 'Errore', 404

@app.route('/')
def testoHTML():
    if request.accept_mimetypes['application/json']:
        return jsonify( {'text':'I Love IoT'}), '200 OK'
    else:
        return '<h1>I love IoT</h1>'

if __name__ == '__main__':

    port = 80
    interface = '0.0.0.0'
    app.run(host=interface,port=port)