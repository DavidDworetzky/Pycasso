from tinydb import TinyDB, Query
from Pycasso.Enumerations.Job_Status import Job_Status as JobStatus
import uuid

#using tinydb for pycasso v.0.0.1
def terminate_job_tinydb(job_id):
    def transform(doc):
        new_doc = doc
        new_doc.status = JobStatus.Terminated
        return transform
def complete_job_tinydb(job_id):
    def transform(doc):
        new_doc = doc
        new_doc.status = JobStatus.Completed
        return transform

class Job_Repository:
    def __init__(self, file_path):
        self.file_path = file_path
        self.db = TinyDB(self.file_path)

    #takes a job request object and inserts it into our database
    def queue_job(self, job):
        job_id = uuid.uuid4()
        job = {'name' : job.name, 'id': job_id, 'create_date': job.create_date, 'status': JobStatus.Queued, 'data': job.data}
        self.db.insert(job)
        return job
    def terminate_job(self, job_id):
        Job = Query()
        self.db.Update(terminate_job_tinydb(job_id), Job.id == job_id)
        return True
    def complete_job(self, job_id):
        Job = Query()
        self.db.Update(complete_job_tinydb(job_id), Job.id == job_id)
    def get_status(self, job_id):
        Job = Query()
        #query tinyDB for a job matching job_id
        result = self.db.Search(Job.id == job_id)
        return result
