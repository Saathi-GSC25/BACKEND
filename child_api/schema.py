from marshmallow import Schema, fields, validate

class TextSchema(Schema):
    text = fields.Str()

class AudioSchema(Schema):
    file = fields.Field(required=True, 
                        metadata={"type": "string", "format": "binary"})

# ---------------------------
# Schemas for /child/login
# ---------------------------
class ChildLoginSchma(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)



# ---------------------------
# Schemas for /conversation
# ---------------------------

# class SystemMessageSchema(Schema):
#     role = fields.String(required=True, 
#                          validate=validate.OneOf(["user", "model"]))
#     parts = fields.String(required=True)
#
# class ConversationCreateSchema(Schema):
#     child_id = fields.Str(required=True)
#     chat_history = fields.List(fields.Nested(SystemMessageSchema), 
#                                required=True)
#     emotion = fields.List(fields.Str, required=True)
#     total_duration = fields.Float(required=True)  

