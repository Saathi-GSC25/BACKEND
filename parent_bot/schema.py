from marshmallow import Schema, fields

# Object to be sent inside the history
class HistorySchema(Schema):
    role = fields.Str(required=True)
    parts = fields.Str(required=True)

# Chat Request Schema 
class ChatSchema(Schema):
    history = fields.List(fields.Nested(HistorySchema), required=True)
    chat = fields.Str()
