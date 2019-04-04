from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
from Pycasso.Enumerations.Job_Type import Job_Type as JobType
from Pycasso.Enumerations.Job_Status import Job_Status as JobStatus
from Pycasso.Enumerations.User_Type import User_Type as UserType
from Pycasso.Core.Job_Repository import *
from Pycasso.Core.User_Repository import *
from Pycasso.Core.Neural_Transfer import Neural_Transfer as NT
from Pycasso.Core.Password_Manager import Password_Manager as PM
import datetime
from PIL import Image
from io import BytesIO
import base64
import os
#JWT manager imports
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

app = Flask(__name__)
api = Api(app)
#secret initialization for JWT
app.config['JWT_SECRET_KEY'] = 'my-jwt-secret'
jwt = JWTManager(app)
PASSWORD_SALT = "salt"
#end secret initialization for JWT

#Static definitions
API_VERSIONS = {
    '0.0.5': '0.0.5'
}
#get current directory for relative paths
wd = os.getcwd()

def Process_Json_Arg(string):
    #Removes leading b on string
    return string[1:]
#converts a PIL image to base 64
def Convert_Output_To_Base64(image_output):
    buffered = BytesIO()
    image_output.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str

Repo_Path = os.path.join(wd, 'jobs.json')
Users_Repo_Path = os.path.join(wd, 'users.json')
#api versions
class Version(Resource):
    def get(self):
        return API_VERSIONS['0.0.5']

class User(Resource):
    #returns a list of users
    @jwt_required
    def get(self):
        user_repo = User_Repository(Users_Repo_Path)
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str)
        args = parser.parse_args()
        user_id = args['id']
        if user_id != '-1':
            user = user_repo.get_user(user_id)
            return user, 200
        else:
            users = user_repo.get_all_users()
            return users, 200

    #creates a new user in pycasso
    def post(self):
        user_repo = User_Repository(Users_Repo_Path, password_salt = PASSWORD_SALT)
        #assign user type as admin if this is the first user of the 
        is_admin = user_repo.get_count_all_users() == 0
        print(is_admin)
        user_type = UserType.Admin if is_admin else UserType.User
        print(user_type)
        args = request.get_json(force=True)
        #variable initialization
        First = args['First']
        Last = args['Last']
        Email = args['Email']
        Password = args['Password']
        Name = args['Name']
        user = user_repo.create_user({'first': First, 'last': Last, 'name' : Name, 'email': Email, 'password': Password, 'type' : user_type})
        return user, 200
    #deletes a user in pycasso
    @jwt_required
    def delete(self):
        parser = reqparse.RequestParser()
        args = parser.parse_args()
        parser.add_argument('id', type=str)
        user_id = args['id']
        user_repo = User_Repository(Users_Repo_Path)
        user_repo.delete(user_id)
        return 'User Deleted', 200
class UserLogin(Resource):
    def post(self):
        #get user repo
        user_repo = User_Repository(Users_Repo_Path)
        password_manager = PM(salt = PASSWORD_SALT)
        args = request.get_json(force=True)
        Name = args['Name']
        Password = args['Password']
        #parse args
        # login sample:
        # {Name : Name, Password: Password}
        #get first matching user
        user = user_repo.get_user_from_name(Name)
        #verify hash
        hash_verified = password_manager.sha512_verify(Password, user['password'])
        if hash_verified:
            access_token = create_access_token(identity = Name)
            return {"access_token" : access_token, "message": "success"}, 200
        else:
            return {"access_token" : "", "message": "login failure"}, 200

#Jobs are requests to initiate training a model or processing a pycasso job
class Job(Resource):
    #returns a job status. -1 for job_id is ALL
    @jwt_required
    def get(self):
        #get args
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str)
        args = parser.parse_args()
        job_id = args['id']
        #now return job status query
        job_repo = Job_Repository(Repo_Path)

        #now get our jwt_identity for verifying access
        current_user = get_jwt_identity()
        user_repo = User_Repository(Users_Repo_Path)
        user = user_repo.get_user_from_name(current_user)
        #user id
        user_id = user['id']
        if job_id != '-1':
            status = job_repo.get_status(job_id)
            #if status matches, return status, otherwise, return 404
            if status['user_id'] == user_id: 
                return status, 200
            else:
                return 'job not found', 404
        else:
            statuses = job_repo.get_all_statuses()
            #filter statuses based off of user_id
            statuses_filtered = list(filter(lambda x: x['user_id'] == user_id, statuses))
            statuses_summary = [{'name': x['name'], 'id': x['id'], 'create_date': x['create_date'], 'status': x['status'], 'end_date': x.get('end_date', '')} for x in statuses_filtered]
            return statuses_summary, 200

    #Starts a job on Pycasso
    @jwt_required
    def post(self):
        job_repo = Job_Repository(Repo_Path)
        args = request.get_json(force=True)
        # job definition sample:
        # {Type : Job_Type, Source_Image: Base64Image, Target_Image : Base64Image, ImCrop : CropSize}

        #variable initialization
        Converted_Type = JobType(args['Job_Type'])
        Job_Start = datetime.datetime.now()
        Crop_Size = args['ImCrop']
        Source_Image = Process_Json_Arg(args['Source_Image'])
        Target_Image = Process_Json_Arg(args['Target_Image'])
        #now get our jwt_identity for recording jobs
        current_user = get_jwt_identity()
        user_repo = User_Repository(Users_Repo_Path)
        user = user_repo.get_user_from_name(current_user)
        #job execution
        if Converted_Type == JobType.Neural_Transfer:
            #Source Image is the Content Image, and Target_Image is the style image
            Job_Data = [Source_Image, Target_Image]
            job_out = job_repo.queue_job({'name': 'Neural_Transfer', 'create_date': Job_Start, 'data': Job_Data, 'user_id' : user['id']})
            Neural_Transfer = NT(Crop_Size, Source_Image, Target_Image)
            #run a 600 step transfer to begin
            output = Neural_Transfer.run_transfer(600)
            job_repo.complete_job(job_out['id'])
            output_str = Convert_Output_To_Base64(output)
            decoded = output_str.decode('utf-8')
            return decoded, 200
        elif Converted_Type == JobType.GAN:
            return 'GAN Not Supported Yet', 400
        else:
            return 'Type Not Supported Yet', 400

    #Terminates a job on Pycasso
    @jwt_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str)
        args = parser.parse_args()
        job_id = args['id']
        #invoke terminate on the job repository
        job_repo = Job_Repository(Repo_Path)
        job_repo.terminate_job(job_id)
        return 'Job Terminated', 200
##
## Actually setup the Api resource routing here
##
api.add_resource(Version, '/version')
api.add_resource(Job, '/job')
api.add_resource(User, '/user')
api.add_resource(UserLogin, '/login')


if __name__ == '__main__':
    app.run(debug=True)