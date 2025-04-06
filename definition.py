from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat
import pandas as pd
import regex as re

import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("open_ai_api_key")

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

    def submit_prompt(self, prompt, **kwargs) -> str:
        if prompt is None:
            raise Exception("Prompt is None")

        if len(prompt) == 0:
            raise Exception("Prompt is empty")

        # Count the number of tokens in the message log
        # Use 4 as an approximation for the number of characters per token
        num_tokens = {'input_tokens':0, 'output_tokens':0}

        if kwargs.get("model", None) is not None:
            model = kwargs.get("model", None)
            response = self.client.chat.completions.create(
                model=model,
                messages=prompt,
                stop=None,
                temperature=self.temperature,
            )
        elif kwargs.get("engine", None) is not None:
            engine = kwargs.get("engine", None)
            response = self.client.chat.completions.create(
                engine=engine,
                messages=prompt,
                stop=None,
                temperature=self.temperature,
            )
        elif self.config is not None and "engine" in self.config:
            response = self.client.chat.completions.create(
                engine=self.config["engine"],
                messages=prompt,
                stop=None,
                temperature=self.temperature,
            )
        elif self.config is not None and "model" in self.config:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=prompt,
                stop=None,
                temperature=self.temperature,
            )
        else:
            if num_tokens > 3500:
                model = "gpt-3.5-turbo-16k"
            else:
                model = "gpt-3.5-turbo"

            response = self.client.chat.completions.create(
                model=model,
                messages=prompt,
                stop=None,
                temperature=self.temperature,
            )

        # print('\nresponse in submit_prompt >', response)

        # token count -
        usage = response.usage
        # print('usage >', usage)
        num_tokens['input_tokens'] = usage.prompt_tokens
        num_tokens['output_tokens'] = usage.completion_tokens
        # print('tokens used for this functionality >', num_tokens)

        # Find the first response from the chatbot that has text in it (some responses may not have text)
        # for choice in response.choices:
        #     if "text" in choice:
        #         # return choice.text
        #         return [choice.text, num_tokens]

        # If no response with text is found, return the first response's content (which may be empty)
        return [response.choices[0].message.content, num_tokens]
    
    def generate_sql(self, question: str, allow_llm_to_see_data=False, **kwargs) -> str:
        """
        Example:
        ```python
        vn.generate_sql("What are the top 10 customers by sales?")
        ```

        Uses the LLM to generate a SQL query that answers a question. It runs the following methods:

        - [`get_similar_question_sql`][vanna.base.base.VannaBase.get_similar_question_sql]

        - [`get_related_ddl`][vanna.base.base.VannaBase.get_related_ddl]

        - [`get_related_documentation`][vanna.base.base.VannaBase.get_related_documentation]

        - [`get_sql_prompt`][vanna.base.base.VannaBase.get_sql_prompt]

        - [`submit_prompt`][vanna.base.base.VannaBase.submit_prompt]


        Args:
            question (str): The question to generate a SQL query for.
            allow_llm_to_see_data (bool): Whether to allow the LLM to see the data (for the purposes of introspecting the data to generate the final SQL).

        Returns:
            str: The SQL query that answers the question.
        """
        if self.config is not None:
            initial_prompt = self.config.get("initial_prompt", None)
        else:
            initial_prompt = None
        if 'history' in kwargs.keys():
            chat_history = kwargs.get('history')
            question_sql_list = chat_history[-2:]
        # question_sql_list = self.get_similar_question_sql(question, **kwargs)
        print("chat history/question sql list in base.py >", question_sql_list)
        ddl_list = self.get_related_ddl(question, **kwargs)
        doc_list = self.get_related_documentation(question, **kwargs)
        prompt = self.get_sql_prompt(
            initial_prompt=initial_prompt,
            question=question,
            question_sql_list=question_sql_list,
            ddl_list=ddl_list,
            doc_list=doc_list,
            **kwargs,
        )
        self.log(title="SQL Prompt", message=prompt)
        response = self.submit_prompt(prompt, **kwargs)
        llm_response = response[0]
        tokens_used = response[1]
        self.log(title="LLM Response", message=llm_response)
        self.log(title="Tokens used in generate_sql", message=tokens_used)

        if 'intermediate_sql' in llm_response:
            if not allow_llm_to_see_data:
                return "The LLM is not allowed to see the data in your database. Your question requires database introspection to generate the necessary SQL. Please set allow_llm_to_see_data=True to enable this."

            if allow_llm_to_see_data:
                intermediate_sql = self.extract_sql(llm_response)

                try:
                    self.log(title="Running Intermediate SQL", message=intermediate_sql)
                    df = self.run_sql(intermediate_sql)

                    prompt = self.get_sql_prompt(
                        initial_prompt=initial_prompt,
                        question=question,
                        question_sql_list=question_sql_list,
                        ddl_list=ddl_list,
                        doc_list=doc_list+[f"The following is a pandas DataFrame with the results of the intermediate SQL query {intermediate_sql}: \n" + df.to_markdown()],
                        **kwargs,
                    )
                    self.log(title="Final SQL Prompt", message=prompt)
                    response = self.submit_prompt(prompt, **kwargs)
                    llm_response = response[0]
                    tokens_used = response[1]
                    self.log(title="LLM Response", message=llm_response)
                    self.log(title="Tokens used in generate_sql intermediate_sql stage", message=tokens_used)
                except Exception as e:
                    return f"Error running intermediate SQL: {e}"
        
        # return self.extract_sql(llm_response)
        extracted_sql = self.extract_sql(llm_response)
        return [extracted_sql, tokens_used]
    
    def generate_summary(self, question: str, df: pd.DataFrame, **kwargs) -> str:
        """
        **Example:**
        ```python
        vn.generate_summary("What are the top 10 customers by sales?", df)
        ```

        Generate a summary of the results of a SQL query.

        Args:
            question (str): The question that was asked.
            df (pd.DataFrame): The results of the SQL query.

        Returns:
            str: The summary of the results of the SQL query.
        """

        message_log = [
            self.system_message(
                f"You are a helpful data assistant. The user asked the question: '{question}'\n\nThe following is a pandas DataFrame with the results of the query: \n{df.to_markdown()}\n\n"
            ),
            self.user_message(
                "Briefly summarize the data based on the question that was asked. Do not respond with any additional explanation beyond the summary." +
                self._response_language()
            ),
        ]

        # summary = self.submit_prompt(message_log, **kwargs)
        response = self.submit_prompt(message_log, **kwargs)
        llm_response = response[0]
        tokens_used = response[1]
        self.log(title="LLM Response", message=llm_response)
        self.log(title="Tokens used in generate_summary", message=tokens_used)

        # return summary
        return [llm_response, tokens_used]

    def generate_followup_questions(
        self, question: str, sql: str, df: pd.DataFrame, n_questions: int = 5, **kwargs
    ) -> list:
        """
        **Example:**
        ```python
        vn.generate_followup_questions("What are the top 10 customers by sales?", sql, df)
        ```

        Generate a list of followup questions that you can ask Vanna.AI.

        Args:
            question (str): The question that was asked.
            sql (str): The LLM-generated SQL query.
            df (pd.DataFrame): The results of the SQL query.
            n_questions (int): Number of follow-up questions to generate.

        Returns:
            list: A list of followup questions that you can ask Vanna.AI.
        """

        message_log = [
            self.system_message(
                f"You are a helpful data assistant. The user asked the question: '{question}'\n\nThe SQL query for this question was: {sql}\n\nThe following is a pandas DataFrame with the results of the query: \n{df.head(25).to_markdown()}\n\n"
            ),
            self.user_message(
                f"Generate a list of {n_questions} followup questions that the user might ask about this data. Respond with a list of questions, one per line. Do not answer with any explanations -- just the questions. Remember that there should be an unambiguous SQL query that can be generated from the question. Prefer questions that are answerable outside of the context of this conversation. Prefer questions that are slight modifications of the SQL query that was generated that allow digging deeper into the data. Each question will be turned into a button that the user can click to generate a new SQL query so don't use 'example' type questions. Each question must have a one-to-one correspondence with an instantiated SQL query." +
                self._response_language()
            ),
        ]

        # llm_response = self.submit_prompt(message_log, **kwargs)
        response = self.submit_prompt(message_log, **kwargs)
        llm_response = response[0]
        tokens_used = response[1]
        self.log(title="LLM Response", message=llm_response)
        self.log(title="Tokens used in generate_followup_questions", message=tokens_used)

        numbers_removed = re.sub(r"^\d+\.\s*", "", llm_response, flags=re.MULTILINE)
        # return numbers_removed.split("\n")
        return [numbers_removed.split("\n"), tokens_used]
    
    def generate_plotly_code(
        self, question: str = None, sql: str = None, df_metadata: str = None, **kwargs
    ) -> str:
        if question is not None:
            system_msg = f"The following is a pandas DataFrame that contains the results of the query that answers the question the user asked: '{question}'"
        else:
            system_msg = "The following is a pandas DataFrame "

        if sql is not None:
            system_msg += f"\n\nThe DataFrame was produced using this query: {sql}\n\n"

        system_msg += f"The following is information about the resulting pandas DataFrame 'df': \n{df_metadata}"

        message_log = [
            self.system_message(system_msg),
            self.user_message(
                "Can you generate the Python plotly code to chart the results of the dataframe? Assume the data is in a pandas dataframe called 'df'. If there is only one value in the dataframe, use an Indicator. Respond with only Python code. Do not answer with any explanations -- just the code."
            ),
        ]

        # plotly_code = self.submit_prompt(message_log, kwargs=kwargs)
        response = self.submit_prompt(message_log, **kwargs)
        llm_response = response[0]
        tokens_used = response[1]
        self.log(title="LLM Response", message=llm_response)
        self.log(title="Tokens used in generate_plotly_code", message=tokens_used)

        # return self._sanitize_plotly_code(self._extract_python_code(plotly_code))
        # return self._sanitize_plotly_code(self._extract_python_code(llm_response))
        return [self._sanitize_plotly_code(self._extract_python_code(llm_response)), tokens_used]
    

system_prompt = """You are an SQLite expert. This data is a NBFC(Non-banking financial company) data. There is only table in this Database called 'nbfc_table'. Your job is to generate an SQL query to answer the question. Your response should ONLY be based on the given context and follow the response guidelines and format instructions.
"""
# Create an instance of MyVanna
vn = MyVanna(config={'api_key': api_key, 'model': 'gpt-4o-mini', 'initial_prompt':system_prompt, 'temperature': 0.0})