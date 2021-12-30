import asyncio
import logging

from agents import Agent
import random
import uuid
from PIL import Image, ImageDraw
from sewar.full_ref import uqi
import numpy as np
import matplotlib.pyplot as plt

log = logging.getLogger(Agent.DrawingAgent)


class DrawingAgent:
    # publish = None # No need to assign it will automatically assigned by rakun

    def __init__(self, *args, **kwargs):
        log.info(f"{self} Start")

    async def start(self):
        log.info("Agent AgentOne Starting...")

    async def accept_message(self, message):
        log.info(message)

    async def stop(self, *args, **kwargs):
        log.info("Agent AgentOne Stopping...")

    async def execute(self, *args, **kwargs):

        await self.dynamic_agent(Agent.ColorAgent, {
            'name': 'agent_one',
            'color': 'red'
        })
        await self.dynamic_agent(Agent.ColorAgent, {
            'name': 'agent_two',
            'color': 'green'
        })
        await asyncio.sleep(2)
        # image_width = 1600
        # image_height = 1600
        # pixel_size = 8
        #
        # original_image = Image.open('./data/sample_1.jpg').resize((image_width, image_height))
        # original_image = np.array(original_image)
        #
        # run_id, gen_image = await self.draw_image(image_width, image_height, pixel_size)
        # gen_image = np.array(gen_image)
        #
        # log.info(f"image shape: {original_image.shape} {gen_image.shape}")
        #
        # uqi_score = uqi(gen_image, original_image)
        # log.info(f"{run_id} MSE score: {uqi_score}")
        #
        # plt.imshow(gen_image)
        #
        # f = plt.figure()
        # f.add_subplot(1, 2, 1)
        # plt.imshow(original_image)
        # f.add_subplot(1, 2, 2)
        # plt.imshow(gen_image)
        # plt.show()

    async def draw_image(self, image_width, image_height, pixel_size):
        run_id = uuid.uuid1()

        log.info(f'Processing run_id: {run_id}')

        image = Image.new('RGB', (image_width, image_height))

        rectangle_width = pixel_size
        rectangle_height = pixel_size

        number_of_squares = int(image_width * image_height / rectangle_width / rectangle_height)

        log.info(f'Number of squares: {number_of_squares}')

        draw_image = ImageDraw.Draw(image)

        all_points = {}
        iteration = 1

        x_points = [i for i in range(int(image_width // rectangle_width))]
        y_points = [i for i in range(int(image_height // rectangle_height))]

        while len(all_points) != number_of_squares:
            rectangle_x = random.choice(x_points) * rectangle_width
            rectangle_y = random.choice(y_points) * rectangle_height
            rectangle_red = random.randint(0, 255)
            rectangle_green = random.randint(0, 255)
            rectangle_blue = random.randint(0, 255)

            point = (rectangle_x, rectangle_y)
            point_key = f'{rectangle_x}_{rectangle_y}'

            rectangle_shape = [
                point,
                (rectangle_x + rectangle_width,
                 rectangle_y + rectangle_height)]

            if point_key not in all_points:
                all_points[point_key] = (*point, rectangle_red, rectangle_green, rectangle_blue)

                draw_image.rectangle(
                    rectangle_shape,
                    fill=(
                        rectangle_red,
                        rectangle_green,
                        rectangle_blue)
                )
            iteration += 1
        return run_id, image
