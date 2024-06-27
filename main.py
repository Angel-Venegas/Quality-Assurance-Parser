'''
Create a script that a user is able to parse and input data from a QA CSV into a database.

Will input your weekly QA reports into MyCollection.csv.

Will input a mock "DB dump" which will be everyone's reports in one mega file into EveryonesReports. (watch out! missing dates!) EG4-DBDump.xlsx
    + Make sure to filter out all of the reports with missing data from the rows and also incorrect data.

Parse your collection csv file to the database (Notice that these csv files have correct formats for the columns and no missing values)

1. List all work done by Your user - from both collections(MyCollection and AllReports) (No duplicates)
2. Generate a csv file KevinChaja.csv where the test owner is "Kevin Chaja" (Do not filter any data, just include all of it, unless you parsed the xlsx file first and filtered the data before hand.)
3. All repeatable bugs - from both collections (No duplicates)
4. All Blocker bugs - from both collections (No duplicates)
5. All reports on build 3/19/2024 - from both collections (No duplicates)
6. Report back the very 1st test case (Test #1), the middle test case (you determine that),and the final test case of your database - from AllReports

    
CREATE DATABASE qa_reports;
CREATE USER 'QA_User'@'localhost' IDENTIFIED BY 'QA_User_Login123';
GRANT ALL PRIVILEGES ON `qa_reports`.* TO 'QA_User'@'localhost';
FLUSH PRIVILEGES;
'''


import os
import pandas as pd
import mysql.connector
import re
from datetime import datetime

def execute_query(query):
    try:
        # Connect to MySQL server
        mydb = mysql.connector.connect(
            host="localhost",
            user="QA_User",
            password="QA_User_Login123",
            database="qa_reports"
        )

        # Create cursor
        mycursor = mydb.cursor()

        # Execute query
        mycursor.execute(query)

        # Fetch results
        result = mycursor.fetchall()

        # Close connection
        mydb.close()

        return result
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
        return None



# 10. Report back the final test case from AllReports by Build # greatest to least and the first one in that order.
def get_last_test_case_from_allreports():
    query = """
        SELECT *
        FROM qa_reports.AllReports
        ORDER BY `Build #` DESC
        LIMIT 1
    """
    return execute_query(query)

# 9. Report back the middle test case from AllReports (ASC) by Build # get the middle date.
def get_middle_test_case_from_allreports():
    query = """
        SELECT *
        FROM (
            SELECT *, ROW_NUMBER() OVER (ORDER BY `Build #` ASC) AS row_num
            FROM qa_reports.AllReports
        ) AS ranked_cases
        WHERE row_num = (SELECT FLOOR((COUNT(*) + 1) / 2) FROM qa_reports.AllReports)
    """
    return execute_query(query)

# 8. Report back the very 1st test case (Test #1) from AllReports by Build #(Date), least to greatest and the first one.
def get_first_test_case_from_allreports():
    query = """
        SELECT *
        FROM qa_reports.AllReports
        ORDER BY `Build #` ASC
        LIMIT 1
    """
    return execute_query(query)

# 7. All reports on build 3/19/2024 - from both collections (No duplicates)
def reports_on_build(build_date):
    query = f"""
        SELECT DISTINCT *
        FROM (
            SELECT *
            FROM qa_reports.MyCollection
            WHERE `Build #` = '{build_date}'
            UNION
            SELECT *
            FROM qa_reports.AllReports
            WHERE `Build #` = '{build_date}'
        ) AS build_reports
    """
    return execute_query(query)

# 6. All Blocker bugs - from both collections (No duplicates)
def list_blocker_bugs():
    query = """
        SELECT DISTINCT *
        FROM (
            SELECT *
            FROM qa_reports.MyCollection
            WHERE LOWER(`Blocker?`) = 'yes'
            UNION
            SELECT *
            FROM qa_reports.AllReports
            WHERE LOWER(`Blocker?`) = 'yes'
        ) AS blocker_bugs
    """
    return execute_query(query)

# 5. All repeatable bugs - from both collections(MyCollection and AllReports)(No duplicates)
def list_repeatable_bugs():
    query = """
        SELECT DISTINCT *
        FROM (
            SELECT *
            FROM qa_reports.MyCollection
            WHERE LOWER(`Repeatable?`) = 'yes'
            UNION
            SELECT *
            FROM qa_reports.AllReports
            WHERE LOWER(`Repeatable?`) = 'yes'
        ) AS repeatable_bugs
    """
    return execute_query(query)

