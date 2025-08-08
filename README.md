# guvi_projects

# guvi_projects
I started this project from scratch — not just building a dashboard, but also generating realistic synthetic data, creating a relational database, applying Object-Oriented Programming (OOP) in Python, writing SQL queries, and building an interactive Streamlit app.

Here's a breakdown of what I tackled:

 1. Created MySQL Database & Tables
Set up a MySQL database called placement_app.

Designed and created four interrelated tables:

students: basic info (name, age, email, etc.)

programming: coding skills and project work

soft_skills: communication, leadership, etc.

placements: placement status and outcomes

2. Generated Synthetic Data using Faker
Used the faker library and random module to generate fake student profiles.

Created 100+ rows of consistent, realistic data across all tables.

Inserted them into the database using Python.

 3. Wrote SQL Queries for Insights
Came up with 10 useful insights, like:

Average performance per batch

Top students by coding skills

Who’s placed and who’s not

Placement packages by company, and more.
 4. Used Python + OOP to Connect to MySQL
Built a Database class to handle database connections and queries cleanly using object-oriented principles.

 5. Built the Frontend in Streamlit
Created a multi-page interface:

Home: Welcome message

View Students: See raw data

Check Eligibility: Filter students by communication & problem-solving scores

Analytics: Display insights and dashboards

Tech Stack
Backend: Python, MySQL

Frontend: Streamlit

Data Generation: Faker

Database Connectivity: mysql.connector

 Why This Project?
I wanted to build something close to what EdTech platforms or training institutes might use to track student progress. This project helped me practice:

Database design

Writing and debugging SQL queries

Clean Python code using OOP

Building a full app frontend in Streamlit

Handling real-life debugging (like broken joins, nulls, and orphan rows 😅)
