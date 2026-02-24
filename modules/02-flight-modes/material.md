# Modul 02 - Flight Modes

---

## Apa itu Flight Mode?

Flight Mode adalah konfigurasi yang menentukan bagaimana autopilot (ArduPilot) mengontrol drone. Setiap mode memiliki perilaku berbeda - mulai dari kendali manual penuh oleh pilot, semi-otomatis, hingga otomatis penuh.

Dalam DroneKit, kita berpindah-pindah mode secara programatik sesuai kebutuhan misi.

```python
from dronekit import VehicleMode

# Mengubah mode
vehicle.mode = VehicleMode("GUIDED")

# Membaca mode saat ini
print(vehicle.mode.name)
```

---

## Mode-Mode Utama ArduCopter

### STABILIZE

Mode paling dasar. Pilot mengontrol penuh throttle, roll, pitch, dan yaw. Autopilot hanya menjaga agar drone tidak terbalik.

- GPS diperlukan: Tidak
- Ketinggian otomatis: Tidak
- Cocok untuk: Terbang manual, latihan dasar

```
Pilot gerak stik  ->  Drone mengikuti langsung
Autopilot         ->  Hanya menjaga keseimbangan
```

---

### ALT HOLD

Drone menjaga ketinggian secara otomatis menggunakan barometer. Pilot masih mengontrol arah horizontal dan yaw.

- GPS diperlukan: Tidak (menggunakan barometer)
- Ketinggian otomatis: Ya
- Cocok untuk: Terbang lebih stabil tanpa khawatir ketinggian berubah

```
Pilot lepas throttle  ->  Drone hover di ketinggian saat ini
Pilot gerak stik      ->  Drone bergerak horizontal
```

---

### LOITER

Drone menjaga **posisi GPS dan ketinggian** secara otomatis. Drone akan "diam di tempat" bahkan jika ada gangguan angin.

- GPS diperlukan: Ya
- Ketinggian otomatis: Ya
- Posisi otomatis: Ya
- Cocok untuk: Hover stabil di satu titik, pengambilan foto/video, menunggu perintah selanjutnya

```
Pilot lepas stik  ->  Drone diam di koordinat GPS saat ini
Pilot gerak stik  ->  Drone bergerak, berhenti dan hover lagi
```

LOITER menggunakan GPS dan barometer untuk mengunci posisi tiga dimensi (lintang, bujur, ketinggian) secara bersamaan.

```python
from dronekit import VehicleMode
import time

vehicle.mode = VehicleMode("LOITER")

while vehicle.mode.name != "LOITER":
    print("Menunggu mode LOITER...")
    time.sleep(1)

print("LOITER aktif - drone hover di posisi GPS saat ini")
print(f"Posisi: {vehicle.location.global_relative_frame}")

# Drone akan bertahan di posisi ini
time.sleep(10)

print("Melanjutkan misi...")
```

---

### GUIDED

Mode yang **wajib** digunakan untuk kendali via DroneKit. Drone mengikuti perintah yang diberikan oleh skrip Python.

- GPS diperlukan: Ya
- Cocok untuk: Semua skenario otomasi dengan DroneKit

```python
vehicle.simple_goto(target)       # Drone terbang ke target
vehicle.simple_takeoff(10)        # Drone naik ke 10 meter
```

> Drone tidak bisa arm dan takeoff jika tidak dalam mode GUIDED.

---

### AUTO

Drone menjalankan **misi waypoint yang sudah di-upload** ke flight controller. Misi berisi daftar titik beserta perintah di setiap titik.

- GPS diperlukan: Ya
- Cocok untuk: Misi inspeksi, pemetaan, pengiriman terjadwal

```python
# Upload misi terlebih dahulu, lalu:
vehicle.mode = VehicleMode("AUTO")
# Drone akan mengeksekusi misi secara otomatis
```

---

### RTL (Return to Launch)

Drone otomatis kembali ke titik launch (lokasi takeoff) dan mendarat di sana.

- GPS diperlukan: Ya
- Cocok untuk: Kondisi darurat, baterai rendah, kehilangan sinyal

```python
vehicle.mode = VehicleMode("RTL")
# Drone akan naik ke ketinggian RTL, kembali ke home, lalu landing otomatis
```

---

### LAND

Drone mendarat secara vertikal di posisi saat ini.

- GPS diperlukan: Tidak wajib
- Cocok untuk: Mengakhiri misi, landing darurat

```python
vehicle.mode = VehicleMode("LAND")

while vehicle.location.global_relative_frame.alt > 0.2:
    print(f"Mendarat... {vehicle.location.global_relative_frame.alt:.2f} m")
    time.sleep(1)

print("Drone telah mendarat.")
```

---

### BRAKE

