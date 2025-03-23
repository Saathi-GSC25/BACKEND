from datetime import datetime
from marshmallow import Schema, fields
# ---------------------------
# Marshmallow Schemas
# ---------------------------

# ---------------------------
# Schemas for /child/create
# ---------------------------

class ChildCreateSchema(Schema):
    name = fields.Str(required=True)
    age = fields.Int(required=True)
    sex = fields.Str(required=True)
    neuro_cat = fields.List(fields.Str(), required=True)
    additional_info = fields.Str(missing=None)

# ---------------------------
# Schemas for /child/cred
# ---------------------------
class ChildCredentialsUpdateSchma(Schema):
    child_id = fields.Str(required=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)

# ---------------------------
# Schemas for /child/login
# ---------------------------
class ChildLoginSchma(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


# ---------------------------
# Schemas for /child/details
# ---------------------------
class ChildDetailsSchema(Schema):
    child_id = fields.Str(required=True)



class StressSchema(Schema):
    stress = fields.Float(missing=None)
    reason = fields.Str(missing=None)

class ConversationSummarySchema(Schema):
    mood = fields.Str(missing=None)
    stress = fields.Nested(StressSchema, missing=None)
    number_of_conversation = fields.Int(missing=None)
    time_spent = fields.Int(missing=None)
    interest = fields.Str(missing=None)

class ChildSchema(Schema):
    report_id = fields.Str(missing=None)
    name = fields.Str(missing=None)
    age = fields.Int(missing=None)
    sex = fields.Str(missing=None)
    neuro_cat = fields.List(fields.Str(), missing=None)
    additional_info = fields.Str(missing=None)
    points = fields.Int(missing=None)
    date_and_time_created = fields.DateTime(missing=None)
    username = fields.Str(missing=None)
    password = fields.Str(missing=None)
    conversation_summary = fields.Nested(ConversationSummarySchema, missing=None)
    conversation_ids = fields.List(fields.Str(), missing=None)


class EmotionSchema(Schema):
    happy = fields.Float(missing=None)
    sad = fields.Float(missing=None)
    anxious = fields.Float(missing=None)
    anger = fields.Float(missing=None)


class ConversationSchema(Schema):
    date_and_time = fields.DateTime(missing=None)
    duration = fields.Float(missing=None)  # conversation time in minutes
    summary = fields.Str(missing=None)
    emotion = fields.Nested(EmotionSchema, missing=None)
    stress = fields.Nested(StressSchema, missing=None)
    interests = fields.Str(missing=None)
