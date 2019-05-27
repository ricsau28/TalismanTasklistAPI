#talismansoftwaresolutions/db.py
import psycopg2 as psy
import psycopg2.extras as psyextra
import json
import datetime

TESTING = False

CONNECTION_STRING = ''
COMMIT = 1
ROLLBACK = -1

STATUS_OPEN = 1
STATUS_CLOSED = 0

def get_current_datetime():
    return datetime.datetime.now.strftime("%I:%M%p on %B %d, %Y")


def update_task(user_id, task_id, taskname, duedate, priority, status):
    commit_state = COMMIT
    conn, cur = connectToDBAndGetCursor()

    success_flag = False

    try:
        cur.execute("UPDATE dev.tasks SET modification_date=CURRENT_TIMESTAMP(2), task_name=%s, due_date=%s, priority=%s, " \
            "status=%s WHERE user_id=%s AND task_id=%s;", 
                    (taskname, duedate, priority, status, user_id, task_id))
        success_flag = True
    except Exception as e:   
        commit_state = ROLLBACK 
    finally:
        closeConnection(conn, cur, commit_state)

    return success_flag


def update_task_complete(task_id, task_completed=False):
    commit_state = COMMIT
    conn, cur = connectToDBAndGetCursor()

    try:
        if task_completed == True:  
            cur.execute("UPDATE dev.tasks SET modification_date=CURRENT_TIMESTAMP(2), status = %s WHERE task_id=%s;", (STATUS_OPEN, task_id))
        else:    
            cur.execute("UPDATE dev.tasks SET modification_date=CURRENT_TIMESTAMP(2), status = %s WHERE task_id=%s;", (STATUS_CLOSED, task_id))
    except Exception as e:   
        commit_state = ROLLBACK 
        print(e)
    finally:
        closeConnection(conn, cur, commit_state)


def purge_task(task_id):
    commit_state = COMMIT
    conn, cur = connectToDBAndGetCursor()    

    try:
        cur.execute("DELETE FROM tasks WHERE to_delete=true AND task_id=%s;", (task_id,))  

    except Exception as e:   
        commit_state = ROLLBACK 
        print(e)
    finally:
        closeConnection(conn, cur, commit_state)


def delete_task(task_id):
    commit_state = COMMIT
    conn, cur = connectToDBAndGetCursor()    

    try:
        cur.execute("UPDATE dev.tasks SET to_delete=true, modification_date=CURRENT_TIMESTAMP(2) WHERE task_id=%s;", (task_id,))  

    except Exception as e:   
        commit_state = ROLLBACK 
        print(e)
    finally:
        closeConnection(conn, cur, commit_state)


def undelete_task(task_id):
    commit_state = COMMIT
    conn, cur = connectToDBAndGetCursor()    

    try:
        cur.execute("UPDATE dev.tasks SET to_delete=false, modification_date=CURRENT_TIMESTAMP(2) WHERE task_id=%s;", (task_id,))  

    except Exception as e:   
        commit_state = ROLLBACK 
        print(e)
    finally:
        closeConnection(conn, cur, commit_state)


#TODO: Create DELETE_FLAG in table (RS, 5/9/2019)
""" def purge_tasks(user_id):
    commit_state = COMMIT
    conn, cur = connectToDBAndGetCursor()

    try:
        cur.execute("DELETE FROM dev.tasks WHERE status=-1 AND user_id=%s;", (user_id,))
    except Exception as e:   
        commit_state = ROLLBACK 
        print(e)
    finally:
        closeConnection(conn, cur, commit_state)
"""

def add_task_returning_id(userId, localUserId, localTaskId, taskname, duedate, priority, status, dateAdded,
                          modificationDate, modifiedBy, toDelete):
    #See: https://stackoverflow.com/questions/35397459/using-psycopg2-to-insert-return-and-update-in-bulk
    commit_state = COMMIT
    conn, cur = connectToDBAndGetCursor()

    new_id = 1
  
    try: 
        #cur.execute("INSERT INTO dev.tasks (user_id, task_name, due_date, priority, status) VALUES (%s, %s, %s, %s, %s);",
        #('1', 'Hey, hey, hey', '5/21/2019', '3', '1'))
         

        cur.execute("INSERT INTO dev.tasks (user_id, local_user_id, local_task_id, task_name, due_date, priority, status, " \
                                           "date_added, modification_date, modified_by, to_delete) " \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                    (userId, localUserID, localTaskId, taskname, duedate, priority, status, dateAdded, modificationDate, modifiedBy, toDelete))
        cur.execute('SELECT LASTVAL();')
        new_id = cur.fetchone()['lastval']
        
        
    except Exception as e:
        commit_state = ROLLBACK
        print(e)        
    finally:    
        closeConnection(conn, cur, commit_state)
        
    return new_id

