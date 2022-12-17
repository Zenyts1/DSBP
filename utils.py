import time
import threading


class Events:
    def __init__(self, *args, noerr):
        """
        Initialize the Event class.
        :param *args: Events to add.
        :param noerr: If True, do not raise an error if an event is already set or not set.
        """
        self.funcs = {x: [] for x in args}
        self.lnoerr = None
        self.noerr = noerr or None

    def __call__(self, name, noerr=False):
        """
        Add a function to an event.
        :param name: Name of the event.
        :param noerr: If True, do not raise an error if an event is already set or not set.
        """
        self.lnoerr = noerr
        noerr = (
            self.noerr
            if self.noerr != None
            else (noerr if noerr != None else self.lnoerr)
        )

        def sec(func):
            if name not in self.funcs:
                if noerr:
                    self.append(name)
                else:
                    raise KeyError("{} is not a valid event".format(name))
            self.funcs[name].append(func)
            return func

        return sec

    def append(self, name, noerr=False):
        """
        Append a function to the event list.
        :param name: Name of the event.
        :param noerr: If True, do not raise an error if an event is already set or not set.
        """
        self.lnoerr = noerr
        noerr = (
            self.noerr
            if self.noerr != None
            else (noerr if noerr != None else self.lnoerr)
        )
        if name not in self.funcs:
            self.funcs[name] = []
        elif not noerr:
            raise Exception("Event name already exists")

    def trigger(self, names, *args, **kwargs):
        """
        Trigger the event(s).
        :param names: Names of the event(s).
        :param *args: Arguments to pass to the functions.
        :param **kwargs: Keyword arguments to pass to the functions.
        """
        noerr = (
            self.noerr
            if self.noerr != None
            else (self.lnoerr if self.lnoerr != None else False)
        )
        if type(names) == str:
            names = [names]
        for name in names:
            if not name in self.funcs.keys():
                if noerr:
                    self.append(name)
                else:
                    raise KeyError("{} is not a valid event".format(name))
            for func in self.funcs[name]:
                threading.Thread(target=func, args=args, kwargs=kwargs).start()


def setInterval(callback, interval, *args, **kwargs):
    class temp:
        def __init__(self):
            self.run = False

    """
    This function is used to set an interval for a callback function.
    :param interval: The interval in seconds.
    :param callback: The callback function.
    :param args: The arguments for the callback function.
    :param kwargs: The keyword arguments for the callback function.
    """
    r = temp()

    def _callback(*args, **kwargs):
        r.run = True
        while r.run:
            callback(*args, **kwargs)
            time.sleep(interval)

    if interval < 0:
        raise ValueError("Interval must be greater than 0.")

    thread = threading.Thread(target=_callback, args=args, kwargs=kwargs)
    thread.start()
    return r


def rotate(text):
    text += "   "
    while True:
        for n in range(len(text)):
            yield text[n:] + text[:n]
