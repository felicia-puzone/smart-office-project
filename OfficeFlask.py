from flask import Flask, request
from Script.Operators import AIOperator as aio, GlobalDataOperator as gdo
from Script.Generators import ModelSetup as ms

model_op = ms.Network(None)
global_op = gdo.Operator()
ai_op = aio.Operator()

# Current parameters
temp_model_curr = './AI/temp_model.h5'
light_model_curr = './AI/light_model.h5'
color_model_curr = './AI/color_model.h5'

nv_path_curr = './Data/OpData/NormValues.json'
uq_path_curr = './Data/OpData/UniqueValues.json'

# Updated parameters
temp_model_upd = './AI/Update/temp_model.h5'
light_model_upd = './AI/Update/light_model.h5'
color_model_upd = './AI/Update/color_model.h5'

nv_path_upd = './Data/OpData/Update/NormValues.json'
uq_path_upd = './Data/OpData/Update/UniqueValues.json'

temp_model = model_op.load_model(temp_model_curr)
light_model = model_op.load_model(light_model_curr)
color_model = model_op.load_model(color_model_curr)

nv_path = nv_path_curr
uq_path = uq_path_curr

# Default server status: available
server_status = 1

appname = "IoT - Smart Office"
app = Flask(appname)


def serverStatus():
    global server_status
    curr_status = server_status
    return curr_status


@app.route('/systemUpdate/', methods=['POST'])
def systemUpdate():
    global server_status

    global temp_model
    global light_model
    global color_model

    global nv_path
    global uq_path

    # AI Server goes "offline" in order to update itself
    server_status = 0

    temp_model = model_op.load_model(temp_model_upd)
    light_model = model_op.load_model(light_model_upd)
    color_model = model_op.load_model(color_model_upd)

    nv_path = nv_path_upd
    uq_path = uq_path_upd

    # AI Server comes back online after completing the update
    server_status = 1
    return "<p> System Updated Correctly </p>"


@app.route('/getUserTemp/', methods=['POST'])
def getUserTemp():
    status = serverStatus()
    if status == 1:
        data = request.get_json(force=True)
        if data is None:
            return "<p> No data </p>"
        else:
            conv_data = global_op.from_flask_in(data, 0, nv_path)
            return str(global_op.from_temp_idx(ai_op.predict_feature(temp_model, conv_data), uq_path))
    else:
        return "000"


@app.route('/getUserLight/', methods=['POST'])
def getUserLight():
    status = serverStatus()
    if status == 1:
        data = request.get_json(force=True)
        if data is None:
            return "<p> No data </p>"
        else:
            conv_data = global_op.from_flask_in(data, 1, nv_path)
            return str(ai_op.predict_feature(light_model, conv_data))
    else:
        return "000"


@app.route('/getUserColor/', methods=['POST'])
def getUserColor():
    status = serverStatus()
    if status == 1:
        data = request.get_json(force=True)
        if data is None:
            return "<p> No data </p>"
        else:
            # print(data)
            conv_data = global_op.from_flask_in(data, 2, nv_path)
            return str(ai_op.predict_feature(color_model, conv_data))
    else:
        return "000"


if __name__ == '__main__':
    port = 5000
    interface = '0.0.0.0'
    app.run(host=interface, port=port)
