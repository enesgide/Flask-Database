#!/usr/bin/env python3

from modules import pg8000
import configparser


################################################################################
# Connect to the database
#   - This function reads the config file and tries to connect
#   - This is the main "connection" function used to set up our connection
################################################################################

def database_connect():
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Create a connection to the database
    connection = None
    try:
        '''
        This is doing a couple of things in the back
        what it is doing is:

        connect(database='y12i2120_unikey',
            host='soit-db-pro-2.ucc.usyd.edu.au,
            password='password_from_config',
            user='y19i2120_unikey')
        '''
        connection = pg8000.connect(database=config['DATABASE']['user'],
                                    user=config['DATABASE']['user'],
                                    password=config['DATABASE']['password'],
                                    host=config['DATABASE']['host'])
    except pg8000.OperationalError as e:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(e)
    except pg8000.ProgrammingError as e:
        print("""Error, config file incorrect: check your password and username""")
        print(e)
    except Exception as e:
        print(e)

    # Return the connection to use
    return connection


################################################################################
# Login Function
################################################################################

def check_login(sid, pwd):
    conn = database_connect()
    if(conn is None):
        return None

    cur = conn.cursor()
    try:
        sql = """SELECT *
                 FROM unidb.student
                 WHERE studid=%s AND password=%s"""
        cur.execute(sql, (sid, pwd))
        r = cur.fetchone()
        cur.close()
        conn.close()
        return r
    except:
        pass
        #print("Error Invalid Login")

    cur.close()
    conn.close()
    return None


################################################################################
# List Units
################################################################################

def list_units():
    conn = database_connect()
    if(conn is None):
        return None

    cur = conn.cursor()
    val = None
    try:
        cur.execute("""SELECT uosCode, uosName, credits, year, semester
                        FROM UniDB.UoSOffering JOIN UniDB.UnitOfStudy USING (uosCode)
                        ORDER BY uosCode, year, semester""")
        val = cur.fetchall()
    except:
        pass
        #print("Error fetching from database")

    cur.close()
    conn.close()
    return val


################################################################################
# Get transcript function
################################################################################

def get_transcript(sid):
    conn = database_connect()
    if(conn is None):
        return None

    cur = conn.cursor()
    val = None
    try:
        cur.execute("""SELECT T.UosCode, U.UosName, U.Credits, T.Year, T.Semester, T.Grade
                        FROM Transcript T JOIN UnitOfStudy U ON (T.UosCode = U.UosCode)
                        WHERE studId = {}
                        ORDER BY uosCode, year, semester""".format(sid))
        val = cur.fetchall()
    except:
        pass
        #print("Error fetching from database")

    cur.close()
    conn.close()
    return val

#####################################################
#  Academic Staff
#####################################################

def list_all():   
    conn = database_connect()
    if(conn is None):
        return None
    
    cur = conn.cursor()
    val = None
    try:
        cur.execute("""SELECT id, name, deptid, address
                        FROM AcademicStaff;""")
        val = cur.fetchall()
    except:
        pass
        #print("Error listing")

    cur.close()
    conn.close()
    return val


def search_department(id):   
    if (not isinstance(id, str)) or len(id) != 3:
        return None
    
    conn = database_connect()
    if(conn is None):
        return None
    
    cur = conn.cursor()
    val = None
    try:
        cur.execute("""SELECT id, name, deptid, address
                        FROM AcademicStaff
                        WHERE deptid = %s;""", (id,))
        val = cur.fetchall()
    except:
        pass
        #print("Error searching")

    cur.close()
    conn.close()
    return val


def count_staff():   
    conn = database_connect()
    if(conn is None):
        return None
    
    cur = conn.cursor()
    val = None
    try:
        cur.execute("""SELECT deptid, COUNT(id)
                        FROM AcademicStaff
                        GROUP BY deptid;""")
        val = cur.fetchall()
    except:
        pass
        #print("Error counting")

    cur.close()
    conn.close()
    return val


def add_staff(staffid, name, dept, pw, address, salary):  
    if not (staffid, name, dept, pw):
        return None
    
    for var in [staffid, name, dept, pw, address, salary]:
        if not all(c.isalnum() or c.isspace() for c in var):
            return None
    
    if not staffid.isdigit():
        return None
    
    if (not isinstance(dept, str)) or len(dept) != 3:
        return None
    
    if address == '':
            address = "NULL"            
            
    if salary == '':
        salary = "NULL"
    elif salary.isdigit():
        salary = int(salary)
    else:
        return None    
            
    conn = database_connect()
    if(conn is None):
        return None
    
    cur = conn.cursor()
    val = None
    try: 
        SQL = "INSERT INTO AcademicStaff Values(%s, %s, %s, %s, {}"
        
        if address == "NULL":
            SQL = SQL.format(address)
        else:
            SQL = SQL.format("%s")
        
        SQL += ", {});"
        SQL = SQL.format(salary)
        
        if address == "NULL":
            cur.execute(SQL, (staffid, name, dept, pw))
        else:
            cur.execute(SQL, (staffid, name, dept, pw, address))
        
        conn.commit()
        val = True                    
    except Exception as e:
        #val = str(e)
        pass
        #print("Error inserting")

    cur.close()
    conn.close()
    
    return val

#####################################################
#  Python code if you run it on it's own as 2tier
#####################################################


if (__name__ == '__main__'):
    print("{}\n{}\n{}".format("=" * 50, "Welcome to the 2-Tier Python Database", "=" * 50))