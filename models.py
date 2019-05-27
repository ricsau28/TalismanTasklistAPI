# talismansoftwaresolutions/models.py

"""
Adapted from Real Python Part 2
"""

import datetime


class Task():

    __tablename__ = "tasks"    

    #def __init__(self, name, due_date, priority, posted_date, status, user_id):
    def __init__(self, task_name, date_added, modification_date, user_id = None, local_user_id = None, local_task_id = None, due_date = None, 
                priority = None, status = None, modified_by = None, to_delete = None):

        self.user_id = user_id
        self.local_user_id = local_user_id
        self.local_task_id = local_task_id
        self.task_name = task_name        
        self.due_date = due_date
        self.status = status
        self.priority = priority
        self.date_added = date_added
        self.modification_date = modification_date
        self.modified_by = modified_by
        self.to_delete = to_delete

    def __repr__(self):
        return '<name {0}>'.format(self.name)

class User():

    __tablename__ = 'users'

    def __init__(self, name, email=None, password=None, local_user_id=None, role=None):
        self.name = name
        self.email = email
        self.password = password
        self.local_user_id = local_user_id
        self.role = role

    def __repr__(self):
        return '<User {0}>'.format(self.name)
