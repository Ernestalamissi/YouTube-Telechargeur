#30/07/2025 Alamissi Ernest 
"""
✅ Téléchargement de segments (audio/vidéo) avec yt_dlp
✅ Extraction audio en .wav avec ffmpeg
✅ Fusion de plusieurs segments
✅ Sous-dossier optionnel
✅ Choix du dossier de sortie
✅ Nettoyage complet
✅ Interface conviviale avec retour visuel dynamique
2. 📦 Emballer en .exe pour distribution (si tu veux partager)
Avec PyInstaller : pyinstaller --noconfirm --onefile --windowed 
nomduscript.py
Cela génère un .exe (Windows) ou binaire autonome (Mac/Linux).
Si tu veux inclure une icône personnalisée :
pyinstaller --onefile --windowed --icon=icone.ico ton_script.py
3. 🧠 Bonus intelligents
Ajout d’une barre de progression ?
Gérer les erreurs réseau ou lien privé/non listé ?
Ajout d’un menu “À propos / Crédits” ?
Lecture rapide d’un segment avec ffplay ?
Ajout d’un fichier log.txt pour les erreurs en silence ?
"""
# === 📦 Imports ===
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
from yt_dlp import YoutubeDL
import os
import uuid
import contextlib
import platform
import subprocess
import re
import traceback

def log_erreur(exception):
    with open("log.txt", "a") as f:
        f.write(f"[{datetime.now()}] {str(exception)}\n")
        f.write(traceback.format_exc())

#====== Sécuriser les noms de fichiers (avancé)#======
def nettoyer_nom_fichier(nom):
    return re.sub(r'[^\w\-_. ()\[\]]', '_', nom).strip()

#===Ajout d’un bouton “📁 Ouvrir le dossier de sortie”===
def ouvrir_dossier_sortie():
    try:
        if platform.system() == "Darwin":
            subprocess.call(["open", output_directory])
        elif platform.system() == "Windows":
            os.startfile(output_directory)
        elif platform.system() == "Linux":
            subprocess.call(["xdg-open", output_directory])
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d’ouvrir le dossier : {e}")
        log_erreur(e)

# === 🗂️ Dossiers ===
segments_paths = []
temp_dir = "/Users/user/Desktop/DonnerIA/Telecharger"
os.makedirs(temp_dir, exist_ok=True)
output_directory = "/Users/user/Desktop/DonnerIA"

FFMPEG = "/usr/local/bin/ffmpeg"  # 🔧 Adapté à ton système

# === 🪟 Interface Graphique ===
root = tk.Tk()
root.title("Téléchargeur de segments YouTube")
root.geometry("520x600")  # Hauteur ajustée

# === 🎧 Option audio seul ===
audio_only_var = tk.BooleanVar()
tk.Checkbutton(root, text="🎧 Extraire uniquement l'audio (.wav)", 
variable=audio_only_var).pack()

# === 🧾 Champs de saisie ===
tk.Label(root, text="🎥 URL YouTube").pack()
url_entry = tk.Entry(root, width=50)
url_entry.insert(0, "https://youtu.be/TRsrXMZCEdA")
url_entry.pack()

tk.Label(root, text="🕐 Heure de début (hh:mm:ss)").pack()
start_entry = tk.Entry(root)
start_entry.insert(0, "00:00:10")
start_entry.pack()

tk.Label(root, text="🕒 Heure de fin (hh:mm:ss)").pack()
end_entry = tk.Entry(root)
end_entry.insert(0, "00:00:30")
end_entry.pack()

tk.Label(root, text="🎙️ Nom du segment (sans extension)").pack()
audio_entry = tk.Entry(root)
audio_entry.insert(0, "segment1")
audio_entry.pack()

tk.Label(root, text="📁 Nom du sous-dossier (optionnel)").pack()
subfolder_entry = tk.Entry(root)
subfolder_entry.pack()

tk.Label(root, text="📁 Nom du fichier final (sans extension)").pack()
final_name_entry = tk.Entry(root)
final_name_entry.insert(0, "video_completee")
final_name_entry.pack()

sortie_label = tk.Label(root, text="", fg="blue", wraplength=400)
sortie_label.pack()

# === 📜 Liste des segments ===
tk.Label(root, text="📄 Segments téléchargés :").pack()
segments_display = tk.Text(root, height=5, width=60)
segments_display.pack()

def afficher_segments():
    segments_display.delete("1.0", tk.END)
    for path in segments_paths:
        segments_display.insert(tk.END, os.path.basename(path) + "\n")

# === 📂 Dossier de sortie ===
def choisir_dossier_sortie():
    global output_directory
    nouveau_dossier = filedialog.askdirectory()
    if nouveau_dossier:
        output_directory = nouveau_dossier
        dossier_label.config(text=f"Dossier de sortie : {output_directory}")

