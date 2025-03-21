from marshmallow import Schema, fields

class TextSchema(Schema):
    text = fields.Str()

class AudioSchema(Schema):
    file = fields.Field(required=True, 
                        metadata={"type": "string", "format": "binary"})
