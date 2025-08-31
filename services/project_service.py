from datetime import datetime
from bson import ObjectId
from models.project import Project
import logging

logger = logging.getLogger(__name__)

class ProjectService:
    @staticmethod
    def get_all_projects():
        try:
            projects = Project.get_collection().find()
            return [Project.to_dict(project) for project in projects]
        except Exception as e:
            logger.error(f"Error getting all projects: {e}")
            return []
    
    @staticmethod
    def get_project_by_id(project_id):
        try:
            project = Project.get_collection().find_one({'_id': ObjectId(project_id)})
            return Project.to_dict(project)
        except Exception as e:
            logger.error(f"Error getting project by ID {project_id}: {e}")
            return None
    
    @staticmethod
    def get_projects_by_user(user_id):
        try:
            projects = Project.get_collection().find({"created_by": user_id})
            return [Project.to_dict(project) for project in projects]
        except Exception as e:
            logger.error(f"Error getting projects for user {user_id}: {e}")
            return []


    @staticmethod
    def create_project(name, start_date, end_date, description, created_by):
        try:
            new_project = Project(name, start_date, end_date, description, created_by)
            project_id = new_project.save()
            project = Project.get_collection().find_one({'_id': project_id})
            return Project.to_dict(project), None
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return None, str(e)
    
    @staticmethod
    def update_project(project_id, updates):
        try:
            updates['updated_at'] = datetime.utcnow()
            result = Project.get_collection().update_one(
                {'_id': ObjectId(project_id)},
                {'$set': updates}
            )
            if result.modified_count == 0:
                return None, "Project not found or no changes made"
            
            project = Project.get_collection().find_one({'_id': ObjectId(project_id)})
            return Project.to_dict(project), None
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {e}")
            return None, str(e)
    
    @staticmethod
    def delete_project(project_id):
        try:
            result = Project.get_collection().delete_one({'_id': ObjectId(project_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            return False
    
    @staticmethod
    def add_team_member(project_id, user_id, role):
        try:
            member = {'user_id': user_id, 'role': role}
            result = Project.get_collection().update_one(
                {'_id': ObjectId(project_id)},
                {'$addToSet': {'team_members': member}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error adding team member to project {project_id}: {e}")
            return False
    
    @staticmethod
    def add_task(project_id, task):
        try:
            result = Project.get_collection().update_one(
                {'_id': ObjectId(project_id)},
                {'$addToSet': {'tasks': task}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error adding task to project {project_id}: {e}")
            return False