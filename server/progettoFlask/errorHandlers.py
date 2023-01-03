import flask
from flask import session, render_template

from models import getFreeBuildings, db, digitalTwinFeed
from utilities import buildJsonList

blueprint = flask.Blueprint('error_handlers', __name__)

@blueprint.app_errorhandler(404)
def handle404(e):
    if session.get('loggedin') == True:
        if session.get('id_room') and session.get('id_user') and session.get('id_building') and session.get('username'):
            digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=session['id_room']).first()
            return render_template('index.html', digitalTwin=digitalTwin, username=session['username'])
    return render_template('select.html', buildings=buildJsonList(getFreeBuildings()), msg='')
    return 'You are not logged in'