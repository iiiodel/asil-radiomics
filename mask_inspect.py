# 1. GEREKLİ AYAR: Matplotlib'in interaktif backend'ini ayarlıyoruz.
import matplotlib

# 2. Gerekli kütüphaneler
import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt
import os

class InteractiveViewer:
    """
    3D medikal görüntüleri interaktif olarak incelemek için geliştirilmiş sınıf.
    Maske toggle, dilim değiştirme ve piksel değerlerini hem ekranda hem konsolda
    gösterme özellikleri içerir.
    """
    def __init__(self, scan_np, mask_np):
        # Verileri ve temel bilgileri sakla
        self.scan_np = scan_np
        self.mask_np = mask_np
        self.is_mask_multichannel = self.mask_np.ndim == 4
        self.num_slices = scan_np.shape[0]
        self.slice_index = self.num_slices // 2
        
        # Durum değişkenleri
        self.show_mask = True
        self.last_info_text = "Değerleri görmek için fareyi gezdirin..." # Son bilgiyi saklamak için

        # Matplotlib figür ve eksenlerini oluştur
        self.fig, self.ax = plt.subplots(1, 1, figsize=(10, 10))
        
        # Olayları (event) ilgili fonksiyonlara bağlıyoruz
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

        # Başlangıç görüntüsünü ve bilgi kutusunu çiz
        self.update_plot()

    def setup_info_text(self):
        """Sadece bir kez çalışacak olan, sabit metin kutusu gibi ayarları yapar."""
        # Sol alt köşeye, güncellenecek bilgi kutusunu yerleştir
        self.info_text = self.ax.text(0.02, 0.02, '',
                                      transform=self.ax.transAxes,
                                      color='white', fontsize=10,
                                      bbox=dict(facecolor='black', alpha=0.7),
                                      verticalalignment='bottom')

    def update_plot(self):
        """Görüntüyü mevcut dilim indeksi ve maske görünürlüğüne göre günceller."""
        scan_slice = self.scan_np[self.slice_index, :, :]
        self.ax.clear()
        self.ax.imshow(scan_slice, cmap='gray')

        if self.show_mask:
            if self.is_mask_multichannel:
                mask_slice = self.mask_np[self.slice_index, :, :, :]
                alpha_channel = np.ones(mask_slice.shape[:-1]) * 0.5
                background_pixels = (mask_slice.sum(axis=2) == 0)
                alpha_channel[background_pixels] = 0
                rgba_mask = np.dstack((mask_slice, alpha_channel))
                self.ax.imshow(rgba_mask)
            else:
                mask_slice = self.mask_np[self.slice_index, :, :]
                masked_mask = np.ma.masked_where(mask_slice == 0, mask_slice)
                self.ax.imshow(masked_mask, cmap='autumn', alpha=0.5)

        mask_status = "Açık" if self.show_mask else "Kapalı"
        self.ax.set_title(f'Kesit: {self.slice_index + 1}/{self.num_slices} | Maske [M]: {mask_status}')
        
        # Bilgi kutusunu yeniden oluştur ve son bilgiyi yazdır
        self.setup_info_text()
        self.info_text.set_text(self.last_info_text)

        self.ax.axis('off')
        self.fig.canvas.draw_idle()

    def on_scroll(self, event):
        """Fare tekerleği ile dilim değiştirir."""
        if event.button == 'up': self.slice_index = min(self.slice_index + 1, self.num_slices - 1)
        elif event.button == 'down': self.slice_index = max(self.slice_index - 1, 0)
        self.update_plot()

    def on_key_press(self, event):
        """Klavye tuşları ile dilim değiştirir veya maskeyi açıp kapatır."""
        key = event.key.lower()
        if key == 'm': self.show_mask = not self.show_mask
        elif key in ['up', 'k']: self.slice_index = min(self.slice_index + 1, self.num_slices - 1)
        elif key in ['down', 'j']: self.slice_index = max(self.slice_index - 1, 0)
        self.update_plot()
        
    def on_motion(self, event):
        """Fare hareketi ile piksel değerlerini bilgi kutusunda ve konsolda gösterir."""
        if event.inaxes != self.ax: return
        
        x, y = int(event.xdata), int(event.ydata)
        
        if 0 <= y < self.scan_np.shape[1] and 0 <= x < self.scan_np.shape[2]:
            scan_val = self.scan_np[self.slice_index, y, x]
            mask_val = self.mask_np[self.slice_index, y, x]
            
            # Bilgi kutusunun metnini oluştur ve sakla
            info_str = (f"Koor(Y,X): ({y}, {x})\n"
                        f"Tarama Değeri: {scan_val:.2f}\n"
                        f"Maske Değeri: {mask_val}")
            self.last_info_text = info_str
            self.info_text.set_text(info_str)
            
            # Eğer maske çok kanallıysa ve piksel arka plan değilse konsola yazdır
            if self.is_mask_multichannel and np.any(mask_val):
                print(f"Konsol -> Koor({y},{x}): Maske Değeri = {mask_val}")

            self.fig.canvas.draw_idle()

def launch_interactive_viewer(scan_path, mask_path):
    """Verilen yollardan görüntüleri yükler ve interaktif görüntüleyiciyi başlatır."""
    print("--- İnteraktif Görüntüleyici Başlatılıyor... ---")
    if not (os.path.exists(scan_path) and os.path.exists(mask_path)):
        print("HATA: Gerekli dosyalar bulunamadı."); return
        
    try:
        scan_sitk = sitk.ReadImage(scan_path, sitk.sitkFloat32)
        mask_sitk = sitk.ReadImage(mask_path)
        
        if scan_sitk.GetNumberOfComponentsPerPixel() > 1:
            scan_sitk = sitk.VectorIndexSelectionCast(scan_sitk, 0, sitk.sitkFloat32)

        scan_np = sitk.GetArrayFromImage(scan_sitk)
        mask_np = sitk.GetArrayFromImage(mask_sitk)
        
        # --- YENİ KONTROL BURADA ---
        # Maskenin çok kanallı olup olmadığını başlangıçta bir kez kontrol et ve yazdır.
        if mask_np.ndim == 4:
            print("\n[DİKKAT] Yüklenen maske dosyası ÇOK KANALLI (Multi-channel) bir yapıya sahip.")
        
        print("\n--- İnteraktif Görüntüleyici Kontrolleri ---")
        print(" - Fare Tekerleği / Klavye (↑/↓, K/J): Dilim değiştir")
        print(" - M Tuşu: Maskeyi Aç/Kapa (Toggle)")
        print(" - Fareyi Gezdir: Piksel değerlerini sol alttaki kutuda gör")
        
        viewer = InteractiveViewer(scan_np, mask_np)
        plt.show()

    except Exception as e:
        print(f"İnteraktif görüntüleyici başlatılırken hata: {e}")

# --- KULLANIM ---
if __name__ == '__main__':
    patient_folder = 'data/structured/DURİYE YAYLA PRE-KRT T2'
    scan_dosya_yolu = os.path.join(patient_folder, 'scan.nrrd')
    mask_dosya_yolu = os.path.join(patient_folder, 'segmentation.nrrd')

    launch_interactive_viewer(scan_dosya_yolu, mask_dosya_yolu)