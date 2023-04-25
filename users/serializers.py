from rest_framework import serializers
from rest_framework import exceptions

from .models import Users, Permission, Role


############################################################################################
##  User Serializer ########################################################################
############################################################################################


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name', 'email', 'password']

        # make that serializers can't return a password!
        extra_kwargs = {
            'password': {'write_only': True}
        }

    # override default creation method.
    # this will be called whenever the outside user, uses the .save() method.
    def create(self, validated_data):
        print('LOG: started UserSerializer::create')
        # remove password from the what we about to send to the Users Data Base.
        Incoming_password = validated_data.pop('password', None)

        # the '**' should create a dictionary out of the validated_data object
        # instance <-- go to self, find the connection to Users, that held inside model
        #   then prepare to save to db the content of validated_data, BUT without the password.
        instance = self.Meta.model(**validated_data)

        if Incoming_password is not None:
            # add the hashed password,
            # it should be hashed because of '.set_password', to the 'save to db' object.
            instance.set_password(Incoming_password)

        # send instance to the data base.
        instance.save()

        # the result of the crete method.
        print('LOG: ended UserSerializer::create')
        return instance

############################################################################################
##  Permission Serializer ##################################################################
############################################################################################


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

############################################################################################
##  Role Serializer ########################################################################
############################################################################################

# This will be used to bring from the DB roles, or send into the DB Roles.
# the difficulty will be that roles has a foreign key: permissions,
#   And this foreign key represent an object that has useful information like 'name' of permission.
# When i bring roles "out" of the DB i want replace foreign keys with the object itself,
#   So i could display to the endpoint user more then 'flat' ids of a permission.
# for that i need to serialize permissions objects - to be able to link to all roles.
# But when i send new Role object into the DB ? i want to send only the foreign key, Because
#   It is unreasonable to ask the user to provide me the actual object.
#   so now i don't want to serialize permission objects! i want to serialize ID's of permissions.
# rest_framework has a solution for this case: https://www.django-rest-framework.org/api-guide/relations/#custom-relational-fields
# .to_representation(self, value) method will be used to provide the "out of the DB" direction.
# .to_internal_value(self, data) method will be used to provide the "into the DB" direction.


# This will provide me with the ability to handle "out" and "in" differently.
class PermissionRelatedField(serializers.StringRelatedField):

    # the "out of the db" direction
    # in the outward scenario i do want to get permission objects for display.
    def to_representation(self, value):
        return PermissionSerializer(value).data

    # the "into the db" direction
    # in the into scenario i get ids and that is exactly what i want to send to the DB.
    # meaning no changes needed.
    def to_internal_value(self, data):
        return data


# now i will use the 'PermissionRelatedField', to
# Hold the related fields (foreign keys / objects) that are needed for serialization.
class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionRelatedField(many=True)

    class Meta:
        model = Role
        fields = '__all__'

    # but now i have wrapped the permissions in the 'PermissionRelatedField' thingy,
    # 'PermissionRelatedField' could be whatever,
    #   That means i have to manually add permissions to the new Instance.
    def create(self, validated_data):

        permissions = validated_data.pop('permissions', None)
        print('LOG: RoleSerializer -> create: permissions before unpacking= ', permissions)
        print('LOG: RoleSerializer -> create: permissions after unpacking= ', *permissions)
        # the '**' should create a dictionary out of the validated_data object
        # instance <-- go to self, find the connection to Users, that held inside model
        #   then prepare to save to db the content of validated_data, but without the 'permissions'
        instance = self.Meta.model(**validated_data)
        instance.save()  # create new entry, right now without permissions.
        try:
            instance.permissions.add(*permissions)
        except:
            instance.delete()
            raise exceptions.APIException('Unacceptable permissions')
        instance.save()  # update the entry - with permissions.
        return instance
