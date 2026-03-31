import os  # <--- MANCAVA QUESTA RIGA!
import random
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

# 1. Inizializzazione App
app = FastAPI()

# LEGGI LA CHIAVE DA RENDER
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    print("ATTENZIONE: GROQ_API_KEY non trovata nelle variabili di ambiente!")
    # Mettiamo una stringa vuota per non far crashare l'avvio, 
    # ma l'IA darà errore finché non aggiungi la chiave su Render.
    api_key = "" 

client = Groq(api_key=api_key)

# 2. Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. File Statici
app.mount("/static", StaticFiles(directory="."), name="static")



COLORS = {
    "rosso": "#FF4757",
    "blu": "#2E86DE",
    "verde": "#2ED573",
    "giallo": "#FFA502"
}

@app.get("/")
async def read_index():
    return FileResponse('index.html')

@app.get("/api/spin/{gender}")
async def spin_wheel(gender: str, phase: int = 1):
    chosen_color = random.choice(list(COLORS.keys()))
    
    # Conversione sicura della fase
    try:
        p = int(phase)
    except:
        p = 1

    # Definizione prompt per i 3 step (EASY & FUNNY)
    if p == 1:
      s_msg = (
            "Respond ONLY with one of these exact commands: "
            "'KISS THE [COLOR] AREA', 'TOUCH THE [COLOR] AREA', or 'PINCH THE [COLOR] AREA'. "
            "DO NOT mention face parts like nose or eyes. Focus on the COLOR AREA. "
            "Maximum 5 words."
        )
    elif p == 2:
        s_msg = (
            "Invent ONE simple and funny couple challenge. "
            "Examples: 'Dance on one leg', 'Staring contest: loser pays', "
            "'Last to finish their drink pays', 'Take a goofy selfie'. "
            "Maximum 8 words. NO LISTS."
        )
    else:
      s_msg = (
            "You are a party legend. Invent ONE bold command to exchange Instagram or Phone. "
            "Examples: 'Swap Instagrams right now', 'Type your number in their phone', "
            "'Take a selfie and tag each other'. "
            "Maximum 8 words. NO LISTS."
        )

    try:
        # Chiamata all'IA (Modello aggiornato 2026)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": s_msg},
                {"role": "user", "content": f"Colore: {chosen_color}"}
            ],
            temperature=1.0,
        )
        # Pulizia risposta
        res = completion.choices[0].message.content.strip().split('\n')[0]
        ai_action = res.replace('"', '').replace('1.', '').strip().upper()
        
    except Exception as e:
        print(f"ERRORE REALE: {e}")
        # Fallback se l'IA fallisce (Step 2 Easy come richiesto)
        if p == 1:
            ai_action = f"TOCCA IL {chosen_color.upper()}"
        elif p == 2:
            ai_action = "GARA DI SGUARDI: CHI RIDE PAGA!"
        else:
            ai_action = "SCAMBIATEVI L'INSTAGRAM ORA!"

    return {
        "color": chosen_color,
        "color_hex": COLORS[chosen_color],
        "action": ai_action
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)