from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.user_service import UserService
from utils.auth import authenticate_user
from utils.responses import success_response, error_response
from models.user import User

def init_user_routes(app):
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')  # Default to 'user' if not provided
        avatar = data.get('avatar')  # Optional avatar
        
        if not all([username, email, password]):
            return error_response("Missing required fields", 400)
        
        # Validate role
        if role not in ['user', 'admin', 'super_admin']:
            return error_response("Invalid role. Must be 'user', 'admin', or 'super_admin'", 400)
        
        if UserService.get_user_by_username(username):
            return error_response("Username already exists", 400)
        
        if UserService.get_user_by_email(email):
            return error_response("Email already exists", 400)
        
        user = UserService.create_user(username, email, password, role, avatar)
        if not user:
            return error_response("Failed to create user", 500)
        
        return success_response(user, "User created successfully", 201)
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return error_response("Email and password required", 400)
        
        user = UserService.get_user_by_email(email)
        auth_result = authenticate_user(user, password)
        
        if not auth_result:
            return error_response("Invalid credentials", 401)
        
        return success_response(auth_result, "Login successful")
    
    @app.route('/api/users', methods=['GET'])
    # @jwt_required()
    def get_users():
        users = UserService.get_all_users()
        return success_response([User.to_dict(user) for user in users])
    
    @app.route('/api/users/<user_id>', methods=['GET'])
    @jwt_required()
    def get_user(user_id):
        user = UserService.get_user_by_id(user_id)
        if not user:
            return error_response("User not found", 404)
        return success_response(User.to_dict(user))
    
    @app.route('/api/users/email/<email>', methods=['GET'])
    @jwt_required()
    def get_user_by_email(email):
        user = UserService.get_user_by_email(email)
        if not user:
            return error_response("User not found", 404)
        return success_response(User.to_dict(user))
    
    @app.route('/api/users/username/<username>', methods=['GET'])
    @jwt_required()
    def get_user_by_username(username):
        user = UserService.get_user_by_username(username)
        if not user:
            return error_response("User not found", 404)
        return success_response(User.to_dict(user))
    
    @app.route('/api/users/<user_id>', methods=['PUT'])
    @jwt_required()
    def update_user(user_id):
        current_user_id = get_jwt_identity()
        current_user = UserService.get_user_by_id(current_user_id)
        
        # Only allow users to update their own profile, unless they're admin
        if current_user_id != user_id and not User.is_admin(current_user):
            return error_response("Unauthorized", 403)
        
        data = request.get_json()
        
        # Prevent non-admins from changing roles
        if 'role' in data and not User.is_admin(current_user):
            return error_response("Only admins can change roles", 403)
        
        # Validate role if provided
        if 'role' in data and data['role'] not in ['user', 'admin', 'super_admin']:
            return error_response("Invalid role. Must be 'user', 'admin', or 'super_admin'", 400)
        
        updated_user = UserService.update_user(user_id, data)
        if not updated_user:
            return error_response("User not found", 404)
        
        return success_response(User.to_dict(updated_user), "User updated successfully")
    
    @app.route('/api/users/<user_id>/avatar', methods=['PUT'])
    @jwt_required()
    def update_user_avatar(user_id):
        current_user_id = get_jwt_identity()
        
        # Only allow users to update their own avatar
        if current_user_id != user_id:
            return error_response("Unauthorized", 403)
        
        data = request.get_json()
        avatar_url = data.get('avatar')
        
        if not avatar_url:
            return error_response("Avatar URL is required", 400)
        
        updated_user = UserService.update_user_avatar(user_id, avatar_url)
        if not updated_user:
            return error_response("User not found", 404)
        
        return success_response(User.to_dict(updated_user), "Avatar updated successfully")
    
    @app.route('/api/users/<user_id>/role', methods=['PUT'])
    @jwt_required()
    def update_user_role(user_id):
        current_user_id = get_jwt_identity()
        current_user = UserService.get_user_by_id(current_user_id)
        
        # Only allow admins to change roles
        if not User.is_admin(current_user):
            return error_response("Only admins can change roles", 403)
        
        data = request.get_json()
        new_role = data.get('role')
        
        if not new_role or new_role not in ['user', 'admin', 'super_admin']:
            return error_response("Valid role is required: 'user', 'admin', or 'super_admin'", 400)
        
        updated_user = UserService.update_user_role(user_id, new_role)
        if not updated_user:
            return error_response("User not found", 404)
        
        return success_response(User.to_dict(updated_user), "Role updated successfully")
    
    @app.route('/api/users/<user_id>', methods=['DELETE'])
    def delete_user(user_id):
        # current_user_id = get_jwt_identity()
        # current_user = UserService.get_user_by_id(current_user_id)
        
        # # Users can only delete themselves, admins can delete any user
        # if current_user_id != user_id and not User.is_admin(current_user):
        #     return error_response("Unauthorized", 403)
        
        if not UserService.delete_user(user_id):
            return error_response("User not found", 404)
        
        return success_response(None, "User deleted successfully")
    
    @app.route('/api/users/me', methods=['GET'])
    @jwt_required()
    def get_current_user():
        current_user_id = get_jwt_identity()
        user = UserService.get_user_by_id(current_user_id)
        if not user:
            return error_response("User not found", 404)
        return success_response(User.to_dict(user))
    
    @app.route('/api/users/me', methods=['PUT'])
    @jwt_required()
    def update_current_user():
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Remove role from data if present (users can't change their own role)
        if 'role' in data:
            del data['role']
        
        updated_user = UserService.update_user(current_user_id, data)
        if not updated_user:
            return error_response("User not found", 404)
        
        return success_response(User.to_dict(updated_user), "Profile updated successfully")