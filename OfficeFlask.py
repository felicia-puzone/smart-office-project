from flask import Flask, request
from Script.Operators import AIOperator as aio, GlobalDataOperator as gdo
from Script.Generators import ModelSetup as ms

model_op = ms.Network(None)
global_op = gdo.Operator()
ai_op = aio.Operator()

temp_model_path = './AI/temp_model.h5'
light_model_path = './AI/light_model.h5'
color_model_path = './AI/color_model.h5'

temp_model = model_op.load_model(temp_model_path)
light_model = model_op.load_model(light_model_path)
color_model = model_op.load_model(color_model_path)

appname = "IoT - Smart Office"
app = Flask(appname)


@app.route('/getUserTemp/', methods=['POST'])
def getUserTemp():
    data = request.get_json(force=True)
    if data is None:
        return "<p> Dati mancanti </p>"
    else:
        print(data)
        conv_data = global_op.from_flask_in(data, 0)
        return str(global_op.from_temp_idx(ai_op.predict_feature(temp_model, conv_data)))


@app.route('/getUserLight/', methods=['POST'])
def getUserLight():
    data = request.get_json(force=True)
    if data is None:
        return "<p> Dati mancanti </p>"
    else:
        print(data)
        conv_data = global_op.from_flask_in(data, 1)
        return str(ai_op.predict_feature(light_model, conv_data))


@app.route('/getUserColor/', methods=['POST'])
def getUserColor():
    if data is None:
        return "<p> Dati mancanti </p>"
    else:
        print(data)
        conv_data = global_op.from_flask_in(data, 2)
        return str(ai_op.predict_feature(color_model, conv_data))


if __name__ == '__main__':
    port = 5000
    interface = '0.0.0.0'
    app.run(host=interface, port=port)
