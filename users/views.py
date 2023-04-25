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

# Views on this .py will enables endpoint users to:
# Register new user into the DB.
# Login a user and jet a JWT cookie.
# Display all known users.
# logout a user: endpoint user looses the JWT cookie.
# Display all existing permissions.
# display all existing roles.
# display specific role.
# create specific role.
# update specific role.
# delete specific role.


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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)

        return Response({
            'data': serializer.data
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
    permission_classes = [IsAuthenticated]

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

class UserGenericAPIView(
        GenericAPIView,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):

    # setup:
    authentication_classes = [JWTAuthentication]  # <-- is user authenticated.
    permission_classes = [IsAuthenticated]  # <-- does user have permissions.
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

        # from the 'ListModelMixin'
        # return a list using the whole queryset.
        # return Response({
        #     'data': self.list(request).data
        # })
        return self.list(request)

    def post(self, request):
        return Response({
            # from the 'CreateModelMixin'
            # return a result after creating a new entry into the queryset.
            'data': self.create(request).data
        })

    def put(self, request, pk=None):
        # from the 'UpdateModelMixin'
        # return a result after updating a specific pk in the queryset.
        return Response({
            'data': self.update(request, pk).data
        })

    def delete(self, request, pk=None):
        # from the 'DestroyModelMixin'
        # delete a specific pk in the queryset.
        self.destroy(request, pk).data
        return Response(status=status.HTTP_204_NO_CONTENT)
