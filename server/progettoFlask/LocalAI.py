# sample11
# objects
#pip install flask-sqlalchemy


from flask import Flask
from flask import  jsonify

appname = "IOT - local AI"
app = Flask(appname)



@app.route('/AI', methods=['GET','POST'])
def test():
    return jsonify( {'user_temp':25,'user_color':'TEAL','user_light':'MEDIUM'}), '200 OK'



if __name__ == '__main__':
    port = 5001
    interface = '0.0.0.0'
    app.run(host=interface,port=port)