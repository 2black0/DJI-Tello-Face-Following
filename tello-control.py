from djitellopy import Tello
import keyboard

tello = Tello()
tello.connect()
status = 0

while True:
    if keyboard.is_pressed('t') and status == 0:
        status =1
        tello.takeoff()
    elif keyboard.is_pressed('w'):
        tello.move_forward(30)
    elif keyboard.is_pressed('s'):
        tello.move_back(30)
    elif keyboard.is_pressed('a'):
        tello.move_left(30)
    elif keyboard.is_pressed('d'):
        tello.move_right(30)
    elif keyboard.is_pressed('e'):
        tello.rotate_clockwise(30)
    elif keyboard.is_pressed('q'):
        tello.rotate_counter_clockwise(30)
    elif keyboard.is_pressed('r'):
        #tello.move_up(30)
        tello.send_rc_control(0, 0, -25, 0)
    elif keyboard.is_pressed('f'):
        #tello.move_down(30)
        tello.send_rc_control(0, 0, 25, 0)
    elif keyboard.is_pressed('p'):
        tello.send_rc_control(0, 0, 0, 0)
    elif keyboard.is_pressed('l'):
        break

tello.land()

'''tello.takeoff()

print('Tello Hover')
for i in range(5000):
    tello.send_rc_control(0, 0, 0, 0)

print('Tello Moving Forward')
for i in range(3000):
    tello.send_rc_control(0, 0, -50, 0)

print('Tello Moving Backward')
for i in range(3000):
    tello.send_rc_control(0, 0, 50, 0)

print('Tello Hover')
for i in range(5000):
    tello.send_rc_control(0, 0, 0, 0)

tello.land()'''