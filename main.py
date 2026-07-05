from customtkinter import *
from pygame import mixer
import os
from mutagen.mp3 import MP3
import pickle
import pystray
from PIL import Image
import threading
import keyboard
from win11toast import toast
import random
import win32event
import win32api
import winerror
import sys

# Set appearance mode and default color theme
set_appearance_mode("dark")
set_default_color_theme("blue")

# Create the main window
root = CTk()
root.withdraw()
root.title("🎵 Music Laucher")
root.geometry("520x750")
mixer.init()
root.resizable(width=False, height=False)
root.iconbitmap("music.ico")

position_depart = 0
duree = 0
texte_defilant = ""
position_texte = 0
labels_playlist = []
playlist_actuelle = []
music_state = "stop"
index_actuel = 0
volume = 0.5
MUSIC_FOLDER =  "Music"
son = "fort"
nomPlaylist = ""
tray_icon = None
playlist_a_reprendre = None
volume_a_reprendre = 0
index_a_reprendre = 0
position_a_reprendre = 0
musique = "en cours"
lecture = "normale"

mixer.music.set_volume(volume)

mutex = win32event.CreateMutex(None, False, "MusicLauncherUniqueMutex")

if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    print("Music Launcher est déjà ouvert.")
    sys.exit()

def playsong(startmm=0):  #Play
    global playlist_actuelle, index_actuel, music_state, duree, texte_defilant, position_texte, position_depart

    position_depart = startmm

    if not playlist_actuelle:
        return

    buttonPause.configure(text="⏸️")
    mixer.music.load(playlist_actuelle[index_actuel])
    music_state = "chargement"
    if startmm:
        mixer.music.play(start=startmm)
    else:
        mixer.music.play()
    music_state = "lecture"

    nom = os.path.basename(playlist_actuelle[index_actuel])
    audio = MP3(playlist_actuelle[index_actuel])
    duree = audio.info.length


    texte_defilant = f"{nom}        "
    position_texte = 0
    actualiser_playlist()

def pausesong():  #Pause
    global music_state

    if music_state == "lecture":
        mixer.music.pause()
        buttonPause.configure(text="▶️")
        music_state = "pause"
    elif music_state == "pause":
        buttonPause.configure(text="⏸️")
        mixer.music.unpause()
        music_state = "lecture"

def stopsong():  #stop
    global music_state

    mixer.music.stop()
    music_state = "stop"
    labelEncours2.configure(text="Aucune musique")
    actualiser_playlist()
    zero()
    progressBar.set(0)
    labelTemps.configure(text="0:00 / 0:00")

def resumesong():  #Resume
    mixer.music.unpause()

def suivant():
    global index_actuel
    if index_actuel < len(playlist_actuelle) - 1:
        if lecture == "normale":
            index_actuel += 1
            playsong()
        else:
            index_actuel = random.randrange(len(playlist_actuelle))
            playsong()
    else:
        stopsong()

def precedent():
    global index_actuel

    if index_actuel > 0:
        index_actuel -= 1
        playsong()


def lancer_playlist(nom_playlist, startm=0, indexf=0):
    global playlist_actuelle, index_actuel, music_state, nomPlaylist
    nomPlaylist = nom_playlist
    index_actuel = indexf

    dossier = os.path.join(MUSIC_FOLDER, nom_playlist)


    for widget in frameListe.winfo_children():
        widget.destroy()
    
    root.update_idletasks()

    playlist_actuelle.clear()
    labels_playlist.clear()

    for fichier in os.listdir(dossier):
        if fichier.endswith((".mp3", ".ogg", ".wav")):
            playlist_actuelle.append(os.path.join(dossier, fichier))
            bouton = CTkButton(
                frameListe,
                text=fichier,
                anchor="w",
                fg_color="transparent",
                hover_color="#3A3A3A",
                text_color=("black", "white"),
                corner_radius=6,
                command=lambda i=len(labels_playlist): jouer_morceau(i)
            )

            bouton.grid(sticky="w", padx=5, pady=2)
            # bouton.pack(fill="x", padx=5, pady=2)

            labels_playlist.append(bouton)

    if startm:
        playsong(startm)
    else:
        playsong()

