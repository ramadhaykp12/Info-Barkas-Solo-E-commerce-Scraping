import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Base URL (tanpa nomor halaman)
base_url = "https://www.infobarkassolo.com/shop/?product-page="

# Header untuk menghindari blokir
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
}

# Menampung semua link dari semua halaman
all_links = []

# Loop untuk setiap halaman (dari 1 hingga 104)
for page in range(1, 105):
    print(f"Scraping halaman {page}...")
    url = base_url + str(page)
    
    # Mengirim permintaan GET
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # Parsing HTML dengan BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Mencari elemen <ul> dengan class 'products elementor-grid columns-6'
        ul = soup.find('ul', class_='products elementor-grid columns-6')
        
        if ul:
            # Mencari semua elemen <li> di dalam <ul>
            list_items = ul.find_all('li')
            
            # Ekstraksi link dari setiap elemen <li>
            for li in list_items:
                a_tag = li.find('a', class_ = 'woocommerce-LoopProduct-link woocommerce-loop-product__link', href=True)
                if a_tag:
                    all_links.append(a_tag['href'])
        else:
            print(f"Tidak ditemukan elemen <ul> dengan class 'products elementor-grid columns-6' di halaman {page}")
    else:
        print(f"Gagal mengakses halaman {page}, status code: {response.status_code}")
    
    # Tambahkan jeda untuk menghindari blokir
    time.sleep(1)

# Menyimpan link ke dalam Pandas DataFrame
df = pd.DataFrame(all_links, columns=['Links'])

# Menampilkan DataFrame
print(df)

# Simpan ke file CSV
df.to_csv('all_links_new2.csv', index=False)
print("Semua link berhasil disimpan ke file 'all_links.csv'")
