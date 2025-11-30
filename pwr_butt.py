#!/usr/bin/env python3
import gpiod
import time
import os

# Minimální délka stisku (ms), aby se provedlo vypnutí
SHUTDOWNPULSEMINIMUM = 2000  

# Výchozí hodnoty pinů
chip_number = 0           # /dev/gpiochip0
shutdown_pin = 4          # GPIO4 jako vstup (tlačítko)
boot_pin = 17             # GPIO17 jako výstup (nastaví se na 1)

# Inicializace GPIO chipu
chip = gpiod.Chip(f"/dev/gpiochip{chip_number}")

# Inicializace výstupu (boot pin)
boot_line = chip.get_line(boot_pin)
boot_line.request(consumer="boot_led", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[1])

# Inicializace vstupu s eventy (shutdown pin)
shutdown_line = chip.get_line(shutdown_pin)
shutdown_line.request(consumer="shutdown_button", type=gpiod.LINE_REQ_EV_BOTH_EDGES)

print("Monitoring GPIO4 (shutdown pin)...")

pulse_start = None

while True:
    if not shutdown_line.event_wait(sec=10):
        continue

    evt = shutdown_line.event_read()

    if evt.type == gpiod.LineEvent.RISING_EDGE:
        pulse_start = time.time()

    elif evt.type == gpiod.LineEvent.FALLING_EDGE and pulse_start:
        pulse_duration = (time.time() - pulse_start) * 1000  # ms
        pulse_start = None

        if pulse_duration > SHUTDOWNPULSEMINIMUM:
            print("Long press detected: Shutting down...")
            os.system("sudo poweroff")
            break