# 4. List all work done by Your user - from both collections (No duplicates)
def list_work_by_user(user_name):
    query = f"""
        SELECT DISTINCT *
        FROM (
            SELECT *
            FROM qa_reports.MyCollection
            WHERE `Test Owner` = '{user_name}'
            UNION
            SELECT *
            FROM qa_reports.AllReports
            WHERE `Test Owner` = '{user_name}'
        ) AS user_work
    """
    return execute_query(query)

# 3, 5, 6, 7 Function to generate a CSV file from a list of rows
def generate_csv_by_list(rows, output_csv):
    # Define the column names
    columns = ['Test #', 'Build #', 'Category', 'Test Case', 'Expected Result', 'Actual Result', 'Repeatable?', 'Blocker?', 'Test Owner']

    # Convert rows to DataFrame
    df = pd.DataFrame(rows, columns=columns)

    # Save DataFrame to CSV
    df.to_csv(output_csv, index=False, sep=';', encoding='utf-8-sig')

    print(f"CSV file '{output_csv}' generated successfully.")

# 3. Function to list all rows by test owner
def list_rows_by_test_owner(test_owner):
    query = f"""
        SELECT *
        FROM qa_reports.AllReports
        WHERE `Test Owner` = '{test_owner}'
    """
    return execute_query(query)

# Did not need to use this method
def convert_date_format(date_str): # Makes dates from YYYY-MM-DD to MM/DD/YYYY
    # Extract year, month, and day using regex
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})', date_str)
    if match:
        year, month, day = match.groups()
        # Construct the desired format
        return f"{int(month)}/{int(day)}/{year}"
    else:
        return None  # Return None if the date format is invalid
    
def convert_to_date_object(date_str): # 2024-03-05 00:00:00(HH:MM:SS) <class 'datetime.date'>
    if date_str is None:
        return None
    else:
        for fmt in ('%m/%d/%Y', '%m/%d/%y'): # date_str must be of format MM/DD/YYYY
            try:
                return datetime.strptime(date_str, fmt).date() # YYYY-MM-DD 00:00:00
            except ValueError:
                continue
        raise ValueError(f"time data '{date_str}' does not match any supported format")
    
def parse_csv_to_database(csv_file, table_name): 
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig', quotechar='"')

    # Drop rows with missing values
    df.dropna(inplace=True)

    # Ensure column names match expected
    expected_columns = ['Test #', 'Build #', 'Category', 'Test Case', 'Expected Result', 'Actual Result', 'Repeatable?', 'Blocker?', 'Test Owner']
    if not all(col in df.columns for col in expected_columns):
        raise ValueError(f"CSV file does not contain the required columns: {expected_columns}")

    # Connect to MySQL server
    mydb = mysql.connector.connect(
        host="localhost",
        user="QA_User",
        password="QA_User_Login123",
        database="qa_reports"
    )

    mycursor = mydb.cursor()

    # Create table if it does not exist
    mycursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            `Test #` INT,
            `Build #` DATE,
            Category VARCHAR(255),
            `Test Case` TEXT,
            `Expected Result` TEXT,
            `Actual Result` TEXT,
            `Repeatable?` VARCHAR(3),
            `Blocker?` VARCHAR(3),
            `Test Owner` TEXT
        )
    """)

    # Insert data into the table
    for index, row in df.iterrows():
        # Convert the `Build #` to a date object
        try:
            build_date = convert_to_date_object(row["Build #"])  # handle different date formats
            # print(build_date, type(build_date)) # 2024-02-25 <class 'datetime.date'>
        except ValueError as e:
            print(f"Skipping row {index + 1} due to date parsing error: {e}")
            continue
        
        sql = f"""
            INSERT INTO {table_name} (`Test #`, `Build #`, Category, `Test Case`, `Expected Result`, `Actual Result`, `Repeatable?`, `Blocker?`, `Test Owner`)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            int(row["Test #"]),
            build_date,
            row["Category"],
            row["Test Case"],
            row["Expected Result"],
            row["Actual Result"],
            row["Repeatable?"],
            row["Blocker?"],
            row["Test Owner"]
        )
        mycursor.execute(sql, values)

    # Commit changes and close connection
    mydb.commit()
    mydb.close()

    print(f"{csv_file} data inserted into database table {table_name} successfully.\n\n")

