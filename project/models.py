from project.constants import LOAN_STATUS, LOAN_TYPES, ROI, USERTYPE
from werkzeug.security import generate_password_hash
import datetime
import uuid
from project.app import db


class Loan_update_history(db.Model):
    """ Loan update model """
    __tablename__ = "Loan_update_history"

    id = db.Column(db.Integer, primary_key=True)
    original_loan_id = db.Column(db.Integer, db.ForeignKey("Loans.id"))
    loan_type = db.Column(db.Integer,  nullable=False)
    loan_amount = db.Column(db.Float,  nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    state = db.Column(db.Integer, nullable=False)
    create_timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, loan_amount, duration, loan_id, state=LOAN_STATUS['New'], loan_type=LOAN_TYPES['Home_loan']):
        self.loan_type = loan_type
        self.loan_amount = loan_amount
        self.duration = duration
        self.original_loan_id = loan_id
        self.state = state
        self.create_timestamp = datetime.datetime.now(datetime.timezone.utc)


class Loan(db.Model):
    """ Loan model """
    __tablename__ = "Loans"

    id = db.Column(db.Integer, primary_key=True)
    loan_type = db.Column(db.Integer,  nullable=False)
    loan_amount = db.Column(db.Float,  nullable=False)
    roi = db.Column(db.Float,  nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    state = db.Column(db.Integer, nullable=False)
    emi = db.Column(db.Float, nullable=False)
    total_payable_amount = db.Column(db.Float, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("Users.id"))
    agent_id = db.Column(db.Integer, default=None)
    last_updated_by = db.Column(db.Integer, db.ForeignKey("Users.id"))
    create_timestamp = db.Column(db.DateTime, nullable=False)
    update_timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, loan_amount, duration, customer_id, state=LOAN_STATUS['New'], loan_type=LOAN_TYPES['Home_loan']):
        self.loan_type = loan_type
        self.roi = ROI[loan_type]
        self.loan_amount = loan_amount
        self.duration = duration
        self.state = state
        self.emi = loan_amount * (ROI[loan_type]/(12*100)) * (
            (1+(ROI[loan_type]/(12*100)))**duration)/((1+(ROI[loan_type]/(12*100)))**duration - 1)
        self.total_payable_amount = loan_amount + \
            (loan_amount*ROI[loan_type]/(12*100)*duration)
        self.customer_id = customer_id
        self.last_updated_by = customer_id
        self.agent_id = (-1)
        self.create_timestamp = datetime.datetime.now(datetime.timezone.utc)
        self.update_timestamp = datetime.datetime.now(datetime.timezone.utc)

    def __repr__(self):
        return "<Loan {}>".format(self.id)


class Users(db.Model):
    """ Users model """
    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(64), unique=True)
    username = db.Column(db.String(64), index=True,
                         nullable=False, unique=True)
    user_type = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), index=True, nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    password_hash = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, nullable=False)
    approved = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, username, email, phone, password, user_type=USERTYPE['Customers'], approved=True):
        self.public_id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.phone = phone
        self.password_hash = generate_password_hash(
            password, method='pbkdf2:sha256')
        self.user_type = user_type
        self.timestamp = datetime.datetime.now(datetime.timezone.utc)
        self.approved = approved

    def __repr__(self):
        return "<User {}>".format(self.username)
