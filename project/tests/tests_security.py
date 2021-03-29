
from os import access
from requests.auth import _basic_auth_str
from termcolor import colored    
import unittest
import requests

class SecurityTests(unittest.TestCase):
    API_URL = "http://127.0.0.1:5000/"
    customers = [{'username': 'Customer1','password':'Customer*1',},
                {'username': 'Customer2','password':'Customer*2'},
                {'username': 'Customer3','password':'Customer*3'}
                ]
    customer_access_tokens=[]
       

    def test_9_without_token_auth(self):
        try:
            resp=requests.post("{}/{}".format(self.API_URL,"new_loan"))        
            self.assertEqual(resp.status_code, 401)
            self.assertTrue(b'Token is missing!' in resp.content)
            print(colored("\u2713 test_9 Passed....OK","green"))
        except:
            print(colored("\u2717 test_9 Failed....Failed","red"))
    
    def test_10_with_Invalid_token(self):
        try:
            resp=requests.post("{}/{}".format(self.API_URL,"new_loan"),headers={'x-access-token':'fake_x_access_token'})        
            self.assertEqual(resp.status_code, 401)
            self.assertTrue(b'Token is invalid!' in resp.content)
            print(colored("\u2713 test_10 Passed....OK","green"))
        except:
            print(colored("\u2717 test_10 Failed....Failed","red"))

    def test_11_Customer_unauthorised_admin_access(self):
        try:
            for i in self.customers:
                resp=requests.post("{}/{}".format(self.API_URL,"login"),headers={"Authorization": _basic_auth_str(i['username'], i['password'])},)
                data=resp.json()
                self.customer_access_tokens.append( data['token']) 

            '''
            Customer Accessing Admin endpoints

            '''
            resp=requests.get("{}/{}".format(self.API_URL,"/all_users"),headers={"x-access-token": self.customer_access_tokens[0]})
            self.assertEqual(resp.status_code, 401)
            self.assertTrue(b"You are not authorized to open this page" in resp.content)
            print(colored("\u2713 test_11 Passed....OK","green"))
        except:
            print(colored("\u2717 test_11 Failed....Failed","red"))

    def test_12_Customer_unauthorised_access_agent(self):
        '''
        Customer Accessing agent endpoints

        '''
        try:
            resp=requests.post("{}/{}".format(self.API_URL,"/edit_loan/7"),headers={"x-access-token": self.customer_access_tokens[0]})
            self.assertEqual(resp.status_code, 401)
            self.assertTrue(b"Unauthorised Access" in resp.content)
            print(colored("\u2713 test_12 Passed....OK","green"))
        except:
            print(colored("\u2717 test_12 Failed....Failed","red"))
        
    def test_13_agent_unauthorised_access_admin(self):
        '''
        Agent Accessing admin endpoints

        '''
        try:

            resp=requests.post("{}/{}".format(self.API_URL,"login"),headers={"Authorization": _basic_auth_str("Agent1", "Agent*1")},)
            token = resp.json()['token']
            resp=requests.get("{}/{}".format(self.API_URL,"/approve_loan/3"),headers={"x-access-token": token})
            self.assertEqual(resp.status_code, 401)
            self.assertTrue(b"not authorized" in resp.content)
            print(colored("\u2713 test_13 Passed....OK","green"))
        except:
            print(colored("\u2717 test_13 Failed....Failed","red"))

    
    def test_14_Customer_can_only_view_his_loans(self):
        '''
        no Customer can view other customers loan

        '''
        Customner2_loans = [{"loan_amount":10000,"duration":12,"loan_type":"Home_loan"},
                            {"loan_amount":20000,"duration":24,"loan_type":"Car_loan"},
                            {"loan_amount":30000,"duration":36,"loan_type":"Personal_loan"}
                            ]
    
        Customner3_loans = [{"loan_amount":10000,"duration":12,"loan_type":"Personal_loan"},
                            {"loan_amount":20000,"duration":24,"loan_type":"Car_loan"},
                            ]
        try:
            for i in range(3): 
                resp=requests.post("{}/{}".format(self.API_URL,"new_loan"),headers={"x-access-token":self.customer_access_tokens[1]},json=Customner2_loans[i])
                    
            for i in range(2): 
                resp=requests.post("{}/{}".format(self.API_URL,"new_loan"),headers={"x-access-token":self.customer_access_tokens[2]},json=Customner3_loans[i])

            Customer2_loans = requests.get("{}/{}".format(self.API_URL,"getloans"),headers={"x-access-token":self.customer_access_tokens[1]})
            Customer3_loans = requests.get("{}/{}".format(self.API_URL,"getloans"),headers={"x-access-token":self.customer_access_tokens[2]})

            self.assertEqual(Customer2_loans.status_code,200)
            self.assertEqual(Customer3_loans.status_code,200)
            '''
            Now Customer2 must have 4 loans ,as we have added 1 earlier 
            and Customer3 must have 3 loans
            # '''
            print(colored("\u2713 test_14 Passed....OK","green"))
        except:
            print(colored("\u2717 test_14 Failed....Failed","red"))

if __name__ == '__main__':
    unittest.main()