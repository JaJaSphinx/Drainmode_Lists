#All config now in .env 
#All references/documentation now here.

''' Searching for the relevant API calls 
Acquire User ID = {{baseUrl}}/api/v2/users/?userType=TECHNICIAN
--- Provides details of user including first name, last name and email 
--- Cannot filter to id so filtering userType = TECHNICIAN and then will use python to find exact user 
{
        "id": 31,
        "uid": "d6917463-fd25-4cdc-be23-ccaee033f180",
        "firstName": "Lewis", 
        "lastName": "Hatton",
        "email": "lewis.hatton@knightsplc.com",
        "phone": "+447500551255",
        "enabled": true,
        "administrator": false,
        "permitAllClients": false,
        "notifyAllClients": true,
        "mustChangePw": false,
        "mfaConfigured": true,
        "userType": "TECHNICIAN",
        "invitationStatus": "REGISTERED",
        "organizationId": null,
        "tags": null,
        "fields": null
    },

    
Acquire Device ID = {{baseUrl}}/api/v2/devices-detailed?df=id%3D5948
 --- df can be used to filter results, using device id (df=id%3D'DeviceIDNumber')

    {
        "id": 5948,
        "uid": "a8b0c9d0-aaf6-422e-975c-aef27c935de2",
        "organizationId": 13,
        "locationId": 33,
        "nodeClass": "WINDOWS_SERVER",
        "nodeRoleId": 1002,
        "rolePolicyId": 57,
        "policyId": 243,
        "approvalStatus": "APPROVED",
        "offline": false,
        "systemName": "KNI-1FSRDS-001",
        "dnsName": "KNI-1FSRDS-001.knightandsons.co.uk",
        "created": 1743088826.524929000,
        "lastContact": 1759136775.901000000,
        "lastUpdate": 1759136775.901000000,
        "tags": [],
        "ipAddresses": [
            "10.10.88.4"
        ],
        "macAddresses": [
            "00:15:5D:FF:8B:04"
        ],
        "publicIP": "212.57.253.242",
        "os": {
            "manufacturer": "Microsoft Corporation",
            "name": "Windows Server 2022 Standard Edition",
            "architecture": "64-bit",
            "lastBootTime": 1758761443.000000000,
            "buildNumber": "20348",
            "releaseId": "21H2",
            "servicePackMajorVersion": 0,
            "servicePackMinorVersion": 0,
            "locale": "en-GB",
            "language": "English",
            "needsReboot": false
        },
        "system": {
            "name": "KNI-1FSRDS-001",
            "manufacturer": "Microsoft Corporation",
            "model": "Virtual Machine",
            "biosSerialNumber": "7149-6004-6720-8372-7705-4830-48",
            "serialNumber": "7149-6004-6720-8372-7705-4830-48",
            "domain": "KNIGHTS",
            "domainRole": "Member Server",
            "numberOfProcessors": 1,
            "totalPhysicalMemory": 68913397760,
            "virtualMachine": true,
            "chassisType": "DESKTOP"
        },
        "memory": {
            "capacity": 68913397760
        },
        "processors": [
            {
                "architecture": "x64",
                "maxClockSpeed": 2694000000,
                "clockSpeed": 2694000000,
                "name": "Intel(R) Xeon(R) Gold 6258R CPU @ 2.70GHz",
                "numCores": 7,
                "numLogicalCores": 14
            }
        ],
        "volumes": [
            {
                "nodeId": 5948,
                "name": "C:",
                "label": "",
                "deviceType": "Local Disk",
                "fileSystem": "NTFS",
                "autoMount": false,
                "compressed": false,
                "capacity": 136559194112,
                "freeSpace": 60945354752,
                "serialNumber": "3EEA25BE"
            }
        ],
        "lastLoggedInUser": "KNIGHTS\\mree",
        "deviceType": "AgentDevice"

Acquire data from triggered condition = {{baseUrl}}/api/v2/device/:id/activities?activityType=ACTIONSET
 --- Need to find a way to filter inside API ideally not python otherwise will be poorly load balanced on each request 
 --- *Concern* It's mandatory to have the id, really it needs to be filtered by activityType and maybe sourceName but not forced to have the id, 
 --- *RES?* Use another query to find and add all id to list, then run this query on each device, if it's drain mode, move to the next steps, if not, move on. 
 ---- SQL Store Fields (Serv Name, Unique ID, ID): Add / Remove accordingly (KNI-SQL-DEV) - DB Name = NINJA_API_SYNC
 --- Cannot filter additional by sourceName or message so will have to filter through python 
 --- Provides details on triggered condition 
 --- Provides user ID 
 --- Provides Device ID 
 --- Needs activityTime to be converted (or made to not catch everything)
            "id": 347371446,
            "activityTime": 1759133165.953166000,
            "deviceId": 5948,
            "activityType": "ACTIONSET",
            "statusCode": "START_REQUESTED",
            "status": "Start Requested",
            "sourceConfigUid": "4e6ade9a-e196-4dbb-92f9-6b968bdc08be",
            "sourceName": "RDS - Drain Mode",
            "userId": 31,
            "message": "Scheduled automation 'RDS - Drain Mode' running on demand",
            "type": "Action Set"

----- Problems to figure out ----- 
 --- Issue: Query to Acquire data from triggered condition requires the device id, so unable to run this generally with the parameters of within 5 minutes for example filtered down by RDS - Drain Mode
     This causes the issue with the 1st step, if it needs to be specifically supplied per device ID it's going to run the query far to many times before it hits a catch, not an ethical solution 
     --- Achievable by running a query to generate a list of devices then running the next query to each device until a catch, but just super load heavy in theory
 --- Can we use the built in custom field condition triggered which is currently used to prompt this to run, providing the RDS server details which I can use to find the user who ran it with? 
     --- Need to find out how this operates but way less load heavy, negative is it's working inside the current SMTP which ideally I wanted to move away from


----- HOW TO MERGE THESE -----
 --- Start {{baseUrl}}/api/v2/device/:id/activities: Catch when this is ran, provide Device ID 
 --- Next {{baseUrl}}/api/v2/devices-detailed?df=id%3D5948: Find server name using Device ID, provide User ID 
 --- Next {{baseUrl}}/api/v2/users: Find username using User ID, merge all relevant data from each query and send via email. 





--- ALL THESE BELOW I DONT THINK ARE USEFUL --- 

{{baseUrl}}/api/v2/queries/custom-fields-detailed 
 --- Has the Device ID for filtering 
 --- Documents time/date for RDSDrainMode named rdsDrainModeTime 
 --- But User is null 

 {{baseUrl}}/api/v2/queries/custom-fields
 --- Probs useless over others, gives details less detailed than one above (does contain "rdsDrainModeTime": 1759136768000) does 
 --- No user data 

 {{baseUrl}}/api/v2/alerts
 --- Provides information surrounding alert we have in place for catching drain mode tickets (current setup)
 --- "message": "Custom Fields condition was matched: 'RDS - Server in Drain Mode'",
 --- Though SYSTEM does this, does not provide this info on json data 

 




{{baseUrl}}/api/v2/device-custom-fields
 --- Provides insight to Custom Fields
 --- endUserCustomization? null 
 --- 
         "entityType": "NODE",
        "scope": "NODE_ROLE",
        "definitionScope": [
            "NODE"
        ],
        "type": "DATE_TIME",
        "label": "Drain Mode Script Last Run",
        "description": "Shows when the Drain Mode script was last run to reference against the Activity log",
        "name": "rdsDrainModeTime",
        "technicianPermission": "READ_ONLY",
        "scriptPermission": "READ_WRITE",
        "apiPermission": "READ_WRITE",
        "content": {
            "customizeForEndUser": false,
            "endUserCustomization": null,
            "values": [],
            "required": false,
            "footerText": "Shows when the Drain Mode script was last run to reference against the Activity log",
            "tooltipText": "Shows when the Drain Mode script was last run to reference against the Activity log",
            "advancedSettings": {
                "dateFilters": {
                    "type": "NONE",
                    "selected": []
                }
            }
        },
        "system": false,
        "active": true,
        "createTime": 1677580158.344000000,
        "updateTime": 1678292878.418000000
'''

'''Cheat Sheet for Codes: 
200: Everything went okay, and the result has been returned (if any).
301: The server is redirecting you to a different endpoint. This can happen when a company switches domain names or changes an endpoint name.
400: The server thinks you made a bad request. This happens when you send incorrect data or make other client-side errors.
401: The server thinks you're not authenticated. Many APIs require login credentials, so this happens when the correct credentials are not sent.
403: The resource you're trying to access is forbidden. You don’t have the right permissions to see it.
404: The resource you tried to access wasn’t found on the server.
405: Client attempts to use an HTTP method that is not allowed by the server
503: The server is not ready to handle the request.'''

'''
1.Authorization model with testing UI plus features for API language use samples.
https://eu.ninjarmm.com/apidocs-beta/authorization/overview
2.Core API 2.0 beta endpoints availble for and within our API tenant.
https://eu.ninjarmm.com/apidocs-beta/core-resources
3.Postman collection of our API Endpoints via Postman (You can create a fork so you can test and validate endpoints or gather data, whatever you choose).
https://www.postman.com/ninjaone/ninjaone-api-workspace/overview
4.Our Dojo documentation.
https://ninjarmm.zendesk.com/hc/en-us/articles/4403617211277-API-OAuth-Token-Configuration
'''
