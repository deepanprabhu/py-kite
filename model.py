import uuid
import time
import random
import requests
import os

class Model:
	def __init__(self):
		time.sleep(self.setup())
		self.return_val = " - appended to input - " + str(uuid.uuid4())

	def predictItem(self, input: str):
		time.sleep(self.predict_time())
		return {"output": self.return_val, "input": input}

	def setup(self):
		return random.randint(2, 40)

	def predict(self):
		return random.randint(5, 25)

	def write_db(self, input, link):
		print(input)
		print(link)
		output = self.predictItem(input)
		print(output)
		post_data = {'input': input, 'output': output["output"], 'latency': '0'}
		print(requests.post(link, json=post_data).text)