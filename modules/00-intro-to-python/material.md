# Modul 00 - Pengenalan Python

Modul ini membahas konsep-konsep Python yang paling sering digunakan dalam penulisan skrip DroneKit. Jika kamu sudah familiar dengan Python, gunakan modul ini sebagai bahan review.

---

## 1. Menjalankan File Python

Setelah virtual environment aktif, buat file dengan ekstensi `.py`, lalu jalankan dengan:

```bash
python nama_file.py
```

Contoh program pertama:

```python
print("Hello, Drone!")
```

---

## 2. Variabel dan Tipe Data

Python tidak memerlukan deklarasi tipe data secara eksplisit. Tipe ditentukan otomatis saat nilai diberikan.

```python
# Integer - bilangan bulat
target_altitude = 10

# Float - bilangan desimal
groundspeed = 3.5

# String - teks
vehicle_name = "Drone Alpha"

# Boolean - benar/salah
is_armed = False

print(target_altitude)   # 10
print(groundspeed)       # 3.5
print(vehicle_name)      # Drone Alpha
print(is_armed)          # False
```

---

## 3. Operasi Matematika

```python
a = 10
b = 3

print(a + b)    # 13  - penjumlahan
print(a - b)    # 7   - pengurangan
print(a * b)    # 30  - perkalian
print(a / b)    # 3.33 - pembagian
print(a // b)   # 3   - pembagian bulat
print(a % b)    # 1   - sisa bagi
print(a ** b)   # 1000 - perpangkatan
```

Operasi matematika lanjutan menggunakan modul `math`:

```python
import math

print(math.sqrt(25))           # 5.0 - akar kuadrat
print(math.radians(180))       # 3.14 - konversi derajat ke radian
print(math.cos(math.radians(0)))  # 1.0 - kosinus
```

---

## 4. String dan F-String

```python
nama = "IPB Robotic Club"
modul = 0

# Penggabungan string biasa
print("Selamat datang di " + nama)

# F-string (lebih direkomendasikan)
print(f"Selamat datang di {nama}, Modul {modul}")

# Format angka desimal
altitude = 10.567
print(f"Ketinggian saat ini: {altitude:.2f} meter")  # 10.57
```

---

## 5. Kondisional

```python
battery_level = 45

if battery_level > 50:
    print("Baterai cukup, siap terbang.")
elif battery_level > 20:
    print("Baterai rendah, segera landing.")
else:
    print("Baterai kritis, drone mendarat paksa.")
```

Kondisional juga bisa digabung dengan operator logika:

```python
is_armable = True
gps_fix = True

if is_armable and gps_fix:
    print("Drone siap dioperasikan.")

if not is_armable:
    print("Drone belum siap.")
```

---

## 6. While Loop

While loop mengulang blok kode selama kondisi bernilai `True`. Sangat sering digunakan di DroneKit untuk **menunggu kondisi tertentu**, misalnya menunggu drone mencapai ketinggian target.

```python
# Contoh sederhana
count = 0

while count < 5:
    print(f"Hitungan: {count}")
    count += 1

print("Selesai.")
```

Contoh yang mirip dengan pola di DroneKit:

```python
import time

current_altitude = 0
target_altitude = 10

# Simulasi drone naik
while current_altitude < target_altitude:
    current_altitude += 1
    print(f"Ketinggian: {current_altitude} meter")
    time.sleep(0.5)

print("Ketinggian target tercapai!")
```

Menggunakan `break` untuk keluar dari loop:

```python
while True:
    altitude = 8.7  # anggap ini dibaca dari sensor

    if altitude >= 10 * 0.95:  # 95% dari target
        print("Target tercapai, keluar dari loop.")
        break

    time.sleep(1)
```

---

## 7. For Loop

For loop mengulang sebanyak jumlah elemen yang sudah ditentukan.

```python
waypoints = ["Titik A", "Titik B", "Titik C", "Base"]

for point in waypoints:
    print(f"Menuju {point}...")
```

Menggunakan `range()`:

```python
# Countdown sebelum takeoff
for i in range(5, 0, -1):
    print(f"Takeoff dalam {i}...")
    time.sleep(1)

print("Takeoff!")
```

---

## 8. Fungsi (def)

Fungsi mengelompokkan blok kode yang bisa dipanggil berkali-kali. Dalam DroneKit, kita akan banyak membuat fungsi seperti `arm_and_takeoff()` dan `goto()`.

```python
# Fungsi tanpa nilai kembalian
def greet(name):
    print(f"Halo, {name}!")

greet("Budi")
greet("Siti")
```

Fungsi dengan nilai kembalian:

```python
def calculate_distance(x1, y1, x2, y2):
    import math
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

dist = calculate_distance(0, 0, 3, 4)
print(f"Jarak: {dist} meter")  # Jarak: 5.0 meter
```

Fungsi dengan parameter default:

```python
def arm_and_takeoff(vehicle, altitude=10):
    print(f"Takeoff ke {altitude} meter...")
    # kode lanjutan...

arm_and_takeoff(vehicle)        # menggunakan altitude default: 10
arm_and_takeoff(vehicle, 20)    # menggunakan altitude: 20
```

---

## 9. Import Library

```python
# Import seluruh modul
import time
import math

# Import fungsi/class tertentu saja
from dronekit import connect, VehicleMode, LocationGlobalRelative

# Penggunaan
time.sleep(2)                          # dari modul time
angle = math.radians(45)               # dari modul math
vehicle = connect('tcp:...')           # dari dronekit
```

---

## 10. List dan Iterasi

List digunakan untuk menyimpan banyak nilai dalam satu variabel.

```python
# Membuat list waypoint
waypoints = [
    (10, 0),    # 10 meter ke utara
    (10, 10),   # 10 meter ke utara, 10 meter ke timur
    (0, 10),    # 0 meter ke utara, 10 meter ke timur
    (0, 0),     # kembali ke asal
]

# Iterasi melalui waypoint
for north, east in waypoints:
    print(f"Menuju: North={north}m, East={east}m")
```

---

## 11. Komentar

Komentar sangat penting agar kode mudah dipahami orang lain (dan dirimu sendiri di masa depan).

```python
# Ini komentar satu baris

"""
Ini komentar
multi-baris,
biasa dipakai untuk dokumentasi fungsi.
"""

def connect_vehicle(connection_string):
    """
    Menghubungkan ke vehicle melalui connection string yang diberikan.

    Parameter:
        connection_string (str): Alamat koneksi, contoh 'tcp:127.0.0.1:5762'

    Return:
        Vehicle: Objek vehicle DroneKit
    """
    from dronekit import connect
    return connect(connection_string, wait_ready=True)
```

---

## Ringkasan

| Konsep | Kegunaan dalam DroneKit |
|--------|------------------------|
| Variabel | Menyimpan ketinggian, kecepatan, koordinat |
| `while` loop | Menunggu drone mencapai kondisi tertentu |
| `for` loop | Mengiterasi daftar waypoint |
| `def` fungsi | Membungkus logika `arm_and_takeoff()`, `goto()`, dll |
| `import` | Memuat library DroneKit, time, math |
| `time.sleep()` | Memberi jeda antar perintah ke drone |
| `math` | Menghitung jarak, offset koordinat GPS |

---

Lanjut ke [Modul 01 - Pengenalan DroneKit](../01-intro-to-dronekit/material.md)