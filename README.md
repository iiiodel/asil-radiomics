# asil-radiomics
A Python-based pipeline for extracting and analyzing radiomic features from ovarian cancer NRRD scans. This project includes scripts for data structuring, exhaustive feature extraction using PyRadiomics, and interactive data visualization.

![Python](https://img.shields.io/badge/python-3.9-blue.svg)

## 🧬 Proje Hakkında

Bu proje, yumurtalık kanserine ait medikal görüntülerden (NRRD formatında) kapsamlı radyomik özelliklerin çıkarılması için uçtan uca bir çözüm sunmaktadır. Pipeline, dağınık haldeki ham verilerin organize edilmesi, PyRadiomics kütüphanesi ile 1500'den fazla özelliğin çıkarılması ve sonuçların düzenlenmesi adımlarını içerir. Ayrıca, segmentasyonların doğruluğunu kontrol etmek için bir veri inceleme aracı da sunulmaktadır.

## 📂 Proje Yapısı

Projenin ana klasör yapısı aşağıdaki gibidir. `data` klasörü ve içeriği, `.gitignore` dosyası ile versiyon kontrolü dışında tutulmuştur.

```
asil-radiomics/
│
├── data/
│   ├── raw/                      # Ham verilerinizi buraya koyun
│   ├── structured/               # 1. script'in oluşturduğu düzenli veri klasörü
│   └── Radyomik_CSV_Ciktilari/   # 3. script'in oluşturduğu CSV çıktı klasörü
│
├── data_organizer.py             # Ham verileri yapılandıran script
├── radiomics_extractor.py        # Radyomik özellikleri çıkaran script
├── csv_organizer.py              # Üretilen CSV'leri toplayan script
├── mask_inspector.py             # Tarama/maske inceleme aracı
│
├── .gitignore
├── environment.yml
└── README.md
```

## 🛠️ Kurulum

1.  **Depoyu Klonlayın:**
    ```bash
    git clone https://github.com/iiiodel/asil-radiomics.git
    cd asil-radiomics
    ```

2.  **Conda Ortamını Oluşturun:**
    ```bash
    conda env create -f environment.yml
    ```

3.  **Ortamı Aktive Edin:**
    ```bash
    conda activate radiomics_env
    ```

## 📋 Ana Pipeline Kullanımı

#### Adım 0: Veri Hazırlığı

Ham verilerinizi aşağıdaki yapıya uygun şekilde `data/raw/Hastalar/` klasörünün içine yerleştirin:

```
data/
└── raw/
    └── Hastalar/
        ├── Hasta_Adi_1/
        │   ├── ...
        │   ├── segmentasyon.seg.nrrd
        │   └── tarama.nrrd
        └── ...
```

#### Adım 1: Verileri Yapılandırma

`data_organizer.py` script'i, ham verileri okur ve `data/structured/` klasörünü analiz için hazırlar.

```bash
python data_organizer.py
```

#### Adım 2: Radyomik Özellik Çıkarma

`radiomics_extractor.py` script'i, yapılandırılmış verilerden radyomik özellikleri hesaplar ve sonuçları (bireysel ve birleştirilmiş CSV'ler) `data/structured/` içine yazar.

```bash
python radiomics_extractor.py
```

#### Adım 3: CSV Çıktılarını Toplama

`csv_organizer.py` script'i, üretilen tüm CSV dosyalarını `data/Radyomik_CSV_Ciktilari/` klasörüne taşır.

```bash
python csv_organizer.py
```

---

## Ek Araçlar

### Segmentasyon Kontrolü için İnteraktif Görüntüleyici

`mask_inspector.py` script'i, ana pipeline'dan bağımsız bir araçtır. Bu araç, radyomik özelliklerini çıkarmadan önce ham veya yapılandırılmış verilerdeki `scan.nrrd` ve `segmentation.nrrd` dosyalarını interaktif bir pencerede incelemenizi sağlar. Bu sayede segmentasyonlarınızın doğruluğunu ve sınırlarlarını görsel olarak teyit edebilirsiniz.

Kullanmak için script içindeki hasta yolu değişkenini düzenleyip çalıştırın:
```bash
python mask_inspector.py
```

## ⚖️ Lisans

Bu projede bir açık kaynak lisansı belirtilmemiştir. Bu nedenle, varsayılan uluslararası telif hakkı yasaları geçerlidir ve **tüm hakları proje sahibine aittir.** Proje sahibinden yazılı ve açık bir izin alınmadan bu kodun kopyalanması, dağıtılması, değiştirilmesi veya ticari/akademik projelerde kullanılması yasaktır.

## Veri Kullanımı ve Gizliliği

Bu projede kullanılan medikal görüntü verileri (.nrrd, .csv), hasta gizliliği ve etik kurallar gereği **bu repoda bulunmamaktadır ve paylaşıma açık değildir.** Bu script'lerin amacı, benzer veri setlerine sahip diğer araştırmacılara bir metodoloji ve pipeline sunmaktır.
