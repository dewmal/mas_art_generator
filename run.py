import asyncio
import datetime
import logging
import os
import pickle
import time
from importlib.machinery import SourceFileLoader

import click
import grpc
from google.protobuf.timestamp_pb2 import Timestamp

import agent_pb2 as agent_pb2
import agent_pb2_grpc as agent_pb2_grpc

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger("RAKUN-MAS")


class AgentManager:

    def __init__(self, address, agent_id, agent_name, retry):
        self.retry = retry
        self.address = address
        self.agent = agent_pb2.Agent(
            id=agent_id,
            name=agent_name
        )

    async def dynamic_agent(self, agent, params):
        try:
            async with grpc.aio.insecure_channel(self.address) as channel:
                stub = agent_pb2_grpc.BroadcastStub(channel)
                content = []
                for k in params.keys():
                    val = params[k]
                    data = agent_pb2.InitData(
                        key=k,
                        value=val
                    )
                    content.append(data)

                await stub.StartDynamicAgent(agent_pb2.DynamicAgent(
                    name=agent,
                    initConfigs=content
                ))
        except Exception as e:
            log.error(e)
            return

    async def publish(self, message, msg_type="AGENT", id=None, request_id=None, tags=[]):
        try:
            async with grpc.aio.insecure_channel(self.address) as channel:
                stub = agent_pb2_grpc.BroadcastStub(channel)
                content = []
                for k in message.keys():
                    val = message[k]
                    data = agent_pb2.Data(
                        key=k,
                        value=pickle.dumps(val)
                    )
                    content.append(data)

                now = time.time()
                seconds = int(now)
                nanos = int((now - seconds) * 10 ** 9)
                msg_obj = agent_pb2.Message(
                    id=id if id else f"{datetime.datetime.utcnow().timestamp()}",
                    sender=self.agent,
                    content=content,
                    type=msg_type,
                    timestamp=Timestamp(seconds=seconds, nanos=nanos),
                    request_id=request_id if request_id else f"{datetime.datetime.utcnow().timestamp()}",
                    tags=tags
                )
                await stub.BroadcastMessage(msg_obj)
                return True
        except Exception as e:
            log.exception("error: {}".format(e), e)
            raise e

    async def subscribe_for_manager(self, message_processor):
        try:
            async with grpc.aio.insecure_channel(self.address) as channel:
                stub = agent_pb2_grpc.BroadcastStub(channel)

                now = time.time()
                seconds = int(now)
                nanos = int((now - seconds) * 10 ** 9)

                connect = agent_pb2.Connect(
                    user=self.agent,
                    active=True,
                    timestamp=Timestamp(seconds=seconds, nanos=nanos)
                )

                stream = stub.CreateStream(connect)
                await self.publish({
                    "type": "CONNECT",
                })
                async for message in stream:
                    try:
                        await self.__process_message(message, message_processor)
                    except Exception as e:
                        log.exception("error: {}".format(e), e)
                        raise e

        except Exception as e:
            log.exception("error: {}".format(e), e)
            await self.retry(self)

    async def subscribe_for_sync_time(self, time_subscriber):
        try:
            async with grpc.aio.insecure_channel(self.address) as channel:
                stub = agent_pb2_grpc.BroadcastStub(channel)

                now = time.time()
                seconds = int(now)
                nanos = int((now - seconds) * 10 ** 9)

                connect = agent_pb2.Connect(
                    user=self.agent,
                    active=True,
                    timestamp=Timestamp(seconds=seconds, nanos=nanos)
                )

                stream = stub.SyncTime(connect)
                async for td in stream:
                    try:
                        timestamp_dt = datetime.datetime.fromtimestamp(td.timestamp.seconds + td.timestamp.nanos / 1e9)
                        await time_subscriber(timestamp_dt)
                    except Exception as e:
                        log.exception("error: {}".format(e), e)
                        raise e

        except Exception as e:
            log.exception("error: {}".format(e), e)
            await self.retry(self)

    async def __process_message(self, message: agent_pb2.Message, message_processor):
        content = {}
        for c in message.content:
            key = c.key
            value = pickle.loads(c.value)
            content[key] = value
        await message_processor({
            "content": content,
            "sender": message.sender,
            "type": message.type
        })


class AgentWrapper:

    def __init__(self, id, agent, publish, dynamic_agent, exit):
        self.id = id
        self.publish = publish
        self.exit = exit
        self._agent_ = agent
        self._agent_.event_loop = asyncio.get_event_loop()
        self._agent_.publish = publish
        self._agent_.dynamic_agent = dynamic_agent
        self._agent_.time_delta = 0
        self._agent_.exit = self.exit

    async def start_agent(self):
        if hasattr(self._agent_, "start"):
            try:
                await self._agent_.start()
            except Exception as e:
                log.exception(e)
                raise e

    async def stop_agent(self):
        if hasattr(self._agent_, "stop"):
            try:
                log.info(f"AGENT CLOSE REQUEST {self.id}")
                await self._agent_.stop()
            except Exception as e:
                log.exception(e)
                raise e

    async def execute_agent(self):
        if hasattr(self._agent_, "execute"):
            try:
                await self._agent_.execute()
            except Exception as e:
                log.exception(e)
                raise e

    async def accept_message(self, message):
        if hasattr(self._agent_, "accept_message"):
            try:
                await self._agent_.accept_message(message=message)
            except Exception as e:
                log.exception(e)
                raise e

    async def sync_time(self, time_delta):
        self._agent_.time_delta = time_delta

    async def run(self):
        await self.start_agent()
        await self.execute_agent()
        await self.stop_agent()

    # async def dynamic_agent(self, name, params):


async def run(comm_server_url, agent_obj, agent_id, agent_name) -> None:
    async def run_agent_manager(agm: AgentManager, agent: AgentWrapper):
        tasks = [agent.run(),
                 agm.subscribe_for_sync_time(agent.sync_time),
                 agm.subscribe_for_manager(agent.accept_message)]
        tsk = asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
        log.info(f"AGENT {agent_id} STARTED")
        await tsk

    agm = AgentManager(comm_server_url, agent_id=agent_id, agent_name=agent_name, retry=run_agent_manager)
    agent = AgentWrapper(id=id, agent=agent_obj,
                         publish=agm.publish,
                         dynamic_agent=agm.dynamic_agent,
                         exit=exit)
    await run_agent_manager(agm, agent)


@click.command()
@click.option('--stack-name', help='Agent Stack Name')
@click.option('--id', help='Agent ID')
@click.option('--host', help='Rakun Service URL')
@click.option('--name', help='Agent Name')
@click.option('--source', help='Agent Source')
@click.option("--init-params", multiple=True, default=[("name", "agent_init")], type=click.Tuple([str, str]))
def main(stack_name, id, host, name, source, init_params):
    source = f"{os.path.abspath(source)}"
    log.info(source)
    if os.path.exists(source):
        agent_source_code = SourceFileLoader("", source).load_module()
        agent_class = getattr(agent_source_code, name)
        params = {k: v for k, v in init_params}
        log.info(f"{type(init_params)}")
        agent_obj = agent_class(**params)
        asyncio.run(run(host, agent_obj, id, name))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
