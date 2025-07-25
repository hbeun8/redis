# Task destructure
@dataclass
class Task:
    task_id: int
    response_queue: Queue
    response: int = 0


# thread doing some work
while True:
    task = self._queue.get()
    if task is not None:
        task.response = task.val + 2
        task.response_queue.put(task)

# Thread sending work
result_queue = Queue()

while True:
    try:
        v =  # ... some value to be processed
        processor.process(Task(v, result_queue))
        result = result_queue.get()
        print(result.response)