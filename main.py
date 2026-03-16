#Requests module to handle API 
import requests
import requests_oauthlib
import json
from requests.auth import AuthBase
import logging 
import time
from dotenv import load_dotenv
import os


#Custom Class
import config
from custom_token_auth import TokenAuth
from sqlfunctions import sql

class functions():

    #Get API Access Token 
    def get_access_token():
        data = {
        "grant_type": f"{os.getenv('cfg_granttype')}",
        "client_id": f"{os.getenv('cfg_cid')}",
        "client_secret": f"{os.getenv('cfg_cse')}",
        "scope": f"{os.getenv('cfg_scope')}"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(f"{os.getenv('cfg_accessurl')}", data=data, headers=headers)
        response.raise_for_status()
        #Maybe make logging inside SQL to enable reporting on common rds servers in Drain mode? 
        #Maybe make monthly log of top 3 servers to be manually reviewed? 
        #Maybe make the SQL tables enable better visilibilty of the server propblems 
        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info.get('access_token')
            return token_info, access_token
        else:
            error_response = (f"Error {response.status_code}: {response.text}")
            print(error_response)
            return error_response, access_token

    #Obtain All RDS Devices from API 
    def get_devices(access_token):
        try: 
                response = requests.get(f"{os.getenv('cfg_apidevices')}",
                                        auth=TokenAuth(access_token))
                                        #headers=headers)
                if response.status_code == 200: 
                    print(response)
                    response_info = response.json()
                    return response_info
                elif response.status_code == 429: # Handle Rate Limiting
                    retry_after = int(response.headers.get("Retry-After", 5))
                    print(f"Rate limited. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
                else: 
                    error_response = (f"Error {response.status_code}: {response.text}")
                    print(error_response)
                    return error_response
        except Exception as e: 
            return 
    
    #Obtain all TECHNICIAN Users from API 
    def get_users(access_token):
        try: 
                response = requests.get(f"{os.getenv('cfg_apiusers')}",
                                        auth=TokenAuth(access_token))
                                        #headers=headers)
                if response.status_code == 200: 
                    print(response)
                    response_info = response.json()
                    return response_info                    
                elif response.status_code == 429: # Handle Rate Limiting
                    retry_after = int(response.headers.get("Retry-After", 5))
                    print(f"Rate limited. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
                else: 
                    error_response = (f"Error {response.status_code}: {response.text}")
                    print(error_response)
                    return error_response
        except Exception as e: 
            return 


class main():
    def __init__(self):
        super().__init__()
        logging.basicConfig(filename='data.log', level=logging.DEBUG)
        # cfg_oauthtype = os.getenv('cfg_oauthtype')
        # cfg_granttype = os.getenv('cfg_granttype') #Change this to Auth Code
        # cfg_accessurl = os.getenv('cfg_accessurl')
        # cfg_apiusers = os.getenv('cfg_apiusers')
        # cfg_apidevices = os.getenv('cfg_apidevices')
        # cfg_cid = os.getenv('cfg_cid')
        # cfg_cse = os.getenv('cfg_cse')
        # cfg_scope = os.getenv('cfg_scope')
        # target_instance = os.getenv('target_instance')
        # target_db = os.getenv('target_db')
        # driver = os.getenv('driver')

        num_devices: int = 0
        bool_check: bool = None
        sql_device_data: list = []
        num_users: int = 0
        sql_users_data: list = []
        
        
        #Attempt Connection, obtain API Access Token 
        token_info, access_token = functions.get_access_token()
        print(token_info)
        if access_token:
            print("Attempting to find devices data...")
            get_devices_list = functions.get_devices(access_token)
            for i in get_devices_list:
                get_devices_dict: dict = get_devices_list[num_devices]
                num_devices += 1
                #Filter out unneccersary servers
                if get_devices_dict.get('system', {}).get('domainRole') == 'Member Server':
                    if 'RDS' in get_devices_dict['systemName']:
                        devices_row = {'id': get_devices_dict['id'], 
                               'uid': get_devices_dict['uid'], 
                               'systemName': get_devices_dict['systemName'],
                               'domainRole':get_devices_dict.get('system', {}).get('domainRole')}
                        #print(get_devices_dict)
                        sql_device_data.append(devices_row)
            #Add RDS Devices to SQL 
            add_devices_sql = sql.add_devices_sql(sql_device_data, bool_check)
        if access_token:
            get_users_list = functions.get_users(access_token)
            for i in get_users_list:
                get_users_dict: dict = get_users_list[num_users]
                num_users += 1
                fullname = get_users_dict['firstName'] + ' ' + get_users_dict['lastName']
                users_row = {'id': get_users_dict['id'],
                             'name': fullname, 
                             'email': get_users_dict['email'],
                             'userType': get_users_dict['userType']}
                sql_users_data.append(users_row)
            #Add TECHNICIAN Users to SQL
            add_users_sql = sql.add_users_sql(sql_users_data, bool_check)
        #if access_token: 
            #print(sql_device_data)
            
            
                

if __name__ == '__main__':
    load_dotenv()
    run = main()

'''
        num: int = 0
        if access_token:
            print("Attempting to find data...")
            get_devices_list = functions.get_devices(access_token)
            for i in get_devices_list:
                get_devices_dict: dict = get_devices_list[num]
                num += 1
                print(get_devices_dict['id'], get_devices_dict['firstName'], get_devices_dict['lastName'])
'''


    ##Used for testing, obtains list of users from API## 
    # def get_users(access_token):
    #     headers = {
    #         "accept": "application/json"
    #     }
    #     response = requests.get(f"{config.cfg_apiusers}",
    #                             auth=TokenAuth(access_token))
    #                             #headers=headers)
    #     response.status_code
    #     print(response)
    #     response_info = response.json()
    #     return response_info
            #     num += 1
            #     data = get_devices_dict['id'], get_devices_dict['uid'], get_devices_dict['systemName'], get_devices_dict.get('system', {}).get('domainRole')
            #     #print(data)
            #     #Filter out unneccersary servers
            #     if get_devices_dict.get('system', {}).get('domainRole') == 'Member Server':
            #         if 'RDS' in get_devices_dict['systemName']:
            #             data_filtered: list = [get_devices_dict['id'], get_devices_dict['uid'], get_devices_dict['systemName'], get_devices_dict.get('system', {}).get('domainRole')]
            #             print(data_filtered)
            # print("Finished data_filter, running sql")
            # add_devices_sql = sql.add_devices_sqll(data_filtered, bool_check)



            #### Used for testing, for users list not devices, use as reference now working ###
            # get_devices_list = functions.get_users(access_token)
            # for i in get_devices_list:
            #     get_devices_dict: dict = get_devices_list[num]
            #     num += 1
            #     name: str = get_devices_dict['firstName'] + " " + get_devices_dict['lastName']
            #     add_users_sql = sql.add_users_sql(get_devices_dict['id'], name, get_devices_dict['userType'], bool_check)
            #     print(add_users_sql)

