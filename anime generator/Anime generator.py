from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time
from fpdf import FPDF
from io import BytesIO
from PIL import Image
import os

tanggal_sekarang_obj = datetime.now()
tanggal_sekarang = tanggal_sekarang_obj.strftime("%d-%m-%y")
tanggal_masa_depan_obj = tanggal_sekarang_obj + timedelta(days=7)
tanggal_masa_depan = tanggal_masa_depan_obj.strftime("%d-%m-%y")

def find_pdfs(directory):
    pdf_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]
    return pdf_files

# Contoh penggunaan
folder_path = "./gambar/"  # Ganti dengan path folder yang diinginkan
pdfs = find_pdfs(folder_path)
count = 1
counter = 1
if pdfs:
    print("=============================")
    print("File PDF yang ada di folder:|")
    print("=============================")
    for pdf in pdfs:
        print(f"{count}. {pdf}")
        count += 1
else:
    print("Tidak ada file PDF di folder.")

nama_file_txt = "time.txt"

def clear_console():
    os.system("clear")
    
try:
    with open(nama_file_txt, "r") as file:
        baris = file.readlines()
        tanggal_awal_log = datetime.strptime(baris[0].strip(), "%d-%m-%y")
        tanggal_akhir_log = datetime.strptime(baris[1].strip(), "%d-%m-%y")
except FileNotFoundError:
    with open(nama_file_txt, "w") as file:
        file.write(f"{tanggal_sekarang}\n")
        file.write(f"{tanggal_masa_depan}")
 
    baris = [tanggal_sekarang, tanggal_masa_depan]
    tanggal_awal_log = tanggal_sekarang_obj
    tanggal_akhir_log = tanggal_masa_depan_obj

nama_file_input = input("\nMasukkan nama file (default : Anime): ").strip()

if not nama_file_input:
    nama_file_input = "Anime"

# Tentukan direktori tempat menyimpan file
output_directory = "./gambar/"  # Ganti dengan direktori tujuan
os.makedirs(output_directory, exist_ok=True)  # Buat direktori jika belum ada

if tanggal_sekarang_obj > tanggal_akhir_log:
    with open(nama_file_txt, "w") as file:
        file.write(f"{tanggal_sekarang}\n")
        file.write(f"{tanggal_masa_depan}")
    nama_file_pdf = f"{nama_file_input} {tanggal_sekarang}.pdf"
else:
    nama_file_pdf = f"{nama_file_input} ({baris[0].strip()} sd {baris[1].strip()}).pdf"

# Gabungkan direktori dengan nama file
full_file_path = os.path.join(output_directory, nama_file_pdf)

print(f"\nNama file PDF: {nama_file_pdf}")

base_url1 = "https://wallhaven.cc/search?categories=010&purity=110&sorting=date_added&order=desc&ai_art_filter=0"
base_url2 = "https://wallhaven.cc/search?categories=010&purity=110&topRange=1w&sorting=toplist&order=desc&ai_art_filter=0"
base_url3 = "https://wallhaven.cc/search?categories=010&purity=110&topRange=1M&sorting=toplist&order=desc&ai_art_filter=0"

while True:
    print("Pilih base URL:")
    print("1. (anime) terbaru ")
    print("2. (anime) top List Minggu Ini ")
    print("3. (anime) top List bulan Ini ")
    print("4. Masukkan URL Wallhaven secara manual")

    choice = input("Masukkan pilihan (1/2/3/4): ").strip()

    if choice == "1":
        base_url = base_url1
        break
    elif choice == "2":
        base_url = base_url2
        break
    elif choice == "3":
        base_url = base_url3
        break
    elif choice == "4":
        base_url = input("\nMasukkan URL Wallhaven: ").strip()
        if not base_url.startswith("https://wallhaven.cc/search?"):
            print("URL tidak valid! Pastikan URL dimulai dengan 'https://wallhaven.cc/search?'")
            continue
        break
    else:
        print("\rPilihan tidak valid!\n", flush=True)

response = requests.get(base_url)
soup = BeautifulSoup(response.content, 'html.parser')

pagination = soup.find_all('a', {"original-title": True})
pages = [int(a.text) for a in pagination if a.text.isdigit()]
max_page_default = max(pages) if pages else 1

while True:
    user_input = input(f"\nMasukkan jumlah halaman (default: {max_page_default}): ").strip()

    if user_input == "":
        max_page = max_page_default
        clear_console()
        break
    elif user_input.isdigit() and int(user_input) <= max_page_default and int(user_input) > 0:
        max_page = int(user_input)
        clear_console()
        break
    else:
        print("\rInput tidak valid!", flush=True)
        
loading_text = f"Menyiapkan {max_page} halaman"
for i in range(5):
    print(f"\r{loading_text} {'·' * i} |", end="\r", flush=True)
    time.sleep(0.5)


print(f"|         {tanggal_sekarang}         |   anime   |")
with open(nama_file_txt, "r") as file:
    baris = file.readlines()
    print(f"| {baris[0].strip()} sampai {baris[1].strip()} | generator |")
    
