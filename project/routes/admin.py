

from project.constants import LOAN_TYPES, LOAN_STATUS, USERTYPE
from project.models import Loan, Users
from project.app import app, get_key, token_required, db
from flask import jsonify, request


@app.route("/all_users", methods=["GET"])
@token_required
def get_all_user(loggedInUser):
    if loggedInUser.user_type == USERTYPE['Agent'] or loggedInUser.user_type == USERTYPE['Customers']:
        return jsonify({"Message": "You are not authorized to open this page"}), 401
    users = Users.query.all()
    response = {'Users': []}
    for i in users:
        if(loggedInUser.id == i.id):
            continue
        response['Users'].append({
            "id": i.id,
            "username": i.username,
            "password": i.password_hash,
            "public_id": i.public_id,
            "email": i.email,
            "phone": i.phone,
            "Created On": i.timestamp
        })
    if len(response['Users']) == 0:
        return jsonify({"Message": "No Users in the system!"})
    return jsonify(response)


@app.route("/all_agents", methods=["GET"])
@token_required
def get_all_agents(loggedInUser):
    if loggedInUser.user_type == USERTYPE['Agent'] or loggedInUser.user_type == USERTYPE['Customers']:
        return jsonify({"Message": "You are not authorized to open this page"})
    all_agents = Users.query.filter_by(user_type=USERTYPE['Agent'])
    response = {"appoved_agents": []}
    for i in all_agents:
        if(loggedInUser.approved == False):
            continue
        response["approved_agents"].append({
            "id": i.id,
            "username": i.username,
            "password": i.password_hash,
            "public_id": i.public_id,
            "email": i.email,
            "phone": i.phone,
            "Created On": i.timestamp
        })
    if len(response['approved_agents']) == 0:
        return jsonify({"Message": "No agents in the system!"})
    return jsonify(response)


@app.route("/all_Agent_applications", methods=["GET"])
@token_required
def get_agents_requests(loggedInUser):
    if loggedInUser.user_type == USERTYPE['Agent'] or loggedInUser.user_type == USERTYPE['Customers']:
        return jsonify({"Message": "You are not authorized to open this page"})
    all_agents = Users.query.filter_by(user_type=USERTYPE['Agent'])
    response = {"Unapproved_agents": []}
    for i in all_agents:
        if(i.approved == True):
            continue
        response["Unapproved_agents"].append({
            "id": i.id,
            "username": i.username,
            "password": i.password_hash,
            "public_id": i.public_id,
            "email": i.email,
            "phone": i.phone,
            "Created On": i.timestamp
        })
    if len(response["Unapproved_agents"]) == 0:
        return jsonify({"Message": "No pending agent applications  in the system!"})
    return jsonify(response)


@app.route("/Agent_loan_requests/<agent_id>", methods=["GET"])
@token_required
def approve_agent_loan(loggedInUser, agent_id):
    if loggedInUser.user_type == USERTYPE['Agent'] or loggedInUser.user_type == USERTYPE['Customers']:
        return jsonify({"Message": "You are not authorized to open this page"})
    Loans = Loan.query.filter_by(agent_id=agent_id)
    response = {"Agent_loanRequests": []}
    for i in Loans:
        response["Agent_loanRequests"]({
            "id": i.id,
            "Loan Amount": i.loan_amount,
            "Loan Type": get_key(i.loan_type, LOAN_TYPES),
            "Rate of interest": i.roi,
            "Duration": i.duration,
            "EMI": i.emi,
            "Status": get_key(i.state, LOAN_STATUS),
            "Total Payable amount": i.total_payable_amount,
            "Customer Id": i.customer_id,
            "Agent Id": i.agent_id,
            "Created On": i.create_timestamp,
            "Updated On": i.update_timestamp
        })
    if len(response["Agent_loanRequests"]) == 0:
        return jsonify({"Message": "No request for Loans from this particular agent found found !"})
    return jsonify(response)


@app.route("/approve_agent/<agent_id>", methods=["GET"])
@token_required
def approve_agent(loggedInUser, agent_id):
    if loggedInUser.user_type == USERTYPE['Agent'] or loggedInUser.user_type == USERTYPE['Customers']:
        return jsonify({"Message": "You are not authorized to open this page"})
    agent = Users.query.filter_by(id=agent_id).first()
    if(agent.approved == True):
        return jsonify({"Message": "The agent has already been approved by the admin!"})
    agent.approved = True
    db.session.commit()
    return jsonify({"Message": "The agent has been successfully approved!!"})


@app.route("/approve_loan/<loan_id>", methods=["GET"])
@token_required
def approve_loan(loggedInUser, loan_id):
    if loggedInUser.user_type == USERTYPE['Agent'] or loggedInUser.user_type == USERTYPE['Customers']:
        return jsonify({"Message": "You are not authorized to open this page"}), 401
    try:
        loan = Loan.query.filter_by(id=loan_id).first()
    except Exception:
        return jsonify({"Message": "No Loan with Load Id : "+str(loan_id)}), 400
    loan.state = LOAN_STATUS['Approved']
    db.session.commit()
    return jsonify({"Message": "The Loan has been successfully approved!!"})


@app.route("/reject_loan/<loan_id>", methods=["GET"])
@token_required
def reject_loan(loggedInUser, loan_id):
    if loggedInUser.user_type == USERTYPE['Agent'] or loggedInUser.user_type == USERTYPE['Customers']:
        return jsonify({"Message": "You are not authorized to open this page"})
    loan = Loan.query.filter_by(id=loan_id)
    loan.state = LOAN_STATUS['Rejected']
    db.session.commit()
    return jsonify({"Message": "The Loan has been successfully Rejected!!"})
