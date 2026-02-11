import customtkinter as ctk
from tkinter import filedialog, messagebox
import os, json, string, random, sys, threading, shutil

# Modern Tema Ayarları
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class TrigramApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ai-tool v0.01 tr")
        self.geometry("900x650")
        
        self.secili_model = None
        self.veri_yolu = ""
        self.calisma_dizini = ""

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.setup_ana_menu()

    def setup_ana_menu(self):
        self.temizle_ekran()
        self.sol_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.sol_frame.pack(side="left", padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(self.sol_frame, text="Model Seçimi", font=("Arial", 24, "bold")).pack(pady=30)

        self.model_btn = ctk.CTkButton(self.sol_frame, 
                                       text="Trigram Modeli\n(Dahili Derleme Motoru)",
                                       fg_color="#dbdbdb", text_color="black", hover_color="#cccccc",
                                       height=150, width=350, font=("Arial", 16),
                                       command=self.select_trigram)
        self.model_btn.pack(pady=10)
        
        ctk.CTkLabel(self.sol_frame, text="Diğer model mimarileri üstünde çalışıyoruz.", 
                     font=("Arial", 12, "italic")).pack(pady=20)

    def setup_ayar_ekrani(self):
        self.temizle_ekran()
        self.ayar_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.ayar_frame.pack(padx=80, pady=20, fill="both", expand=True)

        ctk.CTkButton(self.ayar_frame, text="← Menü", width=70, fg_color="gray", 
                      command=self.setup_ana_menu).place(x=20, y=20)

        self.sag_baslik = ctk.CTkLabel(self.ayar_frame, text=f"{self.secili_model} Yapılandırması", font=("Arial", 20, "bold"))
        self.sag_baslik.pack(pady=(50, 20))

        ctk.CTkButton(self.ayar_frame, text="1. Veri Seti Seç (.txt)", height=45, fg_color="#dbdbdb", 
                      text_color="black", command=self.sec_veri_dosyasi).pack(pady=10, padx=100, fill="x")

        ctk.CTkButton(self.ayar_frame, text="2. Çıktı Klasörü Seç", height=45, fg_color="#dbdbdb", 
                      text_color="black", command=self.sec_calisma_dizini).pack(pady=10, padx=100, fill="x")

        self.btn_basla = ctk.CTkButton(self.ayar_frame, text="MODELİ EĞİT VE DERLE", 
                                       fg_color="#A020F0", hover_color="#7D1BB8", 
                                       height=55, font=("Arial", 14, "bold"),
                                       command=self.egitim_thread_baslat)
        self.btn_basla.pack(pady=30)

        self.log_text = ctk.CTkTextbox(self.ayar_frame, fg_color="black", text_color="#00FF00", font=("Consolas", 12))
        self.log_text.pack(pady=10, padx=50, fill="both", expand=True)

    def temizle_ekran(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def select_trigram(self):
        self.secili_model = "Trigram"
        self.setup_ayar_ekrani()

    def log_yaz(self, mesaj):
        if hasattr(self, 'log_text'):
            self.log_text.insert("end", f"> {mesaj}\n")
            self.log_text.see("end")
            self.update_idletasks()

    def sec_veri_dosyasi(self):
        yol = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if yol: self.veri_yolu = yol; self.log_yaz(f"Veri: {os.path.basename(yol)}")

    def sec_calisma_dizini(self):
        yol = filedialog.askdirectory()
        if yol: self.calisma_dizini = yol; self.log_yaz(f"Hedef Klasör: {yol}")

    def egitim_thread_baslat(self):
        """Arayüzün donmaması için işlemi ayrı bir kolda çalıştırır."""
        if not self.veri_yolu or not self.calisma_dizini:
            messagebox.showwarning("Hata", "Dosya ve Klasör seçimleri eksik!")
            return
        
        self.btn_basla.configure(state="disabled")
        threading.Thread(target=self.egitimi_baslat, daemon=True).start()

    def egitimi_baslat(self):
        try:
            self.log_yaz("Eğitim algoritması çalıştırılıyor...")
            with open(self.veri_yolu, 'r', encoding='utf-8') as f:
                metin = f.read().lower()
            
            ozel = "“”‘’„…–—" + string.punctuation + string.digits
            tablo = str.maketrans('', '', ozel)
            kelimeler = metin.translate(tablo).split()
            benzersiz = sorted(list(set(kelimeler)))

            # Hafıza Oluşturma
            hafiza = {}
            for i in range(len(kelimeler) - 2):
                k = f"{kelimeler[i]} {kelimeler[i+1]}"
                hafiza.setdefault(k, []).append(kelimeler[i+2])

            cikti_yolu = os.path.join(self.calisma_dizini, "model_cikti")
            os.makedirs(cikti_yolu, exist_ok=True)
            
            with open(os.path.join(cikti_yolu, "trigram.json"), "w", encoding="utf-8") as f:
                json.dump(hafiza, f, ensure_ascii=False, indent=4)

            self.create_test_script(cikti_yolu)

            # DAHİLİ DERLEME MOTORU (PyInstaller import ediliyor)
            self.log_yaz("Derleme motoru (PyInstaller) hazırlanıyor...")
            
            import PyInstaller.__main__
            import customtkinter
            
            # CustomTkinter'ın dosyalarını EXE'ye dahil etmek için yol alıyoruz
            ctk_path = os.path.dirname(customtkinter.__file__)
            
            args = [
                os.path.join(cikti_yolu, "test1.py"),
                '--onefile',
                '--noconsole',
                f'--distpath={cikti_yolu}',
                f'--workpath={os.path.join(self.calisma_dizini, "build")}',
                f'--specpath={self.calisma_dizini}',
                f'--add-data={ctk_path}{os.pathsep}customtkinter', # Tema ve JSON'ları ekler
                '--clean'
            ]

            # Fırını içeriden çalıştırıyoruz
            PyInstaller.__main__.run(args)

            self.log_yaz("--- İŞLEM BAŞARIYLA TAMAMLANDI ---")
            messagebox.showinfo("Başarılı", f"Uygulama '{cikti_yolu}' klasöründe oluşturuldu.")

        except Exception as e:
            self.log_yaz(f"Hata Oluştu: {str(e)}")
        finally:
            self.btn_basla.configure(state="normal")

    def create_test_script(self, yol):
        script = """import customtkinter as ctk
import json, random, os, sys

def get_resource_path(filename):
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), filename)
    return os.path.join(os.path.dirname(__file__), filename)

class TestArayuz(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Model Test Merkezi")
        self.geometry("600x550")
        
        try:
            with open(get_resource_path('trigram.json'), 'r', encoding='utf-8') as f:
                self.hafiza = json.load(f)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Hata", f"trigram.json bulunamadı!\\n{{e}}")
            self.destroy(); return

        ctk.CTkLabel(self, text="Başlangıç Kelimeleri:", font=("Arial", 14)).pack(pady=10)
        self.entry = ctk.CTkEntry(self, width=400)
        self.entry.pack(pady=5)
        self.entry.insert(0, "bir gün")
        
        self.sinirla_var = ctk.BooleanVar(value=False)
        self.cb = ctk.CTkCheckBox(self, text="Kelime Sayısını Sınırla", variable=self.sinirla_var, command=self.toggle_slider)
        self.cb.pack(pady=15)
        
        self.slider = ctk.CTkSlider(self, from_=10, to=1500)
        self.slider.pack()
        self.slider.set(150)
        self.slider.configure(state="disabled")

        ctk.CTkButton(self, text="Metni Üret", fg_color="#A020F0", height=45, font=("Arial", 14, "bold"), command=self.üret).pack(pady=20)
        self.cikti = ctk.CTkTextbox(self, width=540, height=250, font=("Arial", 13))
        self.cikti.pack(pady=10, padx=20)

    def toggle_slider(self):
        self.slider.configure(state="normal" if self.sinirla_var.get() else "disabled")

    def üret(self):
        metin = self.entry.get().lower().split()
        if len(metin) < 2:
            self.cikti.delete("1.0", "end")
            self.cikti.insert("end", "Lütfen en az 2 kelime girin.")
            return
        
        limit = int(self.slider.get()) if self.sinirla_var.get() else 3000
        
        for _ in range(limit):
            anahtar = f"{metin[-2]} {metin[-1]}"
            if anahtar in self.hafiza:
                metin.append(random.choice(self.hafiza[anahtar]))
            else:
                break
        
        self.cikti.delete("1.0", "end")
        self.cikti.insert("end", " ".join(metin))

if __name__ == "__main__":
    app = TestArayuz()
    app.mainloop()
"""
        with open(os.path.join(yol, "test1.py"), "w", encoding="utf-8") as f:
            f.write(script)

if __name__ == "__main__":
    app = TrigramApp()
    app.mainloop()