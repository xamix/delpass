from flask import Flask, Blueprint, render_template
import logging
from waitress import serve
from tools import log

LOG = log.Log(__name__)

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Reduce Flask LOG
app.logger.setLevel(logging.INFO)
logging.getLogger('waitress').disabled = True

blueprint = Blueprint('views', __name__, static_folder="static")

@blueprint.route('/')
def _home():
    return render_template('index.html')

app.register_blueprint(blueprint)

if __name__ == "__main__":
    LOG.wrn("Loaded server directly from Python")
    serve(app, host="0.0.0.0", port=5000)