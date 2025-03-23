from flask import abort, request
from flask.views import MethodView
from flask_smorest import Blueprint

from info.firestore import add_new_conversation, check_username_password, create_child_entry, get_child_entry, update_child_entry
from info.store_schema import Child, Conversation 
from info.api_schema import ChildCreateSchema, ChildCredentialsUpdateSchma, ChildDetailsSchema, ChildLoginSchma, ConversationSchema


info_bp = Blueprint('Firestore API', __name__, 
                    url_prefix='/store', 
                    description="")

@info_bp.route("/child/create")
class ChildPOST(MethodView):
    # POST REQUEST 
    @info_bp.response(status_code=201)
    @info_bp.arguments(schema=ChildCreateSchema)
    def post(self, params):
        child = Child.from_dict(params)
        cid = create_child_entry(child) 
        return { "message":"Successfully created", "cid":cid }


@info_bp.route("/child/cred")
class ChildCredPUT(MethodView):
    # PUT REQUEST 
    @info_bp.response(status_code=200)
    @info_bp.arguments(schema=ChildCredentialsUpdateSchma)
    def put(self, params):
        child: Child = Child.from_dict(params)
        status = update_child_entry(params['child_id'], child) 
        return { "message" : status }


@info_bp.route("/child/login")
class ChildLoginPOST(MethodView):
    # POST REQUEST 
    @info_bp.response(status_code=200)
    @info_bp.arguments(schema=ChildLoginSchma)
    def post(self, params):
        child: Child = Child.from_dict(params)
        status, child_id = check_username_password(params['username'], params['password']) 
        if child_id is None:
            abort(403, description="Forbidden: Incorrect username or password.")
        return { "message" : status,  "cid": child_id }


@info_bp.route("/child/details")
class ChildDetailsPOST(MethodView):
    # POST REQUEST 
    @info_bp.response(status_code=201)
    @info_bp.arguments(schema=ChildDetailsSchema)
    def post(self, params):
        child_id = params['child_id']
        child_dict = get_child_entry(child_id)
        return child_dict











@info_bp.route("/conversation/<child_id>")
class ConvPOST(MethodView):
    # POST REQUEST 
    @info_bp.response(status_code=201)
    @info_bp.arguments(schema=ConversationSchema)
    def post(self, params, child_id):
        conv = Conversation.from_dict(params)
        add_new_conversation(child_id, conv)
        return {"message":"Successfully created"}


