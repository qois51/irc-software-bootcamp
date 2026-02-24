# Modul 03 - Simulasi Misi

---

## Overview

Modul ini menggabungkan semua yang sudah dipelajari untuk membuat skrip simulasi misi penerbangan drone yang lengkap. Kita akan mempelajari fungsi-fungsi helper yang sering dipakai, cara menyusun misi, dan berbagai pola terbang.

Pastikan sudah memahami [Modul 02 - Flight Modes](../02-flight-modes/material.md) sebelum melanjutkan.

---

## Fungsi-Fungsi Penting

Dalam membuat skrip misi, ada beberapa fungsi yang hampir selalu dibutuhkan. Sebaiknya fungsi-fungsi ini ditulis di awal skrip agar bisa digunakan berulang kali.

### switch_mode()

```python
def switch_mode(vehicle, mode_name, timeout=10):
    """
    Berpindah ke mode tertentu dan menunggu konfirmasi flight controller.

    Parameter:
        vehicle   : objek Vehicle DroneKit
        mode_name : str - nama mode tujuan
        timeout   : int - batas waktu tunggu dalam detik

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
```

### arm_and_takeoff()

```python
def arm_and_takeoff(vehicle, target_altitude):
    """
    Menunggu drone siap, melakukan arm, dan takeoff ke ketinggian target.

    Parameter:
        vehicle         : objek Vehicle DroneKit
        target_altitude : float - ketinggian target dalam meter
    """
    print("[INFO] Menunggu drone siap...")
    while not vehicle.is_armable:
        time.sleep(1)

    switch_mode(vehicle, "GUIDED")

    vehicle.armed = True
    while not vehicle.armed:
        print("  Menunggu arm...")
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
```

### get_offset_location()

Fungsi ini mengkonversi offset meter (utara/timur) menjadi koordinat GPS baru. Ini diperlukan karena `simple_goto()` membutuhkan koordinat GPS, bukan offset meter.

```python
def get_offset_location(original, d_north, d_east, alt):
    """
    Menghitung koordinat GPS baru berdasarkan offset dari posisi saat ini.

    Parameter:
        original : LocationGlobalRelative - posisi asal
        d_north  : float - offset ke utara dalam meter (negatif = selatan)
        d_east   : float - offset ke timur dalam meter (negatif = barat)
        alt      : float - ketinggian target dalam meter

    Return:
        LocationGlobalRelative - koordinat GPS target
    """
    earth_radius = 6378137.0
    d_lat = d_north / earth_radius
    d_lon = d_east / (earth_radius * math.cos(math.radians(original.lat)))
    new_lat = original.lat + math.degrees(d_lat)
    new_lon = original.lon + math.degrees(d_lon)
    return LocationGlobalRelative(new_lat, new_lon, alt)
```

### get_distance()

```python
def get_distance(loc1, loc2):
    """
    Menghitung jarak dalam meter antara dua koordinat GPS.

    Parameter:
        loc1, loc2 : LocationGlobalRelative

    Return:
        float - jarak dalam meter
    """
    d_lat = loc2.lat - loc1.lat
    d_lon = loc2.lon - loc1.lon
    return math.sqrt(d_lat ** 2 + d_lon ** 2) * 1.113195e5
```

### goto()

```python
def goto(vehicle, d_north, d_east, altitude, label="target", threshold=1.5):
    """
    Menggerakkan drone ke titik offset dari posisi saat ini dan menunggu
    hingga drone tiba di titik tersebut.

    Parameter:
        vehicle   : objek Vehicle DroneKit
        d_north   : float - offset ke utara dalam meter
        d_east    : float - offset ke timur dalam meter
        altitude  : float - ketinggian terbang dalam meter
        label     : str   - nama titik untuk log
        threshold : float - jarak (meter) untuk dianggap sudah tiba
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
```

---

## Pola Terbang yang Bisa Dibuat

Dengan mengkombinasikan `goto()` dan offset utara/timur, berbagai pola terbang bisa dibuat:

### Pola Lurus (Maju-Mundur)
```
Start -> (maju) -> A -> (mundur) -> Start -> Landing
```