def actualiser_playlist():
    for i, label in enumerate(labels_playlist):
        try:
            if music_state == "stop":
                label.configure(fg_color="transparent")
            elif i == index_actuel:
                label.configure(
                    fg_color="#3B8ED0",
                    corner_radius=6
                )
            else:
                label.configure(
                    fg_color="transparent"
                )
        except TclError:
            pass

def raccourcis():
    keyboard.add_hotkey("play/pause media", pausesong)
    keyboard.add_hotkey("next track", suivant)
    keyboard.add_hotkey("previous track", precedent)



##################################### FONCTIONS REDUCTIONS

def afficher_fenetre(icon=None, item=None):
    global tray_icon

    if tray_icon:
        tray_icon.stop()
        tray_icon = None

    root.after(0, root.deiconify)

def minimiser_barre_systeme():
    global tray_icon

    root.withdraw()

    image = Image.open("music.ico")
    if playlist_a_reprendre and musique != "reprise":
        menu = pystray.Menu(
            pystray.MenuItem("▶ Reprendre musique", reprendre_lecture, default=True),
            pystray.MenuItem("Quitter", fermeture)
        )
    else:
        menu = pystray.Menu(
            pystray.MenuItem("Afficher", afficher_fenetre, default=True),
            pystray.MenuItem("Quitter", fermeture)
        )

    tray_icon = pystray.Icon(
        "MusicLauncher",
        image,
        "Music Launcher",
        menu
    )

    threading.Thread(target=tray_icon.run, daemon=True).start()


# SAUVEGARDE SAUVEGARDE SAUVEGARDE SAUVEGARDE SAUVEGARDE SAUVEGARDE SAUVEGARDE SAUVEGARDE SAUVEGARDE SAUVEGARDE SAUVEGARDE SAUVEGARDE SAUVEGARDE SAUVEGARDE SAUVEGARDE
#
#
#

def sauvegarder():
    donnees = {
        "playlist" : nomPlaylist,
        "index" : index_actuel,
        "position" : position_depart + mixer.music.get_pos() / 1000,
        "volume" : mixer.music.get_volume(),
        "mode" : lecture
    }
    fichier_donnees = open("donnees.dat", "wb")
    pickle.dump(donnees, fichier_donnees)
    fichier_donnees.close()

def charger():
    global volume_a_reprendre, index_a_reprendre, playlist_a_reprendre, position_a_reprendre, lecture
    
    fichier_donnees = open('donnees.dat', 'rb')
    donnees_chargees = pickle.load(fichier_donnees)
    fichier_donnees.close()
    
    if "volume" in donnees_chargees:
        mixer.music.set_volume(donnees_chargees['volume'])
        playlist_a_reprendre = donnees_chargees['playlist']
        position_a_reprendre = donnees_chargees["position"]
        index_a_reprendre = donnees_chargees['index']
        lecture = donnees_chargees['mode']

def reprendre_lecture():
    global playlist_a_reprendre, position_a_reprendre, index_a_reprendre, musique

    if playlist_a_reprendre is None:
        return
    
    afficher_fenetre()
    lancer_playlist(
        playlist_a_reprendre,
        position_a_reprendre,
        index_a_reprendre
    )
    musique = "reprise"

def zero():
    donnees = {}
    fichier_donnees = open("donnees.dat", "wb")
    pickle.dump(donnees, fichier_donnees)
    fichier_donnees.close()

def fermeture(icon=None, item=None):
    global tray_icon

    if music_state != "stop":
        sauvegarder()

    if tray_icon is not None:
        tray_icon.stop()
        tray_icon = None

    root.after(0, root.destroy)



############################################################################################################################################

def verifier_fin_musique():
    if music_state == "lecture" and not mixer.music.get_busy():
        suivant()
    
    root.after(500, verifier_fin_musique)


