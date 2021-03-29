
from project.app import app
import datetime
from flask import jsonify, request
import jwt
from werkzeug.security import check_password_hash
from project.constants import USERTYPE
from project.models import Users
from flask.helpers import make_response


@app.route("/login", methods=["POST"])
def login():
    """Endpoint to login"""
    auth = request.authorization

    if not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})
    user = Users.query.filter_by(username=auth.username).first()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})
    if check_password_hash(user.password_hash, auth.password):
        if(user.user_type == USERTYPE['Agent']):
            if(user.approved == False):
                return make_response('Your Application for agent is not approved by the admin.', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
        return jsonify({"token": token})
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})
