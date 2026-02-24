# Modul 01 - Pengenalan DroneKit dan Koneksi SITL

---

## Apa itu DroneKit?

DroneKit adalah library Python open-source yang dikembangkan oleh 3DR untuk berkomunikasi dengan drone berbasis **ArduPilot** menggunakan protokol komunikasi bernama **MAVLink**.

Dengan DroneKit, kita dapat:
- Mengontrol drone secara programatik (arm, takeoff, navigasi, landing)
- Membaca data sensor (GPS, baterai, attitude, kecepatan)
- Membuat dan mengeksekusi misi otomatis
- Melakukan simulasi sebelum terbang dengan drone nyata

```
Kode Python (DroneKit)
        |
   Protokol MAVLink
        |
  ArduPilot (Autopilot Firmware)
        |
   Drone Fisik  /  SITL Simulator
```

---

## Apa itu SITL?

**SITL (Software In The Loop)** adalah simulator yang menjalankan firmware ArduPilot langsung di dalam komputer, tanpa memerlukan hardware drone fisik. SITL memungkinkan kita:

- Menguji skrip sebelum diterbangkan ke drone nyata
- Belajar tanpa risiko kerusakan hardware
- Melakukan debugging dengan aman

Mission Planner menyediakan fitur SITL bawaan yang bisa langsung digunakan.

---

## Menjalankan SITL di Mission Planner

1. Buka **Mission Planner**
2. Klik tab **Simulation** di toolbar atas
3. Pilih jenis drone: **Multirotor**
4. Klik **Start** - simulator akan mulai berjalan
5. Mission Planner akan otomatis terhubung ke SITL
6. SITL berjalan dan dapat diakses pada alamat: `tcp:127.0.0.1:5762`

> Biarkan Mission Planner tetap terbuka saat menjalankan skrip Python.

---

## Koneksi ke SITL

### Koneksi Dasar

```python
from dronekit import connect

# Hubungkan ke SITL Mission Planner
# wait_ready=True berarti program menunggu hingga semua data vehicle siap
vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)

print("Berhasil terhubung ke drone!")

vehicle.close()
```

### Membaca Informasi Vehicle

```python
from dronekit import connect

vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)

print(f"Mode saat ini  : {vehicle.mode.name}")
print(f"Status armed   : {vehicle.armed}")
print(f"Siap di-arm    : {vehicle.is_armable}")
print(f"Lokasi GPS     : {vehicle.location.global_relative_frame}")
print(f"Ketinggian     : {vehicle.location.global_relative_frame.alt} m")
print(f"Heading        : {vehicle.heading} derajat")
print(f"Groundspeed    : {vehicle.groundspeed} m/s")
print(f"Baterai        : {vehicle.battery}")
print(f"Status GPS     : {vehicle.gps_0}")
print(f"Attitude       : {vehicle.attitude}")

vehicle.close()
```

---

## Atribut Vehicle

Setelah terhubung, semua informasi drone dapat diakses melalui objek `vehicle`:

### Lokasi

| Atribut | Deskripsi |
|---------|-----------|
| `vehicle.location.global_frame` | Koordinat GPS absolut (lat, lon, alt AMSL) |
| `vehicle.location.global_relative_frame` | Koordinat GPS dengan altitude relatif terhadap titik launch |
| `vehicle.location.local_frame` | Koordinat lokal (north, east, down) |

```python
loc = vehicle.location.global_relative_frame
print(f"Latitude  : {loc.lat}")
print(f"Longitude : {loc.lon}")
print(f"Altitude  : {loc.alt} m")  # relatif dari titik launch
```

### Status dan Sensor

| Atribut | Deskripsi | Contoh |
|---------|-----------|--------|
| `vehicle.mode` | Mode terbang saat ini | `VehicleMode("GUIDED")` |
| `vehicle.armed` | Status arm motor | `True` / `False` |
| `vehicle.is_armable` | Apakah drone siap di-arm | `True` / `False` |
| `vehicle.attitude` | Orientasi drone (roll, pitch, yaw) dalam radian | `Attitude(...)` |
| `vehicle.velocity` | Vektor kecepatan [vx, vy, vz] dalam m/s | `[0.1, 0.0, -0.5]` |
| `vehicle.groundspeed` | Kecepatan horizontal (m/s) | `3.5` |
| `vehicle.airspeed` | Kecepatan relatif terhadap udara (m/s) | `3.5` |
| `vehicle.heading` | Arah hadap drone (0-360 derajat) | `90` |
| `vehicle.battery` | Status baterai (voltage, current, level) | `Battery(...)` |
| `vehicle.gps_0` | Status GPS (fix_type, jumlah satelit) | `GPSInfo(...)` |

### Parameter GPS Fix Type

