# pte/webapp/app.py
from __future__ import annotations
import streamlit as st
from typing import Dict
from pte.assistant.session import Session
from pte.nlp.llm_intent_ollama import llm_extract_intent

st.set_page_config(page_title="Personal Travel Assistant", page_icon="🛫", layout="centered")

# --- Sidebar: model + data sources ---
st.sidebar.title("Settings")

model = st.sidebar.text_input("Ollama model", value="llama3", help="Any free model you have via Ollama (e.g., llama3, mistral, phi3)")
calendar_mode = st.sidebar.radio("Hyatt data mode", options=["fixture","import"], index=0,
                                 help="Use 'import' to provide actual Hyatt points calendars for Park Hyatt & Andaz.")
prefer_single_hotel = st.sidebar.toggle("Prefer single hotel (only switch if savings ≥ 10k)", value=False)

import_paths = None
if calendar_mode == "import":
    st.sidebar.caption("Upload Hyatt points JSON for your dates")
    ph = st.sidebar.file_uploader("Park Hyatt Tokyo JSON", type=["json"], accept_multiple_files=False)
    az = st.sidebar.file_uploader("Andaz Tokyo JSON", type=["json"], accept_multiple_files=False)
    if ph and az:
        import json, tempfile, os
        import_paths = {}
        for label, fh in (("Park Hyatt Tokyo", ph), ("Andaz Tokyo Toranomon Hills", az)):
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            tmp.write(fh.read()); tmp.close()
            import_paths[label] = tmp.name
        st.sidebar.success("Calendars loaded.")

# --- Initialize session state ---
if "engine" not in st.session_state:
    st.session_state.engine = Session(
        calendar_mode=calendar_mode,
        import_paths=import_paths,
        prefer_single_hotel=prefer_single_hotel
    )

# Keep settings in sync when user changes sidebar
engine: Session = st.session_state.engine
engine.calendar_mode = calendar_mode
engine.import_paths = import_paths
engine.prefer_single_hotel = prefer_single_hotel

st.title("🛫 Personal Travel Assistant")
st.write("Talk to me in natural language. Example: *“Plan Tokyo nonstop, start at Park Hyatt; Nov 20 2027 to Dec 4 2027; show plan.”*")

# --- Chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role":"assistant","content":"Hi! Tell me your dates and preferences. I support MSP→HND nonstop and Hyatt (Park Hyatt, Andaz) allocations."})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- User input ---
user_text = st.chat_input("Type here (e.g., 'Nov 20 2027 to Dec 4 2027; prefer nonstop; start at Park Hyatt; show plan')")
if user_text:
    # Echo user
    st.session_state.messages.append({"role":"user","content":user_text})
    with st.chat_message("user"): st.markdown(user_text)

    # 1) Parse with Ollama
    with st.spinner("Thinking…"):
        intent_obj = llm_extract_intent(user_text, model=model)
        intent = intent_obj.get("intent", "plan_trip")
        slots: Dict = intent_obj.get("slots", {})

    # 2) Apply to engine
    result = engine.apply_llm_intent(intent, slots)

    # 3) Show result + plan (if generated)
    with st.chat_message("assistant"):
        st.markdown(result)
        if engine.last_markdown and intent in ("show_plan","plan_trip"):
            st.markdown("---")
            st.markdown(engine.last_markdown)

    st.session_state.messages.append({"role":"assistant","content":result})
    if engine.last_markdown and intent in ("show_plan","plan_trip"):
        st.session_state.messages.append({"role":"assistant","content":engine.last_markdown})
