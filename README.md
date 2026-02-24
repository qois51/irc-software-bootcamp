# IRC Software Bootcamp

**IPB Robotic Club - VTOL Divisi Software**

Repository ini berisi seluruh materi, contoh kode, dan informasi penugasan untuk Bootcamp Software VTOL IPB Robotic Club. Peserta akan mempelajari dasar Python hingga membuat simulasi penerbangan drone menggunakan DroneKit dan Mission Planner SITL.

---

## Daftar Modul

| Modul | Judul | Deskripsi |
|-------|-------|-----------|
| 00 | [Pengenalan Python](./modules/00-intro-to-python/material.md) | Sintaks Python yang relevan untuk DroneKit |
| 01 | [Pengenalan DroneKit & Koneksi SITL](./modules/01-intro-to-dronekit/material.md) | Instalasi, koneksi, dan atribut vehicle |
| 02 | [Flight Modes](./modules/02-flight-modes/material.md) | Mode terbang ArduCopter dan cara penggunaannya |
| 03 | [Simulasi Misi](./modules/03-mission/material.md) | Membuat skrip misi penerbangan lengkap |

---

## Penugasan

Detail tugas ada di: [assignment/README.md](./assignment/README.md)

### Alur Pengumpulan Tugas

```
Fork repo ini  →  Kerjakan tugas  →  Simpan di submissions/nama_kamu/  →  Pull Request
```

1. **Fork** repository ini ke akun GitHub kamu
2. **Clone** hasil fork ke komputer kamu
   ```bash
   git clone https://github.com/USERNAME_KAMU/irc-software-bootcamp.git
   cd irc-software-bootcamp
   ```
3. Buat folder dengan nama kamu di dalam `submissions/`
4. Masukkan semua file tugas ke folder tersebut
5. **Commit & Push** ke fork kamu
6. Buat **Pull Request** ke repository ini

---

## Persiapan Sebelum Bootcamp

Pastikan semua tools berikut sudah terinstall sebelum sesi dimulai.

### 1. Python 3.9+

Cek apakah Python sudah terinstall:
```bash
python --version
```

Jika belum, download di: https://www.python.org/downloads/

> Saat instalasi di Windows, centang **Add Python to PATH**.

### 2. Virtual Environment dan DroneKit

Buka terminal di folder tempat kamu akan bekerja, lalu jalankan:

```bash
python -m venv venv
```

Aktivasi virtual environment:

- Windows:
  ```bash
  venv\Scripts\activate
  ```
- Mac/Linux:
  ```bash
  source venv/bin/activate
  ```

Install library yang dibutuhkan:

```bash
pip install dronekit pymavlink
```

Verifikasi instalasi:
```bash
python -c "import dronekit; print('DroneKit OK')"
```

### 3. Mission Planner

Download dan install Mission Planner di:
https://ardupilot.org/planner/docs/mission-planner-installation.html

Setelah install:
- Buka Mission Planner
- Klik tab **Simulation**
- Pilih **Multirotor**
- Klik **Start** untuk menjalankan SITL

Pastikan simulasi bisa berjalan sebelum bootcamp.

### 4. Git

Download di: https://git-scm.com/downloads

Cek instalasi:
```bash
git --version
```

### 5. Code Editor

Disarankan menggunakan **VS Code**: https://code.visualstudio.com/

Setelah install VS Code, install juga extension **Python** dari marketplace.

### 6. Akun GitHub

Daftar di https://github.com jika belum punya akun.
Akun GitHub akan digunakan untuk fork dan pull request saat pengumpulan tugas.

---

## Catatan Penggunaan Virtual Environment

Setiap kali membuka terminal baru untuk ngoding, **aktifkan dulu virtual environment**:

```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

Tanda bahwa venv aktif: nama `(venv)` akan muncul di awal baris terminal.

```bash
(venv) C:\Users\kamu\irc-bootcamp>
```

---

## Pertanyaan

Gunakan fitur **Issues** di repository ini untuk bertanya atau berdiskusi.