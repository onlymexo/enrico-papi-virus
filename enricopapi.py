import cv2
import time
import os
import platform
import subprocess
import urllib.request

# Configurazione
VIDEO_PATH = "video.mp4"
SEC_DISTRACTED = 2.0
XML_FILE = "haarcascade_frontalface_default.xml"
XML_URL = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"

# Scarica l'XML se non c'è già
if not os.path.exists(XML_FILE):
    print("Download XML in corso...")
    try:
        urllib.request.urlretrieve(XML_URL, XML_FILE)
    except Exception as e:
        print(f"Errore download XML: {e}")

def play_video(path):
    """Apre il video col player predefinito"""
    system_name = platform.system()
    if system_name == "Windows":
        os.startfile(path)
    elif system_name == "Darwin":
        subprocess.call(["open", path])
    else:
        subprocess.call(["xdg-open", path])

def close_video_player():
    """Chiude i lettori video più comuni appena torni attento"""
    system_name = platform.system()
    if system_name == "Windows":
        # Kill dei lettori standard di Windows (Film e TV, Windows Media Player, VLC, MPV)
        players = ["Microsoft.Media.Player.exe", "wmplayer.exe", "vlc.exe", "mpv.exe", "ApplicationFrameHost.exe"]
        for player in players:
            subprocess.call(f"taskkill /f /im {player} >nul 2>&1", shell=True)
    elif system_name == "Darwin":
        subprocess.call(["killall", "QuickTime Player"])
    else:
        subprocess.call(["pkill", "-f", "vlc|mpv|totem"])

face_cascade = cv2.CascadeClassifier(XML_FILE)

cap = cv2.VideoCapture(0)
distracted_start_time = None
video_played = False

print("👀 Enrico Papi con Auto-Close attivo. Premi 'q' per uscire.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

    is_looking_away = len(faces) == 0

    if is_looking_away:
        if distracted_start_time is None:
            distracted_start_time = time.time()
        
        elapsed = time.time() - distracted_start_time
        cv2.putText(frame, f"DISTRAZIONE! {elapsed:.1f}s", (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Se ti distrai troppo, fa partire il video
        if elapsed >= SEC_DISTRACTED and not video_played:
            print("🚨 DISTRAZIONE DETECTED! Parte il video.")
            play_video(VIDEO_PATH)
            video_played = True
    else:
        # Se eri distratto e il video era già partito, lo CHIUDE appena torni a guardare!
        if video_played:
            print("👍 Bravo, ti sei rimesso attento. Chiudo il video!")
            close_video_player()
            video_played = False

        distracted_start_time = None
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
        cv2.putText(frame, "STAI ATTENTO: OK", (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Anti-Distraction Cam", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()