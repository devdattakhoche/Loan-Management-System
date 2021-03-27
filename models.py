from logging import NullHandler
from werkzeug.security import generate_password_hash
import datetime
import uuid
from flask import app
from app import  db , bcrypt
from flask_sqlalchemy import SQLAlchemy 

USERTYPE = {

    'Customers' : 0,
    'Admin' : 1,
    'Agent' : 2,
}
LOAN_STATUS = {

    'Approved' : 0,
    'Rejected' : 1,
    'New' : 2,
}

LOAN_TYPES = {
    'Home_loan':0,
    'Personal_loan':1,
    'Car_loan':2,
    'Educational_loan':4,
}

ROI = {
    0:6.90,
    1:10.75,
    2:7.25,
    3:14.7,
}


class Loan(db.Model):
    """ Loan model """
    __tablename__ = "Loans"

    id = db.Column(db.Integer, primary_key=True)
    loan_type = db.Column(db.Integer,  nullable=False)
    loan_amount = db.Column(db.Float,  nullable=False)
    roi = db.Column(db.Float,  nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    state = db.Column(db.Integer, nullable=False)
    emi = db.Column(db.Float,nullable=False)
    total_payable_amount = db.Column(db.Float,nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("Users.id"))
    agent_id = db.Column(db.Integer,default=None)
    last_updated_by = db.Column(db.Integer, db.ForeignKey("Users.id"))
    create_timestamp = db.Column(db.DateTime, nullable=False)
    update_timestamp = db.Column(db.DateTime, nullable=False)


    def __init__(self, loan_amount, duration,customer_id, state=LOAN_STATUS['New'], loan_type=LOAN_TYPES['Home_loan'] ):
        self.loan_type = loan_type
        self.roi = ROI[loan_type]
        self.loan_amount = loan_amount
        self.duration = duration
        self.state = state
        self.emi = loan_amount * (ROI[loan_type]/(12*100)) * ((1+(ROI[loan_type]/(12*100)))**duration)/((1+(ROI[loan_type]/(12*100)))**duration - 1)
        self.total_payable_amount = (loan_amount * ROI[loan_type] * ((1+ROI[loan_type])**duration)/((1+ROI[loan_type])**duration - 1)) * duration
        self.customer_id = customer_id
        self.last_updated_by = customer_id
        self.agent_id = (-1)
        self.create_timestamp = datetime.datetime.utcnow().date()
        self.update_timestamp = datetime.datetime.utcnow().date()


    
    def __repr__(self): 
        return "<Loan {}>".format(self.id)






class Users(db.Model):
    """ Users model """
    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(64),unique=True)
    username = db.Column(db.String(64), index=True, nullable=False, unique=True)
    user_type = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), index=True, nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    password_hash = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, nullable=False)
    approved = db.Column(db.Boolean, nullable=False,default=True)

    
    def __init__(self, username, email, phone, password, user_type=USERTYPE['Customers'],approved = True):
        # bcrypt.gensalt(10)
        self.public_id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.phone = phone
        self.password_hash = generate_password_hash(password,method='pbkdf2:sha256')
        self.user_type = user_type 
        self.timestamp = datetime.datetime.utcnow().date()
        self.approved = approved


    def __repr__(self):
        return "<User {}>".format(self.username)

