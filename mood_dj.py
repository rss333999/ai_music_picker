import streamlit as pd_app
import json
import urllib.parse  # Built-in tool to format web links safely
from google import genai
from google.genai import types

# Grab your API key from your existing local setup or Streamlit secrets
MY_API_KEY = pd_app.secrets.get("GEMINI_API_KEY")
client = genai.Client(api_key=MY_API_KEY)

pd_app.set_page_config(page_title="AI Mood DJ", page_icon="🎵", layout="centered")

pd_app.title("🎵 AI Mood DJ & Playlist Generator")
pd_app.write("Tell me your exact vibe, and I'll generate a custom Spotify roadmap.")
# 1. Quick-select mood buttons or custom text input
mood_tags = [
    "🧠 Deep Focus Coding",
    "🔥 Gym Pump", 
    "☕ Lo-Fi Study", 
    "🔋 Post-Exam Burnout",
    "🌧️ Rainy Day Melancholy", 
    "🌌 Midnight Drive", 
    "📈 Hyper Productive",
    "🌅 Chill Morning Vibe"
]
selected_tag = pd_app.radio("Choose a quick vibe:", mood_tags, horizontal=True)

custom_mood = pd_app.text_input("Or type your exact custom vibe/feeling:")

# Determine the final mood payload
final_mood = custom_mood if custom_mood.strip() != "" else selected_tag

if pd_app.button("Generate My Vibe", type="primary"):
    with pd_app.spinner("Curating your tracks..."):
        
        # 2. Tell Gemini to return structured music data
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f'Act as an expert music curator. Recommend 5 distinct songs perfectly suited for this mood: "{final_mood}".',
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "playlist_title": types.Schema(type=types.Type.STRING),
                        "tracks": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(
                                type=types.Type.OBJECT,
                                properties={
                                    "song_name": types.Schema(type=types.Type.STRING),
                                    "artist": types.Schema(type=types.Type.STRING),
                                    "reason": types.Schema(type=types.Type.STRING)
                                },
                                required=["song_name", "artist", "reason"]
                            )
                        ),
                    },
                    required=["playlist_title", "tracks"],
                ),
            ),
        )
        
        # 3. Store the result in memory
        pd_app.session_state['music_data'] = json.loads(response.text)

# 4. Display the results with direct Spotify Search links
if 'music_data' in pd_app.session_state:
    data = pd_app.session_state['music_data']
    pd_app.markdown("---")
    pd_app.subheader(f"🎧 Curated Album: {data['playlist_title']}")
    
    for track in data['tracks']:
        song = track['song_name']
        artist = track['artist']
        reason = track['reason']
        
        # Generate a safe, clickable Spotify search URL automatically
        search_query = urllib.parse.quote(f"{song} {artist}")
        spotify_url = f"https://open.spotify.com/search/{search_query}"
        
        # Display nicely in UI
        pd_app.markdown(f"### 🎵 {song} — *{artist}*")
        pd_app.write(f"👉 *Why it fits:* {reason}")
        pd_app.markdown(f"[🟢 Open and Play on Spotify]({spotify_url})")
        pd_app.write("")
