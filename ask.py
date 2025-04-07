from definition import vn
import os

def vanna_ask(user_query, db_path, history):
    similar_question = vn.get_similar_question_sql(user_query)
    print('\nsimilar question from training data >', similar_question)
    # related_ddl = vn.get_related_ddl(user_query)
    # print('\nget related ddl >', related_ddl)
    print('\n-------------------------------')
    vn.connect_to_sqlite(db_path)

    final_tokens = {"input_tokens":0, "output_tokens":0}

    # result = vn.ask(user_query)

    # sql_query = vn.generate_sql(user_query)
    generate_sql_response = vn.generate_sql(user_query, history=history) # currently LLM will accept only the last 2 conversations as part of history in its prompt
    sql_query = generate_sql_response[0]
    final_tokens['input_tokens'] += generate_sql_response[1]['input_tokens']
    final_tokens['output_tokens'] += generate_sql_response[1]['output_tokens']
    print('sql_query >', sql_query, type(sql_query))
    print('final_tokens after generate_sql_query >', final_tokens)
    print('\n-------------------------')

    sql_result = vn.run_sql(sql_query)
    print('sql_result >', sql_result, type(sql_result))
    sql_result_to_dict = sql_result.to_dict(orient="records") # this is done to convert the df to list of dicts since Fastapi can't properly return a df. So, we will return sql_result_to_dict instead of directly returning sql_result.
    print('sql_result >', sql_result, type(sql_result))
    print('\n-------------------------')

    # nl_summary = vn.generate_summary(user_query, sql_result)
    generate_summary_response = vn.generate_summary(user_query, sql_result)
    nl_summary = generate_summary_response[0]
    final_tokens['input_tokens'] += generate_summary_response[1]['input_tokens']
    final_tokens['output_tokens'] += generate_summary_response[1]['output_tokens']
    print('answer >', nl_summary, type(nl_summary))
    print('final_tokens after generate_summary >', final_tokens)
    print('\n-------------------------')

    # follow_up_questions = vn.generate_followup_questions(user_query, sql_query, sql_result, 3)
    generate_followup_questions_response = vn.generate_followup_questions(user_query, sql_query, sql_result, 3)
    follow_up_questions = generate_followup_questions_response[0]
    final_tokens['input_tokens'] += generate_followup_questions_response[1]['input_tokens']
    final_tokens['output_tokens'] += generate_followup_questions_response[1]['output_tokens']
    print('follow_up_questions > ', follow_up_questions, type(follow_up_questions))
    print('final_tokens after generate_followup_questions >', final_tokens)
    print('\n-------------------------')

    chart_status = vn.should_generate_chart(sql_result) # this will return false if the DataFrame has more than one row and has numerical columns.
    print('chart_status >', chart_status)
    if chart_status == True:
        print('generating plot----')

        # plotly_code = vn.generate_plotly_code(user_query, sql_query, sql_result)
        generate_plotly_code_response = vn.generate_plotly_code(user_query, sql_query, sql_result)
        plotly_code = generate_plotly_code_response[0]
        final_tokens['input_tokens'] += generate_plotly_code_response[1]['input_tokens']
        final_tokens['output_tokens'] += generate_plotly_code_response[1]['output_tokens']
        print('plotly code >', plotly_code, type(plotly_code))
        print('final_tokens after generate_plotly_code >', final_tokens)
        print('\n-------------------------')

        plotly_figure = vn.get_plotly_figure(plotly_code, sql_result)
        image_path = os.path.join('D:\Mahindra finance\Projects_data\Vanna_AI\chart_images',"plotly_image.png")
        plotly_figure.write_image(image_path, format="png")
    else:
        plotly_code = ""

    final_price = price_calculator(final_tokens)
    print('final_price >', final_price)
    
    return {
            "sql_query": sql_query, 
            "sql_result": sql_result_to_dict,
            "nl_summary": nl_summary, 
            "plotly_code":plotly_code,
            "follow_up_questions":follow_up_questions,
            "final_tokens":final_tokens,
            "final_price_in_INR": final_price 
            }

def price_calculator(final_tokens):
    input_price = round(((final_tokens['input_tokens']*0.01289)/1000),4) 
    output_price = round(((final_tokens['output_tokens']*0.05156)/1000),4) 
    final_price = {"input_price":input_price,"output_price":output_price,"total_price":input_price+output_price}
    return final_price

# To know about other Vanna functions - https://vanna.ai/docs/base/#vanna.base.base.VannaBase.get_plotly_figure