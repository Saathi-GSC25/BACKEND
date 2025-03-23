from typing import Any, Dict, List, Optional, Union
from datetime import datetime

# ---------------------------
# Domain Class: Child 
# ---------------------------
class Child:
    def __init__(self, 
                 report_id: Optional[str] = None,
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
                 date_and_time: Optional[datetime] = None,
                 duration: Optional[Union[int, float]] = None,
                 summary: Optional[str] = None,
                 emotion: Optional[Dict[str, Union[int, float]]] = None,
                 stress: Optional[Dict[str, Union[int, float, str]]] = None,
                 interests: Optional[str] = None):
        """
        Initialize a Conversation instance.
        Unprovided parameters default to None.
        """
        self.date_and_time = date_and_time
        self.duration = duration
        self.summary = summary
        self.emotion = emotion
        self.stress = stress
        self.interests = interests

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Conversation instance to a dictionary,
        only including keys with non-None values.
        """
        return {
            key: (value.isoformat() if isinstance(value, datetime) else value)
            for key, value in self.__dict__.items() if value is not None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        # Copy the original dictionary
        new_data = {key: value for key, value in data.items()}
        
        # Process the date field if it's provided as a string
        date_field = new_data.get("date_and_time")
        if date_field and isinstance(date_field, str):
            new_data["date_and_time"] = datetime.fromisoformat(date_field)
        
        return cls(**new_data)

