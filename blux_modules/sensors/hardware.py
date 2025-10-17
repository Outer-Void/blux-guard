"""
Hardware sensors: charging, BT pairing, USB attach
"""

def charging_status():
    # Placeholder: just simulate
    status = True
    print(f"[HW] Charging: {status}")
    return status

def bt_paired_devices():
    devices = ["BT-Headset-1"]
    print(f"[HW] Paired BT devices: {devices}")
    return devices

def usb_attached():
    usb = ["USB-Drive-1"]
    print(f"[HW] USB attached: {usb}")
    return usb

def monitor_loop(interval=5):
    import time
    while True:
        charging_status()
        bt_paired_devices()
        usb_attached()
        time.sleep(interval)