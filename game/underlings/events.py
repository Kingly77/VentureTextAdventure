from collections import defaultdict
import abc
import logging


# Custom exception classes for better error handling
class EventError(Exception):
    """Base exception for event system errors."""

    pass


class EventNotFoundError(EventError):
    """Raised when trying to access a non-existent event."""

    pass


class HandlerNotFoundError(EventError):
    """Raised when trying to remove a non-existent handler."""

    pass


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


class EventHandler(Handler):
    """Enhanced handler with priority and metadata support."""

    def __init__(self, func, priority=0, description="", one_time=False):
        super().__init__()
        self.func = func
        self.priority = priority
        self.description = description
        self.one_time = one_time

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


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

        Raises:
            EventNotFoundError: If the event doesn't exist
            HandlerNotFoundError: If the handler is not found in the event
        """
        if name not in self.events:
            raise EventNotFoundError(f"Event '{name}' does not exist.")

        handlers_to_keep = []
        found_handler = False
        for existing_handler_func, existing_one_time_flag in self.events[name]:
            if (
                existing_handler_func is handler
            ):  # Use 'is' to compare by object identity
                found_handler = True
                # Don't add this handler to handlers_to_keep, effectively removing it
            else:
                handlers_to_keep.append((existing_handler_func, existing_one_time_flag))

        if found_handler:
            self.events[name] = handlers_to_keep
            if not self.events[name]:  # Clean up if the list becomes empty
                del self.events[name]
            logging.debug(f"Removed handler from event '{name}'")
        else:
            raise HandlerNotFoundError(f"Handler function not found in event '{name}'.")

    def trigger_event(self, name, *args, **kwargs):
        """
        Trigger all functions registered to an event with the given name.

        This calls each registered function with its stored arguments.

        Args:
            name (str): The name of the event to trigger
            *args: The arguments to pass to each registered function
            **kwargs: The keyword arguments to pass to each registered function

        Returns:
            list: A list of results from all handlers, or None if no results

        Raises:
            EventNotFoundError: If the event doesn't exist
        """
        if name in self.events:
            results = []
            handlers_to_remove = []

            for index, (handler, one_time) in enumerate(self.events[name]):
                try:
                    result = handler(*args, **kwargs)
                    if result is not None:
                        results.append(result)
                    if one_time:
                        handlers_to_remove.append(index)
                except Exception as e:
                    # Log error but continue with other handlers
                    logging.error(f"Error in event handler for '{name}': {e}")

            # Remove one-time handlers
            for index in sorted(handlers_to_remove, reverse=True):
                self.events[name].pop(index)

            # Clean up empty event lists
            if not self.events[name]:
                del self.events[name]

            logging.debug(f"Triggered event '{name}' with {len(results)} results")
            return results if results else None
        else:
            logging.debug(f"try_trigger: Event '{name}' not found; skipping.")
            return None

    def list_events(self):
        """Return a dictionary of all registered events and their handler counts."""
        return {name: len(handlers) for name, handlers in self.events.items()}

    def get_event_info(self, name):
        """Get detailed information about an event.

        Args:
            name (str): The name of the event to get info for

        Returns:
            dict: Event information including name, handler count, and handler details

        Raises:
            EventNotFoundError: If the event doesn't exist
        """
        if name not in self.events:
            raise EventNotFoundError(f"Event '{name}' does not exist")

        return {
            "name": name,
            "handler_count": len(self.events[name]),
            "handlers": [
                {
                    "function": (
                        handler.__name__
                        if hasattr(handler, "__name__")
                        else str(handler)
                    ),
                    "one_time": one_time,
                }
                for handler, one_time in self.events[name]
            ],
        }

    def clear_all_events(self):
        """Clear all registered events. Useful for testing and cleanup."""
        self.events.clear()
        logging.debug("Cleared all events")


Events = _Event()
