
from flask import session
from flask.views import MethodView
from flask_smorest import Blueprint

from common_api.schema import ChildDetailsSchema, HabitualTaskDELSchema, HabitualTaskPOSTSchema, HabitualTaskPUTSchema, LearningTaskDELSchema, LearningTaskPOSTSchema, LerningTaskPUTSchema
from firestore import add_habitual_task, add_learning_task, delete_habitual_task, delete_learning_task, get_child_entry, list_all_habitual_tasks, list_all_learning_tasks, update_habitual_task, update_learning_task
from firestore_schema import HabitualTask, LearningTask


# --------------------------------------------------------------------
# Tasks Function routes
# --------------------------------------------------------------------

common_bp = Blueprint('Shared API', __name__, 
                    url_prefix='/common', 
                    description="")

common_habitual_bp = Blueprint('Shared API - Habitual Tasks', __name__, 
                    url_prefix='/common/habitual', 
                    description="")

common_learning_bp = Blueprint('Shared API - Learning Tasks', __name__, 
                    url_prefix='/common/learning', 
                    description="")

# -----------------------------------------------------------------------
# Task Related Routes
# -----------------------------------------------------------------------

@common_habitual_bp.route("/")
class HabitualView(MethodView):
    
    @common_habitual_bp.response(status_code=200)
    def get(self):
        ''' Fetches all habitual tasks '''
        child_id = session.get('child_id', None)  
        if child_id == None:
            return {"status":400,
                    "message": "Child_ID not found" }, 400 
        list_of_tasks = list_all_habitual_tasks(child_id)
        return {"status":200, 
                "message": "Successfully retrieved all tasks", 
                "habitual_tasks": list_of_tasks }

    @common_habitual_bp.response(status_code=201)
    @common_habitual_bp.arguments(schema=HabitualTaskPOSTSchema)
    def post(self, params):
        '''Creating a Habitual task for the Child by the Parent'''
        ht = HabitualTask.from_dict(params)
        child_id = session.get('child_id', None)  
        if child_id == None:
            return {"status":400,
                    "message": "Child_ID not found" }, 400
        status, task_id = add_habitual_task(child_id, ht)
        if status == False:
            return {"message":task_id, "status":400}, 400 
        return {"status":201, "message":"Habitual Task successfully created"}
        
    @common_habitual_bp.response(status_code=200)
    @common_habitual_bp.arguments(schema=HabitualTaskPUTSchema)
    def put(self, params):
        '''Updating a Habitual task for the Child by the Parent'''
        child_id = session.get('child_id', None)  
        if child_id == None:
            return {"status":400,
                    "message": "Child_ID not found" }, 400
        task_id = params['task_id']
        del params['task_id']
        ht = HabitualTask.from_dict(params)
        ret, mssg = update_habitual_task( child_id, task_id, ht)

        if ret:
            return {"status":200, "message":mssg}

        return {"status":400, "message":mssg}

    @common_habitual_bp.response(status_code=200)
    @common_habitual_bp.arguments(schema=HabitualTaskDELSchema)
    def delete(self, params):
        '''Deleting a Habitual task for the Child by the Parent'''
        child_id = session.get('child_id', None)  
        if child_id == None:
            return {"status":400,
                    "message": "Child_ID not found" }, 400
        task_id = params['task_id']
        ret, mssg = delete_habitual_task( child_id, task_id)

        if ret:
            return {"status":200, "message":mssg}

        return {"status":400, "message":mssg}


@common_learning_bp.route("/")
class LearningView(MethodView):
    
    @common_learning_bp.response(status_code=200)
    def get(self):
        ''' Fetches all learning tasks '''
        child_id = session.get('child_id', None)  
        if child_id == None:
            return {"status":400,
                    "message": "Child_ID not found" }, 400 
        list_of_tasks = list_all_learning_tasks(child_id)
        return {"status":200, 
                "message": "Successfully retrieved all tasks", 
                "habitual_tasks": list_of_tasks }

    @common_learning_bp.response(status_code=201)
    @common_learning_bp.arguments(schema=LearningTaskPOSTSchema)
    def post(self, params):
        '''Creating a Learning task for the Child by the Parent'''
        lt = LearningTask.from_dict(params)
        child_id = session.get('child_id', None)  
        if child_id == None:
            return {"status":400,
                    "message": "Child_ID not found" }, 400
        status, task_id = add_learning_task(child_id, lt)
        if status == False:
            return {"message":task_id, "status":400}, 400 
        return {"status":201, "message":"Learning Task successfully created"}
        
    @common_learning_bp.response(status_code=200)
    @common_learning_bp.arguments(schema=LerningTaskPUTSchema)
    def put(self, params):
        '''Updating a Learning task for the Child by the Parent'''
        child_id = session.get('child_id', None)  
        if child_id == None:
            return {"status":400,
                    "message": "Child_ID not found" }, 400
        task_id = params['task_id']
        del params['task_id']
        lt = LearningTask.from_dict(params)
        ret, mssg = update_learning_task( child_id, task_id, lt)

        if ret:
            return {"status":200, "message":mssg}

        return {"status":400, "message":mssg}

    @common_learning_bp.response(status_code=200)
    @common_learning_bp.arguments(schema=LearningTaskDELSchema)
    def delete(self, params):
        '''Deleting a Learning task for the Child by the Parent'''
        child_id = session.get('child_id', None)  
        if child_id == None:
            return {"status":400,
                    "message": "Child_ID not found" }, 400
        task_id = params['task_id']
        ret, mssg = delete_learning_task(child_id, task_id)

        if ret:
            return {"status":200, "message":mssg}

        return {"status":400, "message":mssg}


# -----------------------------------------------------------------------
# Child information Related Routes
# -----------------------------------------------------------------------

@common_bp.route("/child_details")
class ChildDetailsPOST(MethodView):
    @common_bp.response(status_code=200)
    @common_bp.arguments(schema=ChildDetailsSchema)
    def post(self, params):
        '''Fetches all details of a particular child given child_id or parent uuid'''

        print(params)
        # Find out if session contatins child information
        child_id = session.get('child_id', None)  
        if child_id  == None and 'parent_uuid' not in params:
            return {"status":404,
                    "message": "Child_ID not found and Parent UUID not provided" }, 404

        # Provide both infromation to function to retrieve from firestore
        # It will prioritize parent_uuid
        ret = get_child_entry(child_id, params['parent_uuid'])
        
        if ret:
            child_dict, child_id = ret 
            # Store the child_id in the session cookie
            session['child_id'] = child_id
            return child_dict
        else:
            return {"status":404,
                    "message": "Child Document not Found" }, 404

