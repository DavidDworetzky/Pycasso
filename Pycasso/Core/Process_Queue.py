import multiprocessing as mp

class Process_Queue:
    def __init__(self, Queue, Func, Num_Process = 4):
        self.num_process = Num_Process
        self.function = Func
        self.Queue = mp.Queue()
        #load our queue with jobs
        for item in Queue:
            self.Queue.put(item)
        self.Processes = []
        #locking and synchronization
        self.QueueLock = mp.Lock()

    def Enqueue(self, queue_item):
        self.QueueLock.acquire()
        self.Queue.put(queue_item)
        self.QueueLock.release()

    def Dequeue(self, queue):
        self.QueueLock.acquire()
        result = self.Queue.get()
        self.QueueLock.release()
        return result

    def Start_Processes(self, override_function = None):
        for i in range(1, self.num_process):
            function = override_function if override_function is not None else self.function
            p = mp.Process(target = function)
            self.Processes.append(p)
            p.start()
        return

    def Stop_Processes(self):
        for p in self.Processes:
            p.join()
        return
    
class Process_Job:
    def __init__(self, id, func):
        self.id = id
        self.func = func

    