"""


def add_task_returning_id(user_id, taskname, duedate, priority, status):
    #See: https://stackoverflow.com/questions/35397459/using-psycopg2-to-insert-return-and-update-in-bulk
    commit_state = COMMIT
    conn, cur = connectToDBAndGetCursor()

    new_id = 1
  
    try: 
        #cur.execute("INSERT INTO dev.tasks (user_id, task_name, due_date, priority, status) VALUES (%s, %s, %s, %s, %s);",
        #('1', 'Hey, hey, hey', '5/21/2019', '3', '1'))
         

        cur.execute("INSERT INTO dev.tasks (user_id, task_name, due_date, priority, status) " \
                    "VALUES (%s, %s, %s, %s, %s);",(user_id, taskname, duedate, priority, STATUS_OPEN))
        cur.execute('SELECT LASTVAL();')
        new_id = cur.fetchone()['lastval']
        
        
    except Exception as e:
        commit_state = ROLLBACK
        print(e)        
    finally:    
        closeConnection(conn, cur, commit_state)
        
    return new_id
"""

def add_task(user_id, taskname, duedate, priority, status):
    commit_state = COMMIT
    conn, cur = connectToDBAndGetCursor()
  
    try:       
        cur.execute("INSERT INTO dev.tasks (user_id, task_name, due_date, priority, status) " \
                    "VALUES (%s, %s, %s, %s, %s);",(user_id, taskname, duedate, priority, STATUS_OPEN))
    except Exception as e:
        commit_state = ROLLBACK
        print(e)        
    finally:    
        closeConnection(conn, cur, commit_state)


def getOpenTasks(user_id):
    return getTasksByStatus(user_id, STATUS_OPEN)


def getClosedTasks(user_id):
    return getTasksByStatus(user_id, STATUS_CLOSED)


def getTasksByUser(user_id):
    if TESTING == True:
        print("getTasksByStatus: TESTING is ON!")

    results = None
    conn, cur = connectToDBAndGetCursor()

    try:
        # TODO: Change dev.tasks to tasks in production 10/2/2018  
        if TESTING == True:
            cur.execute('select task_id, U.user_id, user_name, task_name, due_date, priority, status, T.to_delete from dev.tasks T INNER JOIN dev.users U ON '
                        'T.user_id=U.user_id where U.user_id=%s LIMIT 2;',(user_id,))
        else:
            cur.execute('select task_id, U.user_id, user_name, task_name, due_date, priority, status, T.to_delete from dev.tasks T INNER JOIN dev.users U ON '
                        'T.user_id=U.user_id where U.user_id=%s;',(user_id,))
        results = cur.fetchall()
    except Exception as e:
        print(e)
        raise(e)
    finally:    
        closeConnection(conn, cur)

    return results


def getTasksByStatus(user_id, task_status):
    if TESTING == True:
        print("getTasksByStatus: TESTING is ON!")

    conn, cur = connectToDBAndGetCursor()
    try:
        # TODO: Change dev.tasks to tasks in production 10/2/2018  
        if TESTING == True:
            cur.execute('select task_id, U.user_id, user_name, task_name, due_date, priority, T.to_delete, status from dev.tasks T INNER JOIN dev.users U ON '
                        'T.user_id=U.user_id where T.to_delete=false AND U.user_id=%s AND status=%s LIMIT 2;',(user_id, task_status))
        else:
            cur.execute('select task_id, U.user_id, user_name, task_name, due_date, priority, T.to_delete, status from dev.tasks T INNER JOIN dev.users U ON '
                        'T.user_id=U.user_id where T.to_delete=false AND U.user_id=%s AND status=%s;',(user_id, task_status))
        results = cur.fetchall()
    except Exception as e:
        print(e)
        raise(e)
    finally:    
        closeConnection(conn, cur)

    return results

def getUserID(user):    
    conn, cur = connectToDBAndGetCursor()
    new_id = -15
    
    try:
        cur.execute("SELECT user_id FROM dev.users WHERE user_name=%s;", (user.name,))
        #cur.execute('SELECT LASTVAL();')
        new_id = cur.fetchone()['user_id']
    except Exception as e:                
        if int(e.pgcode) != 23505:
            print("Error code: {0}".format(e.pgcode)) #raise(e)
    finally:                     
        closeConnection(conn, cur)

    #return commit_state <> ROLLBACK
    return new_id


def getUserCredentials(user):
    conn, cur = connectToDBAndGetCursor()
    try:        
        cur.execute("SELECT user_id, password, email, role FROM dev.users WHERE user_name = %s;", (user,))
        result = cur.fetchone()
    except Exception as e:        
        print(e)   #raise e
        return None
    finally:
        closeConnection(conn, cur)   
    
    return result

