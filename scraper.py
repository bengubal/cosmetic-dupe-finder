import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

BASE_URL = "https://incidecoder.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

# Scrape edilecek kategoriler
CATEGORIES = ["moisturizer", "serum", "sunscreen", "cleanser", "toner"]


def get_product_links(category, max_pages=5):
    """
    Arama sayfasından ürün linklerini toplar.
    Her sayfa yaklaşık 50 ürün içeriyor.
    """
    links = []

    for page in range(1, max_pages + 1):
        if page == 1:
            url = f"{BASE_URL}/search?query={category}&activetab=products"
        else:
            url = f"{BASE_URL}/search?query={category}&activetab=products&ppage={page}"

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            # Ürün linklerini bul — class="klavika simpletextlistitem"
            product_links = soup.find_all("a", class_="simpletextlistitem")

            if not product_links:
                print(f"  Sayfa {page}: ürün bulunamadı, duruyorum.")
                break

            for link in product_links:
                links.append({
                    "name": link.text.strip(),
                    "url": BASE_URL + link["href"],
                    "category": category
                })

            print(f"  [{category}] Sayfa {page}: {len(product_links)} ürün bulundu")
            time.sleep(1.5)  # Siteye nazik ol

        except Exception as e:
            print(f"  Hata (sayfa {page}): {e}")
            break

    return links


def get_product_details(product_url):
    """
    Ürün sayfasından şunları çeker:
    - Marka adı
    - Kısa açıklama
    - INCI içerik listesi (virgülle ayrılmış string)
    """
    try:
        response = requests.get(product_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # --- Marka ---
        brand_tag = soup.find("a", href=lambda h: h and h.startswith("/brands/"))
        brand = brand_tag.text.strip() if brand_tag else ""

        # --- Kısa açıklama ---
        desc_tag = soup.find("span", id="product-details")
        description = desc_tag.text.strip() if desc_tag else ""

        # --- INCI listesi ---
        # <div id="showmore-section-ingredlist-short"> içindeki tüm ingred-link'leri al
        inci_section = soup.find("div", id="showmore-section-ingredlist-short")
        ingredients = []

        if inci_section:
            ingred_links = inci_section.find_all("a", class_="ingred-link")
            for link in ingred_links:
                ingredient_name = link.text.strip()
                if ingredient_name:
                    ingredients.append(ingredient_name)

        inci_list = ", ".join(ingredients)

        return {
            "brand": brand,
            "description": description,
            "inci_list": inci_list,
            "ingredient_count": len(ingredients)
        }

    except Exception as e:
        print(f"  Hata (ürün detayı): {e}")
        return {
            "brand": "",
            "description": "",
            "inci_list": "",
            "ingredient_count": 0
        }


def main():
    # Klasörü oluştur
    os.makedirs("data/raw", exist_ok=True)

    all_products = []

    for category in CATEGORIES:
        print(f"\n{'='*50}")
        print(f"  Kategori: {category.upper()}")
        print(f"{'='*50}")

        # 1. Adım: Linkleri topla
        links = get_product_links(category, max_pages=3)
        print(f"  Toplam {len(links)} ürün linki bulundu\n")

        # 2. Adım: Her ürünün detayını çek
        for i, product in enumerate(links):
            print(f"  [{i+1}/{len(links)}] {product['name']}")

            details = get_product_details(product["url"])

            all_products.append({
                "product_name": product["name"],
                "brand": details["brand"],
                "category": category,
                "description": details["description"],
                "inci_list": details["inci_list"],
                "ingredient_count": details["ingredient_count"],
                "url": product["url"]
            })

            # Her 10 üründe bir ara kayıt yap (veri kaybı olmasın)
            if (i + 1) % 10 == 0:
                df_temp = pd.DataFrame(all_products)
                df_temp.to_csv("data/raw/products_raw_temp.csv", index=False, encoding="utf-8")
                print(f"  --> Ara kayıt yapıldı ({len(all_products)} ürün)")

            time.sleep(1)  # Her ürün arasında 1 saniye bekle

    # Final CSV'yi kaydet
    df = pd.DataFrame(all_products)
    df.to_csv("data/raw/products_raw.csv", index=False, encoding="utf-8")

    print(f"\n{'='*50}")
    print(f"  TAMAMLANDI!")
    print(f"  Toplam ürün: {len(df)}")
    print(f"  Kategoriler: {df['category'].value_counts().to_dict()}")
    print(f"  Boş INCI listesi: {(df['inci_list'] == '').sum()} ürün")
    print(f"  Dosya: data/raw/products_raw.csv")
    print(f"{'='*50}")

    print("\nİlk 3 ürün:")
    print(df[["product_name", "brand", "category", "ingredient_count"]].head(3))


if __name__ == "__main__":
    main()