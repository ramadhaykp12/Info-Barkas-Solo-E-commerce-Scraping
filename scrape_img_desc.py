import os
import re
import scrapy
import pandas as pd
from scrapy.crawler import CrawlerProcess

# Fungsi untuk membersihkan nama folder atau file
def sanitize_filename(name, max_length=100):
    sanitized = re.sub(r'[<>:"/\\|?*\u2060]', '_', name)  # Mengganti karakter tidak valid
    sanitized = re.sub(r'\s+', '_', sanitized)  # Mengganti spasi dengan underscore
    return sanitized[:max_length]  # Potong jika terlalu panjang

# Folder utama untuk menyimpan data produk
main_folder = r"D:\data analytics\Infobarkas solo\products_data_new_3"
os.makedirs(main_folder, exist_ok=True)

# Membaca link dari hasil scraping sebelumnya
import pandas as pd
df = pd.read_csv('all_links_new2.csv')  # Ganti dengan nama file CSV
product_links = df['Links'].tolist()

class ProductSpider(scrapy.Spider):
    name = 'product_spider'
    start_urls = product_links

    custom_settings = {
        'USER_AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }

    def parse(self, response):
        # Mengambil nama produk dari elemen <title>
        title_tag = response.xpath('//title/text()').get()
        if title_tag:
            product_name = sanitize_filename(title_tag.strip())
            product_folder = os.path.join(main_folder, product_name)
            os.makedirs(product_folder, exist_ok=True)
            self.log(f"Nama Produk (dari title): {product_name}")
        else:
            self.log(f"Gagal menemukan title di {response.url}")
            return

        # Mengambil deskripsi lengkap dari elemen
        description_section = response.css('div.elementor-widget-woocommerce-product-content')
        if description_section:
            description = description_section.get().strip()
            description_file = os.path.join(product_folder, "description.txt")
            with open(description_file, "w", encoding="utf-8") as f:
                f.write(description)
            self.log(f"Deskripsi ditemukan dan disimpan di: {description_file}")
        else:
            self.log(f"Gagal menemukan deskripsi di {response.url}")

        # Mengambil semua gambar dalam div dengan class tertentu
        img_tags = response.css('div.woocommerce-product-gallery__wrapper img::attr(src)').getall()
        if img_tags:
            for idx, img_url in enumerate(img_tags, start=1):
                img_filename = sanitize_filename(f"image_{idx}_{os.path.basename(img_url)}")
                img_path = os.path.join(product_folder, img_filename)
                yield scrapy.Request(
                    url=img_url,
                    callback=self.save_image,
                    meta={'img_path': img_path}
                )
        else:
            self.log(f"Gagal menemukan gambar di {response.url}")

    def save_image(self, response):
        img_path = response.meta['img_path']
        with open(img_path, 'wb') as f:
            f.write(response.body)
        self.log(f"Gambar disimpan: {img_path}")

# Menjalankan spider
process = CrawlerProcess()
process.crawl(ProductSpider)
process.start()

print("Scraping selesai. Data tersimpan di folder:", main_folder)
