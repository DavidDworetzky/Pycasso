import unittest
import sys
sys.path.append("..")
sys.path.append("..\..")
from Pycasso.Core.Password_Manager import Password_Manager as PM
from Pycasso.Core.Process_Queue import Process_Job as Process_Job
from Pycasso.Core.Process_Queue import Process_Queue as Process_Queue
import uuid
import time
import random

#Fixtures
TEST_PASSWORD = "Password!"
def get_password_manager():
    manager = PM(salt = "salt")
    return manager

#Constants
Num_Processes = 4

#Test Password Manager
class TestPasswordManager(unittest.TestCase):

    def test_crypt(self):
        manager = get_password_manager()
        hash = manager.sha512_hash(TEST_PASSWORD)
        #trivial assert
        self.assertTrue(hash != "")

    def test_verifyhash(self):
        #hash password and then verify hash works
        manager = get_password_manager()
        hash = manager.sha512_hash(TEST_PASSWORD)
        #trivial assert
        self.assertTrue(hash != "")
        #assert hash verification
        self.assertTrue(manager.sha512_verify(TEST_PASSWORD, hash))

    def test_failhash(self):
        #hash password and then verify hash fails with different password
        manager = get_password_manager()
        hash = manager.sha512_hash(TEST_PASSWORD)
        #trivial assert
        self.assertTrue(hash != "")
        #assert hash failure
        self.assertFalse(manager.sha512_verify("Another Password", hash))

def simple_method():
    return True

def complex_method():
    #simulating a random execution time of 1 to 5 seconds
    time.sleep(random.randint(1, 5))
    return True

def simple_notify(process):
    print(process)
    return True

class TestMultiProcessing(unittest.TestCase):

    def test_queue_single_job(self):
        print('Executing test queue single job')
        id = uuid.uuid4()
        id_str = str(id)
        simple_job = Process_Job(id, simple_method, simple_notify)
        #now create process queue and verify the only job complete
        process_queue = Process_Queue()
        process_queue.Enqueue(simple_job)
        process_queue.Start_Processes()
        #sleep and then assert completed
        time.sleep(1)
        self.assertTrue(simple_job.completed)
    def test_queue_jobs_simple(self):
        print('Executing test queue jobs simple')
        id = uuid.uuid4()
        id_str = str(id)
        id2 = uuid.uuid4()
        id_str_2 = str(id2)
        simple_job = Process_Job(id, simple_method, simple_notify)
        simple_job_2 = Process_Job(id2, simple_method, simple_notify)
        #now create process queue and verify jobs complete
        process_queue = Process_Queue()
        process_queue.Enqueue(simple_job)
        process_queue.Enqueue(simple_job_2)
        #start process queue
        process_queue.Start_Processes()
        #sleep and then assert completed
        time.sleep(1)
        self.assertTrue(simple_job.completed)
        self.assertTrue(simple_job_2.completed)

    def test_queue_jobs_staggered(self):
        print('Executing test queue jobs staggered')
        id = uuid.uuid4()
        id_str = str(id)
        id2 = uuid.uuid4()
        id_str_2 = str(id2)
        complex_job = Process_Job(id, complex_method, simple_notify)
        complex_job_2 = Process_Job(id2, complex_method, simple_notify)
        #now create process queue and verify jobs complete
        process_queue = Process_Queue()
        process_queue.Enqueue(complex_job)
        process_queue.Start_Processes()
        time.sleep(2)
        process_queue.Enqueue(complex_job_2)
        #sleep and then assert completed
        time.sleep(5)
        self.assertTrue(complex_job.completed)
        self.assertTrue(complex_job_2.completed)

    def test_queue_jobs_concurrent(self):
        print('Executing test queue jobs concurrent')
        id = uuid.uuid4()
        id_str = str(id)
        id2 = uuid.uuid4()
        id_str_2 = str(id2)
        complex_job = Process_Job(id, complex_method, simple_notify)
        complex_job_2 = Process_Job(id2, complex_method, simple_notify)
        #now create process queue and verify jobs complete
        process_queue = Process_Queue()
        process_queue.Enqueue(complex_job)
        process_queue.Enqueue(complex_job_2)
        process_queue.Start_Processes()
        #sleep and then assert completed
        time.sleep(5)
        self.assertTrue(complex_job.completed)
        self.assertTrue(complex_job_2.completed)
    



    

if __name__ == '__main__':
    unittest.main()
        