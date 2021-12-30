import logging

from agents import Agent

log = logging.getLogger(Agent.ColorAgent)


class ColorAgent:
    # publish = None # No need to assign it will automatically assigned by rakun

    def __init__(self, name, color, *args, **kwargs):
        self.name = name
        self.color = color
        log.info(f"{self} Start {args} {kwargs}")

    async def start(self):
        log.info("Agent AgentTwo Starting...")

    async def accept_message(self, message):
        log.info(message)

    async def stop(self, *args, **kwargs):
        log.info("Agent AgentTwo Stopping...")

    async def execute(self, *args, **kwargs):
        log.info("RUN")
        while True:
            await self.publish({
                "name": self.name,
                "color": self.color
            })
