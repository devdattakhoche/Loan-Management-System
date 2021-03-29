
from flask import request, jsonify
from project.app import app, db, get_key, token_required
from project.models import LOAN_TYPES, Loan, Users


@app.route("/new_loan", methods=["POST"])
@token_required
def new_loan(loggedInUser):

    data = request.get_json()

    if(data == None):
        return jsonify({'message': 'Data should be passed for loan'}), 401

    new_loan = Loan(data["loan_amount"], data["duration"],
                    loggedInUser.id, loan_type=LOAN_TYPES[data['loan_type']])
    db.session.add(new_loan)
    db.session.commit()

    return jsonify({'Message': 'Your Loan Application has been successfully created', "data":
                    {
                        "Loan amount": new_loan.loan_amount,
                        "Duration": new_loan.duration,
                        "Rate of Interest": new_loan.roi,
                        "EMI": new_loan.emi,
                        "Total amount to be paid": new_loan.total_payable_amount,
                        "Loan Type": get_key(new_loan.loan_type, LOAN_TYPES),
                        "Created on ": new_loan.create_timestamp
                    }
                    })


@app.route("/register_Customer", methods=["POST"])
def register_Customer():
    """Endpoint to register/add more users to the system"""
    data = request.get_json()
    new_user = Users(data["username"], data["email"],
                     data['phone'], data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'Message': 'Your Account has been added successfully !'})
