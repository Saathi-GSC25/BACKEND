from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date, time

# ---------------------------
# Domain Class: Child 
# ---------------------------
class Child:
    def __init__(self, 
                 report_id: Optional[str] = None,
                 parent_uuid: Optional[str] = None,
                 name: Optional[str] = None, 
                 age: Optional[int] = None, 
                 sex: Optional[str] = None, 
                 neuro_cat: Optional[List[str]] = None, 
                 additional_info: Optional[str] = None, 
                 points: Optional[int] = None,
                 date_and_time_created: Optional[datetime] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 conversation_summary: Optional[Dict[str, Any]] = None,
                 conversation_ids: Optional[List[str]] = None):

        self.parent_uuid = parent_uuid 
        self.report_id = report_id
        self.name = name
        self.age = age
        self.sex = sex
        self.neuro_cat = neuro_cat
        self.additional_info = additional_info
        self.points = points
        self.date_and_time_created = date_and_time_created
        self.username = username
        self.password = password
        self.conversation_summary = conversation_summary
        self.conversation_ids = conversation_ids

    def to_dict(self) -> Dict[str, Any]:
        return {
            key: (value.isoformat() if isinstance(value, datetime) else value)
            for key, value in self.__dict__.items() if value is not None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Child":
        # Copy the original dictionary
        new_data = {key: value for key, value in data.items()}
        
        # Process the date field if it's provided as a string
        date_field = new_data.get("date_and_time_created")
        if date_field and isinstance(date_field, str):
            new_data["date_and_time_created"] = datetime.fromisoformat(date_field)

        if "child_id" in new_data:
            del new_data["child_id"]
        
        return cls(**new_data)

# ---------------------------
# Domain Class: Conversation
# ---------------------------
class Conversation:
    def __init__(self, 
                 date: Optional[date] = None,
                 time: Optional[time] = None,
                 duration: Optional[Union[int, float]] = None,
                 summary: Optional[str] = None,
                 emotion: Optional[str] = None,
                 stress: Optional[str] = None,
                 stressSummary: Optional[str] = None,
                 interests: Optional[str] = None
                 ):
        """
        Initialize a Conversation instance.
        Unprovided parameters default to None.
        """
        self.date = date
        self.time = time
        self.duration = duration
        self.summary = summary
        self.emotion = emotion
        self.stress = stress
        self.stressSummary = stressSummary
        self.interests = interests

    def to_dict(self) -> Dict[str, Any]:
        """ Convert the Conversation instance to a dictionary,
            only including keys with non-None values """
        return {
            key: (value.isoformat() if isinstance(value, (date, time) ) else value)
            for key, value in self.__dict__.items() if value is not None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        # Copy the original dictionary
        new_data = {key: value for key, value in data.items()}
       
        date_field = new_data.get("date")
        time_field = new_data.get("time")

        if date_field and isinstance(date_field, str) :
            date_obj = date.fromisoformat(date_field)  
            new_data['date'] = date_obj
        if time_field and isinstance(time_field, str):
            time_obj = time.fromisoformat(time_field) 
            new_data['time'] = time_obj
        
        return cls(**new_data)

# ---------------------------
# Domain Class: Conversation Summary
# ---------------------------
class ConversationSummary:
    def __init__(self, 
                 last_updated: Optional[datetime] = None,
                 emotion: Optional[str] = None,
                 conversations: Optional[int] = None,
                 stress: Optional[str] = None,
                 stressSummary: Optional[str] = None,
                 total_duration: Optional[Union[int, float]] = None,
                 interests_summary:Optional[str] = None, 
                 ):
        """
        Initialize a Conversation instance.
        Unprovided parameters default to None.
        """
        self.last_updated = last_updated
        self.total_duration = total_duration
        self.emotion = emotion
        self.stress = stress
        self.stressSummary = stressSummary
        self.conversations = conversations
        self.interests_summary = interests_summary

    def to_dict(self) -> Dict[str, Any]:
        """ Convert the Conversation instance to a dictionary,
            only including keys with non-None values """
        return {
            key: (value.strftime("%H:%M, %d/%m/%Y") if isinstance(value, datetime) else value)
            for key, value in self.__dict__.items() if value is not None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationSummary":
        # Copy the original dictionary
        new_data = {key: value for key, value in data.items()}
        
        # Process the date field if it's provided as a string
        date_field = new_data.get("last_updated")
        if date_field and isinstance(date_field, str):
            new_data["last_updated"] = datetime.strptime(date_field, "%H:%M, %d/%m/%Y")
        
        return cls(**new_data)

# ---------------------------
# Domain Class: Habitual Task
# ---------------------------

class HabitualTask:
    def __init__(self, 
                 is_done: Optional[bool] = None,
                 from_time: Optional[time] = None,
                 to_time: Optional[time] = None,
                 points: Optional[int] = None,
                 title: Optional[str] = None,
                 ):
        """
        Initialize a Conversation instance.
        Unprovided parameters default to None.
        """
        self.is_done = is_done
        self.from_time = from_time
        self.to_time = to_time
        self.points = points
        self.title = title

    def to_dict(self) -> Dict[str, Any]:
        """ Convert the Conversation instance to a dictionary,
            only including keys with non-None values """
        return {
            key: (value.isoformat() if isinstance(value, time) else value)
            for key, value in self.__dict__.items() if value is not None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HabitualTask":
        # Copy the original dictionary
        new_data = {key: value for key, value in data.items()}
        
        time_field = new_data.get("from_time")
        if time_field and isinstance(time_field, str):
            new_data["from_time"] = datetime.fromisoformat(time_field)

        time_field = new_data.get("to_time")
        if time_field and isinstance(time_field, str):
            new_data["to_time"] = datetime.fromisoformat(time_field)
        
        return cls(**new_data)

# ---------------------------
# Domain Class: Learning Task
# ---------------------------

class LearningTask:
    def __init__(self, 
                 is_done: Optional[bool] = None,
                 points: Optional[int] = None,
                 link:Optional[str] = None,
                 title: Optional[str] = None,
                 ):
        """
        Initialize a Conversation instance.
        Unprovided parameters default to None.
        """
        self.is_done = is_done
        self.link = link
        self.points = points
        self.title = title

    def to_dict(self) -> Dict[str, Any]:
        """ Convert the Conversation instance to a dictionary,
            only including keys with non-None values """
        return {
            key: value 
            for key, value in self.__dict__.items() if value is not None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningTask":
        # Copy the original dictionary
        new_data = {key: value for key, value in data.items()}
        
        return cls(**new_data)

