# Loan Management system 


## Installing

```
$ docker-compose build
$ docker-compose up -d
$ docker-compose run app
```

## Running the tests

There are three types of tests :  <br />
1. Setup test :- These tests correspond to all the setup of dummy data  (login and registrations are checked here)
2. Security tests :  These test are responsible for conducting cross account actions that is to see role based acces of api point <br />
  * eg :- Customer shouldn't access admin roles etc.
3. Api tests : These correspond to whether all the api are working fine and aren't returing unexpected things

<strong>NOTE :Setup tests can only be run once , as the dummy data can't be inserted again due to primary key restrictions</strong>

```
$ docker-compose exec app python project/tests/tests_setup.py -----> Run at the first (only one time)
$ docker-compose exec app python project/tests/tests_security.py
$ docker-compose exec app python project/tests/tests_api.py
```
```
To test again from start and empty the database :-

$ docker-compose exec app python manage.py recreate_db

```

### Tech related Details

* Tech Stack :
  * Flask
  * Docker
  * unittest
  * pyJWT
  * postgres
  * SQLAlchemy


* Authentication for the API endpoint is done using JWT.
* Evey api request will be authoured with the provided JWT.
* The passwords are hashed using pbkdf2:sha256 and with a salt of lenght 8.
* Timezone issue is handled by putting UTC timestamp in the databset


### Workflow
* There are three roles in the system :- admin ,Customer ,agent
* Customer can register into the system 
* All three user have to login before performing any action with username and password which will return token of validity 1 hour.
* If the validity of the token finished the users needs to login again to get a valid token
* Agent can also register ,which send a request to the admin .
* Admin can approve agents into the system post which they can also login into the system
* Customer has the authority to:
  * Apply for a new loan , Rater of interest changes with the type of loan he has selected
  * View his or her loan (Cannot view other customers loans)
  * View his or her loan history

* Agent is supposed to forwrd the loan request on the behalf of customer to the admin ,if and only if the agent is approved by the admin
* Agent has the authority to:
  * View all Customers list
  * Only agent can edit the loan only and only if the loan is not in approved state
  * View edit hisotry of any particular loan object
  * Make request to admin on the behalf of the customer
  * View all loans
  * Filter all loans by approved status, new status,rejected status
  * Filter loans start date to end date (Either create date or update date)
  * View his particular requests which he has made to the admin


* Admin is supposed to manage the system by modifying loan state and accepting or rejecting agents application
* Admin has the authority to:
  * View all Users
  * Approve and reject loans 
  * Approve agents into the system 
  * View all approved agents and pending agents seperatly
  * View all agents applications for permission into the system
  * View all loan requests made by particular agent on the behalf of customer
  * View edit hisotry of any particular loan object
  * View all loans
  * Filter all loans by approved status, new status,rejected status
  * Filter loans start date to end date (Either create date or update date)
  * View all Customers in the system


## Endpoints
### Customer 

POST Methods :
```
/register_Customer

data = {
"username" : "yourusername",
"password" : "yourpassword",
"email" : "email",
}

```
```
/login
Basic Auth header
username and password required
```
```
/new_loan

data = {
"loan_amount" : 10000,
"loan_type" : "Home_loan",
"duration" : 10
}
```
GET Methods :
```
/getloans
params = {"status" : "Approved" or "Rejected" or "New"} (leave blank to see all loans)
```
### Agent

POST Methods : 
```
/register_Agent

data = {
"username" : "yourusername",
"password" : "yourpassword",
"email" : "email",
}
```

```
/login
Basic Auth header
username and password required
```
```
/edit_loan/<loan_id>

data = {
"loan_amount" : 2000
....
}
```

GET Methods:
```
/all_Customers
```

```
/getloans
params = {"status" : "Approved" or "Rejected" or "New"} (leave blank to see all loans)
```

```
Request loan tp admin on behalf of customers
/request_loan/<loan_id>
```
```
All the requests made by that agent (loan requests on behalf of customer)
/loan_Requests_by_agent
```
```
View edit history of particular loan
/view_loan_history/<loan_id>
```
```
/filter-by-update-date
params = {
"start_date" : "1985-01-17",
"end_date" : "2025-09-17"
}
```


```
/filter-by-create-date
params = {
"start_date" : "1985-01-17",
"end_date" : "2025-09-17"
}
```

### Admin

POST Methods

```
/login
Basic Auth header
username and password required
```

GET Methods


```
/all_Users
```
```
/all_Customers
```
```
/all_Agents
```
```
Returns agents which have registered but aren't approved by admin to enter the system
/all_Agent_applications
```
```
Approve agent to allow him to enter the system
/approve_agent/<agent_id>
```

```
Returns all the loan requests made by the particular agent
/Agent_loan_requests/<agent_id>
```
```
Approve loan
/approve_loan/<loan_id>
```
```
Reject loan
/reject_loan/<loan_id>
```
```
View edit history of particular loan
/view_loan_history/<loan_id>
```

```
/filter-by-update-date
params = {
"start_date" : "1985-01-17",
"end_date" : "2025-09-17"
}
```

```
/getloans
params = {"status" : "Approved" or "Rejected" or "New"} (leave blank to see all loans)
```


```
/filter-by-create-date
params = {
"start_date" : "1985-01-17",
"end_date" : "2025-09-17"
}
```
