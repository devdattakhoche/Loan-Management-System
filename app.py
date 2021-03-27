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


add_admin = True

if(add_admin):
    new_user =  Users("Admin","admin@gmail.com","9829829829","adminpass",user_type=USERTYPE['Admin'])
    db.session.add(new_user)
    db.session.commit()
    add_admin=False

def get_key(val,dict):
    for key, value in dict.items():
            if val == value:
                return key

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        
        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except Exception as ex:
            print(ex.__class__.__name__)
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated






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
        if(user.user_type == USERTYPE['Agent']):
            if(user.approved == False):
                    return make_response('Your Application for agent is not approved by the admin.', 401,{'WWW-Authenticate' : 'Basic realm="Login Required!"'}) 
        token = jwt.encode({'public_id':user.public_id,'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=30)} , app.config['SECRET_KEY'])
        return jsonify({"token" : token})
    return make_response('Could not verify', 401,{'WWW-Authenticate' : 'Basic realm="Login Required!"'}) 


'''

Admin Routes

'''

@app.route("/all_users", methods=["GET"])
@token_required
def get_all_user(current_user):
    if current_user.user_type==USERTYPE['Agent'] and current_user.user_type==USERTYPE['Customers'] : 
        return jsonify({"Message":"You are not authorized to open this page"}) 
    users = Users.query.all()
    response  = {}
    for i in users:
        if(current_user.id == i.id) : continue
        response[i.id] = {
            "username" : i.username,
            "password" : i.password_hash,
            "public_id" : i.public_id,
            "email" : i.email,
            "phone" : i.phone,
            "Created On" : i.timestamp
        }
    if len(response) == 0 : return jsonify({"Message":"No Users in the system!"})
    return jsonify(response)


@app.route("/all_agents", methods=["GET"])
@token_required
def get_all_agents(current_user):
    if current_user.user_type==USERTYPE['Agent'] and current_user.user_type==USERTYPE['Customers'] : 
        return jsonify({"Message":"You are not authorized to open this page"}) 
    all_agents = Users.query.filter_by(user_type=USERTYPE['Agent'])
    response  = {}
    for i in all_agents:
        if(current_user.approved == False) : continue
        response[i.id] = {
            "username" : i.username,
            "password" : i.password_hash,
            "public_id" : i.public_id,
            "email" : i.email,
            "phone" : i.phone,
            "Created On" : i.timestamp
        }
    if len(response) == 0 : return jsonify({"Message":"No agents in the system!"})
    return jsonify(response)


@app.route("/all_Agent_applications", methods=["GET"])
def get_agents_requests(current_user):
    if current_user.user_type==USERTYPE['Agent'] and current_user.user_type==USERTYPE['Customers'] : 
        return jsonify({"Message":"You are not authorized to open this page"}) 
    all_agents = Users.query.filter_by(user_type=USERTYPE['Agent'])
    response  = {}
    for i in all_agents:
        if(current_user.approved == True) : continue
        response[i.id] = {
            "username" : i.username,
            "password" : i.password_hash,
            "public_id" : i.public_id,
            "email" : i.email,
            "phone" : i.phone,
            "Created On" : i.timestamp
        }
    if len(response) == 0 : return jsonify({"Message":"No agents in the system!"})
    return jsonify(response)



@app.route("/Agent_loan_requests/<agent_id>", methods=["GET"])
@token_required
def approve_agent(current_user,agent_id):
    if current_user.user_type==USERTYPE['Agent'] and current_user.user_type==USERTYPE['Customers'] : 
        return jsonify({"Message":"You are not authorized to open this page"}) 
    Loans = Loan.query.filter_by(agent_id=agent_id)
    response  = {}
    for i in Loans:
        response[i.id] = {
            "Loan Amount" : i.loan_amount,
            "Loan Type" : get_key(i.loan_type,LOAN_TYPES),
            "Rate of interest" : i.roi,
            "Duration" : i.duration,
            "EMI" : i.emi,
            "Status" : get_key(i.state,LOAN_STATUS),
            "Total Payable amount": i.total_payable_amount,
            "Customer Id" : i.customer_id,
            "Agent Id" : i.agent_id,
            "Created On" : i.create_timestamp,
            "Updated On" : i.update_timestamp
        }
    if len(response) == 0 : return jsonify({"Message":"No request for Loans from this particular agent found found !"})
    return jsonify(response)   
    
    return jsonify({"Message":"The agent has been successfully approved!!"})


@app.route("/approve_agent/<agent_id>", methods=["GET"])
@token_required
def approve_agent(current_user,agent_id):
    if current_user.user_type==USERTYPE['Agent'] and current_user.user_type==USERTYPE['Customers'] : 
        return jsonify({"Message":"You are not authorized to open this page"}) 
    agent = Users.query.filter_by(id=agent_id)
    agent.approved = True
    db.session.commit()
    return jsonify({"Message":"The agent has been successfully approved!!"})

@app.route("/approve_loan/<loan_id>", methods=["GET"])
@token_required
def approve_loan(current_user,loan_id):
    if current_user.user_type==USERTYPE['Agent'] and current_user.user_type==USERTYPE['Customers'] : 
        return jsonify({"Message":"You are not authorized to open this page"}) 
    loan = Loan.query.filter_by(id=loan_id)
    loan.state = LOAN_STATUS['Approved']
    db.session.commit()
    return jsonify({"Message":"The Loan has been successfully approved!!"})


@app.route("/reject_loan/<loan_id>", methods=["GET"])
@token_required
def reject_loan(current_user,loan_id):
    if current_user.user_type==USERTYPE['Agent'] and current_user.user_type==USERTYPE['Customers'] : 
        return jsonify({"Message":"You are not authorized to open this page"}) 
    loan = Loan.query.filter_by(id=loan_id)
    loan.state = LOAN_STATUS['Rejected']
    db.session.commit()
    return jsonify({"Message":"The Loan has been successfully Rejected!!"})


# @app.route("/delete_user/<user_id>", methods=["GET"])
# @token_required
'''
Agent routes

'''



@app.route("/register_Agent", methods=["POST"])
def register_Agent():
    """Endpoint to register/add more agents to the system"""
    data = request.get_json()

    new_user =  Users(data["username"],data["email"],data['phone'],data['password'],user_type=USERTYPE['Agent'],approved=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'Message' : 'Your request has been sent successfully! You will be able to login after Admin approves your request!'})


@app.route("/all_Customers", methods=["GET"])
@token_required
def get_all_Customers(current_user):
    if current_user.user_type==USERTYPE['Customers'] : return jsonify({"Message":"You are not authorized to open this page"}) 
    all_Customers = Users.query.filter_by(user_type=USERTYPE['Customers'])
    response  = {}
    for i in all_Customers:
        response[i.id] = {
            "username" : i.username,
            "password" : i.password_hash,
            "public_id" : i.public_id,
            "email" : i.email,
            "phone" : i.phone,
            "Created On" : i.timestamp
        }
    if len(response) == 0 : return jsonify({"Message":"No Customers in the system!"})
    return jsonify(response)


@app.route("/get_loans_State_filter", methods=["GET"])
@token_required
def all_loans(current_user):
    
    status = request.args.get('status', 'all')
    if current_user.user_type==USERTYPE['Customers'] :
        if(status == 'all') :
            Loans = Loan.query.all(customer_id=current_user.id)
        else :
            Loans = Loan.query.filter_by(state=LOAN_STATUS[status],customer_id=current_user.id)
    elif(status == 'all') :
        Loans = Loan.query.all()
    else :
        Loans = Loan.query.filter_by(state=LOAN_STATUS[status])
    
    
    
    response  = {}
    for i in Loans:
        response[i.id] = {
            "Loan Amount" : i.loan_amount,
            "Loan Type" : get_key(i.loan_type,LOAN_TYPES),
            "Rate of interest" : i.roi,
            "Duration" : i.duration,
            "EMI" : i.emi,
            "Status" : get_key(i.state,LOAN_STATUS),
            "Total Payable amount": i.total_payable_amount,
            "Customer Id" : i.customer_id,
            "Agent Id" : i.agent_id,
            "Created On" : i.create_timestamp,
            "Updated On" : i.update_timestamp
        }
    if len(response) == 0 : return jsonify({"Message":"No "+status+" Loans found !"})
    return jsonify(response)
    

@app.route("/request_loan/<loan_id>", methods=["GET"])
@token_required
def make_request_agent(current_user,loan_id):
    Loan = Loan.query.filter_by(id=loan_id).first()
    Loan.agent_id = current_user.id
    db.session.commit()
    return jsonify({"Message":"Request to Admin on behalf of this customer is successfully made by you."})





@app.route("/loan_Requests_by_agent", methods=["GET"])
@token_required
def get_requests(current_user):
    if(current_user.user_type == USERTYPE['Agent']):
        Loan = Loan.query.filter_by(agent_id=current_user.id)
        response  = {}
        for i in Loan:
            response[i.id] = {
                "Loan Amount" : i.loan_amount,
                "Loan Type" : get_key(i.loan_type,LOAN_TYPES),
                "Rate of interest" : i.roi,
                "Duration" : i.duration,
                "EMI" : i.emi,
                "Status" : get_key(i.state,LOAN_STATUS),
                "Total Payable amount": i.total_payable_amount,
                "Customer Id" : i.customer_id,
                "Agent Id" : i.agent_id,
                "Created On" : i.create_timestamp,
                "Updated On" : i.update_timestamp
            }
        if len(response) == 0 : return jsonify({"Message":"No requests found !"})
        return jsonify(response)
    else : 
        return jsonify({"Message":"Not Authorized to view this page"})

@app.route("/filter_loans_by_date", methods=["GET"])
def mydun():
    return 1


'''
Customer Routes
'''


@app.route("/register_Customer", methods=["POST"])
def register_Customer():
    """Endpoint to register/add more users to the system"""
    data = request.get_json()
    new_user =  Users(data["username"],data["email"],data['phone'],data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'Message' : 'Your Account has been added successfully !'})




@app.route("/new_loan", methods=["POST"])
@token_required
def new_loan(current_user):

    data = request.get_json()

    if(data == None) : 
        return jsonify({'message' : 'Data should be passed for loan'}), 401

    new_loan =  Loan(data["loan_amount"],data["duration"],current_user.id,loan_type=LOAN_TYPES[data['loan_type']])
    db.session.add(new_loan)
    db.session.commit()

    return jsonify({'Message' : 'Your Loan Application has been successfully created',"data":
       {
            "Loan amount":new_loan.loan_amount,
            "Duration":new_loan.duration,
            "Rate of Interest":new_loan.roi,
            "EMI":new_loan.emi,
            "Total amount to be paid":new_loan.total_payable_amount,
            "Loan Type" : get_key(new_loan.loan_type,LOAN_TYPES),
            "Created on ": new_loan.create_timestamp
       }
    })

