#!/usr/bin/env python3
import os
import time
import threading
import sys

PWMCHIP = "/sys/class/pwm/pwmchip0"
PWM = os.path.join(PWMCHIP, "pwm0")   # budeme používat pwm0

# ---------- pomocné funkce ----------
def read_temp():
    path = "/sys/class/thermal/thermal_zone0/temp"
    try:
        with open(path, "r") as f:
            val = int(f.read().strip())
        return val / 1000.0
    except:
        return None

def write_file(path, data):
    try:
        with open(path, "w") as f:
            f.write(str(data))
        return True
    except:
        return False

def ensure_pwm_exported():
    if not os.path.exists(PWM):
        export = os.path.join(PWMCHIP, "export")
        write_file(export, "0")
        time.sleep(0.1)
    # nastavíme periodu na 25kHz (typická pro ventilátory)
    period_path = os.path.join(PWM, "period")
    write_file(period_path, "40000")  # v nanosekundách
    enable_path = os.path.join(PWM, "enable")
    write_file(enable_path, "1")

def set_pwm_percent(pct):
    pct = max(0, min(100, float(pct)))
    period = int(read_int(os.path.join(PWM, "period")))
    duty = int(period * (pct / 100.0))
    write_file(os.path.join(PWM, "duty_cycle"), str(duty))

def read_int(path):
    try:
        with open(path, "r") as f:
            return int(f.read().strip())
    except:
        return None

# ---------- vlákno pro příkazy ----------
def cmd_thread():
    global running
    while running:
        line = sys.stdin.readline()
        if not line:
            continue
        line = line.strip()
        if line.startswith("set "):
            try:
                pct = float(line.split()[1])
                set_pwm_percent(pct)
                print(f"PWM set to {pct:.1f}%")
            except:
                print("Invalid value")
        elif line in ("exit", "quit"):
            running = False
            break
        elif line == "help":
            print("Commands: set <percent> | exit")

# ---------- hlavní ----------
running = True
ensure_pwm_exported()

t = threading.Thread(target=cmd_thread, daemon=True)
t.start()

try:
    while running:
        temp = read_temp()
        duty = read_int(os.path.join(PWM, "duty_cycle"))
        period = read_int(os.path.join(PWM, "period"))
        pct = (duty / period * 100.0) if duty and period else None
        temp_s = f"{temp:.1f}°C" if temp else "N/A"
        pct_s = f"{pct:.1f}%" if pct else "N/A"
        print(f"[{time.strftime('%H:%M:%S')}] Temp={temp_s} | PWM={pct_s}")
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    write_file(os.path.join(PWM, "enable"), "0")
    print("Exiting...")
