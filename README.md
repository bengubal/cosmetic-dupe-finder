# 💄 SVD ve K-Means Tabanlı Gelişmiş Kozmetik Ürün Muadili (Dupe) Öneri Sistemi ve Duygu Analizi

Bu depo, Kocaeli Üniversitesi Yazılım Mühendisliği Veri Madenciliği dersi dönem projesi kapsamında geliştirilen uçtan uca kozmetik ürün öneri sisteminin kaynak kodlarını ve proje dokümantasyonunu içermektedir.

## 📌 Projenin Amacı
Kozmetik endüstrisinde üst segment (high-end) ürünlerin fiyatlarının yüksek olması, tüketicileri uygun fiyatlı alternatiflere (dupe) yönlendirmektedir. Bu projenin amacı, kullanıcının girdiği hedef ürüne en yakın alternatifleri bulurken; içerik benzerliğini, ürünün ait olduğu gizli kümeyi, pazar puanını ve kullanıcı yorumlarının duygu durumunu entegre bir şekilde analiz eden bütüncül bir karar destek sistemi geliştirmektir.

## 📊 Veri Seti
Projede kullanılan ham veri, Kaggle platformunda sunulan açık kaynaklı [Sephora Products and Skincare Reviews](https://www.kaggle.com/datasets/nadyinky/sephora-products-and-skincare-reviews) veri setinden elde edilmiştir. Veri temizleme adımları sonucunda modelleme için iki temel veri seti oluşturulmuştur:
* **`cleaned_products.csv`**: 2999 adet ürün ve 11 öznitelik (fiyat, içerik, değerlendirme puanı vb.).
* **`cleaned_reviews.csv`**: Ürünlere ait 65.759 adet etiketlenmiş kullanıcı yorumu.

## ⚙️ Kullanılan Yöntemler ve Modelleme
Projede en iyi muadil ürünü bulmak amacıyla birbirini tamamlayan 4 farklı makine öğrenmesi ve veri madenciliği yaklaşımı kullanılmıştır:

1. **TF-IDF ve Kosinüs Benzerliği:** Ürün içerik metinleri 5000 boyutlu TF-IDF matrisine dönüştürülerek temel içerik benzerliği hesaplanmıştır.
2. **TruncatedSVD ile Boyut İndirgeme:** Seyreklik problemini aşmak için matris 100 latent bileşene indirgenmiştir.
3. **K-Means ile Kümeleme:** Arama uzayını daraltmak ve tamamen ilgisiz ürünlerin eşleşmesini engellemek için SVD matrisi $k=3$ (Silhouette Skoru: 0.0512) olacak şekilde kümelenmiştir.
4. **Naive Bayes ile Duygu Analizi:** 59.890 etiketli yorum üzerinde eğitilen `MultinomialNB` modeli (%93.6 Doğruluk, %96.15 F1-Skoru) ile ürünlerin "Pozitif Olasılık" (Sentiment) skorları hesaplanmıştır.

## 🏆 Gelişmiş Yeniden Sıralama (Re-ranking) ve Filtreleme
Sistem sadece içerik benzerliğine odaklanmaz. `advanced_dupe_finder` algoritması şu filtrelerden geçen ürünleri listeler:
* **Küme Şartı:** Hedef ürünle aynı K-Means kümesinde olmalı.
* **Fiyat Şartı:** Hedef fiyatın dinamik bir oranından (örn. %50'sinden) ucuz olmalı.
* **Marka Şartı:** Hedef ürünle farklı markadan olmalı.
* **Duygu Şartı:** Naive Bayes duygu skoru belirli bir eşiğin (0.3) üzerinde olmalı.

Filtreyi geçen ürünler **İçerik Benzerliği**, **Yıldız Puanı** ve **Yorum Sayısı Popülaritesi** MinMaxScaler ile ölçeklendirilerek ağırlıklı bir "Final Skoru"na göre sıralanır. 

## 📂 Dosya Yapısı
Projeye ait GitHub dizin yapısı aşağıdaki gibidir:
```text
├── data/                  # Ham ve temizlenmiş veri setleri
├── notebooks/             # Veri keşfi (EDA) ve modelleme adımlarını içeren Jupyter Notebook'lar (Veri_Madenciliği.ipynb)
├── visuals/               # Projeye ait grafikler (Silhouette skoru, Confusion Matrix vb.)
├── reports                # Final raporu (IEEE formatında)
└── README.md              # Proje dokümantasyonu
