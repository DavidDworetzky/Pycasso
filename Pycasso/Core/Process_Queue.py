import multiprocessing as mp

class Process_Queue:
    def __init__(self, Queue, Func, Num_Process = 4):
        self.process = Num_Process
        self.f = Func
        self.Queue = mp.Queue()
        #load our queue with jobs
        for item in Queue:
            self.Queue.put(item)
        self.Processes = []
        #create initial processes

    def Enqueue(self, queue_item):
        self.Queue.put(queue_item)

    def Dequeue(self, queue):
        return self.Queue.get()

    def Start_Processes(self):
        return

    def Stop_Processes(self):
        return
    

    