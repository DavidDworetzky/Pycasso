import multiprocessing as mp
import time
#Multiprocessing job queue class
class Process_Queue:
    def __init__(self, Num_Process = 4, debug=True, proc_wait_time = 0.1):
        self.Num_Process = Num_Process
        #Current Work Queue
        self.Queue = mp.Queue()
        #Queue of finished work to communicate back to parent proc
        self.Finished_Queue = mp.Queue()
        self.Processes = []
        #locking and synchronization primitives
        self.QueueLock = mp.Lock()
        self.RunningLock = mp.Lock()
        self.ProcessesLock = mp.Lock()
        #Queue is running
        self.Running = False
        self.debug = debug
        self.Process_Wait_Time = proc_wait_time

    #Enqueue a process item... Anything in queue is waiting to be processed
    def Enqueue(self, queue_item):
        if self.debug:
            print('Enqueueing item')
        self.QueueLock.acquire()
        self.Queue.put(queue_item)
        self.QueueLock.release()
    #Dequeue a process item in order to begin job processing
    def Dequeue(self):
        if self.debug:
            print('Dequeueing item')
        self.QueueLock.acquire()
        result = self.Queue.get()
        self.QueueLock.release()
        return result

    def Get_Work_Result(self):
        return self.Finished_Queue.get()

    #Core run processes loop
    def Run_Processes(self):
        if self.debug:
            print('||Running process loop||')
        while self.Running:
            # while we are running: 
            # check for job completion, and remove completed jobs from the list of running processes, and Dequeue processes to run
            for process in self.Processes:
                if not process.process.is_alive():
                    if self.debug:
                        print(f'Marking process as completed for process id: {process.id}')
                    #process has finished, mark as complete, and remove from self.Processes
                    process.completed = True
                    process.notify_complete(process)
                    #add to finished work queue... but only the id and completed status
                    self.Finished_Queue.put({'id': process.id, 'completed': process.completed})
                    #remove
                    self.ProcessesLock.acquire()
                    self.Processes = self.Remove_Process_After_Complete(process)
                    self.ProcessesLock.release()
            # queue up more processes if we are currently under the max count of processes
            if len(self.Processes) < self.Num_Process and not self.Queue.empty():
                process = self.Dequeue()
                if self.debug:
                    print(f'Queue up more processes. Getting process id: {process.id}')
                multi_p = mp.Process(target = process.function)
                process.process = multi_p
                self.Processes.append(process)
                multi_p.start()
            #sleep so that we only execute the run look every 100 milliseconds
            time.sleep(self.Process_Wait_Time)
        #return if running turned off
        return

    #Starts our processing queue
    def Start_Processes(self, separate_process = True):
        if self.debug:
            print('||Starting Processes||')
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
    #Removes a process from the run queue after it is completed
    def Remove_Process_After_Complete(self, to_remove):
        x_id = to_remove.id
        x_list = list([x for x in self.Processes if x.id != x_id])
        return x_list
    def Stop_Processes(self):
        if self.debug:
            print('||Stopping Processes||')
        self.RunningLock.acquire()
        self.Running = False
        self.RunningLock.release()
        for p in self.Processes:
            p.join()
        if self.debug:
            print('||Processes Stopped||')
        return
    
#Process Job DTO for use in a process queue
class Process_Job:
    def __init__(self, id, function, notify_complete, process = None):
        self.id = id
        self.function = function
        self.completed = False
        self.notify_complete = notify_complete
        self.process = process


    