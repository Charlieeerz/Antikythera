# test_gpio.py
from gpiozero import Button
import time

test = Button(27)
while True:

    if(test.is_pressed):
        print("GPIO OK")
    else:
        print("no")
    time.sleep(0.5)

