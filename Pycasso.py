from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
from Pycasso.Enumerations.Job_Type import Job_Type as JobType
from Pycasso.Enumerations.Job_Status import Job_Status as JobStatus
from Pycasso.Core.Job_Repository import *
from Pycasso.Core.User_Repository import *
from Pycasso.Core.Neural_Transfer import Neural_Transfer as NT
import datetime
from PIL import Image
from io import BytesIO
import base64
import os

app = Flask(__name__)
api = Api(app)

#Static definitions
API_VERSIONS = {
    '0.0.4': '0.0.4'
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
        return API_VERSIONS['0.0.4']


class User(Resource):
    #returns a list of users
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
        user_repo = User_Repository(Users_Repo_Path)
        args = request.get_json(force=True)
        #variable initialization
        First = args['First']
        Last = args['Last']
        Email = args['Email']
        Password = args['Password']
        user = user_repo.create_user({'first': First, 'last': Last, 'email': Email, 'password': Password})
        return user, 200
    #deletes a user in pycasso
    def delete(self):
        parser = reqparse.RequestParser()
        args = parser.parse_args()
        parser.add_argument('id', type=str)
        user_id = args['id']
        user_repo = User_Repository(Users_Repo_Path)
        user_repo.delete(user_id)
        return 'User Deleted', 200

#Jobs are requests to initiate training a model or processing a pycasso job
class Job(Resource):
    #returns a job status. -1 for job_id is ALL
    def get(self):
        #get args
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str)
        args = parser.parse_args()
        job_id = args['id']
        #now return job status query
        job_repo = Job_Repository(Repo_Path)
        if job_id != '-1':
            status = job_repo.get_status(job_id)
            return status, 200
        else:
            statuses = job_repo.get_all_statuses()
            statuses_summary = [{'name': x['name'], 'id': x['id'], 'create_date': x['create_date'], 'status': x['status'], 'end_date': x.get('end_date', '')} for x in statuses]
            return statuses_summary, 200

    #Starts a job on Pycasso
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
        #job execution
        if Converted_Type == JobType.Neural_Transfer:
            #Source Image is the Content Image, and Target_Image is the style image
            Job_Data = [Source_Image, Target_Image]
            job_out = job_repo.queue_job({'name': 'Neural_Transfer', 'create_date': Job_Start, 'data': Job_Data})
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


if __name__ == '__main__':
    app.run(debug=True)