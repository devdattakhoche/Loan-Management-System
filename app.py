from functools import wraps
from werkzeug.security import check_password_hash
import datetime
from flask import Flask, request , jsonify, wrappers
from flask.helpers import make_response
from flask_sqlalchemy import SQLAlchemy
import jwt
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from models import LOAN_STATUS, LOAN_TYPES, Loan, USERTYPE, Users

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = None 

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'message':'Token is missing!'}), 401
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'])
            current_user = Users.query.filter(public_id=data['public_id']).first()
        except:
            return jsonify({'message':'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)
    return decorated


@app.route("/register_Customer", methods=["POST"])
def register_Customer():
    """Endpoint to register/add more users to the system"""
    data = request.get_json()
    new_user =  Users(data["username"],data["email"],data['phone'],data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'Message' : 'Your Account has been added successfully !'})




@app.route("/register_Agent", methods=["POST"])
def register_Agent():
    """Endpoint to register/add more agents to the system"""
    data = request.get_json()
    new_user =  Users(data["username"],data["email"],data['phone'],data['password'],user_type=USERTYPE['Agent'],approved=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'Message' : 'Your request has been sent successfully! You will be able to login after Admin approves your request!'})




@app.route("/login", methods=["POST"])
def login():
    """Endpoint to login"""
    auth  = request.authorization
    print(auth)
    if  not auth.username or not auth.password:
        return make_response('Could not verify', 401,{'WWW-Authenticate' : 'Basic realm="Login Required!"'})
    user = Users.query.filter_by(username=auth.username).first()
    if not user:
         return make_response('Could not verify', 401,{'WWW-Authenticate' : 'Basic realm="Login Required!"'}) 
    print(user.password_hash.encode('utf-8'))
    if check_password_hash(user.password_hash, auth.password):
        token = jwt.encode({'public_id':user.public_id,'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=30)} , app.config['SECRET_KEY'])
        return jsonify({"token" : token})
    return make_response('Could not verify', 401,{'WWW-Authenticate' : 'Basic realm="Login Required!"'}) 


'''

Admin Routes

'''
@app.route("/all_users", methods=["GET"])
@app.route("/all_Customers", methods=["GET"])
@app.route("/all_agents", methods=["GET"]) # approved and not approved and all
@app.route("/approved_loans", methods=["GET"])
@app.route("/new_Loans", methods=["GET"])
@app.route("/rejected_loans", methods=["GET"])
@app.route("/all_Agent_requests", methods=["GET"])
@app.route("/Agent_requests/<agent_id>", methods=["GET"])
@app.route("/approve_agent/<agent_id>", methods=["GET"])
@app.route("/all_loans", methods=["GET"])
@app.route("/approve_loan/<loan_id>", methods=["GET"])
@app.route("/reject_loan/<loan_id>", methods=["GET"])
@app.route("/filter_loans_by_date", methods=["GET"])
@app.route("/delete_user/<user_id>", methods=["GET"])
def mydun1():
    return 1

'''
Agent routes

'''
@app.route("/all_Customers", methods=["GET"])
@app.route("/approved_loans", methods=["GET"])
@app.route("/new_Loans", methods=["GET"])
@app.route("/rejected_loans", methods=["GET"])
@app.route("/request_loan/<loan_id>", methods=["GET"])
@app.route("/loan_Requests_by_agent", methods=["GET"])
@app.route("/all_loans", methods=["GET"])
@app.route("/filter_loans_by_date", methods=["GET"])
def mydun():
    return 1


'''
Customer Routes
'''



@app.route("/new_loan", methods=["POST"])
@token_required
def new_loan(current_user):

    data = request.get_json()
    new_loan =  Loan(data["loan_amount"],data["duration"],current_user.id,loan_type=LOAN_TYPES[data['loan_type']])
    db.session.add(new_loan)
    db.session.commit()
    
    return jsonify({'Message' : 'Your Loan Application has been successfully created','object':new_loan})

