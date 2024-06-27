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

### 1. Install Required Python Libraries

```bash
pip install pandas mysql-connector-python

### Execute This command to create a user:
CREATE DATABASE qa_reports;
CREATE USER 'QA_User'@'localhost' IDENTIFIED BY 'QA_User_Login123';
GRANT ALL PRIVILEGES ON `qa_reports`.* TO 'QA_User'@'localhost';
FLUSH PRIVILEGES;
