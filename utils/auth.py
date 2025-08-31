from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash
from datetime import timedelta
from models.user import User

def authenticate_user(user, password):
    if not user or not check_password_hash(user['password_hash'], password):
        return None
    
    # Convert user to serializable format before creating token
    user_dict = User.to_dict(user)
    
    access_token = create_access_token(
        identity=str(user['_id']),
        additional_claims={
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'role': user.get('role', 'user'),
                'avatar': user.get('avatar', 'https://cdn-icons-png.flaticon.com/512/4715/4715330.png')
            }
        }
    )
    
    return {
        'access_token': access_token,
        'user': user_dict
    }
