from rest_framework import permissions

# This will enforce permissions for every action!

from .serializers import UserSerializer


class ViewPermissions(permissions.BasePermission):

    # default class.
    def has_permission(self, request, view):
        user_data = UserSerializer(request.user).data

        # Testing.
        # print('@@@ @@@ @@@ @@@ user_data=', user_data)
        # print('### ### ### ### permission_object=', view.permission_object)

        """
        all the available permissions: view_users, edit_users, view_roles, edit_roles, ...
            go look at user_permission table if you are board,
                all those can be found under: user_data['role']['permissions']
        
        1.
        for p in user_data['role']['permissions'] <-- for each role iterate all permissions.
        
        2.
        'view_' + view.permission_object <-- some object that this function gets, lets assume 'users' for example,
            and we concatenate the view_,
                so the result should be something like: view_users,
                    notice that this is a possible permission that actually exist in the user_permission table!
        
        3.
        p['name'] == 'view_' + view.permission_object <-- check if in p from 1. there is a 'name'
            that equals to a 'view_Users' from 2.
                meaning: check if a name of SOME role.permission is view_Users
                    and of so, or if no, remember it into view_access.
        
        the same goes for 'edit_access'.
        """
        view_access = any(
            p['name'] == 'view_' + view.permission_object for p in user_data['role']['permissions'])
        edit_access = any(
            p['name'] == 'edit_' + view.permission_object for p in user_data['role']['permissions'])

        # for GET - a True from editing or viewing, both will work.
        if request.method == 'GET':
            return view_access or edit_access

        # anything that is not GET, only the edit permission is considered.
        return edit_access
