from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.project_service import ProjectService
from utils.responses import success_response, error_response
import datetime

def init_project_routes(app):
    @app.route('/api/projects', methods=['POST'])
    @jwt_required()
    def create_project():
        try:
            data = request.get_json()
            if not data:
                return error_response("No JSON data provided", 400)
                
            name = data.get('name')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            description = data.get('description')
            created_by = get_jwt_identity()  # Get user ID from JWT
            
            if not all([name, start_date, end_date, description]):
                return error_response("Missing required fields", 400)
            
            project, err = ProjectService.create_project(
                name, start_date, end_date, description, created_by
            )
            if err:
                return error_response(err, 400)
            
            return success_response(project, "Project created successfully", 201)
        except Exception as e:
            app.logger.error(f"Error in create_project: {str(e)}")
            return error_response("Internal server error", 500)
    
    @app.route('/api/my-projects', methods=['GET'])
    @jwt_required()
    def get_my_projects():
        try:
            user_id = get_jwt_identity()  # Extract user_id from JWT
            projects = ProjectService.get_projects_by_user(user_id)
            return success_response(projects)
        except Exception as e:
            app.logger.error(f"Error in get_my_projects: {str(e)}")
            return error_response("Internal server error", 500)

    @app.route('/api/projects', methods=['GET'])
    @jwt_required()
    def get_projects():
        try:
            projects = ProjectService.get_all_projects()
            return success_response(projects)
        except Exception as e:
            app.logger.error(f"Error in get_projects: {str(e)}")
            return error_response("Internal server error", 500)
    
    @app.route('/api/projects/<project_id>', methods=['GET'])
    @jwt_required()
    def get_project(project_id):
        try:
            project = ProjectService.get_project_by_id(project_id)
            if not project:
                return error_response("Project not found", 404)
            return success_response(project)
        except Exception as e:
            app.logger.error(f"Error in get_project: {str(e)}")
            return error_response("Internal server error", 500)
    
    @app.route('/api/projects/<project_id>', methods=['PUT'])
    @jwt_required()
    def update_project(project_id):
        try:
            data = request.get_json()
            if not data:
                return error_response("No JSON data provided", 400)
                
            updates = {
                'name': data.get('name'),
                'start_date': data.get('start_date'),
                'end_date': data.get('end_date'),
                'description': data.get('description'),
                'status': data.get('status')
            }
            # Remove None values
            updates = {k: v for k, v in updates.items() if v is not None}
            
            project, err = ProjectService.update_project(project_id, updates)
            if err:
                return error_response(err, 400)
            
            return success_response(project, "Project updated successfully")
        except Exception as e:
            app.logger.error(f"Error in update_project: {str(e)}")
            return error_response("Internal server error", 500)
    
    @app.route('/api/projects/<project_id>', methods=['DELETE'])
    @jwt_required()
    def delete_project(project_id):
        try:
            if not ProjectService.delete_project(project_id):
                return error_response("Project not found", 404)
            return success_response(None, "Project deleted successfully")
        except Exception as e:
            app.logger.error(f"Error in delete_project: {str(e)}")
            return error_response("Internal server error", 500)
    
    @app.route('/api/projects/<project_id>/team', methods=['POST'])
    @jwt_required()
    def add_team_member(project_id):
        try:
            data = request.get_json()
            if not data:
                return error_response("No JSON data provided", 400)
                
            user_id = data.get('user_id')
            role = data.get('role')
            
            if not all([user_id, role]):
                return error_response("Missing user_id or role", 400)
            
            if not ProjectService.add_team_member(project_id, user_id, role):
                return error_response("Failed to add team member", 400)
            
            project = ProjectService.get_project_by_id(project_id)
            return success_response(project, "Team member added successfully")
        except Exception as e:
            app.logger.error(f"Error in add_team_member: {str(e)}")
            return error_response("Internal server error", 500)
    
    @app.route('/api/projects/<project_id>/tasks', methods=['POST'])
    @jwt_required()
    def add_task(project_id):
        try:
            data = request.get_json()
            if not data:
                return error_response("No JSON data provided", 400)
                
            task = {
                'name': data.get('name'),
                'description': data.get('description'),
                'assigned_to': data.get('assigned_to'),  # user_id
                'status': 'pending',
                'created_at': datetime.utcnow().isoformat()
            }
            
            if not all([task['name'], task['description']]):
                return error_response("Missing task name or description", 400)
            
            if not ProjectService.add_task(project_id, task):
                return error_response("Failed to add task", 400)
            
            project = ProjectService.get_project_by_id(project_id)
            return success_response(project, "Task added successfully")
        except Exception as e:
            app.logger.error(f"Error in add_task: {str(e)}")
            return error_response("Internal server error", 500)