tk.Button(root, text="📂 Choisir le dossier de sortie",command=choisir_dossier_sortie).pack(pady=5)
dossier_label = tk.Label(root, text=f"Dossier de sortie :{output_directory}", wraplength=400)
dossier_label.pack()
tk.Button(root, text="📁 Ouvrir le dossier de sortie",command=ouvrir_dossier_sortie).pack(pady=5)
# === 📥 Télécharger segment ===
def telecharger_segment_youtube():
    url = url_entry.get()
    start_time = start_entry.get()
    end_time = end_entry.get()
    video_name = nettoyer_nom_fichier(audio_entry.get().strip())
    if not url or not start_time or not end_time or not video_name:
        messagebox.showerror("Erreur", "Tous les champs sont requis.")
        return
    subfolder = nettoyer_nom_fichier(subfolder_entry.get().strip())
    if subfolder:
        output_path = os.path.join(output_directory, subfolder)
        os.makedirs(output_path, exist_ok=True)
    else:
        output_path = output_directory

    try:
        t1 = datetime.strptime(start_time, "%H:%M:%S")
        t2 = datetime.strptime(end_time, "%H:%M:%S")
        duration = int((t2 - t1).total_seconds())
        if duration <= 0:
            raise ValueError
        messagebox.showinfo("Durée", f"Durée du segment : {duration} secondes")    
    except ValueError:
        messagebox.showerror("Erreur", "Format hh:mm:ss invalide ou durée négative.")
        log_erreur(e)
        return

    temp_file = os.path.join(temp_dir, f"temp_{uuid.uuid4()}.mp4")
    output_ext = ".wav" if audio_only_var.get() else ".mp4"
    output_file = os.path.join(temp_dir, f"{video_name}{output_ext}")

    ydl_opts = {
        'format': 'bv*[ext=mp4]+ba[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': temp_file,
        'quiet': True,
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'ignoreerrors': True,
    }

    try:
        with contextlib.redirect_stderr(open(os.devnull, 'w')):
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        if audio_only_var.get():
            cmd = [
                FFMPEG, '-y',
                '-ss', start_time,
                '-i', temp_file,
                '-t', str(duration),
                '-vn',
                '-acodec', 'pcm_s16le',
                '-ar', '44100',
                '-ac', '2',
                output_file
            ]
        else:
            cmd = [
                FFMPEG, '-y',
                '-ss', start_time,
                '-i', temp_file,
                '-t', str(duration),
                '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
                '-r', '30',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-crf', '20',
                '-preset', 'veryfast',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-movflags', '+faststart',
                output_file
            ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(temp_file):
            os.remove(temp_file)

        segments_paths.append(output_file)
        afficher_segments()
        messagebox.showinfo("Succès", f"Segment téléchargé : {os.path.basename(output_file)}")

    except Exception as e:
        messagebox.showerror("Erreur", f"Échec du téléchargement : {e}")
        log_erreur(e)

tk.Button(root, text="📥 Télécharger segment",command=telecharger_segment_youtube).pack(pady=10)

# === 🔗 Fusionner segments ===
def fusionner_segments():
    if not segments_paths:
        messagebox.showerror("Erreur", "Aucun segment à fusionner.")
        return
    final_name = nettoyer_nom_fichier(final_name_entry.get().strip())
    if not final_name:
        messagebox.showerror("Erreur", "Veuillez entrer un nom pour le fichier final.")
        return

    ext_set = set(os.path.splitext(p)[1].lower() for p in segments_paths)
    if len(ext_set) != 1:
        messagebox.showerror("Erreur", "Tous les segments doivent être du même type (.mp4 ou .wav)")
        return
    subfolder = nettoyer_nom_fichier(subfolder_entry.get().strip())
    if subfolder:
        output_path = os.path.join(output_directory, subfolder)
        os.makedirs(output_path, exist_ok=True)
    else:
        output_path = output_directory
    extension = ext_set.pop()
    output_file = os.path.join(output_path, f"{final_name}{extension}")
    list_file = os.path.join(temp_dir, "list.txt")

    with open(list_file, 'w') as f:
        for segment in segments_paths:
            f.write(f"file '{segment}'\n")

    if extension == ".mp4":
        commande = [
            FFMPEG, "-y", "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-c:v", "libx264",
            "-c:a", "aac",
            output_file
        ]
    elif extension == ".wav":
        commande = [
            FFMPEG, "-y", "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            output_file
        ]
    else:
        messagebox.showerror("Erreur", "Type non supporté.")
        return

    subprocess.run(commande, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    messagebox.showinfo("Succès", f"Segments fusionnés : {output_file}")
    try:
        if platform.system() == "Darwin":
            subprocess.call(["open", output_file])
        elif platform.system() == "Windows":
            os.startfile(output_file)
        elif platform.system() == "Linux":
            subprocess.call(["xdg-open", output_file])
    except Exception as e:
        print("Erreur à l'ouverture :", e)
    if os.path.exists(list_file):
        os.remove(list_file)
        
tk.Button(root, text="🧩 Fusionner segments",command=fusionner_segments).pack(pady=10)

# ===Fusionner les .wav extraits en un seul fichier audio
def fusionner_audio_si_wav():
    if not segments_paths:
        messagebox.showerror("Erreur", "Aucun segment audio à fusionner.")
        return

    ext_set = set(os.path.splitext(p)[1].lower() for p in segments_paths)
    if ext_set != {".wav"}:
        messagebox.showerror("Erreur", "Tous les segments doivent être des fichiers .wav.")
        return
    final_name = nettoyer_nom_fichier(final_name_entry.get().strip())
    if not final_name:
        messagebox.showerror("Erreur", "Veuillez entrer un nom pour le fichier final.")
        return
    subfolder = nettoyer_nom_fichier(subfolder_entry.get().strip())
    if subfolder:
        output_path = os.path.join(output_directory, subfolder)
        os.makedirs(output_path, exist_ok=True)
    else:
        output_path = output_directory
        
    output_file = os.path.join(output_path, f"{final_name}.wav")

    list_file = os.path.join(temp_dir, "wav_list.txt")
    with open(list_file, "w") as f:
        for path in segments_paths:
            f.write(f"file '{path}'\n")

    cmd = [
        FFMPEG, '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', list_file,
        '-c', 'copy',
        output_file
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    messagebox.showinfo("Succès", f"Segments audio fusionnés : {output_file}")

    try:
        if platform.system() == "Darwin":
            subprocess.call(["open", output_file])
        elif platform.system() == "Windows":
            os.startfile(output_file)
        elif platform.system() == "Linux":
            subprocess.call(["xdg-open", output_file])
    except Exception as e:
        print("Erreur à l'ouverture :", e)
        log_erreur(e)

    if os.path.exists(list_file):
        os.remove(list_file)
    

tk.Button(root, text="🎵 Fusionner audio (.wav)",command=fusionner_audio_si_wav).pack(pady=5)

# === ♻️ Réinitialiser ===
def reinitialiser_segments():
    global segments_paths
    segments_paths.clear()
    afficher_segments()
    for fichier in os.listdir(temp_dir):
        chemin = os.path.join(temp_dir, fichier)
        if os.path.isfile(chemin):
            os.remove(chemin)
    for fichier in os.listdir(temp_dir):
        if fichier.endswith(".txt") or fichier.startswith("temp_"):
            os.remove(os.path.join(temp_dir, fichier))
        
    messagebox.showinfo("Réinitialisation", "Tous les segments ont été supprimés.")

tk.Button(root, text="♻️Réinitialiser segmens",command=reinitialiser_segments).pack(pady=10)

def desactiver_boutons():
    for widget in root.winfo_children():
        if isinstance(widget, tk.Button):
            widget.config(state="disabled")

def activer_boutons():
    for widget in root.winfo_children():
        if isinstance(widget, tk.Button):
            widget.config(state="normal")

def afficher_a_propos():
    messagebox.showinfo("À propos", "🎬 Téléchargeur YouTube\nVersion 1.0\nPar Alamissi Ernest\n31/07/2025")

menu = tk.Menu(root)
root.config(menu=menu)
menu_aide = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="❓ Aide", menu=menu_aide)
menu_aide.add_command(label="À propos", command=afficher_a_propos)


def mettre_a_jour_sortie():
    final_name = nettoyer_nom_fichier(final_name_entry.get().strip())
    subfolder = nettoyer_nom_fichier(subfolder_entry.get().strip())
    dossier = os.path.join(output_directory, subfolder) if subfolder else output_directory
    ext = ".wav" if audio_only_var.get() else ".mp4"
    sortie_label.config(text=f"📄 Fichier final : {os.path.join(dossier,final_name + ext)}")

# Mettre à jour automatiquement quand l'utilisateur tape
final_name_entry.bind("<KeyRelease>", lambda e: mettre_a_jour_sortie())
subfolder_entry.bind("<KeyRelease>", lambda e: mettre_a_jour_sortie())
audio_only_var.trace_add("write", lambda *args: mettre_a_jour_sortie())
root.bind("<Return>", lambda e: telecharger_segment_youtube())
root.bind("<Escape>", lambda e: reinitialiser_segments())
mettre_a_jour_sortie()

statut_label = tk.Label(root, text="", fg="green")
statut_label.pack(pady=3)

def update_statut(msg, couleur="green"):
    statut_label.config(text=msg, fg=couleur)

update_statut("Téléchargement en cours...")
update_statut("Segment ajouté ✔")
update_statut("Erreur : URL invalide", couleur="red")

# === ▶️ Lancer interface ===
root.mainloop()

