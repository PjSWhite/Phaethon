import json
import threading
import redis
import tkinter as tk
import math
from datetime import datetime

# Some root setup
root = tk.Tk()
root.configure(bg='white')
root.title('Main Application')
screen_w = 1024
screen_h = 600
root.geometry(f'{screen_w}x{screen_h}+0+0')
root.bind('<Escape>', lambda _: root.destroy())

class Arrow:
	def __init__(self, canvas, x, y, length):
		# Receive the canvas from the main application
		self.canvas = canvas
		self.x = x
		self.y = y
		self.length = length

		# Create the line object on the shared canvas
		self.arrow_id = self.canvas.create_line(
            0, 0, 0, 0, 
            arrow=tk.LAST, 
            width=3, 
            fill='black',
            arrowshape=(20, 25, 10) 
        )

		self.rotate(0)

	def rotate(self, angle):
		radians = math.radians(angle)
		half_len = self.length / 2 
		# Calculate offset from the center (self.x, self.y)
		dx = half_len * math.cos(radians)
		dy = half_len * math.sin(radians)
		
		# Point 0 (Tail): Subtract the offset from center
		x0 = self.x - dx
		y0 = self.y - dy
		
		# Point 1 (Head): Add the offset to center
		x1 = self.x + dx
		y1 = self.y + dy
		
		# Update the arrow with both new points
		self.canvas.coords(self.arrow_id, x0, y0, x1, y1)

FONT_SIZE = 22

# Utilities
def label(x, y, text='Empty Text...', color='black') -> tk.Label:
	_label = tk.Label(root, text=text, bg='white', font=('Arial', FONT_SIZE), fg=color)
	_label.place(x=x, y=y)
	return _label

labels: dict = {
	"temperature": "Temperature: {} °C",
	"humidity": "Humidity: {}%",
	"pressure": "Air Pressure: {} Pa",
	"wind_speed": "Wind Speed: {} m/s",
	"wind_direction": "Wind Direction: {}",
	"precipitation": "Precipation: {} mm",
	"pm1_0": "PM 1.0: {} μg/m³",
	"pm25": "PM 2.5: {} μg/m³",
	"pm10": "PM 10: {} μg/m³",
	"aqi": "Air Quality Index: {}",
	"last_updated": "Last Updated: {}",
	"current_time": "Current Time: {}"
}

labels_object = {name: label(25, 25+i*FONT_SIZE*2, text_format.format("Loading...")) for i, (name, text_format) in enumerate(labels.items())}

# Man idk how to say about recursion but here it is
def update_time():
	now = datetime.now()	
	string_format = now.strftime("%b %d, %Y %I:%M:%S %p")
	# string_format = now.strftime("%c")
	time_label = labels_object.get("current_time", None)
	if time_label:
		time_label.config(text=labels.get("current_time", "Current Time: {}").format(string_format))

	root.after(1000, update_time)
update_time()

canvas_width = 300
canvas_height = 300
main_canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg='white', borderwidth=0)
main_canvas.pack(side=tk.RIGHT)
wind_direction_arrow = Arrow(main_canvas, canvas_width/2, canvas_height/2, 150)


aqi_words = ["Good", "Moderate", "Unhealthy", "Very Unhealthy", "Hazardous"]


def handle_update(data: dict):
	now = datetime.now()
	data['last_updated'] = now.strftime("%b %d, %Y %I:%M:%S %p")
	wind_direction_arrow.rotate(data.get("wind_direction", 0))

	for key, value in data.items():
		target = labels_object.get(key, None)
		text_format = labels.get(key, None)
		if not (target and text_format):
			continue

		target.after(0, lambda v=value, t=target, f=text_format: t.config(text=f.format(v)))

REDIS_HOST   = "localhost"
REDIS_PORT   = 6379
REDIS_DB     = 0
REDIS_TOPIC  = "weather"

def connect_redis():
	client = redis.Redis(
		host=REDIS_HOST,
		port=REDIS_PORT,
		decode_responses=True,
	)

	channel = client.pubsub()
	print("There is no point for this logger to exist, but if there is, then redis is connected successfully")

	return channel

running = True

def listen():
	channel = connect_redis()

	print(f"Trying to subscribe to channel: {REDIS_TOPIC}")
	channel.subscribe(REDIS_TOPIC)
	
	print("Receiving...")
	while running:
		message = channel.get_message(timeout=1.0)
		if not message:
			continue
			
		if message['type'] == 'message':
			print(f"Received: {message['data']}")
			data = json.loads(message['data'])
			# weird gimmick but cool
			root.after(0, lambda d=data: handle_update(d))

# Gayest thing known to man
redis_thread = threading.Thread(target=listen, daemon=True) # 
redis_thread.start()

# Run main application
if __name__ == "__main__":
	copyright = label(0, 0, "Copyright: ivan_is_gay.py").pack(anchor='s', side="bottom")
	root.mainloop()
















































































































































































































































































































































































































































































































































































































































































# Welcome to headaches 
else:
    raise RuntimeError("Could not resolve error due to invalid filename. Please revert it to its original name.")
