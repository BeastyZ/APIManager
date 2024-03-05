import os
import requests
import logging
from typing import Dict
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from .base import MessageSender

class LarkSender(MessageSender):
    """A Sender for Lark

    Args
    ----
    webhook_addr: str=None
        A url link to access your lark robot.
    """
    def __init__(self, webhook_addr: str=None, *args, **kwargs):
        # The `name` and `description` attributes can be set through keyword arguments, e.g. LarkSender(name="lark", description="This is a MessageSender of ...")
        super().__init__(*args, **kwargs)
        if webhook_addr is None:
            if 'WEBHOOK_ADDR' in os.environ:
                webhook_addr = os.environ['WEBHOOK_ADDR']
            else:
                raise ValueError('Failed to get webhook address of Lark. Add address to environment or pass it as an argument to class `LarkSender`.')
        self.webhook_addr = webhook_addr

    def send(self, message: str) -> None:
        params = {
            "msg_type": "text",
            "content": {"text": message},
        }
        resp = requests.post(url=self.webhook_addr, json=params)
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") and result["code"] != 0:
            logger.warning(f"{self.name} occurred error when sending messages. Error info: {result['msg']}")

        
class WandbSender(MessageSender):
    """A Sender for Wandb

    Args
    ----
    api_key: str=None
        An API key of Wandb.
    """
    def __init__(self, api_key: str=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if api_key is None:
            if "API_KEY" in os.environ:
                api_key = os.environ["API_KEY"]
            else:
                raise ValueError('Failed to get API key of wandb. Add API key to environment or pass it as an argument to class `WandbSender`.')
        self.api_key = api_key
        self.register()
            
    def send(self, message: Dict[str, float | int]) -> None:
        self.wandb_logger.log(message)

    def register(self):
        import wandb
        wandb.login(key=self.api_key)
        self.wandb_logger = wandb.init()
        

class AutoSender:
    def __init__(self):
        raise EnvironmentError("AutoSender is designed to be instantiated using the `AutoSender.from_sender_name(sender_name)` method.")
    
    @classmethod
    def from_sender_name(cls, sender_name: str, *args, **kwargs):
        """Get specific sender class by sender name.

        NOTICE: The `description` attribute can be set through keyword arguments, e.g. AutoSender.from_sender_name(sender_name="lark", description="This is a MessageSender of ...")

        Args
        ----
        sender_name: str
            A name for supported senders.
        """
        if sender_name == "lark":
            return LarkSender(kwargs.pop("webhook_addr", None), name=sender_name, *args, **kwargs)
        elif sender_name == "wandb":
            return WandbSender(kwargs.pop("api_key", None), name=sender_name, *args, **kwargs)
        else:
            raise ValueError(f"{sender_name} not supported.")
