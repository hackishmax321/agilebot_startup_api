from datetime import datetime
from bson import ObjectId
from models.user import User
import logging

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def get_all_users():
        try:
            users = User.get_collection().find()
            return [User.to_dict(user) for user in users]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    @staticmethod
    def get_user_by_id(user_id):
        try:
            user = User.get_collection().find_one({'_id': ObjectId(user_id)})
            return user  # Return raw user document for role checking
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(email):
        try:
            user = User.get_collection().find_one({'email': email})
            return user  # Return raw user document for authentication
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    @staticmethod
    def get_user_by_username(username):
        try:
            user = User.get_collection().find_one({'username': username})
            return user  # Return raw user document
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    @staticmethod
    def create_user(username, email, password, role, avatar=None):
        print(role)
        try:
            # Check if user already exists
            if UserService.get_user_by_email(email):
                return None
            if UserService.get_user_by_username(username):
                return None
                
            new_user = User(username, email, password, role, avatar)
            user_id = new_user.save()
            user = User.get_collection().find_one({'_id': user_id})
            return User.to_dict(user)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def update_user(user_id, update_data):
        try:
            # Remove None values from update data
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            if not update_data:
                return None
                
            # Add updated_at timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            result = User.get_collection().update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                updated_user = User.get_collection().find_one({'_id': ObjectId(user_id)})
                return User.to_dict(updated_user)
            return None
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return None
    
    @staticmethod
    def update_user_role(user_id, new_role):
        try:
            if new_role not in ['user', 'admin', 'super_admin']:
                return None
                
            result = User.get_collection().update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {
                    'role': new_role,
                    'updated_at': datetime.utcnow()
                }}
            )
            
            if result.modified_count > 0:
                updated_user = User.get_collection().find_one({'_id': ObjectId(user_id)})
                return User.to_dict(updated_user)
            return None
        except Exception as e:
            logger.error(f"Error updating user role {user_id}: {e}")
            return None
    
    @staticmethod
    def update_user_avatar(user_id, avatar_url):
        try:
            result = User.get_collection().update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {
                    'avatar': avatar_url,
                    'updated_at': datetime.utcnow()
                }}
            )
            
            if result.modified_count > 0:
                updated_user = User.get_collection().find_one({'_id': ObjectId(user_id)})
                return User.to_dict(updated_user)
            return None
        except Exception as e:
            logger.error(f"Error updating user avatar {user_id}: {e}")
            return None
    
    @staticmethod
    def delete_user(user_id):
        try:
            result = User.get_collection().delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    @staticmethod
    def get_users_by_role(role):
        try:
            if role not in ['user', 'admin', 'super_admin']:
                return []
                
            users = User.get_collection().find({'role': role})
            return [User.to_dict(user) for user in users]
        except Exception as e:
            logger.error(f"Error getting users by role {role}: {e}")
            return []
    
    @staticmethod
    def search_users(query):
        try:
            users = User.get_collection().find({
                '$or': [
                    {'username': {'$regex': query, '$options': 'i'}},
                    {'email': {'$regex': query, '$options': 'i'}}
                ]
            })
            return [User.to_dict(user) for user in users]
        except Exception as e:
            logger.error(f"Error searching users with query {query}: {e}")
            return []
    
    @staticmethod
    def deactivate_user(user_id):
        try:
            result = User.get_collection().update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {
                    'is_active': False,
                    'updated_at': datetime.utcnow()
                }}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {e}")
            return False
    
    @staticmethod
    def activate_user(user_id):
        try:
            result = User.get_collection().update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {
                    'is_active': True,
                    'updated_at': datetime.utcnow()
                }}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error activating user {user_id}: {e}")
            return False