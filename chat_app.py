import streamlit as st
import requests
import pandas as pd
import os

API_URL = "http://localhost:5050/ask"  # Change to your FastAPI endpoint

st.set_page_config(page_title="NBFC Chat Assistant", layout="centered")

# Initialize session state
if "chat_blocks" not in st.session_state:
    st.session_state.chat_blocks = []

if "user_history" not in st.session_state:
    st.session_state.user_history = []

# Title
st.title("💬 NBFC Chat Assistant")

# --- Function to call API ---
def call_api(query):
    payload = {
        "user_query": query,
        "history": st.session_state.user_history,
        "db_path": "D:\\Mahindra finance\\Projects_data\\Vanna_AI\\sqlite_nbfc_data.db\\nbfc_data.db"
    }

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        print('\nresponse >', response.json())
        return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# --- Display previous Q&A blocks ---
for idx, block in enumerate(st.session_state.chat_blocks):
    st.markdown(f"**🧍 You:** {block['user_input']}")

    st.markdown("##### 🧠 Natural Language Summary")
    st.success(block['nl_summary'])

    st.markdown("##### 🛠️ SQL Query")
    st.code(block['sql_query'], language='sql')

    if block['sql_result']:
        st.markdown("##### 📊 SQL Result")
        df_result = pd.DataFrame(block['sql_result'])
        st.dataframe(df_result)

    path = "D:\\Mahindra finance\\Projects_data\\Vanna_AI\\chart_images"
    image_path = os.path.join(path, "plotly_image.png")
    if block['plotly_code']:  # Means it's not empty
        print("\nplotly code exists")
        st.markdown("##### 📈 Plotly Result")
        st.image(image_path)
    else:
        print("\nplotly code does not exist")
        if os.path.exists(image_path):
            os.remove(image_path)

    if block['tokens']:
        st.markdown("##### 💰 Tokens used Breakdown")
        tokens_table = pd.DataFrame([
            {"Type": "Input", "Tokens": block['tokens']["input_tokens"]},
            {"Type": "Output", "Tokens": block['tokens']["output_tokens"]},
        ])
        st.table(tokens_table)

    if block['price']:
        st.markdown("##### 💰 Cost Breakdown (in INR)")
        price_table = pd.DataFrame([
            {"Type": "Input", "Price (₹)": block['price']["input_price"]},
            {"Type": "Output", "Price (₹)": block['price']["output_price"]},
            {"Type": "Total", "Price (₹)": block['price']["total_price"]}
        ])
        st.table(price_table)

    if block['follow_ups']:
        st.markdown("##### 💡 Follow-up Questions")
        for q in block['follow_ups']:
            st.markdown(f"- {q}")

    st.divider()

# --- Input for the next user question ---
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Ask your question:", key="user_input")
    submitted = st.form_submit_button("Submit")

# --- Handle submission ---
if submitted and user_input.strip() != "":
    # data = call_api(user_input)
    with st.spinner("⏳ Getting response..."):
        data = call_api(user_input)

    if data:
        sql_query = data['message']['sql_query']
        sql_result = data['message']['sql_result']
        nl_summary = data['message']['nl_summary']
        plotly_code = data['message']['plotly_code']
        tokens = data['message']['final_tokens']
        price = data['message']['final_price_in_INR']
        follow_ups = data['message'].get("follow_up_questions", [])

        # Store this interaction in history
        st.session_state.user_history.append({
            "question": user_input,
            "sql": sql_query
        })

        st.session_state.chat_blocks.append({
            "user_input": user_input,
            "nl_summary": nl_summary,
            "sql_query": sql_query,
            "sql_result": sql_result,
            "plotly_code": "",
            "tokens": tokens,
            "price": price,
            "follow_ups": follow_ups
        })

        st.rerun()