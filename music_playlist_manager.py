import tkinter as tk
from tkinter import messagebox, ttk, Toplevel, simpledialog
import pygame
import os
import random
# BACKEND YAAAH
class Lagu:
    def __init__(self, judul, file_path):
        self.judul = judul
        self.file_path = file_path
        self.durasi = self._get_durasi_asli()
        self.artis = "Unknown Artist"

    def _get_durasi_asli(self):
        try:
            s = pygame.mixer.Sound(self.file_path)
            return int(s.get_length())
        except:
            return 0
        
    def format_waktu(self, detik_input=None):
        d = detik_input if detik_input is not None else self.durasi
        m = int(d // 60)
        s = int(d % 60)
        return f"{m:02d}:{s:02d}"

class RiwayatStack:
    def __init__(self): self.items = []
    def push(self, lagu): self.items.append(lagu)
    def pop(self): return self.items.pop() if self.items else None

class Pengguna:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.riwayat = RiwayatStack()
        self.playlists = {}

class SistemMusik:
    def __init__(self):
        pygame.mixer.init()
        self.users = {}
        self.user_aktif = None
        self.lagu_sekarang = None
        self.playlist_aktif = []
        self.index_aktif = -1
        self.db_lagu = self._scan_mp3_otomatis()

    def _scan_mp3_otomatis(self):
        lagu_ditemukan = []
        try:
            files = os.listdir('.')
            for f in files:
                if f.endswith(".mp3"):
                    judul = f.replace(".mp3", "").replace("_", " ").title()
                    lagu_ditemukan.append(Lagu(judul, f))
        except:
            pass
        if not lagu_ditemukan:
            return [Lagu("Contoh (Butuh file MP3)", "dummy.mp3")]
        return lagu_ditemukan

    def login(self, u, p):
        if u in self.users and self.users[u].password == p:
            self.user_aktif = self.users[u]; return True
        return False
    
    def daftar(self, u, p):
        if u in self.users: return False
        self.users[u] = Pengguna(u, p); return True

    def buat_playlist(self, nama):
        if not nama or nama in self.user_aktif.playlists: return False
        self.user_aktif.playlists[nama] = []; return True

    def tambah_playlist(self, nama, lagu):
        self.user_aktif.playlists[nama].append(lagu); return True

    def hapus_dari_playlist(self, nama, index):
        if nama in self.user_aktif.playlists:
            try:
                self.user_aktif.playlists[nama].pop(index)
                return True
            except IndexError:
                return False
        return False
# UI UXXX NYA KIDSS
class ScrollableFrame(tk.Frame):
    def __init__(self, container, bg_color, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_color)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

class AplikasiMusikGUI:
    def __init__(self, root, sistem):
        self.root = root
        self.sistem = sistem
        self.timer_id = None
        self.is_playing = False
        self.is_paused = False
        self.detik_berjalan = 0
        self.current_page = "Library"
        self.search_var = tk.StringVar()
        self._setup_window()
        self._setup_theme()
        self._show_login()

    def _setup_window(self):
        self.root.title("Spotipu - Program Music Player dan Manajer")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 500)

    def _setup_theme(self):
        self.colors = {
            "bg_dark": "#120520",
            "sidebar": "#1a0925",
            "right_panel": "#150618",
            "player_bar": "#0f0312",
            "card_bg": "#250f33",
            "neon_pink": "#ff33cc",
            "neon_purple": "#aa00ff",
            "danger_red": "#ff4444",
            "text_fg": "#ffffff",
            "text_dim": "#b39ddb"
        }
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Neon.Horizontal.TProgressbar", troughcolor=self.colors["player_bar"], background=self.colors["neon_pink"], thickness=6, borderwidth=0)
        style.configure("Eq.Vertical.TProgressbar", troughcolor=self.colors["right_panel"], background=self.colors["neon_purple"], borderwidth=0)

    def _create_btn(self, parent, text, cmd, icon=None, bg=None, fg="white", font_size=11):
        c_bg = bg if bg else self.colors["sidebar"]
        txt = f"{icon}  {text}" if icon else text
        return tk.Button(parent, text=txt, command=cmd, bg=c_bg, fg=fg, activebackground=self.colors["neon_purple"], activeforeground="white", bd=0, font=('Segoe UI', font_size), anchor='w', padx=20, pady=10, cursor="hand2")

    def _clear_root(self):
        if self.timer_id: self.root.after_cancel(self.timer_id)
        for w in self.root.winfo_children(): w.destroy()

    # LOGIN SIRRR
    def _show_login(self):
        self._clear_root()
        self.root.configure(bg=self.colors["bg_dark"])
        f = tk.Frame(self.root, bg=self.colors["card_bg"], padx=60, pady=60)
        f.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(f, text="LOGIN SPOTIPU", font=("Montserrat", 24, "bold"), bg=self.colors["card_bg"], fg=self.colors["neon_pink"]).pack(pady=(0,30))
        tk.Label(f, text="Username", bg=self.colors["card_bg"], fg=self.colors["text_dim"]).pack(anchor='w')
        u_e = ttk.Entry(f, font=('Arial', 14)); u_e.pack(pady=5, ipady=5, fill='x'); u_e.insert(0, "bobi")
        tk.Label(f, text="Password", bg=self.colors["card_bg"], fg=self.colors["text_dim"]).pack(anchor='w', pady=(15,0))
        p_e = ttk.Entry(f, show="*", font=('Arial', 14)); p_e.pack(pady=5, ipady=5, fill='x'); p_e.insert(0, "pass")
        tk.Button(f, text="MASUK", bg=self.colors["neon_purple"], fg="white", font=('Arial', 12, 'bold'), pady=10, command=lambda: self._aksi_login(u_e.get(), p_e.get())).pack(pady=30, fill='x')
        tk.Button(f, text="Daftar Akun", bg=self.colors["card_bg"], fg="white", bd=0, font=('Arial', 10), command=lambda: self._aksi_daftar(u_e.get(), p_e.get())).pack(fill='x')

    def _aksi_login(self, u, p):
        if self.sistem.login(u, p): self._show_dashboard()
        else: messagebox.showerror("Gagal", "Cek username/password")
        
    def _aksi_daftar(self, u, p):
        if self.sistem.daftar(u, p): messagebox.showinfo("Sukses", "Silakan login")
        else: messagebox.showerror("Gagal", "Username sudah dipakai")

    #  DASHBOARD UTAMA
    def _show_dashboard(self):
        self._clear_root()
        main_container = tk.Frame(self.root, bg=self.colors["bg_dark"])
        main_container.pack(fill='both', expand=True)
        
        # SIDEBAR
        self.sidebar = tk.Frame(main_container, bg=self.colors["sidebar"], width=220)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        # PANEL KANAN CIK
        self.right_panel = tk.Frame(main_container, bg=self.colors["right_panel"], width=280)
        self.right_panel.pack(side='right', fill='y')
        self.right_panel.pack_propagate(False)

        # KONTENNN
        self.content_area = tk.Frame(main_container, bg=self.colors["bg_dark"])
        self.content_area.pack(side='left', fill='both', expand=True)

        # BENTUKAN BAR
        self.player_bar = tk.Frame(self.root, bg=self.colors["player_bar"], height=90)
        self.player_bar.pack(side='bottom', fill='x')
        self.player_bar.pack_propagate(False)

        self._setup_sidebar_content()
        self._setup_right_panel_content()
        self._setup_player_bar()
        self._load_page("Library")

    def _setup_sidebar_content(self):
        tk.Label(self.sidebar, text="🎧 Spotipu", font=("Helvetica", 18, "bold"), bg=self.colors["sidebar"], fg="white").pack(pady=30)
        self._create_btn(self.sidebar, "Library", lambda: self._load_page("Library"), "📚").pack(fill='x', pady=2)
        self._create_btn(self.sidebar, "Playlist", lambda: self._load_page("Playlist"), "🎵").pack(fill='x', pady=2)
        self._create_btn(self.sidebar, "Riwayat", lambda: self._load_page("History"), "🕒").pack(fill='x', pady=2)
        tk.Frame(self.sidebar, bg=self.colors["sidebar"]).pack(fill='both', expand=True)
        self._create_btn(self.sidebar, "Log Out", self._show_login, "🚪", fg="#ff5555").pack(fill='x', side='bottom', pady=20)

    # PANEL KANAN
    def _setup_right_panel_content(self):
        tk.Label(self.right_panel, text="Now Playing", font=("Arial", 12, "bold"), bg=self.colors["right_panel"], fg="white").pack(pady=20)
        
        self.rp_art_frame = tk.Frame(self.right_panel, bg=self.colors["card_bg"], width=180, height=180)
        self.rp_art_frame.pack(pady=10)
        self.rp_art_frame.pack_propagate(False)
        self.rp_icon = tk.Label(self.rp_art_frame, text="♫", font=("Arial", 70), bg=self.colors["card_bg"], fg=self.colors["neon_pink"])
        self.rp_icon.pack(expand=True)
        
        self.rp_judul = tk.Label(self.right_panel, text="Pilih lagu...", font=("Arial", 13, "bold"), bg=self.colors["right_panel"], fg="white", wraplength=250)
        self.rp_judul.pack(pady=(15, 5))
        self.rp_artis = tk.Label(self.right_panel, text="--", font=("Arial", 10), bg=self.colors["right_panel"], fg=self.colors["text_dim"])
        self.rp_artis.pack()
        
        tk.Frame(self.right_panel, bg=self.colors["sidebar"], height=2).pack(fill='x', padx=30, pady=20)
        tk.Label(self.right_panel, text="Berikutnya:", font=("Arial", 9, "bold"), bg=self.colors["right_panel"], fg=self.colors["text_dim"]).pack(anchor='w', padx=30)
        self.rp_next_song = tk.Label(self.right_panel, text="--", font=("Arial", 10), bg=self.colors["right_panel"], fg="white", anchor='w')
        self.rp_next_song.pack(fill='x', padx=30, pady=5)

        tk.Frame(self.right_panel, bg=self.colors["sidebar"], height=2).pack(fill='x', padx=30, pady=20)
        eq_frame = tk.Frame(self.right_panel, bg=self.colors["right_panel"])
        eq_frame.pack(fill='x', padx=30, pady=5)
        
        for i in range(5):
            bar = ttk.Progressbar(eq_frame, orient="vertical", length=40, style="Eq.Vertical.TProgressbar")
            bar.pack(side='left', padx=3, expand=True)
            bar['value'] = random.randint(30, 80)

    def _update_right_panel(self):
        lagu = self.sistem.lagu_sekarang
        if lagu:
            self.rp_judul.config(text=lagu.judul)
            self.rp_artis.config(text=lagu.artis)
            
            idx = self.sistem.index_aktif
            playlist = self.sistem.playlist_aktif
            if idx + 1 < len(playlist):
                self.rp_next_song.config(text=playlist[idx+1].judul)
            else:
                self.rp_next_song.config(text="End of Playlist")

    def _setup_player_bar(self):
        info_frame = tk.Frame(self.player_bar, bg=self.colors["player_bar"], width=200)
        info_frame.pack(side='left', fill='y', padx=20)
        self.lbl_now_title = tk.Label(info_frame, text="Siap Memutar", font=("Arial", 11, "bold"), bg=self.colors["player_bar"], fg="white", anchor='w')
        self.lbl_now_title.pack(side='top', pady=(25, 2), fill='x')
        self.lbl_now_time = tk.Label(info_frame, text="--:--", font=("Arial", 9), bg=self.colors["player_bar"], fg=self.colors["text_dim"], anchor='w')
        self.lbl_now_time.pack(side='top', fill='x')

        ctrl_frame = tk.Frame(self.player_bar, bg=self.colors["player_bar"])
        ctrl_frame.pack(side='left', fill='both', expand=True)
        btns_frame = tk.Frame(ctrl_frame, bg=self.colors["player_bar"])
        btns_frame.pack(side='top', pady=(15, 5))
        tk.Button(btns_frame, text="⏮", command=self._prev_song, bg=self.colors["player_bar"], fg="white", bd=0, font=("Arial", 14)).pack(side='left', padx=15)
        self.btn_play_pause = tk.Button(btns_frame, text="▶", command=self._toggle_pause, bg="white", fg="black", bd=0, font=("Arial", 14), width=4) 
        self.btn_play_pause.pack(side='left', padx=15)
        tk.Button(btns_frame, text="⏭", command=self._next_song, bg=self.colors["player_bar"], fg="white", bd=0, font=("Arial", 14)).pack(side='left', padx=15)
        self.pbar = ttk.Progressbar(ctrl_frame, orient='horizontal', mode='determinate', style="Neon.Horizontal.TProgressbar")
        self.pbar.pack(side='top', fill='x', padx=50)

    # TEMPAT NAVIGASI
    def _load_page(self, page_name, data_tambahan=None):
        self.current_page = page_name
        for w in self.content_area.winfo_children(): w.destroy()
        header = tk.Frame(self.content_area, bg=self.colors["bg_dark"], pady=20, padx=30)
        header.pack(fill='x')
        tk.Label(header, text=page_name.upper(), font=("Helvetica", 24, "bold"), bg=self.colors["bg_dark"], fg="white").pack(anchor='w')
        scroll_frame = ScrollableFrame(self.content_area, bg_color=self.colors["bg_dark"])
        scroll_frame.pack(fill='both', expand=True, padx=20, pady=10)
        content = scroll_frame.scrollable_frame

        if page_name == "Library": self._render_library(content)
        elif page_name == "History": self._render_history(content)
        elif page_name == "Playlist": self._render_playlist_menu(content)
        elif page_name == "Playlist Detail": self._render_detail_playlist(content, data_tambahan)

    def _create_song_row(self, parent, lagu, idx=None, cmd_play=None, cmd_hapus=None):
        row = tk.Frame(parent, bg=self.colors["card_bg"], pady=8, padx=10)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="♫", font=("Arial", 12), bg=self.colors["card_bg"], fg=self.colors["neon_pink"]).pack(side='left', padx=10)
        title_txt = f"{idx}. {lagu.judul}" if idx else lagu.judul
        tk.Label(row, text=title_txt, font=("Arial", 11), bg=self.colors["card_bg"], fg="white").pack(side='left', padx=10)
        
        if cmd_play:
            tk.Button(row, text="PUTAR", font=("Arial", 8, "bold"), bg=self.colors["neon_purple"], fg="white", bd=0, padx=10, command=cmd_play).pack(side='right', padx=5)
        
        if cmd_hapus:
            tk.Button(row, text="🗑", font=("Arial", 10), bg=self.colors["danger_red"], fg="white", bd=0, padx=8, command=cmd_hapus).pack(side='right', padx=5)
        
        if self.current_page == "Library":
            tk.Button(row, text="+ PL", font=("Arial", 8), bg="#333", fg="white", bd=0, padx=5, command=lambda: self._popup_playlist_select(lagu)).pack(side='right', padx=5)

    def _render_library(self, parent):
        search_frame = tk.Frame(parent, bg=self.colors["bg_dark"])
        search_frame.pack(fill='x', pady=(0, 20))
        entry_cari = tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 12), bg="#333", fg="white", insertbackground="white")
        entry_cari.pack(side='left', fill='x', expand=True, padx=(0, 10))
        tk.Button(search_frame, text="Cari", bg=self.colors["neon_purple"], fg="white", font=("Arial", 10), command=lambda: self._load_page("Library")).pack(side='left')
        keyword = self.search_var.get().lower()
        list_lagu = [l for l in self.sistem.db_lagu if keyword in l.judul.lower()]
        if not list_lagu: tk.Label(parent, text="Lagu tidak ditemukan.", fg="gray", bg=self.colors["bg_dark"]).pack()
        for i, lagu in enumerate(list_lagu):
            self._create_song_row(parent, lagu, idx=i+1, cmd_play=lambda l=lagu, idx=i: self._mainkan_context(list_lagu, idx))

    def _render_history(self, parent):
        items = list(reversed(self.sistem.user_aktif.riwayat.items))
        if not items: tk.Label(parent, text="Belum ada riwayat", fg="gray", bg=self.colors["bg_dark"]).pack(pady=20); return
        for i, lagu in enumerate(items): self._create_song_row(parent, lagu, idx=i+1, cmd_play=lambda l=lagu: self._mainkan_context([l], 0))

    def _render_playlist_menu(self, parent):
        tk.Button(parent, text="+ Buat Playlist Baru", bg=self.colors["neon_pink"], fg="white", bd=0, font=("Arial", 11, "bold"), padx=15, pady=10, command=self._buat_pl).pack(anchor='w', pady=(0, 20))
        playlists = self.sistem.user_aktif.playlists
        if not playlists: tk.Label(parent, text="Belum ada playlist", fg="gray", bg=self.colors["bg_dark"]).pack(); return
        for nama, lagus in playlists.items():
            card = tk.Frame(parent, bg=self.colors["card_bg"], pady=15, padx=15)
            card.pack(fill='x', pady=5)
            tk.Label(card, text=f"{nama}", font=("Arial", 14, "bold"), bg=self.colors["card_bg"], fg="white").pack(side='left')
            tk.Label(card, text=f"• {len(lagus)} Lagu", font=("Arial", 10), bg=self.colors["card_bg"], fg=self.colors["text_dim"]).pack(side='left', padx=10)
            tk.Button(card, text="Lihat Lagu", bg="#444", fg="white", bd=0, command=lambda n=nama: self._load_page("Playlist Detail", n)).pack(side='right', padx=5)

    def _render_detail_playlist(self, parent, nama_playlist):
        tk.Button(parent, text="< Kembali ke Menu", bg=self.colors["bg_dark"], fg=self.colors["text_dim"], bd=0, command=lambda: self._load_page("Playlist")).pack(anchor='w', pady=(0,10))
        lagu_list = self.sistem.user_aktif.playlists[nama_playlist]
        if not lagu_list: tk.Label(parent, text="Playlist ini kosong", fg="gray", bg=self.colors["bg_dark"]).pack(); return
        
        btn_frame = tk.Frame(parent, bg=self.colors["bg_dark"])
        btn_frame.pack(fill='x', pady=(0, 15))
        tk.Button(btn_frame, text="▶ Putar Urut", bg=self.colors["neon_purple"], fg="white", bd=0, padx=15, pady=5, command=lambda: self._mainkan_context(lagu_list, 0)).pack(side='left', padx=5)
        tk.Button(btn_frame, text="🔀 Putar Acak", bg="#444", fg="white", bd=0, padx=15, pady=5, command=lambda: self._mainkan_acak(lagu_list)).pack(side='left', padx=5)
        
        for i, lagu in enumerate(lagu_list):
            self._create_song_row(
                parent,
                lagu,
                idx=i+1,
                cmd_play=lambda idx=i: self._mainkan_context(lagu_list, idx),
                # Menambahkan logika hapus di sini:
                cmd_hapus=lambda idx=i: self._aksi_hapus_lagu_pl(nama_playlist, idx)
            )
    def _aksi_hapus_lagu_pl(self, nama_pl, idx):
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus lagu ini dari playlist?"):
            if self.sistem.hapus_dari_playlist(nama_pl, idx):
                self._load_page("Playlist Detail", nama_pl)
            else:
                messagebox.showerror("Error", "Gagal menghapus lagu")

    # TEMPAT ENGINE
    def _mainkan_context(self, list_lagu, index_mulai):
        self.sistem.playlist_aktif = list(list_lagu) 
        self.sistem.index_aktif = index_mulai
        self._putar_index_aktif()

    def _mainkan_acak(self, list_lagu):
        list_acak = list(list_lagu)
        random.shuffle(list_acak)
        self.sistem.playlist_aktif = list_acak
        self.sistem.index_aktif = 0
        self._putar_index_aktif()

    def _putar_index_aktif(self):
        if 0 <= self.sistem.index_aktif < len(self.sistem.playlist_aktif):
            lagu = self.sistem.playlist_aktif[self.sistem.index_aktif]
            self._putar_lagu_fisik(lagu)
        else:
            self.is_playing = False
            self.lbl_now_title.config(text="Playlist Selesai")
            self.btn_play_pause.config(text="▶")

    def _putar_lagu_fisik(self, lagu):
        self.sistem.lagu_sekarang = lagu
        self.sistem.user_aktif.riwayat.push(lagu)
        self.lbl_now_title.config(text=lagu.judul)
        self.btn_play_pause.config(text="||") 
        self.is_playing = True
        self.is_paused = False
        self._update_right_panel()
        try:
            pygame.mixer.music.load(lagu.file_path)
            pygame.mixer.music.play()
        except: return
        if self.timer_id: self.root.after_cancel(self.timer_id)
        self._update_timer()

    def _toggle_pause(self):
        if not self.sistem.lagu_sekarang: return
        if self.is_paused:
            pygame.mixer.music.unpause(); self.is_paused = False; self.btn_play_pause.config(text="||")
        else:
            pygame.mixer.music.pause(); self.is_paused = True; self.btn_play_pause.config(text="▶")

    def _next_song(self):
        if self.sistem.playlist_aktif and self.sistem.index_aktif + 1 < len(self.sistem.playlist_aktif):
            self.sistem.index_aktif += 1; self._putar_index_aktif()
        else: self.is_playing = False

    def _prev_song(self):
        if self.detik_berjalan > 3: self._putar_index_aktif()
        elif self.sistem.playlist_aktif and self.sistem.index_aktif - 1 >= 0:
            self.sistem.index_aktif -= 1; self._putar_index_aktif()

    def _update_timer(self):
        if not self.sistem.lagu_sekarang: return
        if not pygame.mixer.music.get_busy() and self.is_playing and not self.is_paused: self._next_song(); return
        if self.is_playing and not self.is_paused: self.detik_berjalan = pygame.mixer.music.get_pos() / 1000
        total = self.sistem.lagu_sekarang.durasi
        if total > 0: self.pbar['value'] = (self.detik_berjalan / total) * 100
        self.lbl_now_time.config(text=f"{self.sistem.lagu_sekarang.format_waktu(self.detik_berjalan)} / {self.sistem.lagu_sekarang.format_waktu(total)}")
        self.timer_id = self.root.after(1000, self._update_timer)

    def _buat_pl(self):
        nama = simpledialog.askstring("Baru", "Nama Playlist:")
        if self.sistem.buat_playlist(nama): self._load_page("Playlist")
    
    def _popup_playlist_select(self, lagu):
        top = Toplevel(self.root)
        top.title("Tambah ke Playlist")
        top.geometry("400x600")
        top.configure(bg=self.colors["bg_dark"])
        tk.Label(top, text="Pilih Playlist", bg=self.colors["bg_dark"], fg="white", font=("bold", 12)).pack(pady=10)
        for n in self.sistem.user_aktif.playlists:
            tk.Button(top, text=n, bg=self.colors["card_bg"], fg="white", pady=8, width=30, bd=0, command=lambda x=n: [self.sistem.tambah_playlist(x, lagu), top.destroy()]).pack(pady=2)

if __name__ == "__main__":
    root = tk.Tk()
    sys = SistemMusik()
    sys.daftar("bobi", "pass")
    app = AplikasiMusikGUI(root, sys)
    root.mainloop()