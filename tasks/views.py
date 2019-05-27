# talismansoftwaresolutions/tasks/views.py

import datetime
import json
from functools import wraps
from flask import Blueprint, url_for, render_template, redirect, jsonify, \
     json, Response, make_response, request

from talismansoftwaresolutions import db
from talismansoftwaresolutions import app
from talismansoftwaresolutions.models import Task

import psycopg2 as psy

#See #/mnt/shared_data/Programming/Practice/Python/JSONTasks/Test.py

tasks_blueprint = Blueprint('tasks', __name__)

TESTING = True

db.init(app.config['SQLALCHEMY_DATABASE_URI'])

### DML Statements Go Below -- db.init must be called first ###


@tasks_blueprint.route('/api/v1/tasks/delete', methods= ['POST'])
def api_delete_task():    
    data = request.get_json(force = True)

    task_id = data.get("task_id")
    user_id = data.get("user_id")    
    task_name = data.get("task_name")
    due_date = data.get("due_date")
    priority = data.get("priority")
    status = data.get("status")

    try:
        db.delete_task(task_id)
    except Exception as e:
        print(e)
        raise(e)

    return jsonify({"Status": "{} successfully deleted".format(task_id)})



@tasks_blueprint.route('/api/v1/tasks/upload', methods= ['POST'])
def upload_tasks_test():
    data = request.get_json(force = True)

    task_list = data.get("tasks")

    #Step 1. Are there any tasks to parse?  
    task_count = len(task_list)
    if task_count <= 0:
        result = {"error": "no tasks to process"}
        return make_response(jsonify(result), 404)    

    #Step 2. Process each task
    msg = 'Error'
    processed_items = 0

    for jsonTask in task_list:      
        server_task_id, result_exception = do_add_task(jsonTask)                 
        formatted_json_task = format_json_task(jsonTask)       

        if server_task_id < 0:
            msg = result_exception['error_message']

            if result_exception['error_code'] == '23502':                
                index = result_exception['error_message'].find('null value in column "user_id"')
                if index != -1:
                    msg = "Error: Could not process task # {} Exception: {}".format(jsonTask['task_id'], 
                          "Need to add user to database")                                                         

            if result_exception['error_code'] == '23505':                
                index = result_exception['error_message'].find('duplicate key value violates unique constraint')
                if index != -1:
                    msg = "Error: Could not process task # {} Exception: {}".format(jsonTask['task_id'], 
                          "Task already exists in database")  

            if result_exception: db.log_error('upload_tasks', msg)                

            #result = {"error": msg}
            #return make_response(jsonify(result), 404)
        else:
            #TODO
            #Step n. Make sure that each task has its server_task_id set to the id we give it            
            jsonTask['server_task_id'] = server_task_id
            jsonTask['date_synchronized'] = datetime.datetime.now()
            #jsonTask['date_synchronized'] = datetime.datetime.now()
            #msg = "Success: New server task id: {}".format(server_task_id)  
            #msg = "Success: New server task id: {} {}".format(server_task_id, format_json_task(jsonTask)) 
            #Increment *successfully* processed items
            processed_items = processed_items + 1                            

    #return jsonify({"Status": "{}".format(msg)})
    #return jsonify({"Status": jsonTask})
    return jsonify({"Status": "{} {}".format("Successfully processed", processed_items)})


"""
@tasks_blueprint.route('/api/v1/tasks/upload_OLD', methods= ['POST'])
def upload_tasks_old():
    data = request.get_json(force = True)


    # === Send back what we received -- remove this later
    #msg = "Success {} tasks received".format(task_count)
    #if True:
    #    return jsonify({"Status": data})
    # ====

    task_list = data.get("tasks")
    formatted_json_task = None

    #Step 1. Are there any tasks to parse?  
    task_count = len(task_list)
    if task_count <= 0:
        msg = "Success -- received tasks"
    else:
        msg = "Success {} tasks received".format(task_count)

    #Step 2. Process each task
    processed_items = 0
    for jsonTask in task_list:       

        server_task_id, exception = do_add_task(jsonTask)
        formatted_json_task = format_json_task(jsonTask)

        if server_task_id < 0:
            #msg = "Error: Could not process {} Exception: {}".format(jsonTask.get('task_id'), exception)
            if isinstance(exception, psy.Error):
                error_message = exception.pgerror
                index = error_message.find('null value in column "user_id"')
                if index != -1:
                    msg = "Error: Could not process {} Exception: {}".format(formatted_json_task, "Need to add user to database")                    
            

        if exception:                
            db.log_error('upload_tasks', exception)     
            break       
        else:
            #TODO
            #Step n. Make sure that each task has its server_task_id set to the id we give it            
            jsonTask['server_task_id'] = server_task_id
            jsonTask['date_synchronized'] = datetime.datetime.now()
            jsonTask['date_synchronized'] = datetime.datetime.now()
            #msg = "Success: New server task id: {}".format(server_task_id)  
            #msg = "Success: New server task id: {} {}".format(server_task_id, format_json_task(jsonTask)) 
            #Increment *successfully* processed items
            processed_items = processed_items + 1    
            break
            

    #return jsonify({"Status": "{}".format(msg)})
    return jsonify({"Status": "{} {}".format("Successfully processed", processed_items)})
    #return jsonify({"Status": jsonTask})
"""


