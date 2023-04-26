from rest_framework import mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import exceptions, viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView

from .models import Users, Permission, Role
from .serializers import UserSerializer, PermissionSerializer, RoleSerializer
from .authentication import JWTAuthentication, generate_access_token
from admin.pagination import CustomPagination
from .permissions import ViewPermissions

# Views on this .py will enables endpoint users to:
# Register new user into the DB.
# Login a user and jet a JWT cookie.
# Display all known users.
# Display specific user.
# Update specific user.
# Delete specific user.
# Logout a user: endpoint user looses the JWT cookie.
# Display all existing permissions.
# Display all existing roles.
# Display specific role.
# Create specific role.
# Update specific role.
# Delete specific role.


############################################################################################
##  Register ###############################################################################
############################################################################################


# this method will be dependant upon a serializer
@api_view(['POST'])
def register(request):
    register_this_user = request.data

    if register_this_user['password'] != register_this_user['password_confirm']:
        raise exceptions.APIException('Passwords do not match!')

    # this should be thi middle man between incoming data, and the database.
    serializer = UserSerializer(data=register_this_user)

    # let the serializer object test for errors.
    serializer.is_valid(raise_exception=True)

    # if validation didn't result in error, serializer object will write to database.
    # ONLY NOW serializer.create will be called ! (look at your logs).
    print('LOG: Before serializer.save()')
    serializer.save()
    print('LOG: After serializer.save()')

    # return the user data - as a 'handshake'.
    return Response(serializer.data)


############################################################################################
##  Login ##################################################################################
############################################################################################


@api_view(['POST'])
def login(request):
    incoming_email = request.data.get('email')
    incoming_password = request.data.get('password')

    user = Users.objects.filter(email=incoming_email).first()

    # check if user is known.
    if user is None:
        raise exceptions.AuthenticationFailed('User not found!')

    # check if a known user provided correct password.
    # remember that we hold the hashed version, so we can'r compare directly.
    if not user.check_password(incoming_password):
        raise exceptions.AuthenticationFailed('Incorrect password!')

    # create new access authorization
    token = generate_access_token(user)

    # set new cookie with encrypted access authorization
    # it doesn't work as a single line.
    response = Response()
    response.set_cookie(key='jwt', value=token, httponly=True)
    print(response)

    # add some data for the response, could be a simple 'status': 'success'.
    response.data = {  # type: ignore
        'data': token
    }

    return response


############################################################################################
##  Get Users  #############################################################################
############################################################################################


@api_view(['GET'])
def users(request):
    # many = True, because serializer returns an array, array is "many".
    serializer = UserSerializer(
        Users.objects.all(),
        many=True
    )

    return Response(serializer.data)


############################################################################################
##  check user authentication  #############################################################
############################################################################################


class AuthenticatedUser(APIView):

    # i have to create my own authentication
    # look in: authentication.py
    authentication_classes = [JWTAuthentication]

    # uses existing, pre-made 'service' of the rest_framework
    permission_classes = [IsAuthenticated & ViewPermissions]
    permission_object = 'users'  # <-- route access.

    def get(self, request):
        data = UserSerializer(request.user).data
        data['permissions'] = [p['name'] for p in data['role']['permissions']]

        return Response({
            'data': data
        })


############################################################################################
##  Log Out  ###############################################################################
############################################################################################


@api_view(['POST'])
def logout(_):
    response = Response()
    response.delete_cookie(key='jwt')
    response.data = {
        'data': 'logged out'
    }
    return response


############################################################################################
##  All permissions  #######################################################################
############################################################################################


class PermissionApiView(APIView):

    # i have to create my own authentication
    # look in: authentication.py
    authentication_classes = [JWTAuthentication]

    # uses existing, pre-made 'service' of the rest_framework
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = PermissionSerializer(Permission.objects.all(), many=True)

        return Response({
            'data': serializer.data
        })


############################################################################################
##  Roles  #################################################################################
############################################################################################


