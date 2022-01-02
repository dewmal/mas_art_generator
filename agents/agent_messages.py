import logging

log = logging.getLogger("Agent Message Helper")


def filter_message_(agent, message):
    if 'content' in message and 'type' not in message['content'] and 'data' in message['content'] and 'agent' in \
            message['content'] and message['content']['agent'] == agent:
        return message['content']['data']
    return None


def message_filter(message_type, message_sender=None):
    def wrapper(func, *args, **kwargs):
        async def wrapped(*args, **kwargs):
            try:
                self = args[0]
                agent_message = args[1]
                resp = filter_message_(message_type, agent_message)
                if resp is not None:
                    await func(self, **resp)
                # if "content" in agent_message and "type" in agent_message["content"] and \
                #         "id" in agent_message["content"]:
                #     content = agent_message["content"]
                #     sender = agent_message["sender"]
                #     message = Message(**content)
                #     message.sender = Sender(id=sender.id, name=sender.name)
                #     if message.type == message_type and message_sender is None:
                #         return await func(self, message=message)
                #     elif message.type == message_type and message_sender and message.sender.name == message_sender:
                #         return await func(self, message=message)
            except Exception as e:
                log.info(f"{args}")
                log.exception(e)
                raise e

        return wrapped

    return wrapper


def create_message(agent, message):
    return {
        'agent': agent,
        'data': message
    }
