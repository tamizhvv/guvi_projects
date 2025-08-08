from faker import Faker
from faker import Faker
import random
import mysql.connector
from datetime import datetime, timedelta

faker = Faker()
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='placement_app'
)

cursor = connection.cursor()
cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
cursor.execute('TRUNCATE TABLE placements')
cursor.execute('TRUNCATE TABLE soft_skills')
cursor.execute('TRUNCATE TABLE programming')
cursor.execute('TRUNCATE TABLE students')
cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
connection.commit()
print("✅ Tables truncated")

students_data=[]

for _ in range(250):
    name=faker.name()
    age=random.randint(18,28)
    gender=random.choice(['Male','Female','Other'])
    email=faker.unique.email()
    phone=faker.unique.phone_number()
    enrollment_year=random.randint(2015,2021)
    batch_num=random.randint(1,5)
    course_batch=f'Batch - {str(batch_num)}'
    city=faker.city()
    graduation_year=enrollment_year +4

    students_data.append((name,age,gender,email,phone,enrollment_year,course_batch,city,graduation_year))

insert_query=''' 
insert into students (
name,age,gender,email,phone,enrollment_year,course_batch,city,graduation_year)
values(
%s,%s,%s,%s,%s,%s,%s,%s,%s)
'''

cursor.executemany(insert_query,students_data)
connection.commit()
print('Inserted data in students')

cursor.execute('select student_id from students')
rows=cursor.fetchall()
student_ids=[]
for row in rows:
    student_ids.append(row[0]) 

programming_data=[]
languages=['Python','Java','SQL','C++']

for student_id in student_ids:
    language=random.choice(languages)
    problems_solved=random.randint(20,500)
    assessments_completed=random.randint(1,10)
    mini_projects=random.randint(1,5)
    certifications_earned=random.randint(0,3)
    latest_project_score=random.randint(40,100)

    programming_data.append((student_id,language,problems_solved,assessments_completed,mini_projects,certifications_earned,latest_project_score))
insert_query1=''' 
insert into programming(
student_id,language,problems_solved,assessments_completed,mini_projects,certifications_earned,latest_project_score)
values (%s,%s,%s,%s,%s,%s,%s)'''

cursor.executemany(insert_query1,programming_data)
connection.commit()
print('Inserted programming data')

soft_skills=[]
for student_id in student_ids:
    communication=random.randint(50,100)
    teamwork=random.randint(50,100)
    presentation=random.randint(50,100)
    leadership=random.randint(50,100)
    critical_thinking=random.randint(50,100)
    interpersonal_skills=random.randint(50,100)

    soft_skills.append((student_id,communication,teamwork,presentation,leadership,critical_thinking,interpersonal_skills))
insert_query2=''' 
insert into soft_skills(student_id,communication,teamwork,presentation,leadership,critical_thinking,interpersonal_skills) values (%s,%s,%s,%s,%s,%s,%s)'''
cursor.executemany(insert_query2,soft_skills)
print('Soft_skills table values generated')

placements_data=[]
for student_id in student_ids:
    mock_interview_score=random.randint(30,100)
    internships_completed=random.randint(0,3)
    placement_status=random.choice(['Ready','Not Ready','Placed'])

    if placement_status=='Placed':
        company_name=random.choice(['Google','Microsoft','Amazon','Infosys','TCS','Meta','Netflix'])
        placement_package=round(random.uniform(3.0,25.0),2)
        interview_rounds_cleared=random.randint(3,6)
        placement_date=faker.date_between(start_date='-2y',end_date='today')
    else:
        company_name=None
        placement_package=0.0
        interview_rounds_cleared=0
        placement_date=None
    
    placements_data.append((student_id,mock_interview_score,internships_completed,placement_status,company_name,placement_package,interview_rounds_cleared,placement_date))

insert_query3='''
insert into placements(student_id,mock_interview_score,internships_completed,placement_status,company_name,placement_package,interview_rounds_cleared,placement_date)
values(%s,%s,%s,%s,%s,%s,%s,%s)
'''
cursor.executemany(insert_query3,placements_data)
connection.commit()
print('Inserted placements data')








