"""
02_square_pattern.py
--------------------
Misi pola kotak: drone terbang mengikuti pola persegi 20x20 meter
kemudian kembali ke posisi awal dan landing.

Alur misi:
  Start
    |
    A ---- B
           |
    D ---- C
    |
  Landing

  A = 20m Utara dari Start
  B = 20m Timur dari A
  C = 20m Selatan dari B (sejajar Start)
  D = 20m Barat dari C (kembali ke kolom awal)

Pastikan Mission Planner SITL sudah berjalan.
Koneksi default: tcp:127.0.0.1:5762
"""

import time
import math
from dronekit import connect, VehicleMode, LocationGlobalRelative


# --- Helper Functions ---

def switch_mode(vehicle, mode_name, timeout=10):
    """Berpindah mode dan menunggu konfirmasi."""
    vehicle.mode = VehicleMode(mode_name)
    start = time.time()
    while vehicle.mode.name != mode_name:
        if time.time() - start > timeout:
            print(f"[WARN] Timeout: {mode_name}")
            return False
        time.sleep(0.5)
    print(f"[MODE] {mode_name}")
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
    vehicle.simple_takeoff(target_altitude)
    while True:
        alt = vehicle.location.global_relative_frame.alt
        print(f"  Naik... {alt:.2f}m")
        if alt >= target_altitude * 0.95:
            print(f"[INFO] Ketinggian {target_altitude}m tercapai")
            break
        time.sleep(1)


def get_offset_location(original, d_north, d_east, alt):
    """Hitung koordinat GPS baru dari offset meter."""
    earth_radius = 6378137.0
    d_lat = d_north / earth_radius
    d_lon = d_east / (earth_radius * math.cos(math.radians(original.lat)))
    return LocationGlobalRelative(
        original.lat + math.degrees(d_lat),
        original.lon + math.degrees(d_lon),
        alt
    )


def get_distance(loc1, loc2):
    """Hitung jarak meter antara dua titik GPS."""
    d_lat = loc2.lat - loc1.lat
    d_lon = loc2.lon - loc1.lon
    return math.sqrt(d_lat ** 2 + d_lon ** 2) * 1.113195e5


def goto(vehicle, d_north, d_east, altitude, label="target", threshold=1.5):
    """Terbang ke titik offset dan tunggu hingga tiba."""
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

# Ukuran sisi kotak dalam meter
SQUARE_SIZE = 20
FLIGHT_ALTITUDE = 10

print("=" * 55)
print("  02 Square Pattern Mission")
print(f"  Pola Kotak {SQUARE_SIZE}x{SQUARE_SIZE} meter, Ketinggian {FLIGHT_ALTITUDE}m")
print("=" * 55)

print("""
  Pola terbang:
  Start
    |
    A ---- B
           |
    D ---- C
    |
  Landing
""")

# Koneksi
print("[1] Koneksi ke SITL...")
vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)
print(f"    Terhubung. Mode: {vehicle.mode.name}")

# Arm dan takeoff
print(f"\n[2] Arm dan Takeoff ke {FLIGHT_ALTITUDE}m...")
arm_and_takeoff(vehicle, target_altitude=FLIGHT_ALTITUDE)

# Simpan posisi awal (launch point) sebagai referensi
launch_location = vehicle.location.global_relative_frame
print(f"    Launch point: lat={launch_location.lat:.6f}, lon={launch_location.lon:.6f}")

# Titik A: 20m ke utara dari Start
print(f"\n[3] Menuju Titik A ({SQUARE_SIZE}m Utara)...")
goto(vehicle, d_north=SQUARE_SIZE, d_east=0,
     altitude=FLIGHT_ALTITUDE, label="Titik A")
time.sleep(1)

# Titik B: 20m ke timur dari A
print(f"\n[4] Menuju Titik B ({SQUARE_SIZE}m Timur)...")
goto(vehicle, d_north=0, d_east=SQUARE_SIZE,
     altitude=FLIGHT_ALTITUDE, label="Titik B")
time.sleep(1)

# Titik C: 20m ke selatan dari B
print(f"\n[5] Menuju Titik C ({SQUARE_SIZE}m Selatan)...")
goto(vehicle, d_north=-SQUARE_SIZE, d_east=0,
     altitude=FLIGHT_ALTITUDE, label="Titik C")
time.sleep(1)

# Titik D: 20m ke barat dari C (kembali ke kolom awal)
print(f"\n[6] Menuju Titik D ({SQUARE_SIZE}m Barat)...")
goto(vehicle, d_north=0, d_east=-SQUARE_SIZE,
     altitude=FLIGHT_ALTITUDE, label="Titik D / Start")
time.sleep(1)

# Landing
print("\n[7] Landing...")
switch_mode(vehicle, "LAND")
while vehicle.location.global_relative_frame.alt > 0.2:
    print(f"  Mendarat... {vehicle.location.global_relative_frame.alt:.2f}m")
    time.sleep(1)

print("\n[DONE] Misi pola kotak selesai.")
print(f"  Total rute: Start -> A -> B -> C -> D/Start -> Landing")
vehicle.close()