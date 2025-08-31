from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from utils.database import mongo

class User:
    @staticmethod
    def get_collection():
        return mongo.get_db().users
    
    def __init__(self, username, email, password, role='user', avatar=None):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role = role  # Default role is 'user'
        self.avatar = avatar  # Avatar URL or path
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_active = True
    
    def save(self):
        user_data = {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'avatar': self.avatar,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active
        }
        return self.get_collection().insert_one(user_data).inserted_id
    
    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)
    
    @staticmethod
    def to_dict(user):
        if not user:
            return None
        
        # Create a copy to avoid modifying the original document
        user_dict = user.copy()
        
        # Convert ObjectId to string
        if '_id' in user_dict:
            user_dict['_id'] = str(user_dict['_id'])
        
        # Convert datetime objects to ISO format strings (only if they're datetime objects)
        if 'created_at' in user_dict:
            if isinstance(user_dict['created_at'], datetime):
                user_dict['created_at'] = user_dict['created_at'].isoformat()
            # If it's already a string, leave it as is
        
        if 'updated_at' in user_dict:
            if isinstance(user_dict['updated_at'], datetime):
                user_dict['updated_at'] = user_dict['updated_at'].isoformat()
            # If it's already a string, leave it as is
        
        return user_dict
    
    # Additional utility methods for role management
    @staticmethod
    def is_admin(user):
        return user and user.get('role') in ['admin', 'super_admin']
    
    @staticmethod
    def is_super_admin(user):
        return user and user.get('role') == 'super_admin'
    
    @staticmethod
    def update_role(user_id, new_role):
        """Update user's role"""
        if new_role not in ['user', 'admin', 'super_admin']:
            raise ValueError("Invalid role. Must be 'user', 'admin', or 'super_admin'")
        
        return User.get_collection().update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'role': new_role, 'updated_at': datetime.utcnow()}}
        )
    
    @staticmethod
    def update_avatar(user_id, avatar_url):
        """Update user's avatar"""
        return User.get_collection().update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'avatar': avatar_url, 'updated_at': datetime.utcnow()}}
        )
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        return User.get_collection().find_one({'_id': ObjectId(user_id)})
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        return User.get_collection().find_one({'email': email})
    
    @staticmethod
    def find_by_username(username):
        """Find user by username"""
        return User.get_collection().find_one({'username': username})