### Pola Kotak
```
Start
  |
  A ---- B
         |
  D ---- C
```
Dilakukan dengan kombinasi offset utara dan timur secara berurutan.

### Pola Segitiga
```
Start
  |  \
  A    C
  |   /
  B--
```

### Pola Zigzag
```
Start -> A -> B -> C -> D -> ...
         (alternasi utara-timur dan utara-barat)
```

### Variasi Ketinggian
Drone bisa terbang di ketinggian yang berbeda di setiap waypoint dengan mengubah parameter `altitude` pada setiap pemanggilan `goto()`.

---

## Contoh Misi yang Tersedia

| File | Deskripsi |
|------|-----------|
| [01_basic_mission.py](./examples/01_basic_mission.py) | Misi dasar: takeoff, maju, mundur, landing |
| [02_square_pattern.py](./examples/02_square_pattern.py) | Pola terbang kotak 20x20 meter |
| [03_multi_waypoint.py](./examples/03_multi_waypoint.py) | Navigasi multi-waypoint dengan daftar titik |
| [04_loiter_mission.py](./examples/04_loiter_mission.py) | Misi dengan LOITER di setiap titik waypoint |
| [05_altitude_change.py](./examples/05_altitude_change.py) | Misi dengan perubahan ketinggian di setiap titik |

---

## Template Misi

Berikut adalah template dasar yang bisa kamu jadikan titik awal membuat skrip misi sendiri:

```python
import time
import math
from dronekit import connect, VehicleMode, LocationGlobalRelative


def switch_mode(vehicle, mode_name, timeout=10):
    vehicle.mode = VehicleMode(mode_name)
    start = time.time()
    while vehicle.mode.name != mode_name:
        if time.time() - start > timeout:
            return False
        time.sleep(0.5)
    print(f"[MODE] {mode_name}")
    return True


def arm_and_takeoff(vehicle, target_altitude):
    while not vehicle.is_armable:
        time.sleep(1)
    switch_mode(vehicle, "GUIDED")
    vehicle.armed = True
    while not vehicle.armed:
        time.sleep(1)
    vehicle.simple_takeoff(target_altitude)
    while vehicle.location.global_relative_frame.alt < target_altitude * 0.95:
        time.sleep(1)
    print(f"[INFO] Ketinggian {target_altitude}m tercapai")


def get_offset_location(original, d_north, d_east, alt):
    earth_radius = 6378137.0
    d_lat = d_north / earth_radius
    d_lon = d_east / (earth_radius * math.cos(math.radians(original.lat)))
    return LocationGlobalRelative(
        original.lat + math.degrees(d_lat),
        original.lon + math.degrees(d_lon),
        alt
    )


def get_distance(loc1, loc2):
    d_lat = loc2.lat - loc1.lat
    d_lon = loc2.lon - loc1.lon
    return math.sqrt(d_lat ** 2 + d_lon ** 2) * 1.113195e5


def goto(vehicle, d_north, d_east, altitude, label="target", threshold=1.5):
    if vehicle.mode.name != "GUIDED":
        switch_mode(vehicle, "GUIDED")
    current = vehicle.location.global_relative_frame
    target = get_offset_location(current, d_north, d_east, altitude)
    print(f"[NAV] Menuju {label}...")
    vehicle.simple_goto(target)
    while True:
        dist = get_distance(vehicle.location.global_relative_frame, target)
        if dist <= threshold:
            print(f"[NAV] Tiba di {label}")
            break
        time.sleep(1)


# --- Kode Misi Kamu di Sini ---

vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)

arm_and_takeoff(vehicle, target_altitude=10)

# Tambahkan perintah misi di sini
# goto(vehicle, d_north=20, d_east=0, altitude=10, label="Titik A")
# ...

switch_mode(vehicle, "LAND")
while vehicle.location.global_relative_frame.alt > 0.2:
    time.sleep(1)

print("[DONE] Misi selesai.")
vehicle.close()
```

---

## Ringkasan Alur Misi

```
1. connect()          - hubungkan ke SITL
2. arm_and_takeoff()  - arm dan naik ke ketinggian awal
3. goto() / loiter    - navigasi ke waypoint-waypoint
4. LAND / RTL         - mengakhiri misi
5. vehicle.close()    - tutup koneksi
```