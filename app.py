import streamlit as st
import requests
import json

# Konfigurasi halaman dasar
st.set_page_config(
    page_title="🤖 Artificial Ipin Chatbot",
    page_icon="🤖",
    layout="centered"
)

# --- FUNGSI UNTUK API ---
def get_ai_response(messages_payload, model_name, api_key):
    if not api_key:
        st.error("API Key tidak diberikan. Masukkan di sidebar.", icon="🚨")
        return None
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            data=json.dumps({
                "model": model_name,
                "messages": messages_payload,
            })
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal terhubung ke API: {e}", icon="🔥")
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}", icon="👎")
    return None

# --- SIDEBAR UNTUK PENGATURAN ---
with st.sidebar:
    st.markdown("""
    <style>
    .sidebar .block-container {
        background-color: #1e1e2f;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Settings")
    st.markdown("""
    <hr style='border: 1px solid #444;'>
    """, unsafe_allow_html=True)

    api_key_input = st.text_input(
        "🔑 OpenRouter API Key",
        type="password",
        placeholder="sk-or-v1-...",
        help="Dapatkan API key Anda di https://openrouter.ai/keys"
    )

    MODEL_LIST = {
        "Mistral 7B (Free)": "mistralai/mistral-7b-instruct:free",
        "Llama 3 8B (Free)": "meta-llama/llama-3-8b-instruct:free",
        "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
        "Google Gemini Pro": "google/gemini-pro"
    }
    selected_model_name = st.selectbox("🤖 Pilih Model", options=list(MODEL_LIST.keys()))
    selected_model_id = MODEL_LIST[selected_model_name]

    max_tokens = st.slider("🪙 Max Tokens", min_value=50, max_value=4096, value=512, step=50,
                           help="Atur jumlah maksimum token dalam respons AI.")

    if st.button("🧹 Hapus Riwayat Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
# --- AREA CHAT UTAMA ---
st.title("🤖 Artificial Ipin Chatbot")
st.caption(f"Model digunakan: {selected_model_name}")

st.markdown(
    """
    <style>
    .block-container {
        padding: 2rem 1rem;
        height: 90vh;
        display: flex;
        flex-direction: column;
        background-color: #0e1117;
        color: #f0f0f0;
    }
    #chat-input-area {
        position: sticky;
        bottom: 0;
        background: #0e1117;
        padding: 1rem 0;
        border-top: 1px solid #333;
        z-index: 10;
    }
    .stChatMessage {
        margin-bottom: 1.5rem;
        background-color: #1f2b3a;
        padding: 1rem;
        border-radius: 10px;
    }
    .stButton > button, .stTextInput > div > input {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# Inisialisasi riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Menampilkan pesan pembuka dari asisten jika chat kosong
if not st.session_state.messages:
    st.session_state.messages.append(
        {"role": "assistant", "content": "Halo! Ada yang bisa saya bantu hari ini?"}
    )

# Menampilkan semua pesan dari riwayat
for message in st.session_state.messages:
    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Input dari pengguna
if prompt := st.chat_input("Tulis pesan Anda..."):
    # Tambah dan tampilkan pesan pengguna
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # Dapatkan dan tampilkan respons dari AI
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Sedang berpikir..."):
            ai_response = get_ai_response(
                messages_payload=st.session_state.messages,
                model_name=selected_model_id,
                api_key=api_key_input
            )
            if ai_response:
                st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            else:
                st.error("Gagal mendapatkan respons dari AI.")