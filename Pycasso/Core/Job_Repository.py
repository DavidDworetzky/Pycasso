from tinydb import TinyDB, Query
import uuid
from tinydb.operations import set
import datetime
from enum import Enum

class JobStatus(Enum):
     Queued = 1
     Running = 2
     Terminated = 3
     Completed = 4
JobStatusMapping = {
    JobStatus.Queued : 1,
    JobStatus.Running : 2,
    JobStatus.Terminated : 3,
    JobStatus.Completed: 4
}

#using tinydb for pycasso v.0.0.1
def terminate_job_tinydb(job_id):
    def transform(doc):
        doc['status'] = JobStatusMapping[JobStatus.Terminated]
        job_end = datetime.datetime.now()
        doc['end_date'] = str(job_end)
        return doc
    return transform
def complete_job_tinydb(job_id):
    def transform(doc):
        doc['status'] = JobStatusMapping[JobStatus.Completed]
        job_end = datetime.datetime.now()
        doc['end_date'] = str(job_end)
        return doc
        
    return transform

class Job_Repository:
    def __init__(self, file_path):
        self.file_path = file_path
        self.db = TinyDB(self.file_path)

    #takes a job request object and inserts it into our database
    def queue_job(self, job):
        job_id = uuid.uuid4()
        job_id_string = str(job_id)
        create_date_string = str(job['create_date'])
        job_status_int = JobStatusMapping[JobStatus.Queued]
        job = {'name' : job['name'], 'id': job_id_string, 'create_date': create_date_string, 'status': job_status_int, 'data': job['data'], 'end_date': ''}
        self.db.insert(job)
        return job
    def terminate_job(self, job_id):
        Job = Query()
        self.db.update(terminate_job_tinydb(job_id), Job.id == job_id)
        return True
    def complete_job(self, job_id):
        Job = Query()
        self.db.update(complete_job_tinydb(job_id), Job.id == job_id)
    def get_status(self, job_id):
        Job = Query()
        #query tinyDB for a job matching job_id
        result = self.db.search(Job.id == job_id)
        return result
    def get_all_statuses(self):
        #query all jobs
        result = self.db.all()
        return result
