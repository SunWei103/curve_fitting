import queue as Queue

callback_queue = Queue.Queue()


def from_dummy_thread(func_to_call_from_main_thread):
    callback_queue.put(func_to_call_from_main_thread)


def from_main_thread_blocking():
    callback = callback_queue.get()  # blocks until an item is available
    callback()


def from_main_thread_nonblocking():
    while True:
        try:
            callback = callback_queue.get(False)  # doesn't block
        except Queue.Empty:  # raised when queue is empty
            break
        callback()


def dummy_run(func, args):
    from_dummy_thread(lambda: func(args))
