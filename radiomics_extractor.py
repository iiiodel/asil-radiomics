import os
import pandas as pd
import SimpleITK as sitk
from radiomics import featureextractor
import logging

# --- Konsol Çıktısını Düzenleme ---
# PyRadiomics normalde çalıştığı her adımla ilgili çok detaylı bilgi basar.
# Bu, konsolun okunmasını zorlaştırabilir. Bu satır ile sadece ciddi HATA (ERROR) mesajlarını
# göstermesini, diğer bilgilendirme mesajlarını gizlemesini sağlıyoruz.
logger = logging.getLogger("radiomics")
logger.setLevel(logging.ERROR)

# --- Ana Fonksiyon ---
def extract_radiomics_features(data_folder_path):
    """
    Belirtilen klasör yapısından radyomik özellikleri çıkarır.

    Bu fonksiyon, dağınık bir veri setini alır, olası veri formatı hatalarını
    (örn: çok kanallı görüntüler) otomatik olarak düzeltir ve hem her hasta için
    ayrı ayrı hem de tüm hastalar için birleşik bir CSV sonuç dosyası üretir.

    Args:
        data_folder_path (str): İçinde hasta klasörlerinin bulunduğu ana veri klasörünün yolu.
    """
    # --- 1. Radyomik Özellik Çıkarıcının (Extractor) Ayarlanması ---
    # PyRadiomics'e hangi ayarlarla çalışacağını söylediğimiz bölüm.
    # Ayarları bir sözlük (dictionary) yapısı içinde tanımlıyoruz.
    # ÖNEMLİ DÜZELTME: 'force2D' ve 'label' gibi parametreler, 'setting' anahtarı altında olmalıdır.
    settings = {
        'setting': {
            'force2D': False,  # Görüntülerimiz 3D olduğu için bu ayar 'False' olmalı. Eğer 2D analiz yapsaydık 'True' olurdu.
            'label': 1         # Segmentasyon (.nrrd) dosyasındaki tümör etiketinin sayısal değeri. Genellikle 1'dir.
                               # Eğer maskenizde farklı değerler varsa (örn: 2, 3), bu sayıyı değiştirmeniz gerekir.
        }
    }
    
    # Özellik çıkarıcıyı (extractor) yukarıdaki ayarlarla başlatıyoruz.
    extractor = featureextractor.RadiomicsFeatureExtractor(settings)
    
    # Mümkün olan TÜM özellikleri çıkarmasını istiyoruz.
    # Bu iki satır, Shape, First Order, GLCM, GLSZM gibi tüm özellik sınıflarını ve
    # Wavelet, LoG gibi tüm dönüştürülmüş görüntü tiplerini analize dahil eder.
    # Sonuç olarak 400 yerine 1000'in üzerinde özellik çıkarılmasını sağlar.
    extractor.enableAllImageTypes()
    extractor.enableAllFeatures()

    print("Radyomik özellik çıkarıcı, tüm özellikler etkinleştirilmiş şekilde başlatıldı.")
    
    # Tüm hastaların sonuçlarını döngü bittikten sonra birleştirmek için boş bir liste oluşturuyoruz.
    all_patients_features_list = []

    # --- 2. Veri Klasöründe Dolaşma ve İşlemler ---
    print(f"\n'{data_folder_path}' klasörü taranıyor...")

    # Belirtilen yolun bir klasör olup olmadığını kontrol edelim.
    if not os.path.isdir(data_folder_path):
        print(f"HATA: Belirtilen '{data_folder_path}' yolu bir klasör değil veya bulunamadı.")
        return

    # Ana veri klasöründeki her bir öğe (hasta klasörü) için bir döngü başlatıyoruz.
    # sorted() ile klasörlerin isme göre sıralı işlenmesini sağlıyoruz.
    for patient_folder_name in sorted(os.listdir(data_folder_path)):
        # Tam klasör yolunu oluşturuyoruz. os.path.join kullanmak, kodu Windows/Linux/Mac uyumlu yapar.
        patient_folder_path = os.path.join(data_folder_path, patient_folder_name)

        # Eğer işlediğimiz öğe bir dosya değil de bir klasör ise devam ediyoruz.
        if os.path.isdir(patient_folder_path):
            patient_id = patient_folder_name
            print(f"\nİşleniyor: Hasta ID -> {patient_id}")

            image_path = os.path.join(patient_folder_path, 'scan.nrrd')
            mask_path = os.path.join(patient_folder_path, 'segmentation.nrrd')

            # Gerekli 'scan.nrrd' ve 'segmentation.nrrd' dosyaları hasta klasöründe var mı diye kontrol et.
            if not os.path.exists(image_path) or not os.path.exists(mask_path):
                print(f"  UYARI: '{patient_id}' klasöründe gerekli NRRD dosyaları bulunamadı. Bu hasta atlanıyor.")
                continue # Bu hastayı atla ve döngüde bir sonrakine geç.

            # Hata yönetimi: Bir hastanın verisi bozuksa bile programın çökmesini engeller.
            try:
                # --- 3. ÖN İŞLEME: Görüntü Formatı Kontrolü ve Düzeltmesi ---
                # Bu bölüm, "Pixel type... not supported" hatasını çözmek için eklendi.
                # Görüntüleri doğrudan dosya yolundan değil, SimpleITK nesnesi olarak yüklüyoruz.
                image = sitk.ReadImage(image_path)
                mask = sitk.ReadImage(mask_path)

                # Görüntünün piksel başına bileşen sayısını kontrol ediyoruz.
                # Eğer 1'den büyükse, bu bir vektör (çok kanallı, örn: RGB) görüntüdür.
                if image.GetNumberOfComponentsPerPixel() > 1:
                    print(f"  BİLGİ: Scan çok kanallı. Radyomik analiz için tek kanala dönüştürülüyor...")
                    # Görüntüyü tek kanala dönüştürüyoruz. Bunun için ilk kanalı (index 0) seçiyoruz.
                    # Bu, 3D Slicer gibi yazılımların arka planda yaptığı işlemin aynısıdır.
                    # sitk.sitkInt16, medikal görüntüler için yaygın ve güvenli bir piksel türü olduğu için onu seçiyoruz.
                    image = sitk.VectorIndexSelectionCast(image, 0, sitk.sitkInt16)
                
                # --- 4. Radyomik Özelliklerin Çıkarılması ---
                # Artık extractor'a dosya yolları yerine, kontrol edip düzelttiğimiz
                # SimpleITK görüntü nesnelerini veriyoruz.
                result = extractor.execute(image, mask)

                # --- 5. Sonuçların İşlenmesi ve Kaydedilmesi ---
                # extractor.execute'dan dönen sonuçlar, özellikler dışında diagnostik bilgiler de içerir.
                # Sadece özellik olanları (başında 'diagnostics' olmayanları) seçiyoruz.
                feature_values = {key: val for key, val in result.items() if not key.startswith('diagnostics')}
                
                # Hangi hastaya ait olduğunu bilmek için, sözlüğe 'PatientID' anahtarını ekliyoruz.
                feature_values['PatientID'] = patient_id

                print(f"  -> Başarılı: {len(feature_values) - 1} adet radyomik özellik çıkarıldı.")

                # Her hasta için bireysel CSV dosyası oluşturuyoruz.
                # Tek satırlık bir veri için en kolay yol, tek elemanlı bir listeyi DataFrame'e çevirmektir.
                df_patient = pd.DataFrame([feature_values])
                
                # Daha okunaklı olması için 'PatientID' sütununu en başa taşıyoruz.
                id_col = df_patient.pop('PatientID')
                df_patient.insert(0, 'PatientID', id_col)

                # Bireysel CSV dosyasını, ilgili hastanın kendi klasörünün içine kaydediyoruz.
                individual_csv_path = os.path.join(patient_folder_path, f'{patient_id}_radiomics_features.csv')
                df_patient.to_csv(individual_csv_path, index=False)
                print(f"  -> Bireysel CSV kaydedildi: {individual_csv_path}")
                
                # Bu hastanın özelliklerini, en sonda birleştireceğimiz ana listeye ekliyoruz.
                all_patients_features_list.append(feature_values)

            except Exception as e:
                # Döngü sırasında herhangi bir hastada beklenmedik bir hata olursa,
                # programın çökmesini engeller, hatayı basar ve bir sonraki hastaya geçer.
                print(f"  HATA: '{patient_id}' işlenirken bir sorun oluştu: {e}")

    # --- 6. Tüm Sonuçların Birleştirilip Ana CSV Dosyasının Oluşturulması ---
    # Döngü bittikten sonra, eğer en az bir hasta başarıyla işlendiyse devam et.
    if not all_patients_features_list:
        print("\nHiçbir hasta başarıyla işlenemedi. Ana CSV dosyası oluşturulmuyor.")
        return

    print("\nTüm hastalar işlendi. Şimdi tüm verileri birleştiren ana CSV dosyası oluşturuluyor...")
    
    # Her hasta için oluşturduğumuz sözlükleri içeren listeyi, tek bir büyük DataFrame'e dönüştürüyoruz.
    master_df = pd.DataFrame(all_patients_features_list)
    
    # Ana DataFrame'de de PatientID'yi en başa alalım.
    id_col = master_df.pop('PatientID')
    master_df.insert(0, 'PatientID', id_col)
    
    # Ana CSV dosyasını, ana veri klasörünün içine kaydediyoruz.
    master_csv_path = os.path.join(data_folder_path, 'ALL_PATIENTS_radiomics_features.csv')
    master_df.to_csv(master_csv_path, index=False)

    print(f"\nİŞLEM TAMAMLANDI!")
    print(f"Tüm hastaların birleşik sonuçları şu dosyaya kaydedildi: {master_csv_path}")


# --- KODUN KULLANIMI ---
# LÜTFEN BU SATIRI KENDİ KLASÖR YOLUNUZLA DEĞİŞTİRİN:
# Bu, içinde 'scan.nrrd' ve 'segmentation.nrrd' dosyalarını barındıran
# hasta klasörlerinin bulunduğu ana klasörün yolu olmalıdır.
# Örnek: main_data_folder = "C:/Users/Taha/Desktop/YumurtalikKanseri/Duzenlenmis_Veri"
main_data_folder = 'data/structured'

# Hazırladığımız ana fonksiyonu, belirttiğimiz klasör yoluyla çağırarak işlemi başlatıyoruz.
extract_radiomics_features(main_data_folder)