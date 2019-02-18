from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)

API_VERSIONS = {
    '0.0.1': '0.0.1'
}
parser = reqparse.RequestParser()
parser.add_argument('task')

#api versions
class Version(Resource):
    def get(self):
        return API_VERSIONS['0.0.1']

#Jobs are requests to initiate training a model or processing a pycasso job
class Job(Resource):
    def get(self, job_id):
        return 'stub'

##
## Actually setup the Api resource routing here
##

api.add_resource(Version, '/version')
api.add_resource(Job, '/job')


if __name__ == '__main__':
    app.run(debug=True)