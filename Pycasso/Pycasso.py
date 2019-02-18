from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
#using tinydb for pycasso v.0.0.1
from tinydb import TinyDB, Query
from Pycasso.Enumerations.Job_Type import Job_Type as JobType
from Pycasso.Enumerations.Job_Status import Job_Status as JobStatus
from Pycasso.Core.Job_Repository import Job_Repository
from Pycasso.Core.Neural_Transfer import Neural_Transfer

app = Flask(__name__)
api = Api(app)

#Static definitions
API_VERSIONS = {
    '0.0.1': '0.0.1'
}

Repo_Path = ''

parser = reqparse.RequestParser()
parser.add_argument('task')

#api versions
class Version(Resource):
    def get(self):
        return API_VERSIONS['0.0.1']

#Jobs are requests to initiate training a model or processing a pycasso job
class Job(Resource):
    #returns a job status
    def get(self, job_id):
        job_repo = Job_Repository(Repo_Path)
        status = job_repo.get_status(job_id)
        return status, 200

    #Starts a job on Pycasso
    def post(self):
        job_repo = Job_Repository(Repo_Path)
        args = parser.parse_args()
        # job definition sample:
        # {Type : Job_Type, Source_Image: Base64Image, Target_Image : Base64Image, ImXCrop : XCropSize, ImYCrop: YCropSize}
        Initial_Status = JobStatus.Queued
        Converted_Type = Job_Type(args['Type'])
        Job_Start = datetime.datetime.now()
        if Converted_Type == Job_Type.Neural_Transfer:
            return 'Job Queued', 200
        
        else if Converted_Type == Job_Type.GAN:
            return 'Not Supported Yet', 400

    #Terminates a job on Pycasso
    def delete(self, job_id):
        #invoke terminate on the job repository
        job_repo = Job_Repository(Repo_Path)
        job_repo.terminate_job(job_id)
        return 'Job Terminated', 200
        
##
## Actually setup the Api resource routing here
##

api.add_resource(Version, '/version')
api.add_resource(Job, '/job')


if __name__ == '__main__':
    app.run(debug=True)