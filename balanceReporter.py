import time, threading
from typing import Callable

class BalanceReporter:
    def __init__(self, intervalInSeconds: float, actionFunction: Callable) :
        self.intervalInSeconds = intervalInSeconds
        self.actionFunction = actionFunction
        self.stopEvent = threading.Event()
    
    def __reportBalanceWorkerFunction(self) :
        nextTime = time.time() + self.intervalInSeconds
        while not self.stopEvent.wait(nextTime - time.time()) :
            nextTime += self.intervalInSeconds
            self.actionFunction()
        
    def start(self):
        self.actionFunction()
        thread = threading.Thread(target = self.__reportBalanceWorkerFunction)
        thread.start()

    def cancel(self):
        self.stopEvent.set()