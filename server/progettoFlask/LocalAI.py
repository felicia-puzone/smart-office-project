# sample11
# objects
#pip install flask-sqlalchemy


from flask import Flask
from flask import  jsonify

appname = "IOT - local AI"
app = Flask(appname)



@app.route('/AI', methods=['GET','POST'])
def test():
<<<<<<< HEAD
    return jsonify( {'user_temp':25,'user_color':'TEAL','user_light':'MEDIUM'}), '200 OK'
=======
    return jsonify( {'user_temp':25,'user_color':3,'user_light':4}), '200 OK'
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd



if __name__ == '__main__':
    port = 5001
    interface = '0.0.0.0'
    app.run(host=interface,port=port)