def parse_excel_to_database(excel_file, table_name): # Parses all of the reports to allreports table in the database
    # Read Excel file into DataFrame
    df = pd.read_excel(excel_file)

    # Drop rows with missing values
    df.dropna(inplace=True)

    # print(type(df['Build #'][1]), df['Build #'][1]) # 2024-03-19 00:00:00 <class 'datetime.datetime'>
    # Convert 'Build #' column to string to handle any errors with datetime format
    df['Build #'] = df['Build #'].astype(str)
    # print(type(df['Build #'][1]), df['Build #'][1]) # 2024-03-19 00:00:00 <class 'str'>

    # Connect to MySQL server
    mydb = mysql.connector.connect(
        host="localhost",
        user="QA_User",
        password="QA_User_Login123",
        database="qa_reports"
    )

    # Create cursor
    mycursor = mydb.cursor()

    # Create table if not exists
    mycursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            `Test #` INT,
            `Build #` DATE,
            Category VARCHAR(255),
            `Test Case` TEXT,
            `Expected Result` TEXT,
            `Actual Result` TEXT,
            `Repeatable?` VARCHAR(3),
            `Blocker?` VARCHAR(3),
            `Test Owner` TEXT
        )
    """)

    # Insert data into the table
    for index, row in df.iterrows():
        try:
            if not isinstance(row["Test #"], int): # If the test number is not an integer skip it
                continue

            test_number = int(row["Test #"])

            # Handle different date formats
            build_number = row["Build #"]
            # print(build_number) # For some reason this excel file makes the build number to be returned as a date object # YYYY-MM-DD 00:00:00 <class 'datetime.datetime'>
            if build_number != None and build_number != '': # Skip build numbers that do not have values
                # build_date = convert_to_date_object(build_number) # Converts MM/DD/YYYY  to  YYYY-MM-DD HH:MM:SS. We don't need this line for the reason above

                build_date = str(build_number).split()[0]  # Extract only the date part, YYYY-MM-DD
                build_number_str = build_date.replace('-', '')  # Remove hyphens and replace with nothing so they are combined

                # Check if the resulting string is a digit and if not, skip it
                if not build_number_str.isdigit():
                    continue

                # build_date = convert_date_format(build_date)  # Convert YYYY-MM-DD to MM/DD/YYYY We want a date object not a string in the database

                if build_date == None: # Skip build dates that returned none which means they did not have the proper format
                    continue
            else:
                raise ValueError(f"Row {index + 1} Skipped: Date format for 'Build #' is not supported.")

            category = row["Category"]
            test_case = row["Test Case"]
            expected_result = row["Expected Result"]
            actual_result = row["Actual Result"]
            repeatable = row["Repeatable?"]
            blocker = row["Blocker?"]
            test_owner = row["Test Owner"]

            if repeatable.lower() not in ['yes', 'no'] or blocker.lower() not in ['yes', 'no']: # Skip any rows that do not have yes or no for columns repeatable or blocker
                continue

            sql = f"""
                INSERT INTO {table_name} (`Test #`, `Build #`, Category, `Test Case`, `Expected Result`, `Actual Result`, `Repeatable?`, `Blocker?`, `Test Owner`)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                test_number,
                build_date,
                category,
                test_case,
                expected_result,
                actual_result,
                repeatable,
                blocker,
                test_owner
            )
            mycursor.execute(sql, values)

        except Exception as e:
            print(f"Error processing Row {index + 1}: {e}")

    # Commit changes and close connection
    mydb.commit()
    mydb.close()

    print(f"{excel_file} parsed to the database table \"{table_name}\" successfully.")


# Appends all of the data in input_csv after output_csv
def append_first_csv_after_second(input_csv, output_csv):
    try:
        # Reads input from a CSV file
        df_input = pd.read_csv(input_csv, sep=';', encoding='utf-8-sig')
    except FileNotFoundError:
        print(f"Input CSV file '{input_csv}' not found.")
        return
    
    # Appends selected rows to output CSV file
    df_input.to_csv(output_csv, mode='a', index=False, header=False, sep=';', encoding='utf-8-sig')
    
    print(f"Data from '{input_csv}' appended to '{output_csv}'.")




