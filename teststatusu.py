import psutil
import socket
import time
import subprocess
import json
import schedule
import platform

#CPU
CPU_temperature = 0.0
CPU_usage = 0.0
def update_cpu_stats():
    global CPU_temperature, CPU_usage
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        CPU_temperature = round((float(f.readline()) / 1000.0), 2)
    CPU_usage = psutil.cpu_percent(interval=1)

#MEM
MEM_available = 0.0
MEM_percent = 0.0
def update_mem_stats():
    global MEM_available, MEM_percent
    mem = psutil.virtual_memory()
    MEM_available = round((mem.available / (1024 ** 2)), 2)
    MEM_percent = mem.percent


#System
SYS_hostname = ""
SYS_os = ""
SYS_version = ""
SYS_uptime_s = 0
SYS_updates = 0
def update_sys_stats():
    global SYS_hostname, SYS_os, SYS_version, SYS_uptime_s, SYS_updates
    SYS_hostname = socket.gethostname()
    SYS_os = platform.system() + " " + platform.release()
    SYS_version = platform.version()
    with open('/proc/uptime', 'r') as f:
        SYS_uptime_s = float(f.readline().split()[0])
    try:
        result = subprocess.run(['apt-get', '-s', 'upgrade'], 
                              capture_output=True, text=True, timeout=60)
        SYS_updates = len([line for line in result.stdout.split('\n') 
                          if line.startswith('Inst')])
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        SYS_updates = -1



#Network
#ETH0
ETH0_online = False
ETH0_IPs = ""
ETH0_bytes_sent_MB = 0.0
ETH0_bytes_recv_MB = 0.0
ETH0_upload_Bps = 0.0
ETH0_download_Bps = 0.0
#WLAN0
WLAN0_online = False
WLAN0_IPs = ""
WLAN0_bytes_sent_MB = 0.0
WLAN0_bytes_recv_MB = 0.0
WLAN0_upload_Bps = 0.0
WLAN0_download_Bps = 0.0    
#TAILSCALE
TAILSCALE_online = False
TAILSCALE_IPs = ""
TAILSCALE_bytes_sent_MB = 0.0
TAILSCALE_bytes_recv_MB = 0.0
TAILSCALE_upload_Bps = 0.0
TAILSCALE_download_Bps = 0.0
def update_network_stats():
    global ETH0_online, ETH0_IPs, ETH0_bytes_sent_MB, ETH0_bytes_recv_MB, ETH0_upload_Bps, ETH0_download_Bps
    global WLAN0_online, WLAN0_IPs, WLAN0_bytes_sent_MB, WLAN0_bytes_recv_MB, WLAN0_upload_Bps, WLAN0_download_Bps
    global TAILSCALE_online, TAILSCALE_IPs, TAILSCALE_bytes_sent_MB, TAILSCALE_bytes_recv_MB, TAILSCALE_upload_Bps, TAILSCALE_download_Bps

    old_stats = psutil.net_io_counters(pernic=True)
    time.sleep(1)
    new_stats = psutil.net_io_counters(pernic=True)

    addrs = psutil.net_if_addrs()
    statuses = psutil.net_if_stats()

    #ETH0
    if "eth0" in new_stats:
        old = old_stats["eth0"]
        new = new_stats["eth0"]
        ETH0_online = statuses["eth0"].isup if "eth0" in statuses else False
        if ETH0_online:
            ETH0_IPs = ", ".join([addr.address for addr in addrs["eth0"] if addr.family == socket.AF_INET])
            ETH0_bytes_sent_MB = round((new.bytes_sent / (1024 ** 2)), 3)
            ETH0_bytes_recv_MB = round((new.bytes_recv / (1024 ** 2)), 3)
            ETH0_upload_Bps = round(((new.bytes_sent - old.bytes_sent) / 1), 2)
            ETH0_download_Bps = round(((new.bytes_recv - old.bytes_recv) / 1), 2)
        else:
            ETH0_IPs = ""
            ETH0_bytes_sent_MB = 0.0
            ETH0_bytes_recv_MB = 0.0
            ETH0_upload_Bps = 0.0
            ETH0_download_Bps = 0.0

    #WLAN0
    if "wlan0" in new_stats:
        old = old_stats["wlan0"]
        new = new_stats["wlan0"]
        WLAN0_online = statuses["wlan0"].isup if "wlan0" in statuses else False
        if WLAN0_online:
            WLAN0_IPs = ", ".join([addr.address for addr in addrs["wlan0"] if addr.family == socket.AF_INET])
            WLAN0_bytes_sent_MB = round((new.bytes_sent / (1024 ** 2)), 3)
            WLAN0_bytes_recv_MB = round((new.bytes_recv / (1024 ** 2)), 3)
            WLAN0_upload_Bps = round(((new.bytes_sent - old.bytes_sent) / 1), 2)
            WLAN0_download_Bps = round(((new.bytes_recv - old.bytes_recv) / 1), 2)
        else:
            WLAN0_IPs = ""
            WLAN0_bytes_sent_MB = 0.0
            WLAN0_bytes_recv_MB = 0.0
            WLAN0_upload_Bps = 0.0
            WLAN0_download_Bps = 0.0
    #TAILSCALE
    if "tailscale0" in new_stats:
        old = old_stats["tailscale0"]
        new = new_stats["tailscale0"]
        TAILSCALE_online = statuses["tailscale0"].isup if "tailscale0" in statuses else False
        if TAILSCALE_online:
            TAILSCALE_IPs = ", ".join([addr.address for addr in addrs["tailscale0"] if addr.family == socket.AF_INET])
            TAILSCALE_bytes_sent_MB = round((new.bytes_sent / (1024 ** 2)), 3)
            TAILSCALE_bytes_recv_MB = round((new.bytes_recv / (1024 ** 2)), 3)
            TAILSCALE_upload_Bps = round(((new.bytes_sent - old.bytes_sent) / 1), 2)
            TAILSCALE_download_Bps = round(((new.bytes_recv - old.bytes_recv) / 1), 2)
        else:
            TAILSCALE_IPs = ""
            TAILSCALE_bytes_sent_MB = 0.0
            TAILSCALE_bytes_recv_MB = 0.0
            TAILSCALE_upload_Bps = 0.0
            TAILSCALE_download_Bps = 0.0


