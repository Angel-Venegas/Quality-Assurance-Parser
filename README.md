# Quality-Assurance-Parser

# QA Reports Parser and Database Manager

## Overview

This project provides a script to parse and input data from a QA CSV file into a MySQL database. It handles weekly QA reports and a mock "DB dump" file, ensuring correct data formats and filtering out incorrect or missing data. The script allows you to generate various reports and queries from the database.

## Requirements

- Python 3.9.2 0or 3.12.2
- pandas library
- mysql-connector-python library
- MySQL database server
- MySQL Workbench (optional for easier database management)


## Setup

### Install Required Python Libraries

```bash
pip install pandas mysql-connector-python
```

### Execute Command To Create mySQL User:
Execute This command to create a user:
CREATE DATABASE qa_reports;
CREATE USER 'QA_User'@'localhost' IDENTIFIED BY 'QA_User_Login123';
GRANT ALL PRIVILEGES ON `qa_reports`.* TO 'QA_User'@'localhost';
FLUSH PRIVILEGES;

## Menu Options
0. Append all of your reports in "MyReports" folder to a CSV file "MyCollection":
  * Combines all CSV files in the "MyReports" folder into a single CSV file named MyCollection.csv.

1. Parse all valid data in EG4-DBDump.xlsx into the database table AllReports:
  * Parses data from the provided Excel file and inputs it into the AllReports table in the database.

2. Parse MyCollection.csv into the database table MyCollection:
  * Inputs data from MyCollection.csv into the MyCollection table in the database.

3. Generate a CSV file KevinChaja.csv where the test owner is "Kevin Chaja":
  * Generates a CSV file with all reports from "Kevin Chaja".

4. List all work done by "Your Name" from both collections, no duplicates:
  * Lists all work done by the specified user from both collections without duplicates.

5. List all repeatable bugs from both collections, no duplicates:
  * Lists all repeatable bugs from both collections without duplicates and generates a CSV file All_Repeatable_Bugs.csv.

6. List all Blocker bugs from both collections, no duplicates:
  * Lists all Blocker bugs from both collections without duplicates and generates a CSV file All_Blocker_Bugs.csv.

7. List all reports on build 3/19/2024 from both collections, no duplicates:
  * Lists all reports from the specified build date from both collections without duplicates and generates a CSV file Reports_2024-03-19.csv.

8. Report back the very 1st test case (Test #1) from AllReports:
  * Lists the first test case from AllReports ordered by Build #.

9. Report back the middle test case from AllReports:
  * Lists the middle test case from AllReports ordered by Build #.

10. Report back the final test case from AllReports:
  * Lists the last test case from AllReports ordered by Build #.
