
import datetime
from flask import jsonify, request
from project.constants import LOAN_STATUS, LOAN_TYPES, USERTYPE
from project.models import Loan, Loan_update_history, Users
from project.app import app, db, get_key, token_required


@app.route("/register_Agent", methods=["POST"])
def register_Agent():
    """Endpoint to register/add more agents to the system"""
    data = request.get_json()

    new_user = Users(data["username"], data["email"], data['phone'],
                     data['password'], user_type=USERTYPE['Agent'], approved=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'Message': 'Your request has been sent successfully! You will be able to login after Admin approves your request!'})


@app.route("/request_loan/<loan_id>", methods=["GET"])
@token_required
def make_request_agent(loggedInUser, loan_id):
    if(loggedInUser.user_type == USERTYPE['Agent']):
        try:
            Loans = Loan.query.filter_by(id=loan_id).first()
        except Exception as ex:
            return jsonify({"Message": "No loan with the following loan ID"}), 400
        Loans.agent_id = loggedInUser.id
        db.session.commit()
        return jsonify({"Message": "Request to Admin on behalf of this customer is successfully made by you."})
    else:
        return jsonify({"Message": "Unauthorised Access"}), 401


@app.route("/loan_Requests_by_agent", methods=["GET"])
@token_required
def get_requests(loggedInUser):
    if(loggedInUser.user_type == USERTYPE['Agent']):
        Loans = Loan.query.filter_by(agent_id=loggedInUser.id)
        response = {"Loan Requests": []}
        for i in Loans:
            response["Loan Requests"].append({
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
        if len(response["Loan Requests"]) == 0:
            return jsonify({"Message": "No requests found !"})
        return jsonify(response)
    else:
        return jsonify({"Message": "Not Authorized to view this page"}), 401


@app.route("/edit_loan/<loan_id>", methods=["POST"])
@token_required
def edit_loan(loggedInUser, loan_id):
    if(loggedInUser.user_type != USERTYPE['Agent']):
        return jsonify({"Message": "Unauthorised Access"}), 401
    data = request.get_json()
    try:
        Loans = Loan.query.filter_by(id=loan_id).first()
    except Exception:
        return jsonify({"Message": "No Loan with loan id "+loan_id+""}), 400

    if(get_key(Loans.state, LOAN_STATUS) == "Approved"):
        return jsonify({"Message": "This Loan has already been approved by the admin!! It is immutable now."}), 200
    previous_loan = Loan_update_history(
        Loans.loan_amount, Loans.duration, Loans.id, state=Loans.state, loan_type=Loans.loan_type)
    db.session.add(previous_loan)
    db.session.commit()
    if(data == None):
        return jsonify({'message': 'Loan appllication data should be passed for loan'}), 401
    try:
        Loans.loan_amount = data["loan_amount"]
        Loans.last_updated_by = loggedInUser.id
        Loans.update_timestamp = datetime.datetime.now(datetime.timezone.utc)
    except KeyError:
        pass
    try:
        Loans.loan_type = LOAN_TYPES[data["loan_type"]]
        Loans.last_updated_by = loggedInUser.id
        Loans.update_timestamp = datetime.datetime.now(datetime.timezone.utc)
    except KeyError:
        pass
    try:
        Loans.duration = data["duration"]
        Loans.last_updated_by = loggedInUser.id
        Loans.update_timestamp = datetime.datetime.now(datetime.timezone.utc)
    except KeyError:
        pass

    db.session.commit()

    return jsonify({'Message': 'Your Loan Application has been successfully Modified', "data":
                    {
                        "Loan amount": Loans.loan_amount,
                        "Duration": Loans.duration,
                        "Rate of Interest": Loans.roi,
                        "EMI": Loans.emi,
                        "Total amount to be paid": Loans.total_payable_amount,
                        "Loan Type": get_key(Loans.loan_type, LOAN_TYPES),
                        "Created on ": Loans.create_timestamp
                    }
                    })
