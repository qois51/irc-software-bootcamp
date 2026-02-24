"""
03_multi_waypoint.py
--------------------
Misi multi-waypoint menggunakan daftar (list) titik tujuan.
Drone mengunjungi setiap waypoint secara berurutan kemudian landing.

Pendekatan ini lebih fleksibel karena waypoint bisa dengan mudah
ditambah, diubah, atau diatur ulang hanya dengan memodifikasi daftar.

Alur misi:
  Takeoff -> WP1 -> WP2 -> WP3 -> WP4 -> WP5 -> Landing

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


def execute_waypoints(vehicle, waypoints, default_threshold=1.5):
    """
    Mengeksekusi daftar waypoint secara berurutan.

    Setiap waypoint adalah dictionary dengan key:
        name      : str   - nama titik untuk log (wajib)
        d_north   : float - offset ke utara dalam meter (wajib)
        d_east    : float - offset ke timur dalam meter (wajib)
        altitude  : float - ketinggian terbang dalam meter (wajib)
        hover     : float - durasi diam di titik ini dalam detik (opsional, default 0)
        threshold : float - jarak tiba dalam meter (opsional)

    Parameter:
        vehicle   : objek Vehicle DroneKit
        waypoints : list of dict - daftar waypoint
        default_threshold : float - threshold default jika tidak ditentukan per waypoint
    """
    total = len(waypoints)
    print(f"[INFO] Memulai eksekusi {total} waypoint...")

    for i, wp in enumerate(waypoints, start=1):
        name      = wp.get("name", f"WP{i}")
        d_north   = wp["d_north"]
        d_east    = wp["d_east"]
        altitude  = wp["altitude"]
        hover     = wp.get("hover", 0)
        threshold = wp.get("threshold", default_threshold)

        print(f"\n[WP {i}/{total}] {name}")
        print(f"  Target: N={d_north:+.1f}m, E={d_east:+.1f}m, Alt={altitude}m")

        if vehicle.mode.name != "GUIDED":
            switch_mode(vehicle, "GUIDED")

        current = vehicle.location.global_relative_frame
        target = get_offset_location(current, d_north, d_east, altitude)

        vehicle.simple_goto(target)

        while True:
            dist = get_distance(vehicle.location.global_relative_frame, target)
            alt = vehicle.location.global_relative_frame.alt
            print(f"  Jarak: {dist:.1f}m | Alt: {alt:.2f}m")
            if dist <= threshold:
                print(f"  Tiba di {name}")
                break
            time.sleep(1)

        # Hover sebentar jika ditentukan
        if hover > 0:
            print(f"  Hover {hover} detik di {name}...")
            time.sleep(hover)

    print("\n[INFO] Semua waypoint selesai dieksekusi.")


# --- Definisi Waypoint ---
#
# Setiap waypoint menggunakan koordinat RELATIF terhadap posisi saat ini
# pada saat waypoint tersebut dieksekusi.
#
# Jika ingin waypoint relatif terhadap posisi LAUNCH (titik takeoff),
# kamu perlu menghitung offset kumulatif secara manual.
#
# Contoh rute di bawah membentuk pola bintang sederhana:
#
#         WP2
#          |
#  WP3 - Start - WP1
#          |
#         WP4
#          |
#         WP5

WAYPOINTS = [
    {
        "name": "WP1 - Timur",
        "d_north": 0,
        "d_east": 25,
        "altitude": 10,
        "hover": 2,
    },
    {
        "name": "WP2 - Timur Laut",
        "d_north": 15,
        "d_east": -10,  # relatif dari WP1
        "altitude": 12,
        "hover": 2,
    },
    {
        "name": "WP3 - Barat Laut",
        "d_north": 0,
        "d_east": -30,  # relatif dari WP2
        "altitude": 15,
        "hover": 3,
    },
    {
        "name": "WP4 - Selatan",
        "d_north": -20,
        "d_east": 5,    # relatif dari WP3
        "altitude": 12,
        "hover": 2,
    },
    {
        "name": "WP5 - Kembali ke Asal",
        "d_north": 5,
        "d_east": 10,   # relatif dari WP4, menuju dekat launch
        "altitude": 10,
        "hover": 0,
    },
]

# --- Main Program ---

print("=" * 55)
print("  03 Multi-Waypoint Mission")
print(f"  {len(WAYPOINTS)} waypoint akan dikunjungi")
print("=" * 55)

print("\nDaftar waypoint:")
for i, wp in enumerate(WAYPOINTS, start=1):
    print(f"  {i}. {wp['name']} | Alt: {wp['altitude']}m | Hover: {wp.get('hover', 0)}s")

print("\n[1] Koneksi ke SITL...")
vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)
print(f"    Terhubung. Mode: {vehicle.mode.name}")

print("\n[2] Arm dan Takeoff ke 10m...")
arm_and_takeoff(vehicle, target_altitude=10)

print("\n[3] Eksekusi waypoint...")
execute_waypoints(vehicle, WAYPOINTS)

print("\n[4] Landing...")
switch_mode(vehicle, "LAND")
while vehicle.location.global_relative_frame.alt > 0.2:
    print(f"  Mendarat... {vehicle.location.global_relative_frame.alt:.2f}m")
    time.sleep(1)

print("\n[DONE] Misi multi-waypoint selesai.")
vehicle.close()