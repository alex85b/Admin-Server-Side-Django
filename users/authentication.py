import jwt
import datetime
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

from .models import Users


# This .py will use a Json Web Token for user authorization.
# Server will generate a JWT, it will be encrypted and will contain a 'secret',
#   Then said JWT will be sent back to the user, it will not be stored in the server!
#       when and if a user sends a request back with the generated JWT, server will decrypt and check the secret.
# Useful explanation: https://www.youtube.com/watch?v=7Q17ubqLfaM&ab_channel=WebDevSimplified
# the HS256 algo: https://auth0.com/blog/rs256-vs-hs256-whats-the-difference/

# create a session for user that passed log-in.
#   make user authenticated
def generate_access_token(user):
    payload = {
        # expire on = now + the difference between now and 60 minutes from now = expire after 60 minutes.
        'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60), 'iat': datetime.datetime.utcnow()
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

# authenticate incoming user
#   check if user authenticated


class JWTAuthentication(BaseAuthentication):
    print('LOG: JWTAuthentication: Start')

    def authenticate(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            return None

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('un-authenticated')

        # Notice there is a difference between:
        # Users.objects.filter(id=payload['user_id']) <-- a Whole query set, that can contain one result
        # Users.objects.filter(id=payload['user_id']).first() <-- a Result of a Query Set !

        user = Users.objects.filter(id=payload['user_id']).first()

        if user is None:
            raise exceptions.AuthenticationFailed('user not found')

        print('LOG: JWTAuthentication: End')
        return (user, None)
