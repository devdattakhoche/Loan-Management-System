import unittest
import requests
from requests.auth import _basic_auth_str
from termcolor import colored

class ApiTests(unittest.TestCase):
    API_URL = "http://127.0.0.1:5000/"
    resp=requests.post("{}/{}".format(API_URL,"login"),headers={"Authorization": _basic_auth_str("Admin", "Adminpass")})
    admin_access_token=(resp.json()['token'])
    resp=requests.post("{}/{}".format(API_URL,"login"),headers={"Authorization": _basic_auth_str("Agent1", "Agent*1")})
    agent_access_token=(resp.json()['token'])
    resp=requests.post("{}/{}".format(API_URL,"login"),headers={"Authorization": _basic_auth_str("Customer2", "Customer*2")})
    customer_access_token=(resp.json()['token'])
    try:
        loan_id =requests.get("{}/{}".format(API_URL,"getloans?status=New"),headers={"x-access-token": agent_access_token}).json()['Loans'][0]['id']
    except Exception :
        loan_id =requests.get("{}/{}".format(API_URL,"getloans?status=Approved"),headers={"x-access-token": agent_access_token}).json()['Loans'][0]['id']
    previos_loan_id = loan_id


    def test_15_all_Customers(self):

        '''
        Onlu admin and agent will be able to view Customers list
        Customer is not allowed to view other Customer details
        '''
        try:
            resp=requests.get("{}/{}".format(self.API_URL,"all_Customers"),headers={"x-access-token": self.admin_access_token})    
            self.assertEqual(resp.status_code,200)
            resp=requests.get("{}/{}".format(self.API_URL,"all_Customers"),headers={"x-access-token": self.agent_access_token})    
            self.assertEqual(resp.status_code,200)
            resp=requests.get("{}/{}".format(self.API_URL,"all_Customers"),headers={"x-access-token": self.customer_access_token})    
            self.assertEqual(resp.status_code,401)
            print(colored("\u2713 test_15 Passed....OK","green"))
        except:
            print(colored("\u2717 test_15 Failed....Failed","red"))

    
    def test_16_all_Users(self):

        '''
        Only admin  will be able to view all users list
        Customer and agnets are not allowed to view other Customer details
        '''
        try:
            resp=requests.get("{}/{}".format(self.API_URL,"all_users"),headers={"x-access-token": self.admin_access_token})    
            self.assertEqual(resp.status_code,200)
            resp=requests.get("{}/{}".format(self.API_URL,"all_users"),headers={"x-access-token": self.agent_access_token})    
            self.assertEqual(resp.status_code,401)
            resp=requests.get("{}/{}".format(self.API_URL,"all_users"),headers={"x-access-token": self.customer_access_token})    
            self.assertEqual(resp.status_code,401)
            print(colored("\u2713 test_16 Passed....OK","green"))
        except:
            print(colored("\u2717 test_16 Failed....Failed","red"))

    def test_17_make_loan_request_on_behalf_of_customer(self):

        '''
        Loan request on the behalf of customer can only be made by agent
        '''    
        try:
            resp=requests.get("{}/{}".format(self.API_URL,"request_loan/"+str(self.loan_id)),headers={"x-access-token": self.admin_access_token})    
            self.assertEqual(resp.status_code,401)

            resp=requests.get("{}/{}".format(self.API_URL,"request_loan/"+str(self.loan_id)),headers={"x-access-token": self.agent_access_token})    
            self.assertEqual(resp.status_code,200)
            self.assertTrue(b'Request to Admin on behalf of this customer is successfully made by you.' in resp.content)
            
            resp=requests.get("{}/{}".format(self.API_URL,"request_loan/"+str(self.loan_id)),headers={"x-access-token": self.customer_access_token})    
            self.assertEqual(resp.status_code,401)
            print(colored("\u2713 test_17 Passed....OK","green"))
        except:
            print(colored("\u2717 test_17 Failed....Failed","red"))

    def test_18_admin_approve_loan(self):

        '''
        Loans can only be approved by admin
        '''    
        try:
            resp=requests.get("{}/{}/{}".format(self.API_URL,"approve_loan",str(self.loan_id)),headers={"x-access-token": self.admin_access_token})    
            self.assertEqual(resp.status_code,200)
            self.assertTrue(b'The Loan has been successfully approved!!' in resp.content)
            
            resp=requests.get("{}/{}/{}".format(self.API_URL,"approve_loan",str(self.loan_id)),headers={"x-access-token": self.agent_access_token})    
            self.assertEqual(resp.status_code,401)
            
            
            resp=requests.get("{}/{}/{}".format(self.API_URL,"approve_loan",str(self.loan_id)),headers={"x-access-token": self.customer_access_token})    
            self.assertEqual(resp.status_code,401)
            self.previos_loan_id = self.loan_id
            print(colored("\u2713 test_18 Passed....OK","green"))
            try:
                self.loan_id =requests.get("{}/{}".format(self.API_URL,"getloans?status=New"),headers={"x-access-token": self.agent_access_token}).json()['Loans'][0]['id']
            except Exception :
                self.loan_id =requests.get("{}/{}".format(self.API_URL,"getloans?status=Approved"),headers={"x-access-token": self.agent_access_token}).json()['Loans'][0]['id']
        except:
            print(colored("\u2717 test_18 Failed....Failed","red"))

    def test_19_get_loan_by_approved_filter(self):

        '''
        
        all the approved loans can be seen by admin and agent , but user will only see his particular approved requests
        sending query parameters to /getloans will filter the loans accordinly


    
        '''    
        try:
            resp=requests.get("{}/{}".format(self.API_URL,"getloans"),headers={"x-access-token": self.admin_access_token},params={'status':'Approved'})    
            self.assertEqual(resp.status_code,200)
        
            resp=requests.get("{}/{}".format(self.API_URL,"getloans"),headers={"x-access-token": self.agent_access_token},params={'status':'Approved'})    
            self.assertEqual(resp.status_code,200)
            print(colored("\u2713 test_19 Passed....OK","green"))
            
        except:
            print(colored("\u2717 test_19 Failed....Failed","red"))
            
    def test_20_Loans_which_are_approved_cannot_be_edited(self):

        '''
        Loans can only be edited by the agent    
        Niether admin nor customer has this authorisation

        if the loan is approved , then can't do any changes to the system
        '''    
        editdata = {
            'loan_amount' : 2000,
            'duration' : 5
        }
        try:

            resp=requests.post("{}/{}/{}".format(self.API_URL,"edit_loan",self.previos_loan_id),headers={"x-access-token": self.admin_access_token},json=editdata)    
            self.assertEqual(resp.status_code,401)
        
            resp=requests.post("{}/{}/{}".format(self.API_URL,"edit_loan",self.previos_loan_id),headers={"x-access-token": self.agent_access_token},json=editdata)    
            self.assertTrue(b'This Loan has already been approved by the admin!! It is immutable now.' in resp.content)
            print(colored("\u2713 test_20 Passed....OK","green"))
        except:
            print(colored("\u2717 test_20 Failed....Failed","red"))

if __name__ == '__main__':
    unittest.main()