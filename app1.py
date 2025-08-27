import os
import json
import time
import pandas as pd
import pydeck as pdk
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# ------------------------------
# Setup
# ------------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="Pak Auto Doctor", layout="wide")
st.title("🚗 Pak Auto Doctor — Car Issue & Parts Finder for Pakistan")
st.markdown("### 👨‍💻 Developed by **M. Suleman And Team**")


# ------------------------------
# AI Model (Groq)
# ------------------------------
llm = ChatGroq(model="Gemma2-9b-It", groq_api_key=GROQ_API_KEY)

# ------------------------------
# Rule-based Engine
# ------------------------------
RULES = {
    "engine noise": "Possible worn engine bearings, timing chain, or low oil.",
    "smoke": "Check head gasket, piston rings, or valve seals.",
    "car not starting": "Could be battery, starter motor, or fuel pump issue.",
    "brakes not working": "Check brake pads, fluid, or master cylinder.",
}

class DiagnosticEngine:
    def __init__(self, rules):
        self.rules = rules

    def match(self, user_text):
        text = user_text.lower()
        matches = [val for key, val in self.rules.items() if key in text]
        return matches

engine = DiagnosticEngine(RULES)

# ------------------------------
# # Pakistani Markets
# ------------------------------
MARKETS = {
    "Lahore": {"location": [31.5204, 74.3587], "markets": ["Montgomery Road", "Bilal Gunj", "Hall Road"]},
    "Karachi": {"location": [24.8607, 67.0011], "markets": ["Shershah", "Plaza Market", "Tariq Road Auto"]},
    "Islamabad": {"location": [33.6844, 73.0479], "markets": ["G-8 Auto Market", "Pindi Saddar"]},
    "Faisalabad": {"location": [31.4181, 73.0776], "markets": ["Jhang Bazaar", "D Ground Auto Shops"]},
    "Jhang": {"location": [31.2698, 72.3182], "markets": ["Shahbaz Chowk Auto Market", "Ayub Chowk Spare Parts"]},
    "Sheikhupura": {"location": [31.7131, 73.9783], "markets": ["Sheikhupura Auto Market", "Ferozewala Spare Parts"]},
    "Gujrat": {"location": [32.5731, 74.0789], "markets": ["Shadiwal Road Auto Shops", "Bhimbher Road Auto Market"]},
    "Sukkur": {"location": [27.7139, 68.8363], "markets": ["Minara Road Auto Market", "Shalimar Auto Bazaar"]},
    "Larkana": {"location": [27.5589, 68.2141], "markets": ["Larkana Auto Market", "Station Road Spare Parts"]},
    "Sahiwal": {"location": [30.6667, 73.1000], "markets": ["High Street Auto Market", "Mall Mandi Spare Parts"]},
    "Okara": {"location": [30.8103, 73.4593], "markets": ["Okara City Auto Market", "GT Road Spare Parts"]},
    "Ghotki": {"location": [28.0060, 69.3150], "markets": ["Ghotki Auto Market", "Main Bazaar Spare Parts"]},
    "Sambrial": {"location": [32.4750, 74.3520], "markets": ["Sambrial Auto Market", "Airport Road Spare Parts"]},
    "Bhalwal": {"location": [32.2656, 72.8989], "markets": ["Bhalwal Auto Market", "Railway Road Spare Parts"]},
    "Badin": {"location": [24.6550, 68.8380], "markets": ["Badin Auto Market", "Station Road Spare Parts"]},
    "Taunsa Sharif": {"location": [30.7045, 70.6505], "markets": ["Taunsa Auto Market", "Main Chowk Spare Parts"]},
    "Barikot": {"location": [34.6606, 72.3535], "markets": ["Barikot Auto Market", "Shahbaz Chowk Spare Parts"]},
    "Phool Nagar": {"location": [31.2000, 73.9833], "markets": ["Phool Nagar Auto Market", "Main Bazaar Spare Parts"]},
    "Tando Muhammad Khan": {"location": [25.1236, 68.5380], "markets": ["TM Khan Auto Market", "Shahi Bazaar Spare Parts"]},
    "Pattoki": {"location": [31.0200, 73.8500], "markets": ["Pattoki Auto Market", "GT Road Spare Parts"]},
    "Shahdadpur": {"location": [25.9333, 68.6167], "markets": ["Shahdadpur Auto Market", "Main Bazaar Spare Parts"]},
    "Jauharabad": {"location": [32.2902, 72.5700], "markets": ["Jauharabad Auto Market", "Mall Road Spare Parts"]},
    "Kamber Ali Khan": {"location": [27.5867, 68.0000], "markets": ["Kamber Auto Market", "Shahi Bazaar Spare Parts"]},
    "Chichawatni": {"location": [30.5333, 72.7000], "markets": ["Chichawatni Auto Market", "Rail Bazaar Spare Parts"]},
    "Farooqabad": {"location": [31.7500, 74.0167], "markets": ["Farooqabad Auto Market", "Main Bazaar Spare Parts"]},
    "Pishin": {"location": [30.5833, 67.0000], "markets": ["Pishin Auto Market", "Station Road Spare Parts"]},
    "Dera Murad Jamali": {"location": [28.5466, 68.2231], "markets": ["DM Jamali Auto Market", "Main Bazaar Spare Parts"]},
    "Kotri": {"location": [25.3650, 68.3070], "markets": ["Kotri Auto Market", "Station Road Spare Parts"]},
    "Sangla Hill": {"location": [31.7167, 73.3833], "markets": ["Sangla Hill Auto Market", "Main Bazaar Spare Parts"]},
    "Gujar Khan": {"location": [33.2540, 73.3040], "markets": ["Gujar Khan Auto Market", "GT Road Spare Parts"]},
    "Kharian": {"location": [32.8100, 73.8800], "markets": ["Kharian Auto Market", "Grand Trunk Road Spare Parts"]},
    "Pasrur": {"location": [32.2700, 74.6670], "markets": ["Pasrur Auto Market", "Railway Road Spare Parts"]},
    "Shabqadar": {"location": [34.2150, 71.5667], "markets": ["Shabqadar Auto Market", "Main Chowk Spare Parts"]},
    "Kot Radha Kishan": {"location": [31.1700, 74.1000], "markets": ["Kot Radha Kishan Auto Market", "GT Road Spare Parts"]},
    "Ludhewala Waraich": {"location": [32.4600, 74.2000], "markets": ["Ludhewala Auto Market", "Main Bazaar Spare Parts"]},
    "Renala Khurd": {"location": [30.8833, 73.5667], "markets": ["Renala Khurd Auto Market", "Mall Road Spare Parts"]}
}
CITIES = list(MARKETS.keys())
# import json

