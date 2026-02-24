"""
05_altitude_change.py
---------------------
Misi dengan perubahan ketinggian di setiap waypoint.
Drone terbang dalam pola zigzag sambil naik dan turun ketinggian,
mensimulasikan skenario inspeksi di berbagai ketinggian.

Profil ketinggian:
  Start (ground)
    -> Takeoff ke 8m
    -> WP1 (8m)  -> WP2 (15m) -> WP3 (10m)
    -> WP4 (20m) -> WP5 (12m) -> WP6 (8m)
    -> Landing

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


def goto_with_altitude(vehicle, d_north, d_east, target_alt, label, threshold=1.5):
    """
    Terbang ke titik offset pada ketinggian yang ditentukan.
    Menampilkan informasi ketinggian saat ini vs target secara real-time.

    Parameter:
        vehicle    : objek Vehicle DroneKit
        d_north    : float - offset ke utara (meter)
        d_east     : float - offset ke timur (meter)
        target_alt : float - ketinggian target (meter)
        label      : str   - nama titik untuk log
        threshold  : float - jarak tiba dalam meter
    """
    if vehicle.mode.name != "GUIDED":
        switch_mode(vehicle, "GUIDED")

    current = vehicle.location.global_relative_frame
    target = get_offset_location(current, d_north, d_east, target_alt)

    print(f"[NAV] Menuju {label} | Alt target: {target_alt}m...")
    vehicle.simple_goto(target)

    while True:
        dist = get_distance(vehicle.location.global_relative_frame, target)
        alt = vehicle.location.global_relative_frame.alt
        print(f"  Jarak: {dist:.1f}m | Alt: {alt:.2f}m -> target: {target_alt}m")
        if dist <= threshold:
            print(f"[NAV] Tiba di {label} | Alt akhir: {alt:.2f}m")
            break
        time.sleep(1)


# --- Definisi Waypoint dengan Ketinggian Berbeda ---
#
# Kolom: (d_north, d_east, altitude, nama)
# Offset adalah RELATIF terhadap posisi SAAT ITU (bukan dari launch point).
#
# Rute:
#   Takeoff (8m) -> WP1 (8m) -> WP2 (15m) -> WP3 (10m)
#               -> WP4 (20m) -> WP5 (12m)  -> WP6 (8m)

MISSION_WAYPOINTS = [
    # (d_north, d_east, altitude, label)
    (15,  0,   8,  "WP1 - Rendah"),
    (15,  5,  15,  "WP2 - Tinggi"),
    (15, -5,  10,  "WP3 - Sedang"),
    (15,  5,  20,  "WP4 - Tertinggi"),
    (15, -5,  12,  "WP5 - Sedang"),
    (15,  0,   8,  "WP6 - Rendah, kembali ke barat"),
]

# --- Main Program ---

print("=" * 60)
print("  05 Altitude Change Mission")
print("  Misi zigzag dengan variasi ketinggian di setiap waypoint")
print("=" * 60)

print("\nProfil ketinggian misi:")
print("  Takeoff")
alts = [wp[2] for wp in MISSION_WAYPOINTS]
for i, (_, _, alt, label) in enumerate(MISSION_WAYPOINTS, start=1):
    bar = "#" * int(alt / 2)
    print(f"  {label:30s} {alt:3d}m  {bar}")

print("\n[1] Koneksi ke SITL...")
vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)
print(f"    Terhubung. Mode: {vehicle.mode.name}")

print("\n[2] Arm dan Takeoff ke 8m...")
arm_and_takeoff(vehicle, target_altitude=8)

print(f"\n[3] Eksekusi {len(MISSION_WAYPOINTS)} waypoint dengan variasi ketinggian...")

for i, (d_north, d_east, altitude, label) in enumerate(MISSION_WAYPOINTS, start=1):
    print(f"\n  --- Waypoint {i}/{len(MISSION_WAYPOINTS)} ---")
    goto_with_altitude(vehicle, d_north, d_east, altitude, label)
    time.sleep(2)

# Landing
print("\n[4] Landing...")
switch_mode(vehicle, "LAND")
while vehicle.location.global_relative_frame.alt > 0.2:
    print(f"  Mendarat... {vehicle.location.global_relative_frame.alt:.2f}m")
    time.sleep(1)

print("\n[DONE] Misi altitude change selesai.")
print("  Ketinggian yang dilalui:", " -> ".join(f"{wp[2]}m" for wp in MISSION_WAYPOINTS))
vehicle.close()