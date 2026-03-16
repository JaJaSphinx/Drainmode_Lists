from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging #ADD THIS SO WE CAN SEE IF ANY ISSUES ARISE IN LOGGED FILES (May be worth exploring different logging with the created error handling that currently dumps to console)
import config
import pandas as pd #Use when selecting data from SQL for next steps 
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.exc import SQLAlchemyError 
import os

class sql:

    def add_devices_sql(sql_device_data, bool_check):
        #Create Data
        #print(f"{data_filtered}")
        columns: list = ['id', 'uid', 'systemName', 'domainRole']
        df = pd.DataFrame(sql_device_data, columns=columns)
        print(f"{df}")
        table_name: str = 'RDSServers'

        #Create Connection
        conn: str = (f"mssql+pyodbc://@{os.getenv('target_instance')}/{os.getenv('target_db')}"
                        f"?driver={os.getenv('driver')}")
        engine = create_engine(conn)

        #Create table and datatypes for import 
        meta_data = MetaData()
        ninja_import_devices = Table(
            table_name, meta_data,
            Column('id', Integer,),
            Column('uid', String),
            Column('systemName', String),
            Column('domainRole', String)
        )
        # Create Table if not present
        meta_data.create_all(engine) 

        dtype_mapping: dict = {
            'id': Integer(),
            'uid': String(),
            'systemName': String(),
            'domainRole': String()
        }      

        try:
            df.to_sql(table_name, con=engine, if_exists="replace", dtype=dtype_mapping, index=False) # This will replace all data in the table
            result = True
            message = f"Success: Overwritten data in {table_name}"

        except SQLAlchemyError as e:
            result = False
            message = str(e.__cause__ or e)  # get root cause message

        except Exception as e:
            result = False
            message = str(e)  # get root cause message



    def add_users_sql(sql_users_data, bool_check):
            #Create Data
            #print(f"{data_filtered}")
            columns: list = ['id', 'name', 'email', 'userType']
            df = pd.DataFrame(sql_users_data, columns=columns)
            print(f"{df}")
            table_name: str = 'Users'

            #Create Connection
            conn: str = (f"mssql+pyodbc://@{os.getenv('target_instance')}/{os.getenv('target_db')}"
                            f"?driver={os.getenv('driver')}")
            engine = create_engine(conn)

            #Create table and datatypes for import 
            meta_data = MetaData()
            ninja_import_devices = Table(
                table_name, meta_data,
                Column('id', Integer,),
                Column('Name', String),
                Column('Email', String),
                Column('userType', String)
            )
            # Create Table if not present
            meta_data.create_all(engine) 

            dtype_mapping: dict = {
                'id': Integer(),
                'Name': String(),
                'Email': String(),
                'userType': String()
            }      

            try:
                df.to_sql(table_name, con=engine, if_exists="replace", dtype=dtype_mapping, index=False) # This will replace all data in the table
                result = True
                message = f"Success: Overwritten data in {table_name}"

            except SQLAlchemyError as e:
                result = False
                message = str(e.__cause__ or e)  # get root cause message

            except Exception as e:
                result = False
                message = str(e)  # get root cause message


    


    # #Add all Technician users to Users table from API request        
    # def add_users_sql(id, name, usertype, bool_check):
    #     print(id, name, usertype)
    #     #Try block to ensure if fails it presents exact errors inside console for review
    #     try: 
    #         #Format params for SQL Server, piggys off pyodbc 
    #         conn_str = (f"mssql+pyodbc://@{config.target_instance}/{config.target_db}"
    #                     f"?driver={config.driver}")
    #         #Create Connection to SQL
    #         engine = create_engine(conn_str)
    #         with engine.begin() as conn:
    #             #Create Insert Query, supply params, execute, print to console 
    #             query = text('''INSERT INTO [dbo].[Users]
    #                                         VALUES (:id, :name, :usertype)''')
    #             result = conn.execute(query, {"id": id, "name": name, "usertype":usertype} )
    #             conn.commit()
    #             print(result)
    #     #Error handling 
    #     except Exception as e:
    #         bool_check = False
    #         return bool_check, e
    #     return bool_check, conn_str
    

    # #Add all Technician users to Users table from API request        
    # def add_devices_sql(id, uid, servername, domainrole, bool_check):
    #     print(f"Member Server Found... {servername}")
    #     #Try block to ensure if fails it presents exact errors inside console for review
    #     try: 
    #         #Format params for SQL Server, piggys off pyodbc 
    #         conn_str = (f"mssql+pyodbc://@{config.target_instance}/{config.target_db}"
    #                     f"?driver={config.driver}")
    #         #Create Connection to SQL
    #         engine = create_engine(conn_str)
    #         with engine.begin() as conn:
    #             #Create Insert Query, supply params, execute, print to console 
    #             query = text('''INSERT INTO [dbo].[RDSServers]
    #                                         VALUES (:uid, :id, :servername, :domainrole)''')
    #             result = conn.execute(query, {"uid": uid, "id": id, "servername":servername, "domainrole":domainrole} )
    #             conn.commit()
    #             print(result)
    #     #Error handling 
    #     except Exception as e:
    #         bool_check = False
    #         return bool_check, e
    #     return bool_check, conn_str