def format_json_task(data):
    user_id = data.get("user_id")   
    server_user_id = data.get("server_user_id")
    local_user_id = data.get("user_id") 
    local_task_id = data.get("task_id")
    task_name = data.get("task_name")
    due_date = data.get("due_date", None)
    priority = data.get("priority")
    status = data.get("status")
    date_added = data.get("date_added")
    modification_date = data.get("date_modified")
    synchronization_date = data.get("date_synchronized")
    modified_by = data.get("modified_by", None)
    to_delete = data.get("to_delete")

    result = "server_user_id {} user_id {}, local_user_id: {}, local_task_id: {}, task_name: {}, due_date: {}, priority {}, status {}, " \
             "date_added {} modification_date {} modified_by {} to_delete {} date_synchronized {}".format(server_user_id, user_id, local_user_id, 
             local_task_id, task_name, due_date, priority, status, date_added, modification_date, modified_by, to_delete,
             synchronization_date)

    return result



def do_add_task(data):
    server_user_id = data.get("server_user_id")   
    user_id = data.get("user_id")   
    local_user_id = data.get("user_id") 
    local_task_id = data.get("task_id")
    task_name = data.get("task_name")
    due_date = data.get("due_date", None)
    priority = data.get("priority")
    status = data.get("status")
    date_added = data.get("date_added")
    modification_date = data.get("modification_date")
    modified_by = data.get("modified_by", None)
    to_delete = data.get("to_delete")
    synchronization_date  = data.get("date_synchronized")

    """
    if new_task_id:
        return jsonify({"Status": "Success {}".format(new_task_id)})
    else:
        return jsonify({"Status": "Error. Could not add new record to database."})
    """
   
    new_task_id, exception = db.add_task_returning_id(server_user_id, user_id, local_user_id, local_task_id, task_name, 
            due_date, priority, status, date_added, modification_date, modified_by, to_delete, synchronization_date)

    #return jsonify({"Status": "{}".format(new_task_id)})
    return new_task_id, exception


@tasks_blueprint.route('/api/v1/tasks/add', methods= ['POST'])
def api_add_task():    
    data = request.get_json(force = True)    

    new_task_id = do_add_task(data)

    return jsonify({"Status": "{}".format(new_task_id)})



"""
@tasks_blueprint.route('/api/v1/tasks/add', methods= ['POST'])
def api_add_task():    
    data = request.get_json(force = True)

    user_id = data.get("user_id")   
    local_user_id = data.get("local_user_id", -1) 
    local_task_id = data.get("local_task_id", -1)
    task_name = data.get("task_name")
    due_date = data.get("due_date", None)
    priority = data.get("priority")
    status = data.get("status")
    date_added = data.get("date_added")
    modification_date = data.get("modification_date")
    modified_by = data.get("modified_by", None)
    to_delete = data.get("to_delete")

    
    #if new_task_id:
    #    return jsonify({"Status": "Success {}".format(new_task_id)})
    #else:
    #    return jsonify({"Status": "Error. Could not add new record to database."})
    

    new_task_id = db.add_task_returning_id(user_id, task_name, due_date, priority, status)

    return jsonify({"Status": "{}".format(new_task_id)})
"""

"""
@tasks_blueprint.route('/api/v1/tasks/add', methods= ['POST'])
def api_add_task():    
    data = request.get_json(force = True)

    user_id = data.get("user_id")    
    task_name = data.get("task_name")
    due_date = data.get("due_date")
    priority = data.get("priority")
    status = data.get("status")

    
    #if new_task_id:
    #    return jsonify({"Status": "Success {}".format(new_task_id)})
    #else:
    #    return jsonify({"Status": "Error. Could not add new record to database."})
    

    new_task_id = db.add_task_returning_id(user_id, task_name, due_date, priority, status)

    return jsonify({"Status": "{}".format(new_task_id)})
"""
  
 

