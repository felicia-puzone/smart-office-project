# sample11
# objects
#pip install flask-sqlalchemy


from flask import Flask, request
from flask import  jsonify

appname = "IOT - local AI"
app = Flask(appname)



@app.route('/AI', methods=['POST'])
def test():
    data=request.get_json(force=True)
    user_color = 'TEAL'
    user_temp = 17
    user_light = 'LOW'
    if data is not None:
        print(data)
        if int(data['user_sex']) == 1:
            user_color='VIOLET'
        elif int(data['user_sex']) == 2:
            user_color = 'RAINBOW'
        if int(float(data['ext_temp'])) > 30:
            user_temp=30
        elif int(float(data['ext_temp'])) > 17:
            user_temp=int(float(data['ext_temp']))
        if int(data['user_age']) <30:
            user_light='HIGH'
        elif int(data['user_age']) <60:
            user_light='MEDIUM'

    return jsonify( {'user_temp':user_temp,'user_color':user_color,'user_light':user_light}), '200 OK'



if __name__ == '__main__':
    port = 5001
    interface = '0.0.0.0'
    app.run(host=interface,port=port)