# Main Menu-----------------------------------------------------------------------------------------------------------------------------------------
def main_menu():
    while True:
        print("\n--- Main Menu ---")
        print('0. Append all of your reports in \"MyReports\" folder to a csv file \"MyCollection\"')
        print('1. Parse all valid data in EG$-DBDump.xlsx into the database table AllReports')
        print('2. Parse MyCollection.csv into the database table MyCollection')
        print('3. Generate a csv file KevinChaja.csv where the test owner is \"Kevin Chaja\" (Do not filter any data, just include all of it, unless you parsed the xlsx file first and filtered the data before hand.)')
        print("4. List all work done by \"Your Name\" from both collections no duplicates (Database Call)")
        print("5. List all repeatable bugs from both collections no duplicates (Database Call)")
        print("6. List all Blocker bugs from both collections no duplicates (Database Call)")
        print("7. List all reports on build 3/19/2024 from both collections no duplicates (Database Call)")
        print("8. Report back the very 1st test case (Test #1) from AllReports (Database Call)")
        print("9. Report back the middle test case from AllReports (Database Call)")
        print("10. Report back the final test case from AllReports (Database Call)")
        print("q. Quit")

        choice = input("Enter your choice: ")

        if choice == '0':
            print('\nOption 0:')
            if not os.path.exists('MyCollection.csv'):
                # Create an empty DataFrame with the specified columns
                columns = ['Test #', 'Build #', 'Category', 'Test Case', 'Expected Result', 'Actual Result', 'Repeatable?', 'Blocker?', 'Test Owner']
                df_empty = pd.DataFrame(columns=columns)
                
                # Save the DataFrame to a CSV file
                df_empty.to_csv('MyCollection.csv', index=False, sep=';', encoding='utf-8-sig')

                print('MyCollection.csv created.')

            for report in os.listdir('MyReports'): # Iterate over the array of directories
                append_first_csv_after_second('MyReports/' + report, 'MyCollection.csv')

            print()

        elif choice == '1':
            print('\nOption 1:')
            parse_excel_to_database('EG4-DBDump.xlsx', 'AllReports')
            print()

        elif choice == '2':
            print('\nOption 2:')
            parse_csv_to_database('MyCollection.csv', 'MyCollection') # CSV File, Database Table
            print()
        
        elif choice == '3':
            print('\nOption 3:')
            rows = list_rows_by_test_owner('Kevin Chaja') # Test Owner
            generate_csv_by_list(rows, 'KevinChava.csv') # Database rows list, csv file
            print()

        elif choice == '4':
            print('\nOption 4:')
            print_results(list_work_by_user("Angel Venegas"))
            print()

        elif choice == '5':
            print('\nOption 5:')
            generate_csv_by_list(list_repeatable_bugs(), 'All_Repeatable_Bugs.csv')
            print()

        elif choice == '6':
            print('\nOption 6:')
            generate_csv_by_list(list_blocker_bugs(), 'All_Blocker_Bugs.csv')
            print()

        elif choice == '7':
            print('\nOption 7:')
            generate_csv_by_list(reports_on_build("2024-03-19"), 'Reports_2024-03-19.csv') # 3/19/2024
            print()

        elif choice == '8':
            print('\nOption 8:')
            print_results(get_first_test_case_from_allreports())
            print()

        elif choice == '9':
            print('\nOption 9:')
            print_results(get_middle_test_case_from_allreports())
            print()

        elif choice == '10':
            print('\nOption 10:')
            print_results(get_last_test_case_from_allreports())
            print()

        elif choice.lower() == 'q':
            print('\nOption q:')
            print("Exiting the program...")
            break

        else:
            print("\nInvalid choice. Please enter a valid number or 'q' to quit.")

def print_results(results): # Prints all of the results
    if results: # If the list is not empty
        for result in results:
            print(result)
    else:
        print("No results found.")

main_menu()



'''
1st
Append all of your csv reports into a single csv report.

2nd
Parses MyCollection.csv into the database qa_reports to a table named MyCollection whose columns are Test #, Build #, Category, Test Case, Expected Result, Actual Result, Repeatble?, Blocker?
    Test # - There are at least 2 test cases for each user.
    Build # - The build number will be the currewnt date the test was performed in. In the context of software development and QA (Quality Assurance) reports, a build number is a unique identifier assigned to a specific build of the software. This number helps in tracking and identifying different versions or iterations of the software throughout the development and testing phases.
    Category - This is the part of the game you tested such as the tutorial, online match, main page, and etc..
    Test Case - A test case can include bugs found in the software or a user case where a user might suggest a feature for adequacy.
    Expected Result - What was the result you expected?
    Actual Result - What was the outcome of the test case.
    Repeatable? - Refers to the ability to consistently replicate a specific process or test with the same results. This concept is crucial for effective quality assurance, debugging, and development processes.
                  A repeatable build is a software build process that, when given the same source code, dependencies, and build environment, will produce an identical output every time. 
    Blocker? - An issue that prevents further progression in the software or testing phase.

2nd
Run all the menu options to see results, the console limits the amount of stuff printed there so if you want to see everything then run the queries on mySQL Work Bench or generate a csv file of all the outputs
'''