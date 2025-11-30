import RPi.GPIO as GPIO
import time
import subprocess

# Nastavení GPIO
FAN_PIN = 26  # BCM číslo, fyzický pin 37
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(FAN_PIN, GPIO.OUT)
pwm = GPIO.PWM(FAN_PIN, 25)  # 25 Hz
pwm.start(0)

# Hystereze: paměť poslední nastavené rychlosti
last_speed = 0

def get_cpu_temp():
    try:
        temp_str = subprocess.check_output(["cat", "/sys/class/thermal/thermal_zone0/temp"]).decode()
        temp_c = float(temp_str) / 1000.0
        return temp_c
    except Exception:
        return None

def calc_fan_speed(temp_c, last_speed):
    # Definuj teplotní prahy a k nim odpovídající otáčky
    thresholds = [
        (45, 0),
        (50, 30),
        (55, 60),
        (65, 80),
        (float('inf'), 100)
    ]

    # Hystereze ve stupních
    hysteresis = 2

    for i, (temp_threshold, speed) in enumerate(thresholds):
        # Pokud jsme aktuálně na této rychlosti
        if speed == last_speed:
            # Nezměňuj, dokud teplota neopustí rozsah +/- hysteresis
            lower = thresholds[i-1][0] + hysteresis if i > 0 else -float('inf')
            upper = temp_threshold - hysteresis
            if lower <= temp_c <= upper:
                return last_speed

        if temp_c < temp_threshold:
            return speed

    return last_speed  # fallback

try:
    print("Automatická regulace ventilátoru spuštěna. Ukonči Ctrl+C.")
    while True:
        cpu_temp = get_cpu_temp()
        if cpu_temp is not None:
            new_speed = calc_fan_speed(cpu_temp, last_speed)
            if new_speed != last_speed:
                pwm.ChangeDutyCycle(new_speed)
                print(f"[Změna] CPU: {cpu_temp:.1f}°C → {new_speed}%")
                last_speed = new_speed
            else:
                print(f"[Beze změny] CPU: {cpu_temp:.1f}°C, držím {last_speed}%")
        else:
            print("Nepodařilo se zjistit teplotu CPU.")
        time.sleep(10)

except KeyboardInterrupt:
    print("Ukončuji program...")

finally:
    pwm.stop()
    GPIO.cleanup()
