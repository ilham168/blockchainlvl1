# blockchainlvl1

Sebuah proyek kelas dasar yang memperkenalkan konsep blockchain secara sederhana dan aplikatif.

## 🎯 Tujuan
- Memberikan implementasi blockchain sederhana menggunakan Python (dan HTML untuk visualisasi).
- Membangun pemahaman dasar mengenai struktur blok, penambahan blok, hash, dan verifikasi data.
- Menyediakan contoh langsung yang bisa di‑modifikasi dan diperluas (level 1).

## 📁 Struktur Direktorinya
- `src/` : Kode utama implementasi blockchain.  
- `test/` : Unit‑test atau skrip verifikasi untuk mengecek integritas blockchain.  
- `examples/` : Contoh penggunaan / demo blockchain sederhana.  
- `index.html` : Halaman HTML sederhana untuk visualisasi atau penjelasan konsep.  
- `verify_balance.py` : Skrip Python yang melakukan pemeriksaan saldo / verifikasi terkait blockchain.  
- `Dockerfile` : Konfigurasi Docker untuk menjalankan proyek dalam container.  
- `docker‑compose.yml` : Setup multi‑container jika diperlukan untuk demo atau integrasi.  
- `requirements.txt` : Daftar dependensi Python yang diperlukan.

## 🛠 Cara Penggunaan
1. Pastikan kamu punya Python (versi 3.x) terinstal.  
2. Clone repositori ini:  
   ```bash
   git clone https://github.com/ilham168/blockchainlvl1.git
   cd blockchainlvl1
   ```  
3. Instal dependensi:  
   ```bash
   pip install ‑r requirements.txt
   ```  
4. Jalankan demo atau skrip verifikasi:  
   ```bash
   python verify_balance.py
   ```  
   Atau buka `index.html` di browser untuk visualisasi sederhana.  
5. Jika ingin menggunakan Docker:  
   ```bash
   docker build ‑t blockchainlvl1 .  
   docker‑compose up  
   ```

## 📚 Konsep yang Diterapkan
- Blok dengan data, timestamp, hash, dan pointer ke blok sebelumnya.  
- Penambahan blok baru dan hashing untuk menjaga integritas.  
- Verifikasi saldo atau status sebagai contoh aplikasi ringan dari blockchain.  
- Visualisasi sederhana agar konsep lebih mudah dipahami.

## 💡 Bagaimana Mengembangkan Lebih Lanjut
- Tambahkan mekanisme proof‑of‑work atau proof‑of‑stake untuk mengerti konsep konsensus.  
- Integrasi dengan database atau storage untuk persistensi blok.  
- Bangun antarmuka frontend yang lebih interaktif untuk menambah/menampilkan blok.  
- Implementasi jaringan node sederhana untuk memahami distribusi blockchain.  
- Tambahkan logging, monitoring, atau visualisasi grafis yang lebih baik.

## 📌 Catatan
- Proyek ini bersifat **pendidikan** dan **eksplorasi**, bukan untuk produksi atau keperluan komersial.  
- Jangan digunakan untuk transaksi nyata atau menyimpan data sensitif tanpa modifikasi keamanan yang memadai.

## 🧭 Lisensi
Proyek ini dilisensikan di bawah lisensi MIT — silakan gunakan, modifikasi, dan distribusikan — dengan menyertakan atribusi kepada penulis asli.
