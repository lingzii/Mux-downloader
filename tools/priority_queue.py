
class pqueue:
    def __init__(self) -> None:
        self.queue = list()

    def put(self, obj):
        self.queue.append(obj)
        self.queue.sort(key=lambda l: l[0])

    def get(self):
        obj = self.queue[0]
        self.queue.pop(0)
        return obj

    def empty(self):
        return len(self.queue) == 0
