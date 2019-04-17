import multiprocessing as mp

class Process_Queue:
    def __init__(self, Queue, Num_Process = 4):
        self.Num_Process = Num_Process
        self.Queue = mp.Queue()
        self.Processes = []
        #locking and synchronization primitives
        self.QueueLock = mp.Lock()
        self.RunningLock = mp.Lock()
        #Queue is running
        self.Running = False


    #Enqueue a process item... Anything in queue is waiting to be processed
    def Enqueue(self, queue_item):
        self.QueueLock.acquire()
        self.Queue.put(queue_item)
        self.QueueLock.release()
    #Dequeue a process item in order to begin job processing
    def Dequeue(self, queue):
        self.QueueLock.acquire()
        result = self.Queue.get()
        self.Processes.append(result)
        self.QueueLock.release()
        return result

    def Start_Processes(self, override_function = None):
        self.RunningLock.acquire()
        self.Running = True
        self.RunningLock.release()
        while self.Running:
            # while we are running: 
            # check for job completion, and remove completed jobs from the list of running processes, and Dequeue processes to run
            for i in range(1, self.Num_Process):
                function = override_function if override_function is not None else self.function
                p = mp.Process(target = function)
                self.Processes.append(p)
                p.start()
            return

    def Stop_Processes(self):
        self.RunningLock.acquire()
        self.Running = False
        self.RunningLock.release()
        for p in self.Processes:
            p.join()
        return
    
class Process_Job:
    def __init__(self, id, function):
        self.id = id
        self.function = function

    