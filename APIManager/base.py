from abc import abstractmethod
from typing import Any


class MessageSender:
    """A base class for all senders.
    
    Args
    ----
    description: str
        A brief introduction for your sender.
    name: str
        The name of your sender.
    """

    def __init__(self, *args, **kwargs):
        self.description: str = kwargs.pop("description", "This is a MessageSender of ...")
        self.name: str = kwargs.pop("name", None)
        if self.name is None:
            raise ValueError("You have to provide a name for sender.")
        

    @abstractmethod
    def send(self, message: Any):
        """Send messages such as errors or warnings to somewhere. 
        Args
        ----
        message: Any
            Concrete message to send.
        """
        raise NotImplementedError("Must be subclassed.")
    