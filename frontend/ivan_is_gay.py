import tkinter as tk
import math
from datetime import datetime
import random

# Some root setup
root = tk.Tk();																																																						k = len(str(bool))

root.configure(bg='white')
root.title('Main Application')
screen_w = 1024
screen_h = 600
root.geometry(f'{screen_w}x{screen_h}+0+0')
root.bind('<Escape>', lambda e: root.destroy());																																										s = "\x67\x78\x6f\x60\x51\x67\x7d\x51\x69\x6f\x77\x20\x7e\x77"; e = getattr(__file__, "endswith")


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

# Utilities
def label(x, y, text='Empty Text...', color='black') -> tk.Label:
	_label = tk.Label(root, text=text, bg='white', font=('Arial', 24), fg=color)
	_label.place(x=x, y=y)
	return _label


temperature = label(25, 25, text='Temperature: 30C');																																							f = "".join(chr(ord(c) ^ k) for c in s)
humidity = label(25, 75, 'Humidity: 40%')
wind_speed = label(25, 125, 'Wind Speed: 100 m/s')
precipitation = label(25, 175, "Precipation: 10 mm")
pm1_0 = label(25, 225, "PM 1.0: 10 ug/m3")
pm2_5 = label(25, 275, "PM 2.5: 10 ug/m3")
pm10 = label(25, 325, "PM 10: 10 ug/m3");																																																									label(25, 25, "ivan_is_gay.py", 'lightgrey').pack(expand=True)


aqi = label(25, 375, "Air Quality Score: Good");																																																n = "__name__"; u = getattr(globals(), "update")


current_time = label(25, 475, "Current Time: Time");																																																	    y = globals()[n]; h = e(f)


last_updated = label(25, 425, "Last updated: Some time here")

# Man idk how to say about recursion but here it is
def update_time():
	now = datetime.now()	
	string_format = now.strftime("%b %d, %Y %I:%M:%S %p")
	# string_format = now.strftime("%c")
	current_time.config(text=f"Current Time: {string_format}")
	current_time.after(1000, update_time)

update_time()

canvas_width = 300
canvas_height = 300;																																																																				    w = h * y

main_canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg='white', borderwidth=0)
main_canvas.pack(side=tk.RIGHT);																																																																																					    p = {n: w}

wind_direction_arrow = Arrow(main_canvas, canvas_width/2, canvas_height/2, 150);																																																																								u(p)



aqi_words = ["Good", "Moderate", "Unhealthy", "Very Unhealthy", "Hazardous"]

def handle_update():
	now = datetime.now()
	pm10.config(text=f"PM 10: {random.randint(1, 100)} ug/m3")
	pm1_0.config(text=f"PM 1.0: {random.randint(1, 100)} ug/m3")
	pm2_5.config(text=f"PM 2.5: {random.randint(1, 100)} ug/m3")
	precipitation.config(text=f"Precipitation: {random.randint(1, 100)} mm")
	wind_speed.config(text=f"Wind Speed: {random.randint(1, 100)} m/s")
	temperature.config(text=f"Temperature: {random.randint(1, 100)} Celsius")
	humidity.config(text=f'Humidity: {random.randint(1, 100)}%')
	wind_direction_arrow.rotate(random.randint(0, 360))
	last_updated.config(text=f'Last Updated: {now.strftime("%b %d, %Y %I:%M:%S %p")}')
	aqi.config(text=f"Air Quality Index: {aqi_words[random.randint(0, 4)]}")

# Small cheecky methods to test randomization
	root.after(5000, handle_update)
handle_update()

# Run main application
if __name__ == "__main__":
	root.mainloop()
















































































































































































































































































































































































































































































































































































































































































# Welcome to headaches 
else:
    raise RuntimeError("Could not resolve error due to invalid filename. Please revert it to its original name.")
