import time, threading
from typing import Callable

class TaskScheduler:
    def __init__(self, intervalInSeconds: float, actionFunction: Callable) :
        self.intervalInSeconds = intervalInSeconds
        self.actionFunction = actionFunction
        self.stopEvent = threading.Event()
    
    def __workerFunction(self) :
        nextTime = time.time() + self.intervalInSeconds
        while not self.stopEvent.wait(nextTime - time.time()) :
            nextTime += self.intervalInSeconds
            self.actionFunction()
        
    def start(self):
        thread = threading.Thread(target = self.__workerFunction)
        thread.start()

    def cancel(self):
        self.stopEvent.set()