def safe_request(url, retries=5, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                return response
            else:
                print(f"\rError mencoba lagi...        ", end="\r", flush=True)

        except requests.exceptions.RequestException as e:
            print(f"\rRequest error mencoba lagi...        ", end="\r", flush=True)
        time.sleep(delay)
    return None
    
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", style="B",size=27)
pdf.cell(0, 10, f"Walhaven ({tanggal_sekarang})", ln=True, align='C')


print(f"========================================", flush=True)
start_time = time.time()
for page in range(1, max_page + 1):
    page_url = f"{base_url}&page={page}"
    response = safe_request(page_url)
    if not response:
        print(f"Gagal mengakses halaman {page}. Melewati")
        continue

    soup = BeautifulSoup(response.content, 'html.parser')

    favorites = soup.find_all('a', class_='jsAnchor overlay-anchor wall-favs')
    fav_counts = [int(f.text.strip()) for f in favorites if f.text.strip().isdigit()]

    images = soup.find_all('a', class_='preview')
    image_links = [img['href'] for img in images]
    small_images = soup.find_all('img', class_='lazyload')

    fav_with_links = list(zip(fav_counts, image_links))

    pdf.set_font("Arial", size=15)
    pdf.cell(0, 5, f"  ==========================================================", ln=True)
    pdf.set_font("Arial", style="B", size=22)
    pdf.cell(0, 10, f"Halaman {page}:", ln=True)
    pdf.set_font("Arial", size=15)

    for i, (fav, link) in enumerate(fav_with_links, start=1):
        elapsed_time = time.time() - start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        print(f"\r| {hours:02}:{minutes:02}:{seconds:02} | Memproses gambar {str(i).rjust(2)} / {str(len(fav_with_links)).rjust(2)}  |", end="\r", flush=True)
        pdf.cell(0, 5, f"  ==========================================================", ln=True)
        pdf.cell(0, 8, f"    gambar ke {counter}", ln=True)
        
        counter += 1

        small_image = small_images[i-1] if i-1 < len(small_images) else None
        if small_image and small_image.get('data-src'):
            small_image_url = small_image['data-src']
            try:
                image_response = safe_request(small_image_url)
                if image_response:
                    img = Image.open(BytesIO(image_response.content))
                    img_path = f"image_{page}_{i}.jpg"
                    img.save(img_path)
                    pdf.image(img_path, x=15, y=None, w=70)
                    os.remove(img_path)
            except Exception as e:
                pdf.cell(0, 8, f"      Gagal menambahkan gambar: {e}", ln=True)
        else:
            pdf.cell(0, 8, "      Gambar thumbnail tidak ditemukan.", ln=True)

        pdf.cell(0, 8, f"  Link gambar: {link}", ln=True)
        pdf.cell(0, 8, f"      Jumlah favorit: {fav}", ln=True)

        detail_response = safe_request(link)
        if not detail_response:
            pdf.cell(0, 8, f"  Gagal mengakses detail untuk {link}. Melewati...", ln=True)
            continue

        detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
        
        views_element = detail_soup.find('dt', string='Views')
        if views_element:
            views_value = views_element.find_next('dd').get_text(strip=True)
            pdf.cell(0, 8, f"      Dilihat: {views_value}", ln=True)
        else:
            pdf.cell(0, 8, "      Views tidak ditemukan.", ln=True)

        time_element = detail_soup.find('time')
        if time_element:
            time_text = time_element.get_text(strip=True)
            pdf.cell(0, 8, f"      Waktu dibuat: {time_text}", ln=True)
        else:
            pdf.cell(0, 8, "      Waktu tidak ditemukan.", ln=True)
            
        resolution_element = detail_soup.find('h3', class_='showcase-resolution')
        if resolution_element:
            resolution_text = resolution_element.get_text(strip=True)
            pdf.cell(0, 8, f"      Resolusi: {resolution_text}", ln=True)
        else:
            pdf.cell(0, 8, "      Resolusi tidak ditemukan.", ln=True)
            
        size_element = detail_soup.find('dt', string='Size')
        if size_element:
            size_value = size_element.find_next('dd').get_text(strip=True)
            pdf.cell(0, 8, f"      Ukuran: {size_value}", ln=True)
        else:
            pdf.cell(0, 8, "      Ukuran tidak ditemukan.", ln=True)

        source_element = detail_soup.find('p', class_='showcase-source')
        if source_element:
            link_element = source_element.find('a', class_='link')
            if link_element and link_element.get('href'):
                source_link = link_element['href']
                pdf.cell(0, 8, f"      Link Asli: {source_link}", ln=True)
            else:
                pdf.cell(0, 8, "      Link Asli tidak ditemukan.", ln=True)
        else:
            pdf.cell(0, 8, "      Elemen sumber tidak ditemukan.", ln=True)

        image_element = detail_soup.find('img', id='wallpaper')
        if image_element and image_element.get('src'):
            image_url = image_element['src']
            pdf.cell(0, 8, f"      URL Gambar Full: {image_url}", ln=True)
        else:
            pdf.cell(0, 8, "      Gambar tidak ditemukan.", ln=True)

        time.sleep(0.6)
    print(f"\r| {str(page).rjust(5)} / {str(max_page).rjust(5)} | sedang menyelesaikan |",flush=True)
    

print(f"========================================", flush=True)
pdf.output(full_file_path)
print(f"sudah disimpan ke {full_file_path}")

end_time = time.time() - start_time
end_hours = int(end_time // 3600)
end_minutes = int((end_time % 3600) // 60)
end_seconds = int(end_time % 60)

final_time = f"{end_hours:02}:{end_minutes:02}:{end_seconds:02}"
print(f"Waktu akhir: {final_time}")