#Disk usage
#SD card (/dev/mmcblk0p2)
SD_fstype = ""
SD_total_GB = 0.0
SD_used_GB = 0.0
SD_free_GB = 0.0
SD_percent = 0.0
#RAID (/dev/md0)
RAID_fstype = ""
RAID_total_GB = 0.0
RAID_used_GB = 0.0
RAID_free_GB = 0.0
RAID_percent = 0.0
def update_disk_usage():
    global SD_mountpoint, SD_fstype, SD_total_GB, SD_used_GB, SD_free_GB, SD_percent
    global RAID_mountpoint, RAID_fstype, RAID_total_GB, RAID_used_GB, RAID_free_GB, RAID_percent

    partitions = psutil.disk_partitions(all=False)
    for part in partitions:
        if part.device == "/dev/mmcblk0p2":
            usage = psutil.disk_usage(part.mountpoint)
            SD_mountpoint = part.mountpoint
            SD_fstype = part.fstype
            SD_total_GB = round((usage.total / (1024 ** 3)), 3)
            SD_used_GB = round((usage.used / (1024 ** 3)), 3)
            SD_free_GB = round((usage.free / (1024 ** 3)), 3)
            SD_percent = usage.percent
        elif part.device == "/dev/md0":
            usage = psutil.disk_usage(part.mountpoint)
            RAID_mountpoint = part.mountpoint
            RAID_fstype = part.fstype
            RAID_total_GB = round((usage.total / (1024 ** 3)), 3)
            RAID_used_GB = round((usage.used / (1024 ** 3)), 3)
            RAID_free_GB = round((usage.free / (1024 ** 3)), 3)
            RAID_percent = usage.percent


