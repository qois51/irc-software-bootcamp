"""
01_basic_mission.py
-------------------
Misi dasar: arm, takeoff, terbang maju, mundur, lalu landing.
Ini adalah contoh paling sederhana sebagai titik awal belajar.

Alur misi:
  Start -> Takeoff 10m -> Maju 20m -> Mundur 20m -> Landing

Pastikan Mission Planner SITL sudah berjalan.
Koneksi default: tcp:127.0.0.1:5762
"""

import time
import math
from dronekit import connect, VehicleMode, LocationGlobalRelative


# --- Helper Functions ---

def switch_mode(vehicle, mode_name, timeout=10):
    """Berpindah mode dan menunggu konfirmasi flight controller."""
    vehicle.mode = VehicleMode(mode_name)
    start = time.time()
    while vehicle.mode.name != mode_name:
        if time.time() - start > timeout:
            print(f"[WARN] Timeout saat pindah ke {mode_name}")
            return False
        time.sleep(0.5)
    print(f"[MODE] {mode_name} aktif")
    return True


def arm_and_takeoff(vehicle, target_altitude):
    """Arm drone dan takeoff ke ketinggian yang ditentukan."""
    print("[INFO] Menunggu drone siap (is_armable)...")
    while not vehicle.is_armable:
        time.sleep(1)

    switch_mode(vehicle, "GUIDED")

    print("[INFO] Arm drone...")
    vehicle.armed = True
    while not vehicle.armed:
        print("  Menunggu arm...")
        time.sleep(1)
    print("[INFO] Drone ter-arm")

    print(f"[INFO] Takeoff ke {target_altitude} meter...")
    vehicle.simple_takeoff(target_altitude)

    while True:
        alt = vehicle.location.global_relative_frame.alt
        print(f"  Naik... {alt:.2f}m")
        if alt >= target_altitude * 0.95:
            print(f"[INFO] Ketinggian {target_altitude}m tercapai")
            break
        time.sleep(1)


def get_offset_location(original, d_north, d_east, alt):
    """
    Menghitung koordinat GPS baru berdasarkan offset meter dari posisi asal.

    Parameter:
        original : LocationGlobalRelative
        d_north  : float - offset ke utara (meter), negatif = selatan
        d_east   : float - offset ke timur (meter), negatif = barat
        alt      : float - ketinggian target (meter)
    """
    earth_radius = 6378137.0
    d_lat = d_north / earth_radius
    d_lon = d_east / (earth_radius * math.cos(math.radians(original.lat)))
    new_lat = original.lat + math.degrees(d_lat)
    new_lon = original.lon + math.degrees(d_lon)
    return LocationGlobalRelative(new_lat, new_lon, alt)


def get_distance(loc1, loc2):
    """Hitung jarak meter antara dua titik GPS."""
    d_lat = loc2.lat - loc1.lat
    d_lon = loc2.lon - loc1.lon
    return math.sqrt(d_lat ** 2 + d_lon ** 2) * 1.113195e5


def goto(vehicle, d_north, d_east, altitude, label="target", threshold=1.5):
    """
    Terbang ke titik offset dari posisi saat ini dan tunggu hingga tiba.

    Parameter:
        vehicle   : objek Vehicle DroneKit
        d_north   : float - offset ke utara (meter)
        d_east    : float - offset ke timur (meter)
        altitude  : float - ketinggian terbang (meter)
        label     : str   - nama titik untuk log
        threshold : float - jarak dalam meter untuk dianggap tiba
    """
    if vehicle.mode.name != "GUIDED":
        switch_mode(vehicle, "GUIDED")

    current = vehicle.location.global_relative_frame
    target = get_offset_location(current, d_north, d_east, altitude)

    print(f"[NAV] Menuju {label}...")
    vehicle.simple_goto(target)

    while True:
        dist = get_distance(vehicle.location.global_relative_frame, target)
        alt = vehicle.location.global_relative_frame.alt
        print(f"  Jarak ke {label}: {dist:.1f}m | Alt: {alt:.2f}m")
        if dist <= threshold:
            print(f"[NAV] Tiba di {label}")
            break
        time.sleep(1)


# --- Main Program ---

print("=" * 50)
print("  01 Basic Mission")
print("  Arm -> Takeoff -> Maju -> Mundur -> Landing")
print("=" * 50)

# Koneksi ke SITL
print("\n[1] Koneksi ke SITL Mission Planner...")
vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)
print(f"    Terhubung. Mode: {vehicle.mode.name}")

# Arm dan takeoff ke 10 meter
print("\n[2] Arm dan Takeoff...")
arm_and_takeoff(vehicle, target_altitude=10)

# Maju 20 meter ke utara
print("\n[3] Maju 20 meter ke utara...")
goto(vehicle, d_north=20, d_east=0, altitude=10, label="Titik Maju")
time.sleep(2)

# Mundur 20 meter kembali ke posisi awal
print("\n[4] Mundur 20 meter ke selatan...")
goto(vehicle, d_north=-20, d_east=0, altitude=10, label="Titik Asal")
time.sleep(2)

# Landing
print("\n[5] Landing...")
switch_mode(vehicle, "LAND")
while vehicle.location.global_relative_frame.alt > 0.2:
    print(f"  Mendarat... {vehicle.location.global_relative_frame.alt:.2f}m")
    time.sleep(1)

print("\n[DONE] Misi selesai.")
vehicle.close()