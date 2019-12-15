import multiprocessing


class Consumer(multiprocessing.Process):

    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                self.task_queue.task_done()
                break
            answer = next_task()
            self.task_queue.task_done()
            self.result_queue.put(answer)
        return


class Task(object):
    def __init__(self, func, args):
        self.func = func
        self.args = args

    def __call__(self):
        return self.func(*self.args)

    def __str__(self):
        return "Calling {} with {}".format(self.func, self.args)


def map_parallel(func, args_list: list, count: int = None):
    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()

    if count is None:
        num_consumers = multiprocessing.cpu_count() * 2
    else:
        num_consumers = count
    consumers = [Consumer(tasks, results) for i in range(num_consumers)]
    for w in consumers:
        w.start()
    num_jobs = len(args_list)
    for args in args_list:
        tasks.put(Task(func, args))
    for i in range(num_consumers):
        tasks.put(None)
    tasks.join()

    all_results = []
    while num_jobs:
        all_results.extend(results.get())
        num_jobs -= 1
    return all_results