SD_read_MB = 0.0
SD_write_MB = 0.0
SDA_read_MB = 0.0
SDA_write_MB = 0.0
SDB_read_MB = 0.0
SDB_write_MB = 0.0
def update_disk_io():
    global SD_read_MB, SD_write_MB, SDA_read_MB, SDA_write_MB, SDB_read_MB, SDB_write_MB
    io = psutil.disk_io_counters(perdisk=True)
    if "mmcblk0" in io:
        SD_read_MB = round((io["mmcblk0"].read_bytes / (1024 ** 2)), 3)
        SD_write_MB = round((io["mmcblk0"].write_bytes / (1024 ** 2)), 3)
    if "sda" in io:
        SDA_read_MB = round((io["sda"].read_bytes / (1024 ** 2)), 3)
        SDA_write_MB = round((io["sda"].write_bytes / (1024 ** 2)), 3)
    if "sdb" in io:
        SDB_read_MB = round((io["sdb"].read_bytes / (1024 ** 2)), 3)
        SDB_write_MB = round((io["sdb"].write_bytes / (1024 ** 2)), 3)



SDA_temperature = 0.0
SDB_temperature = 0.0
SDA_SMART_status = "UNKNOWN"
SDA_SMART_Warnings = {}
SDB_SMART_status = "UNKNOWN"
SDB_SMART_Warnings = {}
SDA_SMART_Hours = 0
SDB_SMART_Hours = 0
SDA_SMART_PowerCycles = 0
SDB_SMART_PowerCycles = 0

def get_smart_info(device="/dev/sda"):
    try:
        output = subprocess.check_output(
            ["smartctl", "-a", "-j", device],
            stderr=subprocess.STDOUT
        ).decode()
    except subprocess.CalledProcessError as e:
        output = e.output.decode()

    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw_output": output}

def update_smart_data():
    global SDA_temperature, SDB_temperature
    global SDA_SMART_status, SDA_SMART_Warnings, SDB_SMART_status, SDB_SMART_Warnings
    global SDA_SMART_Hours, SDB_SMART_Hours
    global SDA_SMART_PowerCycles, SDB_SMART_PowerCycles

    smart_sda = get_smart_info("/dev/sda")
    smart_sdb = get_smart_info("/dev/sdb")

    # Parse /dev/sda SMART data
    if "error" not in smart_sda:
        SDA_temperature = smart_sda.get("temperature", {}).get("current", 0.0)
        attributes = smart_sda.get("ata_smart_attributes", {}).get("table", [])
        for attr in attributes:
            if attr.get("id") == 9:  # Power-On Hours
                SDA_SMART_Hours = attr.get("raw", {}).get("value", 0)
            elif attr.get("id") == 12:  # Power Cycle Count
                SDA_SMART_PowerCycles = attr.get("raw", {}).get("value", 0)
        SDA_SMART_status = smart_sda.get("smart_status", {}).get("passed", False)
        if not SDA_SMART_status:
            SDA_SMART_status = "FAILED"
            SDA_SMART_Warnings = {attr.get("name"): attr for attr in attributes if attr.get("when_failed") != ""}
        else:
            SDA_SMART_status = "OK"
            SDA_SMART_Warnings = {}
    else:
        SDA_temperature = 0.0
        SDA_SMART_status = "UNKNOWN"
        SDA_SMART_Warnings = {}
        SDA_SMART_Hours = 0
        SDA_SMART_PowerCycles = 0

    # Parse /dev/sdb SMART data
    if "error" not in smart_sdb:
        SDB_temperature = smart_sdb.get("temperature", {}).get("current", 0.0)
        attributes = smart_sdb.get("ata_smart_attributes", {}).get("table", [])
        for attr in attributes:
            if attr.get("id") == 9:  # Power-On Hours
                SDB_SMART_Hours = attr.get("raw", {}).get("value", 0)
            elif attr.get("id") == 12:  # Power Cycle Count
                SDB_SMART_PowerCycles = attr.get("raw", {}).get("value", 0)
        SDB_SMART_status = smart_sdb.get("smart_status", {}).get("passed", False)
        if not SDB_SMART_status:
            SDB_SMART_status = "FAILED"
            SDB_SMART_Warnings = {attr.get("name"): attr for attr in attributes if attr.get("when_failed") != ""}
        else:
            SDB_SMART_status = "OK"
            SDB_SMART_Warnings = {}
    else:
        SDB_temperature = 0.0
        SDB_SMART_status = "UNKNOWN"
        SDB_SMART_Warnings = {}
        SDB_SMART_Hours = 0
        SDB_SMART_PowerCycles = 0



