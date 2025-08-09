#from multiprocessing import Lock, Process, current_process
import time
#import queue # imported for using queue.Empty exception

class Task():
    def __init__(self, v, response_queue, results_queue):
        self.task_id: int
        self._queue = queue
        self.response_queue = response_queue
        self.result_queue = results_queue
        self.response = ""
        self.val = v

    def put(self):# thread doing some work
        while True:
            task = self._queue.get()
            if task is not None:
                task.response = task.val + 2
                task.response_queue.put(task)

    def get(self):
        while True:
            try:
                v =  # ... some value to be processed
               # p = Process(Task(v, result_queue))
                result = result_queue.get()
                print(result.response)