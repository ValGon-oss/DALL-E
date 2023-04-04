# requires: openai, Pillow
from io import BytesIO
from PIL import Image
from .. import loader, utils
import requests
import json
import os

class GenerateImageMod(loader.Module):
    """Generates an image using DALL-E API"""
    strings = {"name": "DALL-E"}

    async def client_ready(self, client, db):
        self.db = db

    async def gencmd(self, message):
        """Generates an image using DALL-E API"""
        args = utils.get_args_raw(message)

        if not args:
            await utils.answer(message, "Please provide a prompt to generate an image with DALL-E.")
            return

        api_key = self.db.get(__name__, "openai_api_key", None)

        if not api_key:
            await utils.answer(message, "No OpenAI API key found. Please set one with .setaikey <key>.")
            return

        await utils.answer(message, "Жди, я генерирую, это немного долго")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key,
        }

        data = {
            'model': 'image-alpha-001',
            'prompt': args,
            'num_images': 1,
            'size': '512x512',
        }

        response = requests.post('https://api.openai.com/v1/images/generations', headers=headers, data=json.dumps(data))

        if response.status_code != 200:
            await utils.answer(message, f"Failed to generate image. Error code: {response.status_code}")
            return

        response_json = response.json()

        if 'data' not in response_json or len(response_json['data']) == 0:
            await utils.answer(message, "Failed to generate image. No data returned.")
            return

        image_url = response_json['data'][0]['url']

        image_data = requests.get(image_url).content
        image = Image.open(BytesIO(image_data))

        image_path = os.path.join(os.getcwd(), 'dall-e-image.png')
        image.save(image_path)

        await message.client.send_file(message.to_id, image_bytes.getvalue(), caption="Generated image")


    async def apicmd(self, message):
        """Sets the OpenAI API key"""
        key = utils.get_args_raw(message)

        if not key:
            await utils.answer(message, "Please provide an OpenAI API key.")
            return

        self.db.set(__name__, "openai_api_key", key)
        await utils.answer(message, "OpenAI API key set.")
