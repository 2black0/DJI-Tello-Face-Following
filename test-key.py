import keyboard
# if key 'a' is pressed 
while True:
    if keyboard.is_pressed('a'):
        print('a key has ben pressed')
    if keyboard.is_pressed('b'):
        break