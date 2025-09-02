#!/usr/bin/env python
# coding: utf-8

# In[1]:


import mysql.connector
import pandas as pd


# In[2]:


connection=mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='cric_sheet'
)


# In[3]:


cursor=connection.cursor()


# In[4]:


import pandas as pd

query = '''
WITH batting_stats AS (
    SELECT 
        batsman,
        COUNT(*) AS balls_faced,
        SUM(runs_batsman) AS total_runs
    FROM odi_match_deliveries
    WHERE batsman IS NOT NULL
    GROUP BY batsman
),
dismissals AS (
    SELECT 
        batsman,
        COUNT(*) AS times_out
    FROM odi_match_deliveries
    WHERE player_out IS NOT NULL
    GROUP BY batsman
)
SELECT 
    b.batsman,
    b.total_runs,
    b.balls_faced,
    d.times_out,
    ROUND(b.total_runs / NULLIF(d.times_out, 0), 2) AS batting_average,
    ROUND((b.total_runs / NULLIF(b.balls_faced, 0)) * 100, 2) AS strike_rate
FROM batting_stats b
LEFT JOIN dismissals d
    ON b.batsman = d.batsman
WHERE b.balls_faced >= 30
ORDER BY batting_average DESC;
'''

# Execute and fetch results into DataFrame
df_batting_stats = pd.read_sql(query, con=connection)

# Preview first 10 rows
print(df_batting_stats.head(10))


# In[5]:


query2 = '''
WITH bowler_death_overs AS (
    SELECT 
        bowler,
        COUNT(*) AS balls_bowled,
        SUM(runs_total) AS runs_given
    FROM odi_match_deliveries
    WHERE `over` BETWEEN 41 AND 50
    GROUP BY bowler
)
SELECT 
    bowler,
    balls_bowled,
    runs_given,
    ROUND(runs_given / (balls_bowled / 6.0), 2) AS economy_rate
FROM bowler_death_overs
WHERE balls_bowled >= 30
ORDER BY economy_rate;
'''

df_pressure_perf = pd.read_sql(query2, con=connection)
print(df_pressure_perf.head())


# In[6]:


query3='''
with bowler_stats as (
select
bowler,
count(*) as balls_bowled,
sum(case when wicket_kind is not null then 1 else 0 end) as wickets
from odi_match_deliveries
group by bowler
)

select 
bowler,
balls_bowled,
wickets,
round(balls_bowled/nullif(wickets,0),2) as strike_rate
from bowler_stats
where balls_bowled >=100
order by strike_rate;
'''

bowler_sr_df=pd.read_sql(query3,con=connection)
print(bowler_sr_df.head())


# In[7]:


query4='''

WITH team_results AS (
    SELECT
        match_id,
        winner,
        CASE 
            WHEN toss_winner = team1 AND toss_decision = 'bat' THEN team1
            WHEN toss_winner = team2 AND toss_decision = 'bat' THEN team2
            WHEN toss_winner = team1 AND toss_decision = 'field' THEN team2
            WHEN toss_winner = team2 AND toss_decision = 'field' THEN team1
        END AS batting_first
    FROM odi_match_deliveries
    GROUP BY match_id, winner, toss_winner, toss_decision, team1, team2
)
SELECT 
    batting_first,
    COUNT(*) AS matches_played,
    SUM(CASE WHEN batting_first = winner THEN 1 ELSE 0 END) AS wins_batting_first,
    ROUND(SUM(CASE WHEN batting_first = winner THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS win_pct_batting_first
FROM team_results
GROUP BY batting_first
ORDER BY win_pct_batting_first DESC;
'''
team_results_df=pd.read_sql(query4,con=connection)
print(team_results_df.head())


# In[8]:


query4='''
with toss_impact as(
select match_id, max(toss_winner) as toss_winner,
max(toss_decision) as toss_decision,
max(winner) as winner
from odi_match_deliveries
group by match_id
)

select toss_decision,
count(*) as matches_played,
SUM(CASE WHEN toss_winner = winner THEN 1 ELSE 0 END) AS wins_when_followed,
ROUND(SUM(CASE WHEN toss_winner = winner THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS win_pct
from toss_impact
group by toss_decision
order by win_pct desc;
'''

toss_impact_df=pd.read_sql(query4,con=connection)
print(toss_impact_df.head())


# In[9]:


