import customtkinter as ctk
from tkinter import filedialog, messagebox
import os, json, string, random, sys, threading, shutil
import unicodedata
import re

# Modern Tema Ayarları
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class TrigramApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.version = "v0.02"
        self.title(f"ai-tool {self.version}")
        self.geometry("950x700")
        
        self.lang = "TR" # Varsayılan dil
        self.secili_model = None
        self.veri_yolu = ""
        self.calisma_dizini = ""

        # Dil Sözlüğü
        self.translations = {
            "TR": {
                "title": "Model Seçimi",
                "m1_name": "Trigram Modeli\n(Saf Kelime Motoru)",
                "m2_name": "Trigram V2\n(Noktalama Destekli)",
                "m1_desc": "Trigram modeli gramer yapısını öğrenmek için tasarlanmıştır. En hafif modeldir ancak mantık, noktalama ve sayıları içermez.",
                "m2_desc": "Trigram v2 temel algoritmadan farklı olarak noktalama destekler ancak hala sayı ve mantık içermez.",
                "footer": "Diğer model mimarileri üstünde çalışıyoruz.",
                "config": "Yapılandırması",
                "btn_data": "1. Veri Seti Seç (.txt)",
                "btn_folder": "2. Çıktı Klasörü Seç",
                "btn_train": "MODELİ EĞİT VE DERLE",
                "log_start": "Eğitim algoritması başlatıldı...",
                "log_unicode": "Unicode temizliği yapılıyor...",
                "log_regex": "Regex ile semboller ayrıştırılıyor...",
                "log_compile": "Derleme motoru (PyInstaller) hazırlanıyor...",
                "log_success": "--- İŞLEM BAŞARIYLA TAMAMLANDI ---",
                "err_missing": "Dosya ve Klasör seçimleri eksik!",
                "msg_success": "Uygulama oluşturuldu: ",
                "menu": "← Menü"
            },
            "EN": {
                "title": "Model Selection",
                "m1_name": "Trigram Model\n(Pure Word Engine)",
                "m2_name": "Trigram V2\n(Punctuation Support)",
                "m1_desc": "The Trigram model is designed to learn grammar structure. It's the lightest model but lacks logic, punctuation, and numbers.",
                "m2_desc": "Trigram v2 supports punctuation unlike the base algorithm, but still lacks logic and numbers.",
                "footer": "We are working on other model architectures.",
                "config": "Configuration",
                "btn_data": "1. Select Dataset (.txt)",
                "btn_folder": "2. Select Output Folder",
                "btn_train": "TRAIN AND COMPILE MODEL",
                "log_start": "Training algorithm started...",
                "log_unicode": "Cleaning Unicode characters...",
                "log_regex": "Parsing symbols with Regex...",
                "log_compile": "Preparing compiler (PyInstaller)...",
                "log_success": "--- PROCESS COMPLETED SUCCESSFULLY ---",
                "err_missing": "File and Folder selections are missing!",
                "msg_success": "Application created at: ",
                "menu": "← Menu"
            }
        }

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.setup_ana_menu()

    def t(self, key):
        return self.translations[self.lang][key]

    def toggle_lang(self):
        self.lang = "EN" if self.lang_switch.get() else "TR"
        self.setup_ana_menu()

    def setup_ana_menu(self):
        self.temizle_ekran()
        
        # Dil Switch
        self.lang_switch = ctk.CTkSwitch(self.main_container, text="TR / EN", command=self.toggle_lang)
        self.lang_switch.place(x=20, y=20)
        if self.lang == "EN": self.lang_switch.select()

        self.sol_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.sol_frame.pack(padx=20, pady=60, fill="both", expand=True)

        ctk.CTkLabel(self.sol_frame, text=self.t("title"), font=("Arial", 28, "bold")).pack(pady=20)

        # Model 1 Buton
        self.m1_btn = ctk.CTkButton(self.sol_frame, text=self.t("m1_name"),
                                       fg_color="#dbdbdb", text_color="black", hover_color="#cccccc",
                                       height=100, width=400, font=("Arial", 16),
                                       command=lambda: self.select_model("V1"))
        self.m1_btn.pack(pady=10)
        
        # Model 2 Buton
        self.m2_btn = ctk.CTkButton(self.sol_frame, text=self.t("m2_name"),
                                       fg_color="#dbdbdb", text_color="black", hover_color="#cccccc",
                                       height=100, width=400, font=("Arial", 16),
                                       command=lambda: self.select_model("V2"))
        self.m2_btn.pack(pady=10)

        ctk.CTkLabel(self.sol_frame, text=self.t("footer"), font=("Arial", 12, "italic")).pack(pady=20)

    def setup_ayar_ekrani(self):
        self.temizle_ekran()
        self.ayar_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.ayar_frame.pack(padx=50, pady=20, fill="both", expand=True)

        ctk.CTkButton(self.ayar_frame, text=self.t("menu"), width=70, fg_color="gray", 
                      command=self.setup_ana_menu).place(x=20, y=20)

        model_label = "Trigram V1" if self.secili_model == "V1" else "Trigram V2"
        self.sag_baslik = ctk.CTkLabel(self.ayar_frame, text=f"{model_label} {self.t('config')}", font=("Arial", 22, "bold"))
        self.sag_baslik.pack(pady=(40, 5))

        # Açıklama Metni
        desc_text = self.t("m1_desc") if self.secili_model == "V1" else self.t("m2_desc")
        ctk.CTkLabel(self.ayar_frame, text=desc_text, font=("Arial", 12), wraplength=600, text_color="gray").pack(pady=5)

        ctk.CTkButton(self.ayar_frame, text=self.t("btn_data"), height=45, fg_color="#dbdbdb", 
                      text_color="black", command=self.sec_veri_dosyasi).pack(pady=10, padx=150, fill="x")

        ctk.CTkButton(self.ayar_frame, text=self.t("btn_folder"), height=45, fg_color="#dbdbdb", 
                      text_color="black", command=self.sec_calisma_dizini).pack(pady=10, padx=150, fill="x")

        self.btn_basla = ctk.CTkButton(self.ayar_frame, text=self.t("btn_train"), 
                                       fg_color="#A020F0", hover_color="#7D1BB8", 
                                       height=55, font=("Arial", 14, "bold"),
                                       command=self.egitim_thread_baslat)
        self.btn_basla.pack(pady=20)

        self.log_text = ctk.CTkTextbox(self.ayar_frame, fg_color="black", text_color="#00FF00", font=("Consolas", 12))
        self.log_text.pack(pady=10, padx=40, fill="both", expand=True)

    def temizle_ekran(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def select_model(self, m_type):
        self.secili_model = m_type
        self.setup_ayar_ekrani()

    def log_yaz(self, mesaj):
        if hasattr(self, 'log_text'):
            self.log_text.insert("end", f"> {mesaj}\n")
            self.log_text.see("end")
            self.update_idletasks()

    def sec_veri_dosyasi(self):
        yol = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if yol: self.veri_yolu = yol; self.log_yaz(f"File: {os.path.basename(yol)}")

    def sec_calisma_dizini(self):
        yol = filedialog.askdirectory()
        if yol: self.calisma_dizini = yol; self.log_yaz(f"Path: {yol}")

    def egitim_thread_baslat(self):
        if not self.veri_yolu or not self.calisma_dizini:
            messagebox.showwarning("Error", self.t("err_missing"))
            return
        self.btn_basla.configure(state="disabled")
        threading.Thread(target=self.egitimi_baslat, daemon=True).start()

    def egitimi_baslat(self):
        try:
            self.log_yaz(self.t("log_start"))
            with open(self.veri_yolu, 'r', encoding='utf-8') as f:
                metin = f.read().lower()
            
            hafiza = {}
            
            if self.secili_model == "V1":
                self.log_yaz(self.t("log_unicode"))
                def sadece_harf_ve_bosluk(char):
                    kategori = unicodedata.category(char)
                    return kategori.startswith('L') or kategori.startswith('Z')
                temiz_metin = "".join(char for char in metin if sadece_harf_ve_bosluk(char))
                kelimeler = re.sub(r'\s+', ' ', temiz_metin).strip().split()
                
                for i in range(len(kelimeler) - 2):
                    k = f"{kelimeler[i]} {kelimeler[i+1]}"
                    hafiza.setdefault(k, []).append(kelimeler[i+2])
            
            else: # MODEL V2 (Noktalama Destekli)
                self.log_yaz(self.t("log_regex"))
                cumleler = re.split(r'[.!?]+', metin)
                for cumle in cumleler:
                    # Kelimeler ve semboller, sayılar hariç
                    raw_tokens = re.findall(r"\w+|[^\w\s]", cumle)
                    temiz_tokens = []
                    for t in raw_tokens:
                        if t.isdigit(): continue
                        kat = unicodedata.category(t[0])
                        if kat.startswith('L') or kat.startswith('S') or kat.startswith('P'):
                            temiz_tokens.append(t)
                    
                    if len(temiz_tokens) < 3: continue
                    for i in range(len(temiz_tokens) - 2):
                        anahtar = f"{temiz_tokens[i]} {temiz_tokens[i+1]}"
                        hafiza.setdefault(anahtar, []).append(temiz_tokens[i+2])

            cikti_yolu = os.path.join(self.calisma_dizini, "model_cikti")
            os.makedirs(cikti_yolu, exist_ok=True)
            
            with open(os.path.join(cikti_yolu, "trigram.json"), "w", encoding="utf-8") as f:
                json.dump(hafiza, f, ensure_ascii=False, indent=4)

            self.create_test_script(cikti_yolu, self.secili_model)
            self.log_yaz(self.t("log_compile"))
            
            # PyInstaller Süreci
            import PyInstaller.__main__
            import customtkinter
            ctk_path = os.path.dirname(customtkinter.__file__)
            args = [
                os.path.join(cikti_yolu, "test_app.py"),
                '--onefile', '--noconsole',
                f'--distpath={cikti_yolu}',
                f'--workpath={os.path.join(self.calisma_dizini, "build")}',
                f'--add-data={ctk_path}{os.pathsep}customtkinter',
                '--clean'
            ]
            PyInstaller.__main__.run(args)

            self.log_yaz(self.t("log_success"))
            messagebox.showinfo("Success", f"{self.t('msg_success')}\n{cikti_yolu}")

        except Exception as e:
            self.log_yaz(f"Hata: {str(e)}")
        finally:
            self.btn_basla.configure(state="normal")

    def create_test_script(self, yol, model_type):
        # V2 için gelişmiş formatlama algoritmasını gömüyoruz
        post_process = ""
        if model_type == "V2":
            post_process = """
    def metni_formatla(self, token_listesi):
        if not token_listesi: return ""
        cumle_sonu = {".", "!", "?", "…"}
        sol_yapiskan = {"(", "[", "{", "“", "‘"}
        sag_yapiskan = {")", "]", "}", "”", "’", ".", ",", "!", "?", ":", ";", "…"}
        ozel_kesme = {"'", "’"}
        cikti = []; buyuk_harf_yap = True; tirnak_acik = False
        for i, token in enumerate(token_listesi):
            if buyuk_harf_yap:
                token = token.capitalize(); buyuk_harf_yap = False
            if i == 0: cikti.append(token)
            else:
                onceki = token_listesi[i-1]
                if token in sag_yapiskan or onceki in sol_yapiskan or onceki in ozel_kesme or token in ozel_kesme:
                    cikti.append(token)
                else: cikti.append(" " + token)
            if token == "“": tirnak_acik = True
            if token == "”": tirnak_acik = False
            if token in cumle_sonu: buyuk_harf_yap = True
        final_metin = "".join(cikti)
        if tirnak_acik: final_metin += "”"
        return final_metin
"""
            üret_logic = """
        tokenler = re.findall(r"\\w+|[^\\w\\s]", girdi_ham)
        if len(tokenler) < 2: return
        for _ in range(limit):
            anahtar = f"{tokenler[-2]} {tokenler[-1]}"
            if anahtar in self.hafiza: tokenler.append(random.choice(self.hafiza[anahtar]))
            else: break
        self.cikti.insert("end", self.metni_formatla(tokenler))"""
        else:
            üret_logic = """
        metin = girdi_ham.split()
        if len(metin) < 2: return
        for _ in range(limit):
            anahtar = f"{metin[-2]} {metin[-1]}"
            if anahtar in self.hafiza: metin.append(random.choice(self.hafiza[anahtar]))
            else: break
        self.cikti.insert("end", " ".join(metin))"""

        script = f"""import customtkinter as ctk
import json, random, os, sys, re
def get_resource_path(filename):
    if getattr(sys, 'frozen', False): return os.path.join(os.path.dirname(sys.executable), filename)
    return os.path.join(os.path.dirname(__file__), filename)

class TestArayuz(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Model Test Merkezi {model_type}")
        self.geometry("600x550")
        try:
            with open(get_resource_path('trigram.json'), 'r', encoding='utf-8') as f: self.hafiza = json.load(f)
        except: self.destroy(); return
        ctk.CTkLabel(self, text="Baslangic Kelimeleri:").pack(pady=10)
        self.entry = ctk.CTkEntry(self, width=400); self.entry.pack(); self.entry.insert(0, "bir gün")
        self.slider = ctk.CTkSlider(self, from_=20, to=500); self.slider.pack(pady=20); self.slider.set(100)
        ctk.CTkButton(self, text="Üret", command=self.üret).pack()
        self.cikti = ctk.CTkTextbox(self, width=540, height=300, wrap="word"); self.cikti.pack(pady=20)

    def üret(self):
        girdi_ham = self.entry.get().lower()
        limit = int(self.slider.get())
        self.cikti.delete("1.0", "end")
        {üret_logic}
{post_process}

if __name__ == "__main__":
    app = TestArayuz()
    app.mainloop()
"""
        with open(os.path.join(yol, "test_app.py"), "w", encoding="utf-8") as f:
            f.write(script)

if __name__ == "__main__":
    app = TrigramApp()
    app.mainloop()
