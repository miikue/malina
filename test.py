import RPi.GPIO as GPIO
import time

# Nastavení pinu
FAN_PIN = 26  # BCM číslo (fyzicky pin 37)
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)

# Nastavení PWM – 25 Hz je běžná hodnota pro ventilátory
pwm = GPIO.PWM(FAN_PIN, 25)
pwm.start(0)

try:
    print("Zadej rychlost větráku (1–100 %) nebo 0 pro vypnutí. Ukonči 'exit'.")
    while True:
        user_input = input("Otáčky [%]: ")
        if user_input.lower() == "exit":
            break
        try:
            speed = int(user_input)
            if 0 <= speed <= 100:
                pwm.ChangeDutyCycle(speed)
                print(f"Nastaveno {speed} %")
            else:
                print("Zadej hodnotu 0–100.")
        except ValueError:
            print("Zadej číslo nebo 'exit'.")
except KeyboardInterrupt:
    pass
finally:
    print("Ukončuji...")
    pwm.stop()
    GPIO.cleanup()