query5='''
select wicket_kind,count(*)as dismissals
from odi_match_deliveries
where wicket_kind is not null
group by wicket_kind
order by dismissals desc;
'''
dismissals_df=pd.read_sql(query5,con=connection)
print(dismissals_df.head(15))


# In[10]:


query_odi1 = '''
with phase_runs as (
select match_id,
case
when `over` between 1 and 10 then 'powerplay(1-10)'
when `over` between 11 and 40 then 'middle(11-40)'
when `over` between 41 and 50 then 'death(41-50)'
end as phase,
sum(runs_total) as runs_in_phase
from odi_match_deliveries
group by match_id,phase
)

select
phase,
round(avg(runs_in_phase),2) as avg_runs_scored
from phase_runs
group by phase
order by
case 
when phase='powerplay(1-10)' then 1
when phase='middle(11-40)' then 2
when phase='death(41-50)' then 3
end;
'''
odi1_df=pd.read_sql(query_odi1,con=connection)
print(odi1_df.head())


# In[11]:


query_odi2='''
with player_match_scores as (
select match_id, batsman, sum(runs_batsman) as runs_in_match
from odi_match_deliveries
where batsman is not null
group by match_id,batsman
)

select batsman,
round(avg(runs_in_match),2) as avg_runs,
round(stddev(runs_in_match),2) as stddev_runs
from player_match_scores
group by batsman
having count(*) >=5
order by stddev_runs asc, avg_runs desc
limit 20;'''

odi2_df=pd.read_sql(query_odi2,con=connection)
print(odi2_df.head())


# In[ ]:


query_odi3='''
select
team1 as team,
count(distinct match_id) as matches
from odi_match_deliveries
group by team1
order by matches desc
limit 10;
'''

odi3_df=pd.read_sql(query_odi3,con=connection)
display(odi3_df)


# In[13]:


query_odi4='''
select
venue,count(distinct match_id) as matches
from odi_match_deliveries
group by venue
order by matches desc'''

odi4_df=pd.read_sql(query_odi4,con=connection)
display(odi4_df)


# In[14]:


query_odi5='''
select `over`,round(avg(runs_total),2) as avg_runs
from odi_match_deliveries
group by `over`
order by `over`
'''

odi5_df=pd.read_sql(query_odi5,con=connection)
display(odi5_df)


# In[15]:


query_odi6='''
select 
bowler,
count(*) as balls_bowled,
sum(runs_total) as runs_given,
round(sum(runs_total)/(count(*)/6.0),2) as economy_rate
from odi_match_deliveries
where `over` between 11 and 40
group by bowler
having balls_bowled >=60
order by economy_rate 
limit 10;
'''
odi6_df=pd.read_sql(query_odi6,con=connection)
display(odi6_df)


# In[16]:


query_t20_1='''
with powerplay_runs as (select 
match_id,batting_team,round(sum(runs_total),2) as runs_scored
from t20_match_deliveries
where `over` between 1 and 6
group by match_id,batting_team)

select batting_team, round(avg(runs_scored),2) as avg_powerplay_runs
from powerplay_runs
group by batting_team
order by avg_powerplay_runs desc;
'''
t20_1_df=pd.read_sql(query_t20_1,con=connection)
display(t20_1_df.head())


# In[17]:


query_t20_2='''
with batsmen_strike_rate as (
select batsman, count(*) as balls_faced,sum(runs_batsman) as runs_scored
from t20_match_deliveries
group by batsman)

select batsman,round(runs_scored * 100.0/balls_faced,2) as strike_rate
from batsmen_strike_rate
where balls_faced >=200
order by strike_rate desc
limit 10;
'''

t20_2_df=pd.read_sql(query_t20_2,con=connection)
display(t20_2_df.head(12))


# In[18]:


query_t20_3='''
with bowler_economy_rate as (
select
bowler,count(*) as balls_bowled,sum(runs_total) as runs_given
from t20_match_deliveries
where `over` between 16 and 20
group by bowler 
)

select bowler,
round((runs_given/(balls_bowled/6)),2) as economy_rate
from bowler_economy_rate
where balls_bowled >100
order by economy_rate
limit 10
'''

t20_3_df=pd.read_sql(query_t20_3,con=connection)
display(t20_3_df.head(10))


# In[19]:


query_t20_4='''
with bowler_over_runs as (
select match_id,bowler,`over`,sum(runs_total) as runs
from t20_match_deliveries
group by match_id,bowler,`over`
)

select 
bowler,
avg(runs) as avg_runs_per_over,
stddev(runs) as consistency_score,
count(*) as overs_bowled
from bowler_over_runs
group by bowler
having overs_bowled >=30
order by consistency_score
limit 10
'''

