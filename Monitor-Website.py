import os
import time
import requests
import subprocess
from collections import deque
from datetime import datetime
from tabulate import tabulate

# Bersihkan layar sebelum memulai
os.system("clear")

# Fungsi untuk menampilkan banner profesional
def print_banner():
    print("\033[1;31m" + "="*75)
    print("🔥 SUPER SERVER MONITOR PRO MAX 🔥".center(75))
    print("🚀 Advanced Real-Time Server & DDoS Detection System".center(75))
    print("\033[1;36m          📊 Monitor-Website 📊          \033[0m".center(75))  # Nama lebih kecil di tengah
    print("="*75 + "\033[0m\n")

print_banner()

# Minta input URL server
url = input("\033[1;36mMasukkan URL server (contoh: https://example.com): \033[0m").strip()
if not url.startswith("http"):
    url = "https://" + url

# Simpan riwayat response time & request count
history = deque(maxlen=100)
request_count = deque(maxlen=100)

# Fungsi untuk menghitung jumlah request masuk ke server
def hitung_request():
    try:
        result = subprocess.run(["ss", "-ant"], capture_output=True, text=True)
        connections = result.stdout.count("ESTAB")
        return connections
    except Exception:
        return 0

# Fungsi untuk mencatat log aktivitas server
def log_event(event):
    with open("server_log.txt", "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] {event}\n")

# Mulai monitoring setiap 5 detik
print("\n\033[1;33m🚀 Memulai Monitoring Server...\033[0m\n")
time.sleep(2)

while True:
    os.system("clear")
    print_banner()
    print(f"\033[1;34m📡 Monitoring Server: {url}\033[0m\n")

    try:
        # Cek jumlah request masuk ke server
        current_requests = hitung_request()
        request_count.append(current_requests)

        # Cek status server & response time
        start_time = time.time()
        response = requests.get(url, timeout=5)
        response_time = (time.time() - start_time) * 1000  # ms
        history.append(response_time)

        # Hitung rata-rata response time
        avg_response = sum(history) / len(history)

        # Data untuk ditampilkan dalam bentuk tabel
        table_data = [
            ["Status Code", f"\033[1;32m{response.status_code} (OK)\033[0m"],
            ["Response Time", f"\033[1;36m{response_time:.2f} ms\033[0m"],
            ["Rata-rata Response", f"{avg_response:.2f} ms"],
            ["Total Request Aktif", f"{current_requests}"]
        ]

        # Tampilkan data dalam bentuk tabel
        print(tabulate(table_data, tablefmt="grid"))

        # Analisis status server
        if avg_response < 100:
            status_server = "\033[1;32m🟢 Normal (Cepat)\033[0m"
        elif avg_response < 500:
            status_server = "\033[1;33m🟠 Server Mulai Lemot\033[0m"
        else:
            status_server = "\033[1;31m🔴 Server Bisa Down!\033[0m"

        print(f"\n📡 Status Server: {status_server}")

        # Simpan log jika terjadi perubahan status
        log_event(f"Server status: {status_server}, Response Time: {response_time:.2f} ms, Requests: {current_requests}")

        # Deteksi serangan DDoS
        if len(request_count) == 100:
            avg_request = sum(request_count) / len(request_count)

            if avg_request > 1000:
                attack_type = "🚨 \033[1;41mSerangan DDoS: HTTP Flood Detected!\033[0m"
                log_event("DDoS Attack Detected: HTTP Flood")
            elif avg_request > 800:
                attack_type = "⚠️ \033[1;43mKemungkinan Serangan: SYN Flood!\033[0m"
                log_event("Possible DDoS Attack: SYN Flood")
            elif avg_request > 600:
                attack_type = "⚠️ \033[1;43mKemungkinan Serangan: UDP Flood!\033[0m"
                log_event("Possible DDoS Attack: UDP Flood")
            elif avg_request > 500:
                attack_type = "⚠️ \033[1;43mSerangan Lambat: Slowloris Detected!\033[0m"
                log_event("Possible DDoS Attack: Slowloris")
            else:
                attack_type = "\033[1;32m✅ Tidak ada ancaman DDoS\033[0m"

            print(f"\n🔍 **Analisis Keamanan:** {attack_type}")

    except requests.exceptions.RequestException:
        print("\n\033[1;41m🚨🔴 SERVER DOWN! 🔴🚨\033[0m")
        print("\033[1;31m❌ Server tidak merespons atau mengalami gangguan.\033[0m")
        print("\033[1;33m🔄 Sistem akan mencoba kembali dalam 5 detik...\033[0m")
        log_event("ALERT! Server Down!")
    
    time.sleep(5)  # Refresh setiap 5 detik
