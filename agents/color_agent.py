import logging
import random

from agents import Agent
from agents.agent_messages import create_message

log = logging.getLogger(Agent.ColorAgent)


class ColorAgent:
    # publish = None # No need to assign it will automatically assigned by rakun

    def __init__(self,sender_id, *args, **kwargs):
        self.id = sender_id
        self.is_running = True
        log.info(f"{self} Start {args} {kwargs}")

    async def start(self):
        log.info("Agent AgentTwo Starting...")

    async def accept_message(self, message):
        log.info(message)

    async def stop(self, *args, **kwargs):
        log.info("Agent AgentTwo Stopping...")

    async def execute(self, *args, **kwargs):
        while self.is_running:
            rectangle_red = random.randint(0, 255)
            rectangle_green = random.randint(0, 255)
            rectangle_blue = random.randint(0, 255)

            await self.publish(create_message("colors", {
                'sender_id': self.id,
                "r": rectangle_red,
                "g": rectangle_green,
                "b": rectangle_blue,
            }))
