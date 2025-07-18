from collections import defaultdict
import abc


class Handler(abc.ABC):
    def __init__(self, event=None):
        self.event = event

    def __eq__(self, other):
        if not isinstance(other, Handler):
            return NotImplemented
        return self.event == other.event

    @abc.abstractmethod
    def __call__(self):
        pass


class _Event:
    """
    A simple event management system that allows registering, removing, and triggering
    named events with associated functions and arguments.
    
    This class implements an observer pattern where functions can be registered to
    specific event names and then triggered when that event is fired.
    """

    def __init__(self):
        """
        Initialize a new Event instance with an empty event registry.
        """
        self.events = defaultdict(list)

    def add_event(self, name, handler, one_time=False):
        """
        Register a function to be called when an event with the given name is triggered.
        
        Args:
            :param handler: The functor to call when the event is triggered
            :param name: the name of the event to register for
            :param one_time: If true, the handler will be removed after being called

        """
        self.events[name].append((handler, one_time))

    def remove_event(self, name, handler):
        """
        Remove a previously registered function from an event.
        
        Args:
            :param name: The name of the event to remove from
            :param handler: The functor to remove

        Note:
            Both the function and its arguments must match exactly what was registered.
        """
        if name not in self.events:
            print(f"Event '{name}' does not exist.")
            return

        handlers_to_keep = []
        found_handler = False
        for existing_handler_func, existing_one_time_flag in self.events[name]:
            if existing_handler_func is handler:  # Use 'is' to compare by object identity
                found_handler = True
                # Don't add this handler to handlers_to_keep, effectively removing it
            else:
                handlers_to_keep.append((existing_handler_func, existing_one_time_flag))

        if found_handler:
            self.events[name] = handlers_to_keep
            if not self.events[name]:  # Clean up if the list becomes empty
                del self.events[name]
        else:
            print(f"Handler function not found in event '{name}'.")


    def trigger_event(self, name, *args, **kwargs):
        """
        Trigger all functions registered to an event with the given name.

        This calls each registered function with its stored arguments.

        Args:
            name (str): The name of the event to trigger
            *args: The arguments to pass to each registered function
        """

        if name in self.events:
            handlers_to_remove = []
            out = None
            for index, (funct, one_time) in enumerate(self.events[name]):
                out = [funct(*args, **kwargs)]
                if one_time:
                    handlers_to_remove.append(index)

            for index in sorted(handlers_to_remove, reverse=True):
                self.events[name].pop(index)

                # Clean up empty event lists
            if not self.events[name]:
                del self.events[name]

            return out
        else:
            raise ValueError("attempt to trigger a non-existent event")


Events = _Event()