Drone berhenti mendadak dan hover di posisi saat ini. Berguna saat drone sedang bergerak dan perlu dihentikan secara cepat.

- GPS diperlukan: Ya
- Cocok untuk: Penghentian darurat saat drone bergerak

```python
vehicle.mode = VehicleMode("BRAKE")
# Drone akan menghentikan semua gerakan dan hover di tempat
```

---

## Perbandingan Singkat

| Mode | GPS | Alt Otomatis | Posisi Otomatis | Kendali Utama |
|------|:---:|:------------:|:---------------:|---------------|
| STABILIZE | - | - | - | Pilot penuh |
| ALT HOLD | - | Barometer | - | Pilot (horizontal) |
| LOITER | Ya | Ya | Ya | Semi-otomatis |
| GUIDED | Ya | Ya | Ya | Skrip Python |
| AUTO | Ya | Ya | Ya | Misi waypoint |
| RTL | Ya | Ya | Ya | Otomatis penuh |
| LAND | - | Turun saja | - | Otomatis penuh |
| BRAKE | Ya | Ya | Ya | Otomatis (berhenti) |

---

## Fungsi Helper: switch_mode()

Daripada menulis kode menunggu konfirmasi mode setiap saat, lebih baik buat fungsi helper:

```python
import time
from dronekit import VehicleMode

def switch_mode(vehicle, mode_name, timeout=10):
    """
    Berpindah ke mode tertentu dan menunggu konfirmasi dari flight controller.

    Parameter:
        vehicle   : objek Vehicle DroneKit
        mode_name : str - nama mode (contoh: "GUIDED", "LOITER", "LAND")
        timeout   : int - batas waktu menunggu konfirmasi dalam detik

    Return:
        bool - True jika berhasil, False jika timeout
    """
    vehicle.mode = VehicleMode(mode_name)
    start_time = time.time()

    while vehicle.mode.name != mode_name:
        if time.time() - start_time > timeout:
            print(f"Timeout: gagal berpindah ke mode {mode_name}")
            return False
        time.sleep(0.5)

    print(f"Mode aktif: {mode_name}")
    return True
```

Penggunaan:

```python
switch_mode(vehicle, "GUIDED")
# ... navigasi ...
switch_mode(vehicle, "LOITER")
time.sleep(10)
switch_mode(vehicle, "GUIDED")
# ... navigasi lanjutan ...
switch_mode(vehicle, "LAND")
```

---

## Pola Perpindahan Mode dalam Misi

Pola perpindahan mode yang umum digunakan dalam skrip DroneKit:

```
GUIDED  ->  Arm dan Takeoff
GUIDED  ->  Navigasi ke waypoint
LOITER  ->  Hover stabil di titik tertentu
GUIDED  ->  Lanjut ke waypoint berikutnya
LAND    ->  Mengakhiri misi
```

---

## Deep Dive: LOITER vs GUIDED saat Diam

Sering muncul pertanyaan: kalau drone bisa diam di mode GUIDED, kenapa perlu LOITER?

| Aspek | GUIDED (diam) | LOITER |
|-------|:-------------:|:------:|
| Cara kerja | Drone menahan posisi terakhir dari `simple_goto()` | FC mengunci koordinat GPS secara aktif dan terus-menerus |
| Stabilitas terhadap angin | Kurang stabil, bisa drift | Lebih stabil, aktif mengoreksi drift |
| Dapat dikontrol stik RC | Tidak | Ya |
| Konsumsi baterai | Serupa | Serupa |
| Rekomendasi penggunaan | Saat dalam misi otomatis | Saat perlu hover berkualitas tinggi atau menunggu lama |

Kesimpulan: gunakan **LOITER** ketika drone perlu hover diam cukup lama di satu titik, misalnya saat mengambil foto/video atau menunggu kondisi tertentu.

---

## Ringkasan

- **STABILIZE**: manual penuh, tanpa GPS, mode paling dasar
- **ALT HOLD**: ketinggian dikunci barometer, arah masih manual
- **LOITER**: posisi dan ketinggian dikunci GPS, hover stabil
- **GUIDED**: dikendalikan penuh oleh skrip Python
- **AUTO**: menjalankan misi waypoint yang diupload
- **RTL**: kembali otomatis ke titik launch
- **LAND**: mendarat vertikal di posisi saat ini
- **BRAKE**: berhenti mendadak dan hover

Dalam bootcamp ini, mode yang paling sering digunakan adalah **GUIDED**, **LOITER**, dan **LAND**.

---

Lihat contoh kode di:
- [examples/mode_switching.py](./examples/mode_switching.py)
- [examples/loiter_hover.py](./examples/loiter_hover.py)

Lanjut ke [Modul 03 - Simulasi Misi](../03-mission/material.md)