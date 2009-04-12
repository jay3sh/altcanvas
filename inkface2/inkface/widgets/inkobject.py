

class InkObject:
    def __init__(self):
        self.event_map = {}

    def connect(self, event_str, callback):
        if not self.event_map.has_key(event_str):
            self.event_map[event_str] = []

        self.event_map[event_str].append(callback)

    def disconnect(self, event_str, callback):
        if not self.event_map.has_key(event_str) or \
            self.event_map[event_str] is None:
            return
        self.event_map[event_str].remove(callback)

    def emit(self, event_str, *args):
        if not self.event_map.has_key(event_str) or \
            self.event_map[event_str] is None:
            return

        for handler in self.event_map[event_str]:
            handler(*args)


