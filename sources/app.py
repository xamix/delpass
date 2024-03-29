from flask import Flask, Blueprint, render_template, request
import logging
import json
from delpass import Delpass
from waitress import serve
from tools import log
from typing import Dict, Tuple, Optional

# Create a logger
LOG = log.Log("main")

# Create flask app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Reduce Flask LOG
app.logger.setLevel(logging.INFO)
logging.getLogger('waitress').disabled = False

# Blueprint to route
blueprint = Blueprint('views', __name__, static_folder="static")

# Create Delpass
dp = Delpass()
dp.start()

def build_error_response(message=None) -> Dict[str, any]:
    return {"success": False, "message": message, "data": {}}


def build_success_response(data=None) -> Dict[str, any]:
    if data is None:
        data = {}
    return {"success": True, "message": "", "data": data}


def build_response(result: Tuple[bool, Optional[str]]) -> Dict[str, any]:
    if result[0]:
        return build_success_response()
    else:
        build_error_response(result[1])

@blueprint.route('/')
def _home():
    return render_template('index.html')

@blueprint.route('/list-sound')
def _list_sound():
    return build_success_response(dp.list_sound())

@blueprint.route('/status')
def _status():
    return build_success_response(dp.status())

@blueprint.route('/set-mode', methods=['POST'])
def _set_mode():
    try:
        params = json.loads(request.form['params'])
        dp.set_mode(params)
        return build_success_response({})
    except Exception as e:
        return build_error_response(str(e))

# Reegister all routes
app.register_blueprint(blueprint)

if __name__ == "__main__":
    LOG.wrn("Loaded server directly from Python")
    serve(app, host="0.0.0.0", port=5000)