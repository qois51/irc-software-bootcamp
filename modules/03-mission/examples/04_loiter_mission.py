"""
04_loiter_mission.py
--------------------
Misi dengan LOITER di setiap titik waypoint.
Drone terbang dalam pola segitiga dan hover di setiap sudut.

Pola misi:
  Start/Landing
      |
      A
     / \
    B   C

  A = puncak segitiga (30m Utara)
  B = kiri bawah (15m Selatan, 20m Barat dari A)
  C = kanan bawah (15m Selatan, 20m Timur dari A)

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


def fly_to(vehicle, d_north, d_east, altitude, label, threshold=1.5):
    """Terbang ke titik offset dalam mode GUIDED dan tunggu hingga tiba."""
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


def loiter_at_current(vehicle, duration, label=""):
    """
    Beralih ke mode LOITER dan hover di posisi saat ini selama durasi tertentu.

    Parameter:
        vehicle  : objek Vehicle DroneKit
        duration : int - durasi hover dalam detik
        label    : str - nama titik untuk log
    """
    switch_mode(vehicle, "LOITER")
    pos = vehicle.location.global_relative_frame
    print(f"[LOITER] Hover di {label if label else 'posisi saat ini'} selama {duration}s")
    print(f"  Posisi terkunci: lat={pos.lat:.6f}, lon={pos.lon:.6f}, alt={pos.alt:.2f}m")

    for i in range(duration, 0, -1):
        alt = vehicle.location.global_relative_frame.alt
        print(f"  {i}s tersisa | Alt: {alt:.2f}m")
        time.sleep(1)

    print(f"[LOITER] Selesai di {label}")


# --- Main Program ---

FLIGHT_ALTITUDE = 12
LOITER_DURATION = 10  # detik hover di setiap titik

print("=" * 55)
print("  04 Loiter Mission - Pola Segitiga")
print(f"  Ketinggian: {FLIGHT_ALTITUDE}m | Hover per titik: {LOITER_DURATION}s")
print("=" * 55)

print("""
  Pola terbang (Segitiga):
      Start/Landing
           |
           A  (30m Utara)
          / \\
         B   C
  (15m S, 20m W dari A)  (15m S, 20m E dari A)
""")

print("[1] Koneksi ke SITL...")
vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)
print(f"    Terhubung. Mode: {vehicle.mode.name}")

print(f"\n[2] Arm dan Takeoff ke {FLIGHT_ALTITUDE}m...")
arm_and_takeoff(vehicle, target_altitude=FLIGHT_ALTITUDE)

# Titik A: puncak segitiga, 30m ke utara dari start
print("\n[3] Menuju Titik A (puncak)...")
fly_to(vehicle, d_north=30, d_east=0, altitude=FLIGHT_ALTITUDE, label="Titik A")
loiter_at_current(vehicle, LOITER_DURATION, label="Titik A")

# Titik B: sudut kiri bawah, 15m selatan dan 20m barat dari A
print("\n[4] Menuju Titik B (kiri)...")
fly_to(vehicle, d_north=-15, d_east=-20, altitude=FLIGHT_ALTITUDE, label="Titik B")
loiter_at_current(vehicle, LOITER_DURATION, label="Titik B")

# Titik C: sudut kanan bawah, lurus 40m ke timur dari B
print("\n[5] Menuju Titik C (kanan)...")
fly_to(vehicle, d_north=0, d_east=40, altitude=FLIGHT_ALTITUDE, label="Titik C")
loiter_at_current(vehicle, LOITER_DURATION, label="Titik C")

# Kembali ke sekitar titik start
print("\n[6] Kembali ke titik awal...")
fly_to(vehicle, d_north=15, d_east=-20, altitude=FLIGHT_ALTITUDE, label="Titik Start")
time.sleep(2)

# Landing
print("\n[7] Landing...")
switch_mode(vehicle, "LAND")
while vehicle.location.global_relative_frame.alt > 0.2:
    print(f"  Mendarat... {vehicle.location.global_relative_frame.alt:.2f}m")
    time.sleep(1)

print("\n[DONE] Misi segitiga dengan LOITER selesai.")
print(f"  Rute: Takeoff -> A [LOITER] -> B [LOITER] -> C [LOITER] -> Landing")
vehicle.close()