from datetime import datetime
from bson import ObjectId
from utils.database import mongo

class Project:
    @staticmethod
    def get_collection():
        return mongo.get_db().projects
    
    def __init__(self, name, start_date, end_date, description, created_by):
        self.name = name
        self.start_date = start_date  # String in format "YYYY-MM-DD"
        self.end_date = end_date      # String in format "YYYY-MM-DD"
        self.description = description
        self.created_by = created_by   # User ID who created the project
        self.team_members = []        # Array of {user_id, role}
        self.tasks = []               # Array of task objects
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.status = "planned"       # planned, ongoing, completed, cancelled
    
    def save(self):
        project_data = {
            'name': self.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'description': self.description,
            'created_by': self.created_by,
            'team_members': self.team_members,
            'tasks': self.tasks,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'status': self.status
        }
        return self.get_collection().insert_one(project_data).inserted_id
    
    @staticmethod
    def to_dict(project):
        if not project:
            return None
        project['_id'] = str(project['_id'])
        project['created_at'] = project['created_at'].isoformat()
        project['updated_at'] = project['updated_at'].isoformat()
        return project