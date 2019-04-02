from tinydb import TinyDB, Query
import uuid
from tinydb.operations import set
import datetime
from enum import Enum
from Pycasso.Core.Password_Manager import Password_Manager as PM

class User_Repository:
    def __init__(self, file_path, password_salt = ""):
        self.file_path = file_path
        self.db = TinyDB(self.file_path)
        self.password_salt = password_salt
        self.pw_manager = PM(salt = self.password_salt)

    #takes a job request object and inserts it into our database
    def create_user(self, user):
        user_id = uuid.uuid4()
        user_id_string = str(user_id)
        create_date = datetime.datetime.now()
        create_date_string = str(create_date)
        hash = self.pw_manager.sha512_hash(user['password'])
        user = {'first' : user['first'], 'last' : user['last'], 'name' : user['name'], 'id': user_id_string, 'create_date': create_date_string, 'password' : hash}
        self.db.insert(user)
        return user
    def delete_user(self, user_id):
        user = Query()
        self.db.update(delete('email'), user.id == user_id)
        return True
    def update_user_password(self, user_id):
        user = Query()
        self.db.update(set('password'), user.id == user_id)
    def get_user(self, user_id):
        user = Query()
        #query tinyDB for a user matching user_id
        result = self.db.search(user.id == user_id)
        return result
    def get_user_from_name(self, name):
        user = Query()
        #query tinyDB for a user matching user name
        result = self.db.search(user.name == name)
        #return first matching name
        return result[0]
    def get_all_users(self):
        #query all users
        result = self.db.all()
        return result
