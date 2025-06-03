import mysql.connector

connection=mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='placement_app'
)

cursor=connection.cursor()

cursor.execute(''' 
create table if not exists students(
               student_id int auto_increment primary key,
               name varchar(100),
               age int,
               gender varchar(100),
               email varchar(100),
               phone varchar(25),
               enrollment_year int,
               course_batch varchar(50),
               city varchar(50),
               graduation_year int);
''')

print('students table created')
cursor.execute(''' 
create table if not exists programming (
               programming_id int auto_increment primary key,
               student_id int,
               language varchar(50),
               problems_solved int,
               assessments_completed int,
               mini_projects int,
               certifications_earned int,
               latest_project_score float,
               foreign key (student_id) references students(student_id)
               );
''')
print('programming table created')


cursor.execute(''' 
create table if not exists soft_skills(
               soft_skill_id int auto_increment primary key,
               student_id int,
               communication int,
               teamwork int,
               presentation int,
               leadership int,
               critical_thinking int,
               interpersonal_skills int,
               foreign key(student_id) references students(student_id)
               );
''')
print('soft_skills table created')


cursor.execute(''' 
create table if not exists placements(
               placement_id int auto_increment primary key,
               student_id int,
               mock_interview_score int,
               internships_completed int,
               placement_status varchar(20),
               company_name varchar(100),
               placement_package float,
               interview_rounds_cleared int,
               placement_date date,
               foreign key(student_id) references students(student_id));
''')
print('placements table created')
print('all tables created')

cursor.close()
connection.close()

