"""
mode_switching.py
-----------------
Demonstrasi perpindahan mode terbang menggunakan DroneKit.
Alur: GUIDED -> Takeoff -> LOITER (hover) -> GUIDED -> LAND

Pastikan Mission Planner SITL sudah berjalan sebelum menjalankan skrip ini.
Koneksi default: tcp:127.0.0.1:5762
"""

import time
import math
from dronekit import connect, VehicleMode, LocationGlobalRelative


# --- Helper Functions ---

def switch_mode(vehicle, mode_name, timeout=10):
    """
    Berpindah ke mode tertentu dan menunggu konfirmasi flight controller.

    Parameter:
        vehicle   : objek Vehicle DroneKit
        mode_name : str - nama mode tujuan
        timeout   : int - batas waktu tunggu (detik)

    Return:
        bool - True jika berhasil, False jika timeout
    """
    vehicle.mode = VehicleMode(mode_name)
    start = time.time()

    while vehicle.mode.name != mode_name:
        if time.time() - start > timeout:
            print(f"[WARN] Timeout saat pindah ke mode {mode_name}")
            return False
        time.sleep(0.5)

    print(f"[MODE] {mode_name} aktif")
    return True


def arm_and_takeoff(vehicle, target_altitude):
    """
    Menunggu drone siap, melakukan arm, dan takeoff ke ketinggian target.

    Parameter:
        vehicle          : objek Vehicle DroneKit
        target_altitude  : float - ketinggian target dalam meter
    """
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
        print(f"  Ketinggian: {alt:.2f} m")
        if alt >= target_altitude * 0.95:
            print(f"[INFO] Ketinggian {target_altitude}m tercapai")
            break
        time.sleep(1)


def get_offset_location(original, d_north, d_east, alt):
    """
    Menghitung lokasi GPS baru berdasarkan offset dari posisi saat ini.

    Parameter:
        original : LocationGlobalRelative - posisi asal
        d_north  : float - offset ke utara dalam meter (negatif = selatan)
        d_east   : float - offset ke timur dalam meter (negatif = barat)
        alt      : float - ketinggian target dalam meter

    Return:
        LocationGlobalRelative - koordinat target
    """
    earth_radius = 6378137.0
    d_lat = d_north / earth_radius
    d_lon = d_east / (earth_radius * math.cos(math.radians(original.lat)))
    new_lat = original.lat + math.degrees(d_lat)
    new_lon = original.lon + math.degrees(d_lon)
    return LocationGlobalRelative(new_lat, new_lon, alt)


# --- Main Program ---

print("=" * 50)
print("  Mode Switching Demo - DroneKit SITL")
print("=" * 50)

# Koneksi ke SITL
print("\n[1] Menghubungkan ke SITL Mission Planner...")
vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)
print(f"    Terhubung. Mode: {vehicle.mode.name} | Armed: {vehicle.armed}")

# Arm dan takeoff
print("\n[2] Arm dan Takeoff ke 10 meter...")
arm_and_takeoff(vehicle, target_altitude=10)

# Terbang 15 meter ke utara dalam mode GUIDED
print("\n[3] GUIDED - terbang 15 meter ke utara...")
current = vehicle.location.global_relative_frame
target = get_offset_location(current, d_north=15, d_east=0, alt=10)
vehicle.simple_goto(target)
time.sleep(7)
print(f"    Posisi: {vehicle.location.global_relative_frame}")

# Beralih ke LOITER untuk hover stabil
print("\n[4] LOITER - hover stabil 10 detik...")
switch_mode(vehicle, "LOITER")
print(f"    Hovering di: lat={vehicle.location.global_relative_frame.lat:.6f}, "
      f"lon={vehicle.location.global_relative_frame.lon:.6f}, "
      f"alt={vehicle.location.global_relative_frame.alt:.2f}m")

for i in range(10, 0, -1):
    alt = vehicle.location.global_relative_frame.alt
    print(f"    LOITER {i}s | Alt: {alt:.2f}m")
    time.sleep(1)

# Kembali ke GUIDED dan mundur
print("\n[5] GUIDED - kembali ke posisi awal...")
switch_mode(vehicle, "GUIDED")
current = vehicle.location.global_relative_frame
back_target = get_offset_location(current, d_north=-15, d_east=0, alt=10)
vehicle.simple_goto(back_target)
time.sleep(7)

# Landing
print("\n[6] LAND - mendarat...")
switch_mode(vehicle, "LAND")
while vehicle.location.global_relative_frame.alt > 0.2:
    print(f"    Mendarat... {vehicle.location.global_relative_frame.alt:.2f}m")
    time.sleep(1)

print("\n[DONE] Demo selesai.")
print("  Mode yang digunakan: GUIDED -> LOITER -> GUIDED -> LAND")
vehicle.close()