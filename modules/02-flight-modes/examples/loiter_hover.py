"""
loiter_hover.py
---------------
Demonstrasi penggunaan LOITER untuk hover stabil di beberapa titik.
Drone terbang ke dua titik berbeda dan melakukan LOITER di masing-masing titik
sebelum kembali landing.

Alur: Takeoff -> Titik A [LOITER] -> Titik B [LOITER] -> Landing

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
            print(f"[WARN] Timeout saat pindah ke mode {mode_name}")
            return False
        time.sleep(0.5)
    print(f"[MODE] {mode_name} aktif")
    return True


def arm_and_takeoff(vehicle, target_altitude):
    """Arm drone dan takeoff ke ketinggian yang ditentukan."""
    print("[INFO] Menunggu drone siap...")
    while not vehicle.is_armable:
        time.sleep(1)

    switch_mode(vehicle, "GUIDED")

    vehicle.armed = True
    while not vehicle.armed:
        time.sleep(1)
    print("[INFO] Drone ter-arm")

    print(f"[INFO] Takeoff ke {target_altitude}m...")
    vehicle.simple_takeoff(target_altitude)

    while True:
        alt = vehicle.location.global_relative_frame.alt
        print(f"  Naik... {alt:.2f}m")
        if alt >= target_altitude * 0.95:
            print(f"[INFO] Ketinggian {target_altitude}m tercapai")
            break
        time.sleep(1)


def get_offset_location(original, d_north, d_east, alt):
    """Hitung koordinat GPS baru berdasarkan offset meter dari posisi asal."""
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


def fly_to_and_loiter(vehicle, d_north, d_east, altitude, hover_duration, label):
    """
    Terbang ke titik offset dari posisi saat ini dalam mode GUIDED,
    lalu beralih ke LOITER dan hover selama durasi yang ditentukan.

    Parameter:
        vehicle        : objek Vehicle DroneKit
        d_north        : float - offset ke utara dalam meter
        d_east         : float - offset ke timur dalam meter
        altitude       : float - ketinggian terbang dalam meter
        hover_duration : int   - durasi hover LOITER dalam detik
        label          : str   - nama titik untuk log
    """
    # Pastikan dalam mode GUIDED sebelum bergerak
    if vehicle.mode.name != "GUIDED":
        switch_mode(vehicle, "GUIDED")

    current = vehicle.location.global_relative_frame
    target = get_offset_location(current, d_north, d_east, altitude)

    print(f"\n[NAV] Menuju {label}...")
    vehicle.simple_goto(target)

    # Tunggu sampai mendekati target
    while True:
        dist = get_distance(vehicle.location.global_relative_frame, target)
        alt = vehicle.location.global_relative_frame.alt
        print(f"  Jarak ke {label}: {dist:.1f}m | Alt: {alt:.2f}m")
        if dist <= 2.0:
            print(f"[NAV] Tiba di {label}")
            break
        time.sleep(1)

    # LOITER di titik ini
    print(f"[LOITER] Hover di {label} selama {hover_duration} detik...")
    switch_mode(vehicle, "LOITER")
    print(f"  Posisi terkunci: lat={vehicle.location.global_relative_frame.lat:.6f}, "
          f"lon={vehicle.location.global_relative_frame.lon:.6f}")

    for i in range(hover_duration, 0, -1):
        alt = vehicle.location.global_relative_frame.alt
        print(f"  Hovering {i}s | Alt: {alt:.2f}m")
        time.sleep(1)

    print(f"[LOITER] Selesai di {label}")


# --- Main Program ---

print("=" * 55)
print("  LOITER Hover Demo - Multi-Point Mission")
print("=" * 55)

print("\n[1] Koneksi ke SITL...")
vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)
print(f"    Terhubung. Mode: {vehicle.mode.name}")

print("\n[2] Arm dan Takeoff ke 12 meter...")
arm_and_takeoff(vehicle, target_altitude=12)

# Titik A: 20 meter ke utara, hover 8 detik
fly_to_and_loiter(vehicle, d_north=20, d_east=0, altitude=12,
                  hover_duration=8, label="Titik A (20m Utara)")

# Titik B: dari A, 15 meter ke timur, hover 8 detik
fly_to_and_loiter(vehicle, d_north=0, d_east=15, altitude=12,
                  hover_duration=8, label="Titik B (15m Timur)")

# Kembali ke sekitar posisi asal
print("\n[NAV] Kembali ke posisi awal...")
switch_mode(vehicle, "GUIDED")
current = vehicle.location.global_relative_frame
home = get_offset_location(current, d_north=-20, d_east=-15, alt=12)
vehicle.simple_goto(home)
time.sleep(9)

# Landing
print("\n[3] Landing...")
switch_mode(vehicle, "LAND")
while vehicle.location.global_relative_frame.alt > 0.2:
    print(f"  Mendarat... {vehicle.location.global_relative_frame.alt:.2f}m")
    time.sleep(1)

print("\n[DONE] Misi selesai.")
print("  Rute: Takeoff -> Titik A [LOITER] -> Titik B [LOITER] -> Landing")
vehicle.close()