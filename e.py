import tkinter as tk
from tkinter import Canvas, Frame, Scrollbar
import threading
import pyttsx3
import speech_recognition as sr
from openai import OpenAI
import time
import math
import random

# ---------------- OPENAI ----------------
client = OpenAI(api_key="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")  # Replace with your OpenAI API key

# ---------------- VOICE ----------------
engine = pyttsx3.init()
engine.setProperty("rate", 160)
engine.setProperty("volume", 1)
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)

# ---------------- MIC ----------------
recognizer = sr.Recognizer()
mic = sr.Microphone()

# ---------------- GUI ----------------
root = tk.Tk()
root.title("3D Gujarati Voice AI")
root.geometry("650x750")
root.configure(bg="#121212")

# ---------------- TOP FRAME (Planet) ----------------
top_frame = Frame(root, bg="#121212")
top_frame.pack(fill="x", padx=10, pady=5)

canvas = Canvas(top_frame, width=600, height=200, bg="#121212", highlightthickness=0)
canvas.pack(pady=5)

start_btn = tk.Button(top_frame, text="Start AI", bg="#ff6600", fg="white", font=("Helvetica",14,"bold"))
start_btn.pack(pady=5)

# ---------------- BOTTOM FRAME (Chat) ----------------
chat_frame = Frame(root, bg="#1f1f2f")
chat_frame.pack(fill="both", expand=True, padx=10, pady=10)

chat_canvas = Canvas(chat_frame, bg="#1f1f2f", highlightthickness=0)
scrollbar = Scrollbar(chat_frame, orient="vertical", command=chat_canvas.yview)
chat_canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
chat_canvas.pack(side="left", fill="both", expand=True)

messages_frame = Frame(chat_canvas, bg="#1f1f2f")
chat_canvas.create_window((0,0), window=messages_frame, anchor="nw")

# ---------------- CHAT BUBBLES ----------------
def add_message(msg, sender="ai"):
    bubble_color = "#ffcc00" if sender=="ai" else "#00ffcc"
    anchor_side = "w" if sender=="ai" else "e"
    bubble = tk.Label(messages_frame, text=msg, bg=bubble_color, fg="#121212",
                      font=("Helvetica",12,"bold"), wraplength=400, justify="left", padx=10, pady=5)
    bubble.pack(anchor=anchor_side, pady=5, padx=10)
    chat_canvas.update_idletasks()
    chat_canvas.yview_moveto(1.0)

# ---------------- PLANET ROTATION ----------------
angle = 0
stars = [(random.randint(0,600), random.randint(0,200)) for _ in range(40)]

def rotate_planet():
    global angle
    canvas.delete("all")
    # stars
    for x,y in stars:
        canvas.create_oval(x,y,x+2,y+2,fill="white")
    # planet
    x0,y0,x1,y1 = 290,80,310,100
    canvas.create_oval(x0,y0,x1,y1,fill="#00ccff", outline="#00ffcc", width=2)
    # rings
    for i in range(8):
        rad = math.radians(angle + i*45)
        cx = (x0+x1)/2 + 35*math.cos(rad)
        cy = (y0+y1)/2 + 15*math.sin(rad)
        size = 3 + (i%3)
        canvas.create_oval(cx-size, cy-size, cx+size, cy+size, fill="#ffcc00")
    # halo
    canvas.create_oval(x0-10,y0-10,x1+10,y1+10, outline="#33ccff", width=1)
    angle += 3
    root.after(50, rotate_planet)

# ---------------- AI + VOICE ----------------
def speak(text):
    def run():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=run, daemon=True).start()

def ask_ai(question):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are a friendly Gujarati AI assistant. Always reply in Gujarati."},
                {"role":"user","content":question}
            ]
        )
        return response.choices[0].message.content
    except:
        return "Maaf karjo, AI server ma problem chhe."

def listen():
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio, language="gu-IN")
    except:
        return ""

# ---------------- MAIN LOOP ----------------
def main_loop():
    speak("Namaskar! Hu tamari madad mate taiyar chhu.")
    add_message("✅ Gujarati Voice AI Ready","ai")
    while True:
        user_input = listen()
        if user_input == "":
            continue
        add_message(f"🎤 Tame: {user_input}","user")
        if any(word in user_input.lower() for word in ["bandh","exit","bye"]):
            ai_reply = "Barabar, pachi maliye. Aabhar."
            add_message(f"💬 AI: {ai_reply}","ai")
            speak(ai_reply)
            break
        ai_reply = ask_ai(user_input)
        add_message(f"💬 AI: {ai_reply}","ai")
        speak(ai_reply)

# ---------------- START ----------------
def start_ai():
    start_btn.config(state="disabled")
    threading.Thread(target=main_loop, daemon=True).start()
    rotate_planet()

start_btn.config(command=start_ai)

root.mainloop()