def update_ALL():
    update_cpu_stats()
    update_mem_stats()
    update_sys_stats()
    update_network_stats()
    update_disk_usage()
    update_disk_io()
    update_smart_data()


#######################################################
import paho.mqtt.client as mqtt

# Konfigurace MQTT
BROKER = "100.97.149.11"  # nebo váš vlastní broker
PORT = 1883
TOPIC = "test/status"  # nahraďte vlastním tématem
USERNAME = "mqtt_user"
PASSWORD = "mqtt_password"

# Vytvoření MQTT klienta
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USERNAME, PASSWORD)

# Připojení k brokeru
client.connect(BROKER, PORT, 60)

report = {}

def makeReport():
    update_ALL()
    report = {
        "cpu": {
            "temperature_C": CPU_temperature,
            "usage_percent": CPU_usage
        },
        "memory": {
            "available_MB": MEM_available,
            "usage_percent": MEM_percent
        },
        "system": {
            "hostname": SYS_hostname,
            "os": SYS_os,
            "version": SYS_version,
            "uptime_s": SYS_uptime_s,
            "pending_updates": SYS_updates
        },
        "network": {
            "eth0": {
                "online": ETH0_online,
                "IPs": ETH0_IPs,
                "bytes_sent_MB": ETH0_bytes_sent_MB,
                "bytes_recv_MB": ETH0_bytes_recv_MB,
                "upload_Bps": ETH0_upload_Bps,
                "download_Bps": ETH0_download_Bps
            },
            "wlan0": {
                "online": WLAN0_online,
                "IPs": WLAN0_IPs,
                "bytes_sent_MB": WLAN0_bytes_sent_MB,
                "bytes_recv_MB": WLAN0_bytes_recv_MB,
                "upload_Bps": WLAN0_upload_Bps,
                "download_Bps": WLAN0_download_Bps
            },
            "tailscale0": {
                "online": TAILSCALE_online,
                "IPs": TAILSCALE_IPs,
                "bytes_sent_MB": TAILSCALE_bytes_sent_MB,
                "bytes_recv_MB": TAILSCALE_bytes_recv_MB,
                "upload_Bps": TAILSCALE_upload_Bps,
                "download_Bps": TAILSCALE_download_Bps
            }
        },
        "disk": {
            "sd_card": {
                "fstype": SD_fstype,
                "total_GB": SD_total_GB,
                "used_GB": SD_used_GB,
                "free_GB": SD_free_GB,
                "usage_percent": SD_percent
            },
            "raid": {
                "fstype": RAID_fstype,
                "total_GB": RAID_total_GB,
                "used_GB": RAID_used_GB,
                "free_GB": RAID_free_GB,
                "usage_percent": RAID_percent
            },
            "io_counters_MB": {
                "sd_card_read_MB": SD_read_MB,
                "sd_card_write_MB": SD_write_MB,
                "sda_read_MB": SDA_read_MB,
                "sda_write_MB": SDA_write_MB,
                "sdb_read_MB": SDB_read_MB,
                "sdb_write_MB": SDB_write_MB
            },
            "smart": {
                "sda": {
                    "temperature_C": SDA_temperature,
                    "SMART_status": SDA_SMART_status,
                    "SMART_warnings": SDA_SMART_Warnings,
                    "power_on_hours": SDA_SMART_Hours,
                    "power_cycle_count": SDA_SMART_PowerCycles
                },
                "sdb": {
                    "temperature_C": SDB_temperature,
                    "SMART_status": SDB_SMART_status,
                    "SMART_warnings": SDB_SMART_Warnings,
                    "power_on_hours": SDB_SMART_Hours,
                    "power_cycle_count": SDB_SMART_PowerCycles
                }
            }
        }
    }
    json_data = json.dumps(report)
    client.publish("malina/status", json_data)
    print(f"Odesláno: {json_data}")

schedule.every(1).minutes.do(makeReport)

while True:
    schedule.run_pending()
    time.sleep(1)

# Ukončení spojení
client.disconnect()