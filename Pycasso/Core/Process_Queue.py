import multiprocessing as mp

class Process_Queue:
    def __init__(self, Num_Process = 4):
        self.Num_Process = Num_Process
        self.Queue = mp.Queue()
        self.Processes = []
        #locking and synchronization primitives
        self.QueueLock = mp.Lock()
        self.RunningLock = mp.Lock()
        self.ProcessesLock = mp.Lock()
        #Queue is running
        self.Running = False

    #Enqueue a process item... Anything in queue is waiting to be processed
    def Enqueue(self, queue_item):
        self.QueueLock.acquire()
        self.Queue.put(queue_item)
        self.QueueLock.release()
    #Dequeue a process item in order to begin job processing
    def Dequeue(self):
        self.QueueLock.acquire()
        result = self.Queue.get()
        self.QueueLock.release()
        return result

    #Core run processes loop
    def Run_Processes(self):
        while self.Running:
            # while we are running: 
            # check for job completion, and remove completed jobs from the list of running processes, and Dequeue processes to run
            for process in self.Processes:
                if not process.process.is_alive():
                    #process has finished, mark as complete, and remove from self.Processes
                    process.completed = True
                    process.notify_complete(process)
                    #remove
                    self.ProcessesLock.acquire()
                    self.Processes = self.Remove_Process_After_Complete(process)
                    self.ProcessesLock.release()
            # queue up more processes if we are currently under the max count of processes
            while len(self.Processes) < self.Num_Process:
                process = self.Dequeue()
                multi_p = mp.Process(target = process.function)
                process.process = multi_p
                self.Processes.append(process)
                multi_p.start()
        #return if running turned off
        return


    def Start_Processes(self, separate_process = True):
        self.RunningLock.acquire()
        self.Running = True
        self.RunningLock.release()
        if separate_process:
            run_proc = mp.Process(target = self.Run_Processes)
            run_proc.start()
            return run_proc
        else:
            self.Run_Processes()
        return
        
    def Remove_Process_After_Complete(self, to_remove):
        x_id = to_remove.id
        x_list = list([x for x in self.Processes if x.id != x_id])
        return x_list
    def Stop_Processes(self):
        self.RunningLock.acquire()
        self.Running = False
        self.RunningLock.release()
        for p in self.Processes:
            p.join()
        return
    
#Process Job DTO for use in a process queue
class Process_Job:
    def __init__(self, id, function, notify_complete, process = None):
        self.id = id
        self.function = function
        self.completed = False
        self.notify_complete = notify_complete
        self.process = process

    