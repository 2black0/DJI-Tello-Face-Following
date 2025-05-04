from djitellopy import Tello

tello = Tello()
tello.connect()

while True:
    battery = tello.get_battery()
    height = tello.get_height()
    flight_time = tello.get_flight_time()

    pitch = tello.get_pitch()
    roll = tello.get_roll()
    yaw = tello.get_yaw()

    speed_x = tello.get_speed_x()
    speed_y = tello.get_speed_y()
    speed_z = tello.get_speed_z()

    temp = tello.get_temperature()

    print('bat:{} | hei:{} | ft:{} | r:{} | p:{} | y:{} | sx:{} | sy:{} | sz:{} | temp:{}'.format(battery, height, flight_time, roll, pitch, yaw, speed_x, speed_y, speed_z, temp))