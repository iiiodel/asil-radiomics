import os
import shutil

def organize_data_for_radiomics(source_dir, dest_dir):
    """
    Dağınık bir veri setini, radyomik analizi için yapılandırılmış bir formata getirir.

    Her hasta klasöründen '.seg.nrrd' dosyasını ve en büyük boyutlu '.nrrd' dosyasını
    alarak hedef klasörde yeni bir yapı oluşturur.

    Args:
        source_dir (str): Dağınık hasta klasörlerinin bulunduğu ana kaynak klasör.
        dest_dir (str): Düzenlenmiş verilerin kaydedileceği ana hedef klasör.
    """
    print(f"Veri düzenleme işlemi başlatıldı.")
    print(f"Kaynak Klasör: {source_dir}")
    print(f"Hedef Klasör: {dest_dir}")

    # 1. Hedef ana klasörü oluştur (eğer mevcut değilse)
    os.makedirs(dest_dir, exist_ok=True)

    # Kaynak klasördeki tüm öğeleri (hasta klasörleri) tara
    for patient_folder_name in os.listdir(source_dir):
        source_patient_dir = os.path.join(source_dir, patient_folder_name)

        # Sadece klasör olanları işleme al
        if os.path.isdir(source_patient_dir):
            print(f"\nİşleniyor: Hasta -> {patient_folder_name}")

            segmentation_source_path = None
            scan_candidates = []

            # Hasta klasöründeki tüm dosyaları tara
            for filename in os.listdir(source_patient_dir):
                file_path = os.path.join(source_patient_dir, filename)

                # 2. Segmentasyon dosyasını bul
                if filename.lower().endswith('.seg.nrrd'):
                    segmentation_source_path = file_path
                    print(f"  -> Segmentasyon dosyası bulundu: {filename}")

                # 3. Potansiyel tarama dosyalarını bul (segmentasyon olmayan .nrrd'ler)
                elif filename.lower().endswith('.nrrd'):
                    file_size = os.path.getsize(file_path)
                    scan_candidates.append((file_path, file_size))
            
            # 4. En büyük tarama dosyasını seç
            if not scan_candidates:
                print(f"  UYARI: {patient_folder_name} içinde '.nrrd' uzantılı tarama dosyası bulunamadı. Atlanıyor.")
                continue
            
            # Boyuta göre en büyük olanı bul
            largest_scan_path, largest_size = max(scan_candidates, key=lambda item: item[1])
            print(f"  -> En büyük tarama dosyası bulundu: {os.path.basename(largest_scan_path)} (Boyut: {largest_size / (1024*1024):.2f} MB)")

            # Segmentasyon dosyasının bulunduğundan emin ol
            if not segmentation_source_path:
                print(f"  UYARI: {patient_folder_name} içinde '.seg.nrrd' uzantılı dosya bulunamadı. Atlanıyor.")
                continue

            # 5. Yeni klasör yapısını oluştur ve dosyaları kopyala
            # Hedefte yeni hasta klasörünü oluştur
            dest_patient_dir = os.path.join(dest_dir, patient_folder_name)
            os.makedirs(dest_patient_dir, exist_ok=True)

            # Hedef dosya yollarını belirle (yeni isimleriyle)
            dest_scan_path = os.path.join(dest_patient_dir, 'scan.nrrd')
            dest_segmentation_path = os.path.join(dest_patient_dir, 'segmentation.nrrd')

            # Dosyaları kopyala ve yeniden adlandır
            shutil.copy2(largest_scan_path, dest_scan_path)
            shutil.copy2(segmentation_source_path, dest_segmentation_path)
            
            print(f"  -> Dosyalar başarıyla '{dest_patient_dir}' klasörüne kopyalandı.")

    print("\nTüm işlemler tamamlandı!")

# --- BETİĞİ KULLANMA ---

# LÜTFEN BU 2 SATIRI DEĞİŞTİRİN:

# 1. Dağınık verilerinizin bulunduğu ana klasörün yolu
# Örnek: "C:/Users/Kullanici/Desktop/Ham_Veriler"
source_folder = 'data/raw/Hastalar' 

# 2. Düzenlenmiş verilerin kaydedileceği yeni klasörün yolu
# Bu klasör mevcut değilse, betik tarafından otomatik olarak oluşturulacaktır.
# Örnek: "C:/Users/Kullanici/Desktop/Duzenlenmis_Veriler"
destination_folder = 'data/structured'


# Fonksiyonu tanımladığınız yollarla çağırın
organize_data_for_radiomics(source_folder, destination_folder)