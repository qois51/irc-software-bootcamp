# Penugasan - Simulasi Misi DroneKit

## Deskripsi Tugas

Buat sebuah skrip Python menggunakan DroneKit yang mensimulasikan penerbangan drone di Mission Planner SITL sekreatif mungkin.

Skrip minimal harus mengimplementasikan alur berikut:

```
ARM -> TAKEOFF -> MAJU -> MUNDUR -> LANDING
```

Kamu bebas menambahkan kreativitas seperti pola terbang berbeda (zigzag, kotak, segitiga), hover LOITER di beberapa titik, variasi ketinggian di berbagai waypoint, maupun kombinasi arah yang lebih kompleks.

---

## Yang Harus Dikumpulkan

Buat folder dengan format nama kamu di dalam `submissions/` dan isi dengan:

```
submissions/nama_kamu/
├── mission.py          <- kode Python simulasi (wajib)
├── explanation.md      <- penjelasan kode (wajib)
└── screenshots/        <- bukti simulasi berjalan (wajib)
    ├── simulation.png
    └── (tambahan screenshot atau link video)
```

### mission.py (Wajib)

- Kode Python yang bisa dijalankan dan terhubung ke SITL Mission Planner
- Kode harus terstruktur rapi dan diberi komentar yang jelas pada bagian-bagian penting
- Minimal mengimplementasikan: arm, takeoff, maju, mundur, landing

### explanation.md (Wajib)

Jelaskan kode kamu dengan menjawab pertanyaan-pertanyaan berikut:

1. Apa pola terbang yang kamu buat? Deskripsikan rutenya.
2. Fungsi-fungsi apa saja yang kamu buat dan apa kegunaannya?
3. Mode apa saja yang kamu gunakan dan dalam situasi apa?
4. Tantangan apa yang kamu temui dan bagaimana cara mengatasinya?
5. Apa yang ingin kamu kembangkan jika ada waktu lebih?

### Screenshots / Video (Wajib)

- Minimal satu screenshot Mission Planner yang menunjukkan drone bergerak
- Jika merekam video, upload ke Google Drive atau YouTube dan cantumkan linknya di dalam `explanation.md`

---

## Cara Pengumpulan

### Langkah 1 - Fork Repository

Klik tombol **Fork** di pojok kanan atas halaman repository ini untuk membuat salinan repository ke akun GitHub kamu.

### Langkah 2 - Clone Fork

```bash
git clone https://github.com/USERNAME_KAMU/irc-software-bootcamp.git
cd irc-software-bootcamp
```

### Langkah 3 - Aktifkan Virtual Environment

```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

> Jika venv belum dibuat, buat dulu:
> ```bash
> python -m venv venv
> pip install dronekit pymavlink
> ```

### Langkah 4 - Buat Folder dan File Tugas

```bash
# Buat folder dengan nama kamu (gunakan underscore, bukan spasi)
mkdir submissions/nama_kamu
```

Buat file `mission.py`, `explanation.md`, dan folder `screenshots/` di dalamnya.

### Langkah 5 - Commit dan Push

```bash
git add .
git commit -m "submission: nama_kamu"
git push origin main
```

### Langkah 6 - Buat Pull Request

1. Buka halaman fork kamu di GitHub
2. Klik **"Contribute"** lalu **"Open Pull Request"**
3. Isi form Pull Request sesuai template yang tersedia
4. Klik **"Create Pull Request"**

---

## Catatan

- Pastikan Mission Planner SITL sudah berjalan sebelum menjalankan skrip
- Koneksi default ke SITL: `tcp:127.0.0.1:5762`
- Jangan mengubah file di luar folder `submissions/nama_kamu/`
- Jangan push langsung ke repository utama, gunakan Pull Request