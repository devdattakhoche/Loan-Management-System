from termcolor import colored
from requests.auth import _basic_auth_str
import traceback
import unittest
import time
import requests

class PopulateTests(unittest.TestCase):
    API_URL = "http://127.0.0.1:5000/"
    customer_access_tokens = []
    admin_access_tokens=[]
    agent_ids = []
    agent_access_tokens=[]
    new_loans_ids=[]

    def test_1_register_customer(self):
        
        details = [{'username': 'Customer1','password':'Customer*1','email':'Customer1@gmail.com','phone':'Customer1'},
                    {'username': 'Customer2','password':'Customer*2','email':'Customer2@gmail.com','phone':'Customer2'},
                    {'username': 'Customer3','password':'Customer*3','email':'Customer3@gmail.com','phone':'Customer3'}
                    ]
        ## Just to populate the database
        try:
            for i in details:
                resp=requests.post("{}/{}".format(self.API_URL,"register_Customer"),json=i)
        
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(resp.json()), 1)
            time.sleep(1)
            print(colored("\u2713 test_1 Passed....OK","green"))
        except Exception as ex:
            print(ex)
            print(colored("\u2717 test_1 Failed....Failed","red"))
        
    def test_2_register_agent(self):
        details = [{'username': 'Agent1','password':'Agent*1','email':'Agent1@gmail.com','phone':'Agent1'},
                    {'username': 'Agent2','password':'Agent*2','email':'Agent2@gmail.com','phone':'Agent2'}
                    ]
        ## Just to populate the database
        for i in details:
        
            resp=requests.post("{}/{}".format(self.API_URL,"register_Agent"),json=i)
        try :
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(resp.json()), 1)
            time.sleep(1)
            print(colored("\u2713 test_2 Passed....OK","green"))
        except Exception as ex:
            print(ex)
            print(colored("\u2717 test_1 Failed....Failed","red"))
    def test_3_login_user(self):
        details = [{'username': 'Customer1','password':'Customer*1'},
                    {'username': 'Customer2','password':'Customer*2'},
                    {'username': 'Customer3','password':'Customer*3'}
                    ]
        try:    
            for i in details: 
                resp=requests.post("{}/{}".format(self.API_URL,"login"),headers={"Authorization": _basic_auth_str(i['username'], i['password'])},)
                data=resp.json()

                self.customer_access_tokens.append( data['token']) 

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(resp.json()), 1)
            print(colored("\u2713 test_3 Passed....OK","green"))
        except Exception as ex:
            print(traceback.print_exc())
            print(colored("\u2717 test_3 Failed....Failed","red"))

    def test_4_new_loan(self):
        details = [{"loan_amount":10000,"duration":12,"loan_type":"Home_loan"},
                    {"loan_amount":20000,"duration":24,"loan_type":"Car_loan"},
                    {"loan_amount":30000,"duration":36,"loan_type":"Personal_loan"}
                    ]
        try:
            for i in range(3): 
                resp=requests.post("{}/{}".format(self.API_URL,"new_loan"),headers={"x-access-token":self.customer_access_tokens[i]},json=details[i])

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(resp.json()), 2)
            print(colored("\u2713 test_4 Passed....OK","green"))
        except Exception as ex:
            print(traceback.print_exc())
            print(colored("\u2717 test_4 Failed....Failed","red"))
        
    def test_5_Agent_login_without_admin_approval(self):

        '''
        Test should no login the agent as the agent isn't approved the admin.
        Unlsess and until admin doesn't approve agent , agent can no longer perform any operations
        ''' 
        try:
            resp=requests.post("{}/{}".format(self.API_URL,"login"),headers={"Authorization": _basic_auth_str("Agent1", "Agent*1")})
        
            self.assertEqual(resp.status_code, 401)
            self.assertTrue(b'agent is not approved',resp.content)
            print(colored("\u2713 test_5 Passed....OK","green"))
        except Exception as ex:
            print(traceback.print_exc())
            print(colored("\u2717 test_5 Failed....Failed","red"))
            pass

    
    def test_6_Admin_login(self):

        try:
            resp=requests.post("{}/{}".format(self.API_URL,"login"),headers={"Authorization": _basic_auth_str("Admin", "Adminpass")})
            self.admin_access_tokens.append(resp.json()['token'])
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(b'token' in resp.content)
            print(colored("\u2713 test_6 Passed....OK","green"))
        except Exception as ex:
            print(ex)
            print(colored("\u2717 test_6 Failed....Failed","red"))

    
    def test_7_all_agent_applications(self):
        try:
            resp=requests.get("{}/{}".format(self.API_URL,"all_Agent_applications"),headers={"x-access-token":self.admin_access_tokens[0]})
            self.assertEqual(resp.status_code, 200)
            for i in resp.json()["Unapproved_agents"]:
                self.agent_ids.append(i['id'])
            self.assertTrue(b'Unapproved_agents' in resp.content)
            print(colored("\u2713 test_7 Passed....OK","green"))
        except Exception as ex:
            print(ex)
            print(colored("\u2717 test_7 Failed....Failed","red"))

    
    def test_8_approve_agent_application(self):
        '''
        Approving agents from agent id which was previously unapproved

        '''
        try:
            for i in self.agent_ids:
                resp=requests.get("{}/{}".format(self.API_URL,"/approve_agent/"+str(i)+""),headers={"x-access-token":self.admin_access_tokens[0]})
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(b'Message' in resp.content)
            print(colored("\u2713 test_8 Passed....OK","green"))
        except Exception as ex:
            print(ex)
            print(colored("\u2717 test_8 Failed....Failed","red"))
    
if __name__ == '__main__':
    unittest.main()