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

Download the file - streamlit_NBFC_VannaAI_demo.webm provided in this repository to see the Streamlit demo.

## Features and functionalities

1) Gives the SQL Query, NL Summary, SQL Result, Generated Plot graph images, Follow-up queries, Tokens and cost utilized for every user query asked.
2) Supports conversational history for answering follow-up questions based on context.
3) Has 'Add question to Training' feature. Alongwith it you can separately train a question and its SQL query in 'Train the bot' section and also view the trained data.
4) For Geeks - Code has implementations of Behavior customizations of the standard methods of VannaBase class in definition.py file.

## Code setup

To set up and run the project, follow these steps:

1. Clone the repository -
```bash
git clone https://github.com/webdev-rohit/Vanna_AI.git
```

2. Virtual environment creation and activation in the project directory (Windows) -
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

Connect with me on my email - rohitvishssj5@gmail.com. Contributions are welcome!