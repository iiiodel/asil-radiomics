# asil-radiomics
A Python-based pipeline for extracting and analyzing radiomic features from ovarian cancer NRRD scans. This project includes scripts for data structuring, exhaustive feature extraction using PyRadiomics, and interactive data visualization.

![Python](https://img.shields.io/badge/python-3.9-blue.svg)

## 🧬 Proje Hakkında

Bu proje, yumurtalık kanserine ait medikal görüntülerden (NRRD formatında) kapsamlı radyomik özelliklerin çıkarılması için uçtan uca bir çözüm sunmaktadır. Pipeline, dağınık haldeki ham verilerin organize edilmesi, PyRadiomics kütüphanesi ile 1500'den fazla özelliğin çıkarılması, sonuçların düzenlenmesi ve verilerin interaktif olarak incelenmesi adımlarını içerir.

## 📂 Proje Yapısı

Projenin ana klasör yapısı aşağıdaki gibidir. `data` klasörü ve içeriği, `.gitignore` dosyası ile versiyon kontrolü dışında tutulmuştur.

```
asil-radiomics/
│
├── data/
│   ├── raw/                # Ham verilerinizi buraya koyun
│   ├── structured/         # 1. betiğin oluşturduğu düzenli veri klasörü
│   └── Radyomik_CSV_Ciktilari/ # 3. betiğin oluşturduğu CSV çıktı klasörü
│
├── data_organizer.py             # Ham verileri yapılandıran betik
├── radiomics_extractor.py        # Radyomik özellikleri çıkaran betik
├── csv_organizer.py              # Üretilen CSV'leri toplayan betik
├── mask_inspector.py             # Tarama/maske inceleme aracı
│
├── .gitignore
├── environment.yml
└── README.md
```

## 🛠️ Kurulum

1.  **Depoyu Klonlayın:**
    ```bash
    git clone [https://github.com/kullanici_adiniz/asil-radiomics.git](https://github.com/kullanici_adiniz/asil-radiomics.git)
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

## 📋 Kullanım Adımları

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

`data_organizer.py` betiği, ham verileri okur ve `data/structured/` klasörünü analiz için hazırlar.

```bash
python data_organizer.py
```

#### Adım 2: Radyomik Özellik Çıkarma

`radiomics_extractor.py` betiği, yapılandırılmış verilerden radyomik özellikleri hesaplar ve sonuçları `data/structured/` içine yazar.

```bash
python radiomics_extractor.py
```

#### Adım 3: CSV Çıktılarını Toplama

`csv_organizer.py` betiği, üretilen tüm CSV dosyalarını `data/Radyomik_CSV_Ciktilari/` klasörüne taşır.

```bash
python csv_organizer.py
```

#### Adım 4 (Opsiyonel): Veri Kalite Kontrolü

`mask_inspector.py` ile herhangi bir hastanın verisini interaktif olarak inceleyebilirsiniz.

```bash
python mask_inspector.py
```

## ⚖️ Lisans

Bu projede bir açık kaynak lisansı belirtilmemiştir. Bu nedenle, varsayılan uluslararası telif hakkı yasaları geçerlidir ve **tüm hakları proje sahibine aittir.** Proje sahibinden yazılı ve açık bir izin alınmadan bu kodun kopyalanması, dağıtılması, değiştirilmesi veya ticari/akademik projelerde kullanılması yasaktır.

## Veri Kullanımı ve Gizliliği

Bu projede kullanılan medikal görüntü verileri (.nrrd, .csv), hasta gizliliği ve etik kurallar gereği **bu repoda bulunmamaktadır ve paylaşıma açık değildir.** Bu betiklerin amacı, benzer veri setlerine sahip diğer araştırmacılara bir metodoloji ve pipeline sunmaktır.
