from definition import vn

def train_from_a_db(db_path):
    vn.connect_to_sqlite(db_path)
    # vn.connect_to_sqlite('D:\Mahindra finance\Projects_data\Vanna_AI\sqlite-sakila.db\sqlite-sakila.db')

    # test connection -
    test_query = "SELECT COUNT(*) FROM nbfc_table;"  # Adjust table name if different
    result = vn.run_sql(test_query)
    print('db_connection test result >', result)

    # The following sql command will extract all the DDL commands and metadata about the sqlite database
    df_ddl = vn.run_sql("SELECT type, sql FROM sqlite_master WHERE sql is not null")
    # print('df_ddl >', df_ddl, df_ddl.shape)

    # then, each of these are fed for training. Training here means creating the vector embeddings and storing them in vector DB
    for ddl in df_ddl['sql'].to_list():
        # print("\nTraining on this ddl >", ddl)
        vn.train(ddl=ddl)

    # At any time you can inspect what training data the package is able to reference
    training_data = vn.get_training_data()
    print('\nTrained data after hitting /train >')
    # print(training_data.sample(5))
    print(training_data.sample())
    print(training_data.shape)

    return "Training successful"

def add_data_to_training(db_path, user_query, sql_query):
    vn.connect_to_sqlite(db_path)
    vn.train(question=user_query, sql=sql_query)

    training_data = vn.get_training_data()
    print('\nTrained data after hitting /add_data_to_training >')
    # print(training_data)
    print(training_data.sample())
    print(training_data.shape)

    return "Training successful"

def trained_data():
    df_result = vn.get_training_data()
    df_result = df_result.to_dict(orient="records")
    return df_result