# # ------------------------------
# # Load Pakistani Markets from JSON
# # ------------------------------
# with open("markets.json", "r", encoding="utf-8") as f:
#     MARKETS = json.load(f) 


class MarketFinder:
    def __init__(self, markets):
        self.markets = markets

    def suggest(self, city):
        if city in self.markets:
            return self.markets[city]["markets"]
        return ["No info available"]

market = MarketFinder(MARKETS)

# ------------------------------
# Chat memory
# ------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ------------------------------
# User Input
# ------------------------------
user_input = st.text_input("Describe your car issue (in Urdu, Roman Urdu, or English):")

col1, col2 = st.columns([3, 1])
with col1:
    city = st.selectbox("Select your city", CITIES)
with col2:
    use_ai = st.checkbox("Use AI (Groq)", value=True)

# ------------------------------
# Chat Logic
# ------------------------------
if st.button("Diagnose"):
    response_text = ""

    if use_ai:
        with st.spinner("Thinking..."):
            ai_response = llm.invoke([{"role": "user", "content": f"Car issue: {user_input}. Suggest diagnosis and fix."}])
            response_text += "🤖 AI Suggestion:\n" + ai_response.content + "\n\n"

    # Rule-based match
    matches = engine.match(user_input)
    if matches:
        response_text += "📋 Rule-based check:\n" + "\n".join(matches) + "\n\n"

    # Markets
    parts = market.suggest(city)
    response_text += f"🛒 Suggested markets in {city}:\n" + ", ".join(parts)

    # Save conversation
    st.session_state["messages"].append({"user": user_input, "bot": response_text})

# ------------------------------
# Display Chat
# ------------------------------
for chat in st.session_state["messages"]:
    st.markdown(f"**👤 You:** {chat['user']}")
    st.markdown(f"**🤖 Pak Auto Doctor:** {chat['bot']}")
    st.markdown("---")

# ------------------------------
# Map View
# ------------------------------
st.subheader("📍 Market Locations in Pakistan")
layer = pdk.Layer(
    "ScatterplotLayer",
    data=[{"lat": v["location"][0], "lon": v["location"][1], "city": k} for k, v in MARKETS.items()],
    get_position='[lon, lat]',
    get_color='[200, 30, 0, 160]',
    get_radius=50000,
)
view_state = pdk.ViewState(latitude=30.3753, longitude=69.3451, zoom=5)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

# ------------------------------
# Admin Controls (Advanced)
# ------------------------------
with st.expander("⚙️ Edit rules (advanced)"):
    rules_json = st.text_area("Rules JSON", value=json.dumps(RULES, indent=2), height=260)
    if st.button("Load rules from JSON text"):
        try:
            new_rules = json.loads(rules_json)
            engine = DiagnosticEngine(new_rules)
            st.success("Rules updated in memory (not saved to file).")
        except Exception as e:
            st.error(f"Invalid JSON: {e}")

with st.expander("⚙️ Edit markets (advanced)"):
    markets_json = st.text_area("Markets JSON", value=json.dumps(MARKETS, indent=2), height=260)
    if st.button("Load markets from JSON text"):
        try:
            new_markets = json.loads(markets_json)
            market = MarketFinder(new_markets)
            CITIES = list(new_markets.keys())
            st.success("Markets updated in memory (not saved to file).")
        except Exception as e:
            st.error(f"Invalid JSON: {e}")

# ------------------------------
# Export Logs
# ------------------------------
if st.button("Export chat log to CSV"):
    df = pd.DataFrame(st.session_state["messages"])
    df.to_csv("chat_log.csv", index=False)
    st.success("Chat log exported → chat_log.csv")
