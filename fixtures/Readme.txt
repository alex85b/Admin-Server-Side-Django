The fixtures folder and it's json files will be used to preload data into 3 tables,
those 3 tables that Django created for the Users, Permissions and Roles models (after i requested 'makemigrations' and 'migrate' ofc),
I could write an sql query that would have the exact same function, or
I could use Django's pre-made admin section, to create said data.
But i won't, i will use json files instead,
This is because i love the idea of having a ready file that i could look on in a few month from now.

1:
docker-compose exec admin_api sh

2:
python manage.py loaddata fixtures/permissions.json

3:
python manage.py loaddata fixtures/roles.json

4:
python manage.py loaddata fixtures/users.json

^ password = password.


those 3 files, should cover my modest needs in this project.