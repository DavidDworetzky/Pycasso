from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
from Pycasso.Enumerations.Job_Type import Job_Type as JobType
from Pycasso.Enumerations.Job_Status import Job_Status as JobStatus
from Pycasso.Core.Job_Repository import *
from Pycasso.Core.Neural_Transfer import Neural_Transfer as NT
import datetime

app = Flask(__name__)
api = Api(app)

#Static definitions
API_VERSIONS = {
    '0.0.1': '0.0.1'
}
def Process_Json_Arg(string):
    #Removes leading b on string
    return string[1:]


Repo_Path = 'jobs.json'
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
        args = request.get_json(force=True)
        # job definition sample:
        # {Type : Job_Type, Source_Image: Base64Image, Target_Image : Base64Image, ImCrop : CropSize}

        #variable initialization
        Converted_Type = JobType(args['Job_Type'])
        Job_Start = datetime.datetime.now()
        Crop_Size = args['ImCrop']
        Source_Image = Process_Json_Arg(args['Source_Image'])
        Target_Image = Process_Json_Arg(args['Target_Image'])
        print(Source_Image)
        #job execution
        if Converted_Type == JobType.Neural_Transfer:
            #Source Image is the Content Image, and Target_Image is the style image
            Job_Data = [Source_Image, Target_Image]
            job_out = job_repo.queue_job({'name': 'Neural_Transfer', 'create_date': Job_Start, 'data': Job_Data})
            Neural_Transfer = NT(Crop_Size, Source_Image, Target_Image)
            #run a 600 step transfer to begin
            output = Neural_Transfer.run_transfer(600)
            job_repo.complete_job(job_out['id'])
            return output, 200
        elif Converted_Type == JobType.GAN:
            return 'GAN Not Supported Yet', 400

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