class RoleViewSet(viewsets.ViewSet):

    # i have to create my own authentication
    # look in: authentication.py
    authentication_classes = [JWTAuthentication]

    # uses existing, pre-made 'service' of the rest_framework
    permission_classes = [IsAuthenticated & ViewPermissions]
    permission_object = 'roles'  # <-- a permission from users_permissions table

    # get a list of objects
    def list(self, request):
        serializer = RoleSerializer(Role.objects.all(), many=True)
        return Response({
            'data': serializer.data
        })

    # create new record
    def create(self, request):
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    # get single object
    def retrieve(self, request, pk=None):
        role = Role.objects.filter(id=pk).first()
        if role is not None:
            serializer = RoleSerializer(role)
            return Response({
                'data': serializer.data
            })

        raise exceptions.APIException("pk doesn't exists")

    # update record
    def update(self, request, pk=None):
        role = Role.objects.filter(id=pk).first()
        if role is not None:
            serializer = RoleSerializer(instance=role, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                'data': serializer.data
            }, status=status.HTTP_202_ACCEPTED)

        raise exceptions.APIException("pk doesn't exists")

    # delete record
    def destroy(self, request, pk=None):
        role = Role.objects.filter(id=pk).first()
        if role is not None:
            role = Role.objects.get(id=pk)
            role.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise exceptions.APIException("pk doesn't exists")


############################################################################################
##  Users  #################################################################################
############################################################################################

# TODO: The password management here is lazy and illogical, but
# This is what the Udemy instructor implemented.
# change this later!

class UserGenericAPIView(
        GenericAPIView,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):

    # setup:
    authentication_classes = [JWTAuthentication]  # <-- is user authenticated.
    # <-- does user have permissions.
    permission_classes = [IsAuthenticated & ViewPermissions]
    permission_object = 'users'  # <-- a permission from users_permissions table
    pagination_class = CustomPagination

    # link to the DB, map all users to this object.
    # .order_by('id') <-- without order, pagination MAY not work:
    #   https://stackoverflow.com/questions/44033670/python-django-rest-framework-unorderedobjectlistwarning
    queryset = Users.objects.all().order_by('id')
    serializer_class = UserSerializer  # <-- this is used to serialize users.

    def get(self, request, pk=None):
        # if primary key isn't None - get specific user.
        # if primary key is None - get all users.
        if pk:
            # from the 'RetrieveModelMixin'
            # return a narrowed queryset, of a specific pk.
            return Response({
                'data': self.retrieve(request, pk).data
            })

        return self.list(request)

    def post(self, request):

        # Front-end sends: {
        #     "first_name": ?
        #     , "last_name": ?
        #     , "email": ?
        #     , "role_id": ?
        # }

        # I want to add pre-made password and role (not only the id).
        request.data.update({

            # Initial password, i should force users to change it upon login.
            'password': 1234,

            # TODO: rename Users.role to Users.role_id, explanation:
            # there is a Users model with a field poorly named as 'role', also
            # There is a Roles model that consist of {id, name, permissions}.
            # that presents a challenge:
            #   if user passes me a 'role' it seems as if he passes a Role object!
            #   But, i want the user to pass me a role-id, because that is the value i need for Users.role
            #   so i ask frontend to give me role_id then
            #       i do some switcheroo, i add the correct key which is role.
            # this is avoidable - i need to rename Users.role to Users.role_id
            'role': request.data['role_id']
        })

        return Response({
            # from the 'CreateModelMixin'
            # return a result after creating a new entry into the queryset.
            'data': self.create(request).data
        })

    def put(self, request, pk=None):
        # from the 'UpdateModelMixin'
        # return a result after updating a specific pk in the queryset.
        print('UserGenericAPIView --> put --> request = ', request.data)
        if pk:
            request.data.update({
                'password': 1234,
                'role': request.data['role_id']
            })

            return Response({
                'data': self.update(request, pk).data
            })

        raise exceptions.APIException('can not update without pk')

    def delete(self, request, pk=None):
        # from the 'DestroyModelMixin'
        # delete a specific pk in the queryset.
        self.destroy(request, pk).data
        return Response(status=status.HTTP_204_NO_CONTENT)

############################################################################################
##  Profile  ###############################################################################
############################################################################################

# Updates the user that have logged in !
# if 'momo' had logged in ? this will act upon momo and momo alone!

#######################
## Update Info  #######
#######################


class ProfileInfoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated & ViewPermissions]
    permission_object = 'users'  # <-- a permission from users_permissions table

    def put(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


#######################
## Update Password  ###
#######################


class ProfilePasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated & ViewPermissions]
    permission_object = 'users'  # <-- a permission from users_permissions table

    def put(self, request, pk=None):
        user = request.user

        if 'password' not in request.data or 'password_confirm' not in request.data:
            raise exceptions.ValidationError(
                'Password or password_confirm were not provided')

        if request.data['password'] != request.data['password_confirm']:
            raise exceptions.ValidationError('Passwords do not match')

        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
