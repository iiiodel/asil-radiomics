import os
import shutil

def collect_radiomics_csv(source_dir, destination_dir):
    """
    Belirtilen kaynak klasörden bireysel ve ana radyomik CSV dosyalarını
    toplayıp yeni bir hedef klasöre organize eder.

    Args:
        source_dir (str): İçinde hasta klasörleri ve ana CSV'nin bulunduğu klasör.
                          (Örn: 'data/structured')
        destination_dir (str): Tüm CSV dosyalarının kopyalanacağı yeni hedef klasör.
    """
    print(f"Kaynak Klasör: {source_dir}")
    print(f"Hedef Klasör: {destination_dir}")

    # 1. Ana hedef klasörü oluştur (eğer mevcut değilse)
    os.makedirs(destination_dir, exist_ok=True)
    print(f"'{destination_dir}' klasörü oluşturuldu veya zaten mevcut.")

    # 2. Kaynak klasördeki tüm öğeleri tara
    print("\nDosyalar ve klasörler taranıyor...")
    for item_name in os.listdir(source_dir):
        source_item_path = os.path.join(source_dir, item_name)

        # EĞER ÖĞE BİR KLASÖR İSE (Hasta Klasörü)
        if os.path.isdir(source_item_path):
            # Klasörün içine girip .csv uzantılı dosyayı ara
            for filename in os.listdir(source_item_path):
                if filename.lower().endswith('.csv'):
                    # Hedefte bu hasta için yeni bir klasör oluştur
                    dest_patient_dir = os.path.join(destination_dir, item_name)
                    os.makedirs(dest_patient_dir, exist_ok=True)
                    
                    # CSV dosyasını kopyala
                    source_csv_path = os.path.join(source_item_path, filename)
                    shutil.copy2(source_csv_path, dest_patient_dir)
                    print(f"  -> '{item_name}' klasöründeki '{filename}' kopyalandı.")
                    break # Bu hasta için CSV bulundu, sonraki hastaya geç

        # EĞER ÖĞE BİR DOSYA İSE ve adı ana CSV ile eşleşiyorsa
        elif os.path.isfile(source_item_path) and item_name.lower() == 'all_patients_radiomics_features.csv':
            shutil.copy2(source_item_path, destination_dir)
            print(f"  -> Ana CSV dosyası '{item_name}' kopyalandı.")

    print("\nİşlem tamamlandı!")


# --- KULLANIM ---

# Lütfen bu yolları kendi klasör yapınıza göre güncelleyin.

# 1. İçinde hasta klasörlerinin VE birleştirilmiş ana CSV'nin bulunduğu kaynak klasör
#    Sizin tanımınıza göre bu 'data/structured' klasörü.
source_directory = 'data/structured'

# 2. Tüm CSV'lerin toplanmasını istediğiniz yeni klasörün adı.
#    Bu klasör mevcut değilse, betik tarafından otomatik olarak oluşturulacaktır.
csv_destination_folder = 'data/Radyomik_CSV_Ciktilari'


# Fonksiyonu tanımladığınız yollarla çağırın
collect_radiomics_csv(source_directory, csv_destination_folder)