from flask import request, jsonify
from project.app import app, get_key, token_required
from project.models import LOAN_STATUS, LOAN_TYPES, Loan, Loan_update_history, USERTYPE, Users


@app.route("/view_loan_history/<loan_id>", methods=["GET"])
@token_required
def loan_history(loggedInUser, loan_id):

    check_customer = Loan.query.filter_by(id=loan_id).first()
    if loggedInUser.user_type == USERTYPE["Customers"] and loggedInUser.id != check_customer.customer_id:
        return jsonify({"Message": "You are not authorised to see Loan objects except yours!"})
    query = Loan_update_history.query.filter_by(
        original_loan_id=loan_id).order_by(Loan_update_history.create_timestamp)
    response = {'History': []}
    for i in query:
        response['History'].append({
            "id": i.id,
            "Loan amount": i.loan_amount,
            "Duration": i.duration,
            "Loan Type": get_key(i.loan_type, LOAN_TYPES),
            "State At this point": i.state,
            "Origina Loan ID": i.original_loan_id,
            "Created At": i.create_timestamp
        })
    if(len(response['History']) == 0):
        return jsonify({"Message": "No changes have been done on this loan object!"})
    return jsonify(response)


@app.route("/all_Customers", methods=["GET"])
@token_required
def get_all_Customers(loggedInUser):
    if loggedInUser.user_type == USERTYPE['Customers']:
        return jsonify({"Message": "Unauthorised Access"}), 401
    all_Customers = Users.query.filter_by(user_type=USERTYPE['Customers'])
    response = {"Customers": []}
    for i in all_Customers:
        response["Customers"].append({
            "id": i.id,
            "username": i.username,
            "password": i.password_hash,
            "public_id": i.public_id,
            "email": i.email,
            "phone": i.phone,
            "Created On": i.timestamp
        })
    if len(response["Customers"]) == 0:
        return jsonify({"Message": "No Customers in the system!"})
    return jsonify(response)


@app.route("/filter-by-create-date", methods=["GET"])
@token_required
def filter_by_Creationdate(loggedInUser):
    if loggedInUser.user_type == USERTYPE["Customers"]:
        return jsonify({
            "Message": "You are not authorised to view this page!"
        }), 401
    start = request.args.get('start_date', '1985-01-17')
    end = request.args.get('end_date', '2025-09-17')
    qry = Loan.query.filter(Loan.create_timestamp.between(start, end))

    response = {'Loans between' + start+' and '+end: []}
    for i in qry:
        response['Loans between '+start+' and '+end].append({
            "id": i.id,
            "Loan amount": i.loan_amount,
            "Duration": i.duration,
            "Loan Type": get_key(i.loan_type, LOAN_TYPES),
            "State": i.state,
            "Rate of Interest": i.roi,
            "Total Payable amount": i.total_payable_amount,
            "EMI": i.emi,
            "Created At": i.create_timestamp
        })

    if(len(response['Loans between '+start+' and '+end]) == 0):
        return jsonify({"Message": "No records found for the give range!"})
    return jsonify(response)


@app.route("/filter-by-update-date", methods=["GET"])
@token_required
def filter_by_Modificationdate(loggedInUser):
    if loggedInUser.user_type == USERTYPE["Customers"]:
        return jsonify({
            "Message": "You are not authorised to view this page!"
        }), 401
    start = request.args.get('start_date', '1985-01-17')
    end = request.args.get('end_date', '2025-09-17')
    qry = Loan.query.filter(Loan.update_timestamp.between(start, end))

    response = {'Loans between '+start+' and '+end: []}
    for i in qry:
        response['Loans between '+start+' and '+end].append({
            "id": i.id,
            "Loan amount": i.loan_amount,
            "Duration": i.duration,
            "Loan Type": get_key(i.loan_type, LOAN_TYPES),
            "State": i.state,
            "Rate of Interest": i.roi,
            "Total Payable amount": i.total_payable_amount,
            "EMI": i.emi,
            "Created At": i.create_timestamp
        })

    if(len(response['Loans between '+start+' and '+end]) == 0):
        return jsonify({"Message": "No records found for the give range!"})
    return jsonify(response)


@app.route("/getloans", methods=["GET"])
@token_required
def all_loans(loggedInUser):
    '''
    Pass query parameters with request to filter according to the state
    status = "Approved" 
    status = "New"
    status = "Rejected"
    default value :
    status = "all"

    '''

    status = request.args.get('status', 'all')
    if loggedInUser.user_type == USERTYPE['Customers']:
        if(status == 'all'):
            Loans = Loan.query.filter_by(customer_id=loggedInUser.id)
        else:
            Loans = Loan.query.filter_by(
                state=LOAN_STATUS[status], customer_id=loggedInUser.id)
    elif(status == 'all'):
        Loans = Loan.query.all()
    else:
        Loans = Loan.query.filter_by(state=LOAN_STATUS[status])

    response = {"Loans": []}
    for i in Loans:
        response["Loans"].append({
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
    if len(response["Loans"]) == 0:
        return jsonify({"Message": "No "+status+" Loans found !"})
    return jsonify(response)
