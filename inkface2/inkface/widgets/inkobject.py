

class InkObject:
    '''
    This is the base class of Inkface widgets.

    It defines and implements the signal interface for the widgets. \
    '''
    def __init__(self):
        self.event_map = {}

    def connect(self, signal_str, callback):
        '''
        Connect a signal handler to this widget.

        :param signal_str: Name of the signal to register the handler for
        :param callback: A callback handler to be called when this signal is \
        emitted
        '''
        if not self.event_map.has_key(signal_str):
            self.event_map[signal_str] = []

        self.event_map[signal_str].append(callback)

    def disconnect(self, signal_str, callback):
        '''
        Disconnect a signal handler from this widget.

        :param signal_str: Name of the signal for which this callback handler \
        was registered.
        :param callback: The callback handler which was originally connected \
        to handle this signal.
        '''
        if not self.event_map.has_key(signal_str) or \
            self.event_map[signal_str] is None:
            return
        self.event_map[signal_str].remove(callback)

    def emit(self, signal_str, *args):
        '''
        Emit the signal.

        :param signal_str: Name of the signal to emit.
        :param *args: Any number of additional parameters to be passed to the \
        callback handler. The widget subclass should document the signature \
        of the callback handler and should pass these extra args \
        accordingly
        '''
        if not self.event_map.has_key(signal_str) or \
            self.event_map[signal_str] is None:
            return

        for handler in self.event_map[signal_str]:
            handler(*args)