def update_progress():
    if music_state == "lecture":
        position = position_depart + mixer.music.get_pos() / 1000

        if duree > 0:
            progressBar.set(position / duree)

    root.after(200, update_progress)

def faire_defiler_texte():
    global texte_defilant, position_texte

    if music_state == "lecture":
        if texte_defilant:

            affichage = texte_defilant[position_texte:] + texte_defilant[:position_texte]

            labelEncours2.configure(text=affichage)

            position_texte += 1

            if position_texte >= len(texte_defilant):
                position_texte = 0

    root.after(300, faire_defiler_texte)

def format_temps(secondes):
    minutes = int(secondes // 60)
    secondes = int(secondes % 60)
    return f"{minutes}:{secondes:02d}"

def update_temps():
    if music_state == "lecture":
        temps_actuel = position_depart + mixer.music.get_pos() / 1000

        labelTemps.configure(text=f"{format_temps(temps_actuel)} / {format_temps(duree)}")
    
    root.after(500, update_temps)

def jouer_morceau(index):
    global index_actuel

    index_actuel = index

    playsong()

    actualiser_playlist()

def changer_volume(value):
    global son

    mixer.music.set_volume(value)
    if value == 0:
        toggle_son()
    if value > 0:
        BoutonMic.configure(text="🔊")


def toggle_son():
    global son

    if son == "fort":
        son = "eteint"
        mixer.music.set_volume(0)
        BoutonMic.configure(text="🔇")
        ReglageVolume.set(0)
    elif son == "eteint":
        son = "fort"
        mixer.music.set_volume(0.5)
        BoutonMic.configure(text="🔊")
        ReglageVolume.set(0.5)

def toggle_mode_de_lecture():
    global lecture

    if lecture == "normale":
        buttonModeDeLecture.configure(text="➡️")
        lecture = "aleatoire"
    elif lecture == "aleatoire":
        buttonModeDeLecture.configure(text="🔀")
        lecture = "normale"


# Add a label
mainlabel = CTkLabel(root, text="Music Launcher", font=("Helvetica", 22))
mainlabel.grid(row=1, columnspan=2, sticky="nsew", pady=20, padx=50)


frameMain1 = CTkFrame(root, width=250, height=300, corner_radius=0)
frameMain1.grid(row=2, column=0, padx=5)
frameMain1.grid_propagate(False)

label_playlist = CTkLabel(frameMain1, text="📁 Playlists : ", font=("Helvetica", 18))
label_playlist.grid(row=1, pady=10, padx=50)

for i, dossier in enumerate(os.listdir(MUSIC_FOLDER)):
    chemin = os.path.join(MUSIC_FOLDER, dossier)

    if os.path.isdir(chemin):

        bouton = CTkButton(
            frameMain1,
            text=dossier,
            command=lambda d=dossier: lancer_playlist(d)
        )

        bouton.grid(row=int(i+2), pady=10, padx=50)

frameMain2 = CTkFrame(root, width=250, height=300, corner_radius=0)
frameMain2.grid(row=2, column=1, padx=5)
frameMain2.grid_propagate(False)

labelMain2 = CTkLabel(frameMain2, text="📃 Playlist", font=("Helvetica", 18))
labelMain2.grid(row=1, pady=10, padx=50)

frameListe = CTkScrollableFrame(frameMain2, width=220, height=210)
frameListe.grid(row=3, pady=20, padx=5, sticky="ew")


frameEnCours = CTkFrame(root, width=500, corner_radius=10)
frameEnCours.grid(row=3, columnspan=2, pady=10, padx=5, sticky="ew")
frameEnCours.grid_propagate(False)

frameEnCours.grid_columnconfigure(1, weight=1)
frameEnCours.grid_columnconfigure(2, weight=1)

frameTitre = CTkFrame(frameEnCours,
    fg_color="transparent",
    width=300)
frameTitre.grid(row=1, column=1, sticky="wn", padx=10, pady=10)
frameTitre.grid_propagate(False)

labelEncours = CTkLabel(frameTitre, text="🎵 En cours : ", font=("Helvetica", 15))
labelEncours.pack()

frameNom = CTkFrame(frameEnCours,
    fg_color="transparent",
    width=375,
    height=25
    )
frameNom.grid(row=1, column=2, sticky="ew", padx=10, pady=10)
frameNom.grid_propagate(False)

labelEncours2 = CTkLabel(frameNom, text="Aucune musique", font=("Helvetica", 15))
labelEncours2.grid(row=1, sticky="w")

progressBar = CTkProgressBar(frameEnCours)
progressBar.grid(row=2, columnspan=3, padx=10, pady=10, sticky="ew")
progressBar.set(0)

# buttonModeDeLecture = CTkButton(frameEnCours, text="🔀", font=("Helvetica", 18), command=toggle_mode_de_lecture, width=140)
# buttonModeDeLecture.grid(row=3, column=1, padx=10, pady=10)

labelTemps = CTkLabel(
    frameEnCours,
    text="0:00 / 0:00",
    font=("Helvetica", 13)
)
labelTemps.grid(row=3, padx=10  , column=2, sticky="e")

frameSon = CTkFrame(frameEnCours,
    fg_color="transparent",
    width=400
    )
frameSon.grid(row=4, padx=10, pady=10, sticky="w", columnspan=3)

BoutonMic = CTkButton(frameSon, text="🔊", command=lambda : toggle_son(), width=50, font=("Helvetica", 18))
BoutonMic.grid(row=1, column=1)

ReglageVolume = CTkSlider(frameSon, from_=0, to=1, number_of_steps=100, command=changer_volume, width=120)
ReglageVolume.grid(row=1, column=2, padx=10, pady=10)
ReglageVolume.set(0.5)


frameButtonsLecture = CTkFrame(root, corner_radius=0, fg_color="transparent")
frameButtonsLecture.grid(row=4, columnspan=2, pady=10, padx=5, sticky="ew")

frameButtonsLecture.grid_columnconfigure(1, weight=1)
frameButtonsLecture.grid_columnconfigure(2, weight=1)
frameButtonsLecture.grid_columnconfigure(3, weight=1)
frameButtonsLecture.grid_columnconfigure(4, weight=1)

buttonSuivant = CTkButton(frameButtonsLecture, text="⏮️", command=lambda : precedent(), font=("Helvetica", 30), width=45, corner_radius=0, border_color="#000", border_width=2, )
buttonSuivant.grid(row=1, column=1, padx=20)

buttonPause = CTkButton(frameButtonsLecture, text="⏸️", command=lambda : pausesong(), font=("Helvetica", 30), width=45, corner_radius=0, border_color="#000", border_width=2)
buttonPause.grid(row=1, column=2, padx=20)

buttonSuivant = CTkButton(frameButtonsLecture, text="⏭️", command=lambda : suivant(), font=("Helvetica", 30), width=45, corner_radius=0, border_color="#000", border_width=2, )
buttonSuivant.grid(row=1, column=3, padx=20)

buttonStop = CTkButton(frameButtonsLecture, text="⏹️", command=lambda : stopsong(), font=("Helvetica", 30), width=45, corner_radius=0, border_color="#000", border_width=2, )
buttonStop.grid(row=1, column=4, padx=20)

charger()

if lecture == "normale":
    buttonModeDeLecture = CTkButton(frameEnCours, text="🔀", font=("Helvetica", 18), command=toggle_mode_de_lecture, width=140)
else:
    buttonModeDeLecture = CTkButton(frameEnCours, text="➡️", font=("Helvetica", 18), command=toggle_mode_de_lecture, width=140)
buttonModeDeLecture.grid(row=3, column=1, padx=10, pady=10)

minimiser_barre_systeme()

verifier_fin_musique()
update_progress()
faire_defiler_texte()
update_temps()


def test():
    root.after(1000, test)
root.after(1000, test)

threading.Thread(target=raccourcis, daemon=True).start()

root.protocol("WM_DELETE_WINDOW", minimiser_barre_systeme)
# Run the application

root.mainloop()