| Nilai | Arti |
|-------|------|
| 0 | Tidak ada GPS |
| 1 | No Fix |
| 2 | 2D Fix |
| 3 | 3D Fix (minimal untuk terbang) |

```python
gps = vehicle.gps_0
print(f"Fix type  : {gps.fix_type}")    # minimal 3 untuk bisa arm
print(f"Satelit   : {gps.satellites_visible}")
```

---

## Vehicle Mode

Mode menentukan bagaimana ArduPilot mengontrol drone:

| Mode | Deskripsi |
|------|-----------|
| `GUIDED` | Dikendalikan penuh oleh skrip Python - wajib untuk DroneKit |
| `STABILIZE` | Stabil manual oleh pilot |
| `ALT_HOLD` | Ketinggian dikunci otomatis |
| `LOITER` | Posisi dan ketinggian dikunci via GPS |
| `AUTO` | Menjalankan misi waypoint yang diupload |
| `LAND` | Mendarat vertikal di posisi saat ini |
| `RTL` | Return to Launch - kembali ke titik takeoff |
| `BRAKE` | Berhenti mendadak dan hover |

Mengubah mode:

```python
from dronekit import VehicleMode
import time

vehicle.mode = VehicleMode("GUIDED")

# Tunggu konfirmasi dari flight controller
while vehicle.mode.name != "GUIDED":
    print("Menunggu mode GUIDED...")
    time.sleep(1)

print(f"Mode aktif: {vehicle.mode.name}")
```

---

## Arm dan Disarm

```python
import time

# Pastikan drone sudah siap sebelum arm
print("Menunggu drone siap...")
while not vehicle.is_armable:
    print(f"  is_armable: {vehicle.is_armable}, GPS fix: {vehicle.gps_0.fix_type}")
    time.sleep(1)

# Set mode GUIDED (wajib sebelum arm via DroneKit)
vehicle.mode = VehicleMode("GUIDED")
while vehicle.mode.name != "GUIDED":
    time.sleep(0.5)

# Arm
vehicle.armed = True
while not vehicle.armed:
    print("Menunggu arm...")
    time.sleep(1)

print("Drone ter-arm!")

# ... lakukan sesuatu ...

# Disarm setelah selesai
vehicle.armed = False
print("Drone di-disarm.")
```

> `is_armable` akan bernilai `True` ketika GPS sudah mendapat fix yang cukup dan tidak ada error pada sensor.

---

## Simple Takeoff

```python
target_altitude = 10  # meter

vehicle.simple_takeoff(target_altitude)

# Tunggu hingga drone mencapai ~95% dari target ketinggian
while True:
    current_alt = vehicle.location.global_relative_frame.alt
    print(f"Ketinggian: {current_alt:.2f} m")

    if current_alt >= target_altitude * 0.95:
        print("Target ketinggian tercapai.")
        break

    time.sleep(1)
```

> `simple_takeoff()` hanya bekerja saat drone sudah **armed** dan dalam mode **GUIDED**.

---

## Contoh Lengkap: Connect, Arm, Takeoff, Land

```python
import time
from dronekit import connect, VehicleMode

# Koneksi
print("Menghubungkan ke SITL...")
vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)
print(f"Terhubung. Mode: {vehicle.mode.name}")

# Tunggu siap
print("Menunggu drone siap...")
while not vehicle.is_armable:
    time.sleep(1)

# Set mode GUIDED
vehicle.mode = VehicleMode("GUIDED")
while vehicle.mode.name != "GUIDED":
    time.sleep(0.5)

# Arm
vehicle.armed = True
while not vehicle.armed:
    time.sleep(1)
print("Drone ter-arm.")

# Takeoff
target_alt = 10
vehicle.simple_takeoff(target_alt)
while True:
    alt = vehicle.location.global_relative_frame.alt
    print(f"Naik... {alt:.2f} m")
    if alt >= target_alt * 0.95:
        print("Ketinggian tercapai.")
        break
    time.sleep(1)

# Hover sebentar
print("Hover 5 detik...")
time.sleep(5)

# Landing
print("Landing...")
vehicle.mode = VehicleMode("LAND")
while vehicle.location.global_relative_frame.alt > 0.2:
    print(f"Mendarat... {vehicle.location.global_relative_frame.alt:.2f} m")
    time.sleep(1)

print("Drone mendarat.")
vehicle.close()
```

---

## Ringkasan

- DroneKit berkomunikasi dengan drone via protokol **MAVLink**
- SITL memungkinkan simulasi lengkap tanpa hardware
- Koneksi menggunakan `connect(connection_string, wait_ready=True)`
- Objek `vehicle` adalah antarmuka utama ke semua fungsi kendali drone
- Sebelum arm, drone harus dalam mode **GUIDED** dan `is_armable` harus `True`

---

Lanjut ke [Modul 02 - Flight Modes](../02-flight-modes/material.md)