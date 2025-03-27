from marshmallow import Schema, fields



# ---------------------------
# Schemas for /common/habitual
# ---------------------------
class HabitualTaskPOSTSchema(Schema):
    from_time = fields.Time(format="%H:%M", required=True)
    is_done = fields.Bool(missing=False)
    to_time =  fields.Time(format="%H:%M", required=True)
    points = fields.Int(required = True)
    title = fields.Str(required = True)

class HabitualTaskPUTSchema(Schema):
    task_id = fields.Str(required=True)
    is_done = fields.Bool()
    from_time = fields.Time(format="%H:%M")
    to_time =  fields.Time(format="%H:%M")
    points = fields.Int()
    title = fields.Str()

class HabitualTaskDELSchema(Schema):
    task_id = fields.Str(required=True)


# ---------------------------
# Schemas for /common/learning
# ---------------------------
class LearningTaskPOSTSchema(Schema):
    link = fields.Str(required=True)
    is_done = fields.Bool(missing=False)
    points = fields.Int(required = True)
    title = fields.Str(required = True)

class LerningTaskPUTSchema(Schema):
    task_id = fields.Str(required=True)
    link = fields.Str()
    is_done = fields.Bool()
    points = fields.Int()
    title = fields.Str()

class LearningTaskDELSchema(Schema):
    task_id = fields.Str(required=True)

# ---------------------------
# Schemas for /common/child_details
# ---------------------------
class ChildDetailsSchema(Schema):
    parent_uuid = fields.Str(missing=None)
