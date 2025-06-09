import streamlit as st
from database import Database

db = Database(
    host='localhost',
    user='root',
    password='root',
    database='placement_app'
)


st.set_page_config(page_title='Placement Eligibility App',layout='centered')


selection=st.sidebar.selectbox(
    'Navigate',['Home','View Students','Check Eligibility','Analytics']
)

if selection=='Home':
    st.subheader('Welcome to the placement eligibility app')
    st.write('use the sidebar to get started')

if selection=='View Students':
    st.subheader('All students')

    db=Database(
        host='localhost',
        user='root',
        password='root',
        database='placement_app'
    )
    students=db.fetch_all_students()

    if len(students)>0:
        st.dataframe(students)
    else:
        st.warning('No student record found')
    
if selection=='Check Eligibility':
    st.subheader('Check Placement Eligibility')

    min_problems = st.sidebar.number_input("Minimum Problems Solved", min_value=0, max_value=1000, value=50)
    min_communication=st.sidebar.number_input('Minimum Communication Score',min_value=0,max_value=100,value=60)

    query=f'''
select s.name,s.email,p.problems_solved,ss.communication
from students s
join programming p on s.student_id=p.student_id
join soft_skills ss on s.student_id=ss.student_id
where p.problems_solved >={min_problems} and ss.communication >={min_communication} '''
    
    db.cursor.execute(query)
    eligible_students=db.cursor.fetchall()

    st.write(f'showing students with atleast {min_problems} problems and communication score >={min_communication}')
    st.dataframe(eligible_students)

if selection=='Analytics':
    st.subheader('Analytics Dashboard')

    st.markdown('### 1. Average Programming Performance Per Batch')
    query1='''
select s.course_batch,
avg(p.problems_solved) as avg_problems,
avg(p.assessments_completed) as avg_assessments,
avg(p.mini_projects) as avg_projects
from students s
join programming p on s.student_id = p.student_id
group by s.course_batch'''

    db.cursor.execute(query1)
    result1=db.cursor.fetchall()

    if len(result1)>0:
        st.dataframe(result1)
    else:
        st.warning('No data founf for programming performance ')
    
    st.markdown('### 2. Top 5 students by problem solved')
    query2='''
select s.name,p.problems_solved
from students s
join programming p on s.student_id=p.student_id
order by p.problems_solved desc
limit 5'''
    db.cursor.execute(query2)
    result2=db.cursor.fetchall()

    if len(result2)>0:
        st.dataframe(result2)
    else:
        st.warning('No data found')

    st.markdown('### 3. Students with Mini Projects  more than 5')
    query3='''
select s.name,p.mini_projects
from students s
join programming p on s.student_id=p.student_id
where p.mini_projects >=5
'''
    db.cursor.execute(query3)
    result3=db.cursor.fetchall()

    if len(result3) >0:
        st.dataframe(result3)
    else:
        st.warning('No data found')

    st.markdown('### 4. Students placed with highest package')
    query4='''
select s.name,pl.placement_package
from students s
join placements pl on s.student_id=pl.student_id
order by pl.placement_package desc
limit 5'''
    db.cursor.execute(query4)
    result4=db.cursor.fetchall()

    if len(result4) >0:
        st.dataframe(result4)
    else:
        st.warning('No data found')

    st.markdown('### 5. Students who completed all assessments')
    query5='''
select s.name,p.assessments_completed
from students s
join programming p on s.student_id=p.student_id
where p.assessments_completed=10'''

    db.cursor.execute(query5)
    result5=db.cursor.fetchall()
    if len(result5)>0:
        st.dataframe(result5)
    else:
        st.warning('No data found')



    st.markdown('### 6. Companies that hired more than 2 students')
    query6='''
select company_name,count(*) as hires
from placements
group by company_name
having count(*) > 2'''
    db.cursor.execute(query6)
    result6=db.cursor.fetchall()

    if len(result6)>0:
        st.dataframe(result6)
    else:
        st.warning('No data found')


    st.markdown('### 7. Students placed with low performance')
    query7='''
select s.name, p.problems_solved, p.mini_projects, pl.company_name
from students s
join programming p ON s.student_id = p.student_id
join placements pl ON s.student_id = pl.student_id
where p.problems_solved < 30 AND p.mini_projects < 2;

'''
    db.cursor.execute(query7)
    result7=db.cursor.fetchall()

    if len(result7)>0:
        st.dataframe(result7)
    else:
        st.warning('No data found')

    st.markdown('### 8. Top 5 Students by Communication score')
    query8='''
select s.name, ss.communication
from students s
join soft_skills ss ON s.student_id = ss.student_id
order by ss.communication DESC
limit 5;;
'''
    db.cursor.execute(query8)
    result8=db.cursor.fetchall()

    if len(result8)>0:
        st.dataframe(result8)
    else:
        st.warning('No data found')
    
    st.markdown('### 9. Total Number of Placed vs. not placed students')
    query9='''
select placement_status,count(*) as count
from placements
group by placement_status'''
    db.cursor.execute(query9)
    result9=db.cursor.fetchall()

    if len(result9)>0:
        st.dataframe(result9)
    else:
        st.wrning('No data found')

    st.markdown('### 10. Students who solved problems but less mini projects')
    query10='''
select s.name,p.problems_solved,p.mini_projects
from students s
join programming p on s.student_id=p.student_id
where p.problems_solved >50 and p.mini_projects >=2'''
    db.cursor.execute(query10)
    result10=db.cursor.fetchall()

    if len(result10)>0:
        st.dataframe(result10)
    else:
        st.warning('No Data found')