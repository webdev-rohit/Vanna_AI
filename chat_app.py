import streamlit as st
import requests
import pandas as pd
import os

API_URL = "http://localhost:5050/ask"  # Change to your FastAPI endpoint

st.set_page_config(page_title="NBFC Chat Assistant", layout="centered")

# Sidebar Navigation
st.sidebar.title("🔧 Navigation")
selected_page = st.sidebar.radio("Go to", ["Ask the bot", "Train the bot"])

# Initialize session state
if "chat_blocks" not in st.session_state:
    st.session_state.chat_blocks = []

if "user_history" not in st.session_state:
    st.session_state.user_history = []

# Initializing db path
db_path = os.path.abspath('sqlite_nbfc_data.db')

# ===============================
# PAGE 1: ASK THE BOT
# ===============================
if selected_page == "Ask the bot":
    # Title
    st.title("💬 Talk to the NBFC Chat Assistant")

    # --- Function to call API ---
    def call_api(query):
        payload = {
            "user_query": query,
            "history": st.session_state.user_history,
            "db_path": os.path.join(db_path, "nbfc_data.db")
        }

        try:
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            print('\nresponse >', response.json(), type(response.json()['message']))
            return response.json()
        except Exception as e:
            # st.error(f"API Error: {e}")
            st.error("Sorry, I am unable to answer your query at the moment.")
            # return None

    # --- Display previous Q&A blocks ---
    for idx, block in enumerate(st.session_state.chat_blocks):
        st.markdown(f"**🧍 You:** {block['user_input']}")

        st.markdown("##### 🛠️ SQL Query")
        st.code(block['sql_query'], language='sql')

        st.markdown("##### 🧠 Natural Language Summary")
        if block['nl_summary'] == "Sorry, I am unable to answer your query at the moment.":
            st.error(block['nl_summary'])
        else:
            st.success(block['nl_summary'])

        if block['sql_result']:
            st.markdown("##### 📊 SQL Result")
            df_result = pd.DataFrame(block['sql_result'])
            # st.dataframe(df_result)
            st.dataframe(df_result.head(1000))

        chart_images_path = os.path.abspath('chart_images')
        image_path = os.path.join(chart_images_path, "plotly_image.png")
        if block['plotly_code']:  # Means it's not empty
            print("\nplotly code exists")
            st.markdown("##### 📈 Plotly Result")
            print('image_path >', image_path)
            st.image(image_path)

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

        # 👍 Thumbs Up Button to Submit for Training
        if st.button("👍 Add to Training", key=f"thumbs_up_{idx}"):
            training_payload = {
                "db_path": os.path.join(db_path, "nbfc_data.db"),
                "user_query": block['user_input'],
                "sql_query": block['sql_query']
            }

            try:
                response = requests.post("http://localhost:5050/add_to_training", json=training_payload)
                response.raise_for_status()
                st.success(f"✅ Thanks for the feedback. Question added to training!")
            except Exception as e:
                st.error(f"❌ Error adding to training: {e}")

        st.divider()

    # --- Input for the next user question ---
    with st.form("chat_form", clear_on_submit=False):
        user_input = st.text_input("Ask your question:", key="user_input")
        submitted = st.form_submit_button("Submit")

    # --- Handle submission ---
    if submitted and user_input.strip() != "":
        # data = call_api(user_input)
        with st.spinner("⏳ Getting response..."):
            data = call_api(user_input)

        try:
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
                    "plotly_code": plotly_code,
                    "tokens": tokens,
                    "price": price,
                    "follow_ups": follow_ups
                })

                st.rerun()
        except:
            st.error("Sorry, I am unable to answer your query at the moment.")
            st.rerun()

# ===============================
# PAGE 2: TRAIN THE BOT
# ===============================
elif selected_page == "Train the bot":
    st.title("🧪 Add Data to the Trained bot")
    # --- Input for the next user question ---
    with st.form("training_form", clear_on_submit=False):
        user_query = st.text_area("Enter your user query")
        sql_query = st.text_area("Enter your sql query")

        submitted = st.form_submit_button("Submit Training Data")

    if submitted:
        if not user_query.strip() or not sql_query.strip():
            st.warning("Please provide both a question and corresponding valid SQL.")
        else:
            # Make POST request to API
            training_payload = {
                "db_path": os.path.join(db_path, "nbfc_data.db"),
                "user_query": user_query,
                "sql_query": sql_query
            }

            try:
                response = requests.post("http://localhost:5050/add_to_training", json=training_payload)
                response.raise_for_status()
                st.success("✅ Training data submitted successfully!")
            except Exception as e:
                st.error(f"❌ Error submitting training data: {e}")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        show_trained_button = st.button("Show trained data")
    if show_trained_button:
        try:
            response = requests.get("http://localhost:5050/show_trained_data")
            response.raise_for_status()
            st.dataframe(response.json())
        except Exception as e:
            st.error(f"❌ Error showing trained data: {e}")

    
