import streamlit as st

def inject_css():
    CSS = """
    <style>
    .stApp {
      /* Fantasy galaxy gradient + starfield dots */
      background: radial-gradient(1200px 600px at 10% 10%, rgba(64,46,110,.35), transparent 60%),
                  radial-gradient(900px 500px at 85% 25%, rgba(28,64,120,.35), transparent 60%),
                  radial-gradient(800px 400px at 20% 90%, rgba(20,40,80,.35), transparent 60%),
                  linear-gradient(180deg, #0a0f1e 0%, #070b16 60%, #04070f 100%);
      color: #e6ecff;
    }
    .glass { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; backdrop-filter: blur(8px); padding: 1rem 1.2rem; box-shadow: 0 10px 30px rgba(0,0,0,.35); }
    h1, h2, h3 { color: #d9e1ff; text-shadow: 0 0 10px rgba(120,120,255,.25); }
    .badge { display:inline-block; padding:.15rem .5rem; border:1px solid #3a4b8a; border-radius:999px; font-size:.75rem; color:#a7b6ff; }
    .stButton>button { background: linear-gradient(135deg, #3943b7, #933cc3); border:0; color:white; font-weight:600; border-radius: 12px; padding:.6rem 1rem; box-shadow: 0 6px 16px rgba(0,0,0,.35); }
    .stButton>button:hover { filter: brightness(1.1); }
    a { color:#8fb4ff !important; }
    </style>
    """
    st.markdown(CSS, unsafe_allow_html=True)
