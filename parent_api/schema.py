from marshmallow import Schema, fields

# Object to be sent inside the history
class HistorySchema(Schema):
    role = fields.Str(required=True)
    parts = fields.Str(required=True)

# Chat Request Schema 
class ChatSchema(Schema):
    history = fields.List(fields.Nested(HistorySchema), required=True)
    chat = fields.Str()

# ---------------------------
# Schemas for /parent/child_create
# ---------------------------

class ChildCreateSchema(Schema):
    points = fields.Int(missing=0)
    parent_uuid = fields.Str(required=True)
    name = fields.Str(required=True)
    age = fields.Int(required=True)
    sex = fields.Str(required=True)
    neuro_cat = fields.List(fields.Str(), required=True)
    additional_info = fields.Str(missing=None)

# ---------------------------
# Schemas for /parent/child_cred_update
# ---------------------------
class ChildCredentialsUpdateSchma(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