t20_4_df=pd.read_sql(query_t20_4,con=connection)
display(t20_4_df.head(15))


# In[20]:


query_t20_5='''
with dot_balls as (
select
bowler,
count(*) as balls_bowled,
sum(runs_total=0) as dot_balls
from t20_match_deliveries
group by bowler
)

select bowler,
round(dot_balls/balls_bowled,2) as dot_balls_percentage
from dot_balls
group by bowler
order by dot_balls_percentage desc
'''

t20_5_df=pd.read_sql(query_t20_5, con=connection)
display(t20_5_df.head(10))


# In[21]:


query_test_1='''
select 
batsman,
cast(sum(runs_batsman) as signed) as total_runs
from test_match_deliveries
group by batsman
order by total_runs desc
limit 10
'''
test_1_df=pd.read_sql(query_test_1,con=connection)
display(test_1_df.head(10))


# In[22]:


query_test_2='''
select bowler, count(player_out) as wickets
from test_match_deliveries
where player_out is not null
group by bowler
order by wickets desc
limit 10
'''

test_2_df=pd.read_sql(query_test_2,con=connection)
display(test_2_df.head(10))


# In[24]:


query_test_3='''
with batsman_runs as(
select match_id,innings,batsman,sum(runs_batsman) as total_runs
from test_match_deliveries
group by match_id,innings,batsman)

select batsman, count(total_runs) as centuries
from batsman_runs
where total_runs>=100
group by batsman
order by centuries desc

'''

test_3_df=pd.read_sql(query_test_3,con=connection)
display(test_3_df.head())


# In[27]:


query_test_4='''
with batsman_full_data as (
    select 
        match_id,
        innings,
        batsman,
        sum(runs_batsman) as total_runs
    from test_match_deliveries
    group by match_id, innings, batsman
)
select bfd.batsman, bfd.total_runs as highest_score
from batsman_full_data bfd
where bfd.total_runs = (
    select max(total_runs) from batsman_full_data
);

'''

test_4_df=pd.read_sql(query_test_4,con=connection)
display(test_4_df.head())


# In[28]:


query_test_5='''
with bowler_wickets as (
    select match_id, innings, bowler,
           count(player_out) as wickets
    from test_match_deliveries
    where player_out is not null
    group by match_id, innings, bowler
),
five_wicket_hauls as (
    select bowler
    from bowler_wickets
    where wickets >= 5
)
select bowler, count(*) as five_wicket_hauls
from five_wicket_hauls
group by bowler
order by five_wicket_hauls desc
limit 10;
'''

test_5_df=pd.read_sql(query_test_5,con=connection)
display(test_5_df.head())


# In[29]:


query_ipl_1='''
select batsman, sum(runs_batsman) as total_runs
from ipl_match_deliveries
group by batsman
order by total_runs desc
limit 10;
'''
ipl_1_df=pd.read_sql(query_ipl_1,con=connection)
display(ipl_1_df)


# In[30]:


query_ipl_2='''
select bowler, count(player_out) as wickets
from ipl_match_deliveries
where player_out is not null
group by bowler
order by wickets desc
limit 10;
'''
ipl_2_df=pd.read_sql(query_ipl_2,con=connection)
display(ipl_2_df)


# In[31]:


query_ipl_3='''
select batsman, count(*) as sixes
from ipl_match_deliveries
where runs_batsman = 6
group by batsman
order by sixes desc
limit 10;
'''
ipl_3_df=pd.read_sql(query_ipl_3,con=connection)
display(ipl_3_df)


# In[32]:


query_ipl_4='''
select bowler,
       sum(runs_total) as runs_conceded,
       count(*)/6 as overs_bowled,
       round(sum(runs_total) / (count(*)/6), 2) as economy_rate
from ipl_match_deliveries
group by bowler
having overs_bowled >= 50
order by economy_rate asc
limit 10;
'''
ipl_4_df=pd.read_sql(query_ipl_4,con=connection)
display(ipl_4_df)


# In[35]:


query_ipl_5='''
select bowler,
       player_out as batsman,
       count(*) as dismissals
from ipl_match_deliveries
where player_out is not null
group by bowler, player_out
order by dismissals desc
limit 10;
;
'''
ipl_5_df=pd.read_sql(query_ipl_5,con=connection)
display(ipl_5_df)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