"""
def addNewUser(user):
    commit_state = COMMIT
    conn, cur = connectToDBAndGetCursor()
    new_id = -17
    
    try:
        cur.execute("INSERT INTO dev.users (user_name, email, password, role) VALUES(%s, %s, %s, %s);",
                   (user.name, user.email, user.password, user.role))
        cur.execute('SELECT LASTVAL();')
        new_id = cur.fetchone()['lastval']
    except Exception as e:        
        commit_state = ROLLBACK        
        
    finally:                     
        closeConnection(conn, cur, commit_state)

    status = (new_id, None) if not e else (new_id, "{} {}".format(e.pgcode, e.pgerror))
    return status
"""



def addNewUser(user):
    commit_state = COMMIT
    conn, cur = connectToDBAndGetCursor()
    new_id = -17
    exception = None
    
    try:
        cur.execute("INSERT INTO dev.users (user_name, email, password, role) VALUES(%s, %s, %s, %s);",
                   (user.name, user.email, user.password, user.role))
        cur.execute('SELECT LASTVAL();')
        new_id = cur.fetchone()['lastval']
    except Exception as e:        
        new_id = -32
        exception = e
        commit_state = ROLLBACK        
        if int(e.pgcode) != 23505:
            print("Error code: {0}".format(e.pgcode)) 
        #raise(e)
    finally:                     
        closeConnection(conn, cur, commit_state)

    #return commit_state <> ROLLBACK
    return new_id, exception



def getTaskInfo(taskID):
    conn, cur = connectToDBAndGetCursor()    

    try:
        cur.execute("SELECT task_id, task_name, due_date, priority FROM dev.tasks WHERE task_id = %s;", (taskID,))
        #cur.execute('select task_id, task_name, due_date, priority from dev.tasks where status=0')
    except Exception as e:
        #Log e
        raise(e) 

    result = cur.fetchone()
    closeConnection(conn, cur)  
    return result


def connectToDBAndGetCursor():
    conn = connectToDB()
    cur = None

    """
    for normal usage when not needing JSON, use the line below
    #cur = conn.cursor(cursor_factory = psy.extras.DictCursor)
    when returning JSON use this:
    #cur = conn.cursor(cursor_factory=psy.extras.RealDictCursor)
    as suggested at https://www.peterbe.com/plog/from-postgres-to-json-strings
    """
    
    try:
        cur = conn.cursor(cursor_factory=psy.extras.RealDictCursor)
    except Exception as e:
        print(e)
        raise(e)

    return conn, cur


def init(connection_string):
    global CONNECTION_STRING
    CONNECTION_STRING = connection_string    


def connectToDB():
    try:
        return psy.connect(CONNECTION_STRING)
        #Alternate method if the above fails:
        #return psy.connect("host=sandbox-1804 user=flasktaskr password=flasktaskr dbname=flasktaskr")
    except psy.OperationalError as oe:
        print("db.connectToDB: {}".format(oe))    
        raise(oe)
    except Exception as e:
        print("db.connectToDB: {}".format(e))    
        raise(e)

def closeConnection(conn, cur = None, action = None):  
    if conn is None:
        return
    # commit or rollback transaction
    if action in (COMMIT, ROLLBACK):
        try:
            if action == COMMIT:
                conn.commit()
            elif action == ROLLBACK:
                conn.rollback()  
        except Exception as e:            
            print(e)            
            raise(e)

    # close the cursor
    try:    
        if cur != None:
            cur.close()
    except Exception as e:        
        print(e)        
        raise(e)

    #finally, close the connection
    try:       
        conn.close()
    except Exception as e:        
        print(e)


def testConnection2():
    taskID = 49
    task = getTaskInfo(taskID)
    print("Task: {}".format(task['task_name']))

def testConnection(connection_string=""):
    status = ""    
    #conn = None
    #cur = None
    conn, cur = connectToDBAndGetCursor()

    if not connection_string:
        if CONNECTION_STRING:
            connection_string = CONNECTION_STRING
        else:
            connection_string = 'postgresql://flasktaskr:flasktaskr@sandbox-1804/flasktaskr'

    try:
        conn = psy.connect(connection_string)
        #SUCCESS using below
        #conn = psy.connect("host=sandbox-1804 user=flasktaskr password=flasktaskr dbname=flasktaskr")
        status = "testConnection: Successfully opened connection"
        print(status)

        cur = conn.cursor(cursor_factory = psy.extras.DictCursor)
        cur.execute('select task_id, task_name, due_date, priority from dev.tasks where status=1')            
          
        task = cur.fetchone()
        name = "Name: {}".format(task['task_name'])

        status = "testConnection: Successfully closed connection and fetched one record "
        print(status)

        status = name
    except Exception as e:
        status = "testConnection: {}".format(e)
        print(e)
    finally:
        closeConnection(conn, cur)    
        print(status)
