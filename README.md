# Simulasi Tata Surya 2D

Simulasi tata surya 2D interaktif yang dibuat dengan Python dan Pygame sebagai tugas kuliah untuk topik **Transformasi Geometri 2D** pada Grafika Komputer.

Program ini mengimplementasikan transformasi Rotasi, Translasi, dan Skala dari awal—tanpa pustaka fisika atau mesin animasi. Semua proses dilakukan secara manual menggunakan matematika.

> **Kelompok 3—Tugas Grafika Komputer: Transformasi Geometri 2D**

---

## Fitur

- 8 planet dengan tekstur scanline manual dan bayangan siang/malam
- Cincin Saturnus, Bulan milik Bumi, dan Bintik Merah Besar Jupiter
- 200 partikel sabuk asteroid
- Komet Halley dengan orbit Kepler dan ekor partikel
- Matahari berdenyut dengan penskalaan berbasis fungsi sinus
- Peluncur meteor dengan 4 pilihan ukuran dan mekanisme ketapel yang realistis
- Sistem penghancuran planet berdasarkan tingkat kekerasan planet dan massa meteor
- Klik planet untuk melihat detailnya (gravitasi, diameter, periode orbit, dan lainnya)
- Panning kamera, zoom, dan mode mengikuti planet
- Visualisasi grid koordinat, jejak orbit, dan garis medan gravitasi
- Panel HUD yang menampilkan nilai matriks transformasi secara langsung (θ, cos, sin, x', y')
- Panduan pintasan keyboard (tekan F1 atau klik tombolnya)
- Efek suara sintetis tanpa memerlukan berkas audio eksternal

---

## Cara Kerja

Inti simulasi ini dibangun menggunakan tiga transformasi geometri 2D:

### Rotasi
Digunakan untuk peredaran planet mengelilingi Matahari dan Bulan mengelilingi Bumi.

$$x' = R \cdot \cos(\theta), \quad y' = R \cdot \sin(\theta)$$

Pada setiap frame, sudut diperbarui dengan rumus:

$$\theta = \theta + (\text{speed} \times \Delta t)$$

### Translasi
Digunakan untuk panning kamera dan mode mengikuti planet.

$$x' = x + dx, \quad y' = y + dy$$

Posisi Bulan merupakan offset translasi dari posisi Bumi saat ini.

### Skala
Digunakan untuk zoom dan efek denyut Matahari.

$$x' = x \cdot s, \quad y' = y \cdot s$$

Denyut Matahari menggunakan rumus:

$$s_{\text{pulse}} = 1.0 + 0.06 \cdot \sin(t \cdot 1.5)$$

### Dunia ke Layar
Semua koordinat dunia dikonversi menjadi piksel layar dengan rumus:

$$x_{\text{screen}} = \text{cam\_x} + (x_{\text{world}} \times s)$$

---

## Persyaratan

- Python 3.8 atau lebih baru (diuji pada Python 3.10)
- pygame 2.x
- Windows / macOS / Linux

---

## Instalasi dan Menjalankan Program

### 1. Kloning repository

```bash
git clone https://github.com/fathiryasyaa/2d-solar-system-simulation.git
cd 2d-solar-system-simulation
```

### 2. Membuat virtual environment

```bash
python -m venv venv
```

### 3. Memasang dependensi

**Windows (PowerShell):**
```powershell
.\venv\Scripts\pip install pygame
```

**Windows (CMD):**
```cmd
venv\Scripts\pip install pygame
```

**macOS / Linux:**
```bash
./venv/bin/pip install pygame
```

Atau gunakan berkas requirements:
```bash
pip install -r requirements.txt
```

### 4. Menjalankan program

**Windows:**
```powershell
.\venv\Scripts\python tata_surya.py
```

**macOS / Linux:**
```bash
./venv/bin/python tata_surya.py
```

---

## Kontrol

| Input | Aksi |
|-------|--------|
| Gulir ke atas / bawah | Perbesar / perkecil tampilan |
| Klik kiri + tarik | Geser kamera |
| Klik kiri pada planet | Pilih planet (menampilkan kartu informasi) |
| Klik kanan + tarik ke belakang | Meluncurkan meteor dengan ketapel |
| `1` / `2` / `3` / `4` | Memilih ukuran meteor (Kecil / Sedang / Besar / Raksasa) |
| `SPACE` | Jeda / lanjutkan simulasi |
| `→` (Panah kanan) | Maju 1 frame (saat dijeda) |
| `S` | Mengaktifkan/nonaktifkan gerak lambat (0.05x) |
| `F` | Mengikuti planet yang dipilih |
| `[` / `]` | Mengurangi / menambah kecepatan orbit |
| `O` | Menampilkan/menyembunyikan garis orbit |
| `L` | Menampilkan/menyembunyikan label planet |
| `G` | Menampilkan/menyembunyikan grid koordinat |
| `T` | Menampilkan/menyembunyikan jejak orbit |
| `V` | Menampilkan/menyembunyikan garis medan gravitasi |
| `H` | Menyembunyikan/menampilkan panel samping |
| `R` | Mengatur ulang kamera, planet, dan meteor |
| `F1` | Membuka/menutup panduan pintasan keyboard |
| `ESC` | Keluar |

---

## Sistem Meteor

Meteor diluncurkan dengan menahan klik kanan lalu menarik ke belakang, kemudian melepaskannya. Garis putus-putus kuning menampilkan perkiraan lintasan.

Tersedia 4 ukuran meteor:

| Ukuran | Massa | Efek |
|------|------|--------|
| Kecil | 3 | Menghasilkan percikan saat menabrak, tidak pernah menghancurkan planet |
| Sedang | 20 | Dapat menghancurkan planet batuan kecil |
| Besar | 60 | Dapat menghancurkan planet es atau berukuran sedang |
| Raksasa | 200 | Dapat menghancurkan planet raksasa gas |

Planet akan hancur atau tidak berdasarkan perbandingan nilai kekerasan planet dengan massa meteor. Tekan **R** untuk mengatur ulang semua meteor dan memulihkan planet yang hancur.

---

## Struktur Project

```
.
├── tata_surya.py     # program utama
├── requirements.txt  # dependensi
└── README.md
```

---

## Catatan

Project ini dibuat khusus untuk pembelajaran sebagai bagian dari mata kuliah Grafika Komputer. Semua transformasi diimplementasikan secara manual tanpa pustaka fisika atau animasi.
