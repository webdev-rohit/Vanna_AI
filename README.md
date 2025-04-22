# Vanna AI based NBFC chatbot

## About Vanna AI

Vanna is an MIT-licensed open-source Python RAG (Retrieval-Augmented Generation) framework for SQL generation and related functionality.

Vanna works in two easy steps -
a) Train a RAG "model" on your data.
b) Ask questions.

Visit their github page for more information - https://github.com/vanna-ai/vanna

See the [documentation](https://vanna.ai/docs/) for understanding Vanna AI functionalities and features.

## About the Project

The Project is a demonstration of a RAG-to-SQL generation scenario for an NBFC dataset downloaded from Kaggle. Refer - NBFC_data.csv/Test_Dataset.csv from this repository FYR.

## Watch the demo 📽️

<video src="streamlit_NBFC_VannaAI_demo.webm" width="600" autoplay loop></video>

## Code setup

To set up and run the project, follow these steps:

1. Clone the repository -
```bash
git clone https://github.com/webdev-rohit/Vanna_AI.git
```

2. Virtual environment creation and activation in the project directory (Windows)-
```bash
python -m venv venv
cd <project_directory>/venv/Scripts
activate
```

3. Inside the activated virtual environment venv -
```bash
pip install -r requirements.txt
```

## Run the application locally

1. Run the API in a terminal -
```bash
python app.py
```

2. Run the Streamlit frontend in another terminal -
```bash
python -m streamlit run chat_app.py
```