@tasks_blueprint.route('/api/v1/tasks/update/<int:task_id>', methods = ['POST'])
def api_task_update(task_id):
    success_flag = False
    data = request.get_json(force = True)
    user_id = data.get("user_id")
    task_id = data.get("task_id")
    task_name = data.get("task_name")
    due_date = data.get("due_date")
    priority = data.get("priority")
    status = data.get("status")

    success_flag = db.update_task(user_id, task_id, task_name, due_date, priority, status)

    message = ""
    if success_flag == True:
        message = {"Status": "Successfully updated task"}
    else:
        message = {"Status": "Error. Could not update task successfully"}

    return jsonify(message) 





def process_results(results):
    json_results = None
    msg = "Element not found"
    code = 404

    if results:
        json_results = json.dumps(results,  indent = 2)    
    else:
        json_results = jsonify({"Error":msg}, code)

    return json_results


@tasks_blueprint.route("/api/v1/tasks/all/<int:user_id>", methods=['GET', 'POST'])
def api_tasks_all(user_id):    
    results = db.getTasksByUser(user_id)   
    return process_results(results)

@tasks_blueprint.route("/api/v1/tasks/open/<int:user_id>", methods=['GET', 'POST'])
def api_tasks_open(user_id):
    results = db.getTasksByStatus(user_id, 1)  
    return process_results(results)

@tasks_blueprint.route("/api/v1/tasks/completed/<int:user_id>", methods=['GET', 'POST'])
def api_tasks_completed(user_id):
    results = db.getTasksByStatus(user_id, 0)  
    return process_results(results)
    

# FOR TESTING
# =============
# (http://localhost:5000/api/v1/tasks/1)
"""
@tasks_blueprint.route("/api/v1/tasks")
def api_tasks():
    user_id = 0
    results = None   

    if TESTING == True:
        user_id = 1
        status = 1
        results = db.getTasksByStatus(user_id, status)

    #return jsonify({"tasks", results})
    #return jsonify(results)
    json_results = json.dumps(results,  indent = 2)    
    return json_results

@tasks_blueprint.route("/api/v1/hello")
def api_sayhello():
    json_results = []
    data = {
        'message': 'Hello, world from v1 of Tasks API'
    }
    json_results.append(data)
    return jsonify(items = json_results)    

@tasks_blueprint.route("/api/v1/tasks/test")
def api_test():
    return_str = '{"status":"true","message":"Data fetched successfully!","data":[{"id":"1","name":"Roger Federer","country":"Switzerland","city":"Basel","imgURL":"https:\/\/demonuts.com\/Demonuts\/SampleImages\/roger.jpg"},{"id":"2","name":"Rafael Nadal","country":"Spain","city":"Madrid","imgURL":"https:\/\/demonuts.com\/Demonuts\/SampleImages\/nadal.jpg"},{"id":"3","name":"Novak Djokovic","country":"Serbia","city":"Monaco","imgURL":"https:\/\/demonuts.com\/Demonuts\/SampleImages\/djoko.jpg"},{"id":"4","name":"Andy Murray","country":"United Kingdom","city":"London","imgURL":"https:\/\/demonuts.com\/Demonuts\/SampleImages\/murray.jpg"},{"id":"5","name":"Maria Sharapova","country":"Russia","city":"Moscow","imgURL":"https:\/\/demonuts.com\/Demonuts\/SampleImages\/shara.jpg"},{"id":"6","name":"Caroline Wozniacki","country":"Denmark","city":"Odense","imgURL":"https:\/\/demonuts.com\/Demonuts\/SampleImages\/woz.jpg"},{"id":"7","name":"Eugenie Bouchard","country":"Canada","city":" Montreal","imgURL":"https:\/\/demonuts.com\/Demonuts\/SampleImages\/bou.png"},{"id":"8","name":"Ana Ivanovic","country":"Serbia","city":"Belgrade","imgURL":"https:\/\/demonuts.com\/Demonuts\/SampleImages\/iva.jpg"}]}'
    resp = Response(return_str, status=200, mimetype="application/json")
    return resp
"""
#END TESTING    
    
