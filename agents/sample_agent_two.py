import logging

from agents import Agent

log = logging.getLogger(Agent.AgentTwo)


class AgentTwo:
    #publish = None # No need to assign it will automatically assigned by rakun

    def __init__(self, *args, **kwargs):
        log.info(f"{self} Start")

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
                "name": "AgentTwo"
            })
