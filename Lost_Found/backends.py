# Lost_Found/backends.py
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User

class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(f"🔍 DEBUG: Authentication attempt with username: '{username}'")
        
        try:
            # Try to find user by email OR username
            user = User.objects.get(
                Q(email__iexact=username) | Q(username__iexact=username)
            )
            print(f"✅ DEBUG: Found user: {user.username}, email: {user.email}")
            
        except User.DoesNotExist:
            print(f"❌ DEBUG: No user found with email or username: '{username}'")
            return None
        except User.MultipleObjectsReturned:
            print(f"⚠️ DEBUG: Multiple users found with email or username: '{username}'")
            user = User.objects.filter(
                Q(email__iexact=username) | Q(username__iexact=username)
            ).first()
        
        # Check password
        if user:
            print(f"🔑 DEBUG: Checking password for user: {user.username}")
            if user.check_password(password):
                print(f"✅ DEBUG: Password correct for user: {user.username}")
                if self.user_can_authenticate(user):
                    print(f"✅ DEBUG: User can authenticate: {user.username}")
                    return user
                else:
                    print(f"❌ DEBUG: User cannot authenticate (inactive): {user.username}")
            else:
                print(f"❌ DEBUG: Password incorrect for user: {user.username}")
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None