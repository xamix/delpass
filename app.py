from flask import Flask, Blueprint, render_template, request
import logging
import json
from waitress import serve
from tools import log
from typing import Dict, Tuple, Optional

# Create a logger
LOG = log.Log("Delpass")

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Reduce Flask LOG
app.logger.setLevel(logging.INFO)
logging.getLogger('waitress').disabled = False

# Blueprint to route
blueprint = Blueprint('views', __name__, static_folder="static")


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

@blueprint.route('/send-text', methods=['POST'])
def _send_text():
    params = json.loads(request.form['params'])
    LOG.wrn(f"send-text: {params}")
    return build_success_response({})

# Reegister all routes
app.register_blueprint(blueprint)

if __name__ == "__main__":
    LOG.wrn("Loaded server directly from Python")
    serve(app, host="0.0.0.0", port=5000)