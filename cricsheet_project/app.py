import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title='Cric Sheet Explorer',layout='wide')

connection=mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='cric_sheet'
)

st.sidebar.title('Navigation')
match_type=st.sidebar.radio('select match type',['ODI','T20','Test','IPL'])

if match_type=='ODI':
    st.header('ODI Match Analysis')


# odi query 1: average runs scored in each phase of an ODI innings
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
    odi_1_df=pd.read_sql(query_odi1,con=connection)
    st.subheader('average runs scored in each phase of an ODI innings')
    st.dataframe(odi_1_df)

#visualisation
    
    fig, ax = plt.subplots(figsize=(8,6))
    sns.barplot(x="phase", y="avg_runs_scored", data=odi_1_df,ax=ax)
    plt.xlabel("Innings Phase")
    plt.ylabel("Average Runs Scored")
    plt.title("Average Runs Scored in Different ODI Phases")
    st.pyplot(fig)

# odi query 2: consistent ODI batsmen
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
    limit 20;
    '''

    odi_2_df=pd.read_sql(query_odi2,con=connection)
    st.subheader('consistent ODI batsmen')
    st.dataframe(odi_2_df)

#visualisation
  

    fig, ax = plt.subplots(figsize=(10,6))
    sns.scatterplot(data=odi_2_df, x="stddev_runs", y="avg_runs", hue="batsman", legend=False, s=100,ax=ax)

    for i in range(odi_2_df.shape[0]):
        plt.text(odi_2_df['stddev_runs'][i]+0.2, odi_2_df['avg_runs'][i], odi_2_df['batsman'][i], fontsize=8)

    plt.xlabel("Standard Deviation of Runs (Consistency)")
    plt.ylabel("Average Runs per Match")
    plt.title("Top 20 Most Consistent ODI Batsmen")
    st.pyplot(fig)

#odi query 3: Total Matches Played by Each ODI Team
    query_odi3 = '''
    select team, count(distinct match_id) as matches
    from (
        select match_id, team1 as team from odi_match_deliveries
        union all
        select match_id, team2 as team from odi_match_deliveries
    ) all_teams
    group by team
    order by matches desc
    limit 10;
    '''

    odi_3_df = pd.read_sql(query_odi3, con=connection)
    st.header('Total Matches Played by Each ODI Team')
    st.dataframe(odi_3_df)

#visualisation
    
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(data=odi_3_df, x="team", y="matches", palette="Blues_d",ax=ax)
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Team")
    plt.ylabel("Total Matches Played")
    plt.title("Top 10 ODI Teams by Matches Played")
    st.pyplot(fig)

# odi query 4: most frequently used ODI venues
    query_odi4='''
    select
    venue,count(distinct match_id) as matches
    from odi_match_deliveries
    group by venue
    order by matches desc'''

    odi_4_df=pd.read_sql(query_odi4,con=connection)
    st.header('most frequently used ODI venues')
    st.dataframe(odi_4_df)

#visualisation
    
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(
        data=odi_4_df.head(10),
        x="matches",
        y="venue",
        palette="Oranges_r",
        ax=ax
    )
    plt.xlabel("Number of Matches")
    plt.ylabel("Venue")
    plt.title("Top 10 ODI Venues by Matches Hosted")
    st.pyplot(fig)

# odi query 5: average runs scored in each over across all ODIs
    query_odi5='''
    select `over`,round(avg(runs_total),2) as avg_runs
    from odi_match_deliveries
    group by `over`
    order by `over`
    '''

    odi_5_df=pd.read_sql(query_odi5,con=connection)
    st.header('average runs scored in each over across all ODIs')
    st.dataframe(odi_5_df)

#visualisation
   
    fig, ax = plt.subplots(figsize=(12,6))
    sns.lineplot(data=odi_5_df, x="over", y="avg_runs", marker="o",ax=ax)
    plt.xlabel("Over Number")
    plt.ylabel("Average Runs")
    plt.title("Average Runs per Over in ODIs")
    st.pyplot(fig)

#odi query 6: Top Batsmen by Batting Average

    query_odi6 = '''
    WITH batting_stats AS (
        SELECT 
            batsman,
            COUNT(*) AS balls_faced,
            SUM(runs_batsman) AS total_runs
        FROM odi_match_deliveries  -- change table name for T20/Test/IPL
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


    odi_6_df = pd.read_sql(query_odi6, con=connection)

    
    st.subheader("Top Batsmen by Batting Average")
    st.dataframe(odi_6_df.head(20)) 

# Visualization

    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(
        data=odi_6_df.head(20),  
        x="batting_average",
        y="batsman",
        palette="viridis",
        ax=ax
    )
    ax.set_title("Top Batsmen by Batting Average")
    ax.set_xlabel("Batting Average")
    ax.set_ylabel("Batsman")
    st.pyplot(fig)

# odi query 7 : 
    query_odi_7 = '''
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
    odi_7_df = pd.read_sql(query_odi_7, con=connection)

    st.subheader("Bowler Performance in Death Overs (ODI)")

    
    st.dataframe(odi_7_df)

#visualisation

    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(
        data=odi_7_df.head(20),
        x="economy_rate",
        y="bowler",
        palette="magma",
        ax=ax
    )
    ax.set_title("Top Death Over Bowlers by Economy Rate")
    ax.set_xlabel("Economy Rate")
    ax.set_ylabel("Bowler")
    st.pyplot(fig)


#odi query 8:

    query_odi_8='''

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
    odi_8_df=pd.read_sql(query_odi_8,con=connection)
    
    st.subheader("Effectiveness of Batting First in ODIs")
    st.dataframe(odi_8_df)

    # Visualization
    fig, ax = plt.subplots(figsize=(8,6))
    sns.barplot(
        data=odi_8_df,
        x="win_pct_batting_first",
        y="batting_first",
        palette="coolwarm",
        ax=ax
    )
    ax.set_xlabel("Win % When Batting First")
    ax.set_ylabel("Team")
    ax.set_title("Teams Winning % When Batting First in ODIs")
    st.pyplot(fig)

# odi query 9 : 
    query_odi_9='''
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

    odi_9_df=pd.read_sql(query_odi_9,con=connection)
    st.subheader("Impact of Toss Decision in ODIs")
    st.dataframe(odi_9_df)

    # Visualization
    fig, ax = plt.subplots(figsize=(6,4))
    sns.barplot(
        data=odi_9_df,
        x="win_pct",
        y="toss_decision",
        palette="viridis",
        ax=ax
    )
    ax.set_xlabel("Win % When Following Toss Decision")
    ax.set_ylabel("Toss Decision")
    ax.set_title("Toss Decision Impact in ODIs")
    st.pyplot(fig)

#odi query 10:
    query_odi_10='''
    select wicket_kind,count(*)as dismissals
    from odi_match_deliveries
    where wicket_kind is not null
    group by wicket_kind
    order by dismissals desc;
    '''
    odi_10_df=pd.read_sql(query_odi_10,con=connection)
    st.subheader("Types of Dismissals in odis")
    st.dataframe(odi_10_df)

    # Visualization
    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(
        data=odi_10_df.head(10), 
        x="dismissals",
        y="wicket_kind",
        palette="magma",
        ax=ax
    )
    ax.set_xlabel("Number of Dismissals")
    ax.set_ylabel("Dismissal Type")
    ax.set_title("Top odi Dismissal Types")
    st.pyplot(fig)



elif match_type=='T20':
    st.header('T20 Match Analysis')

# t20 query 1: average powerplay runs (overs 1–6) for each team in T20s
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
    st.subheader('average powerplay runs (overs 1–6) for each team in T20s')
    st.dataframe(t20_1_df)

#visualisation

    st.bar_chart(t20_1_df.set_index('batting_team'))

#t20 query2: T20 batting strike rates.

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
    st.subheader('T20 batting strike rates.')
    st.dataframe(t20_2_df)

#visualisation
    plt.figure(figsize=(8,6))
    sns.barplot(
        data=t20_2_df,
        x="strike_rate",
        y="batsman",
        palette="Blues_r"
    )
    plt.xlabel("Strike Rate")
    plt.ylabel("Batsman")
    plt.title("Top 10 T20 Batsmen by Strike Rate")
    st.pyplot(plt)

#t20 query3: Bowler performance in T20 death overs (16–20)
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
    st.subheader('Bowler performance in T20 death overs (16-20)')
    st.dataframe(t20_3_df)

#visualisation
    plt.figure(figsize=(8,6))
    sns.barplot(
    data=t20_3_df,
    x="economy_rate",
    y="bowler",
    palette="Blues_r"
    )
    plt.xlabel("Economy Rate (Death Overs)")
    plt.ylabel("Bowler")
    plt.title("Top 10 Most Economical Bowlers in T20 Death Overs (16–20)")
    st.pyplot(plt)

#t20 query 4: Top 10 Most Consistent T20 Bowlers (30+ overs)
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
    st.subheader("Top 10 Most Consistent T20 Bowlers (30+ overs)")
    st.dataframe(t20_4_df)

#visualisation
    plt.figure(figsize=(10,6))
    plt.barh(t20_4_df['bowler'], t20_4_df['consistency_score'], color='orange')
    plt.xlabel("Consistency Score (Std Dev of Runs per Over)")
    plt.ylabel("Bowler")
    plt.title("Top 10 Most Consistent T20 Bowlers (30+ overs)")
    plt.gca().invert_yaxis()
    st.pyplot(plt)

#t20 query 5: Top 10 Bowlers with Highest Dot Ball % in T20s
    query_t20_5 = '''
    with dot_balls as (
        select
            bowler,
            count(*) as balls_bowled,
            sum(runs_total=0) as dot_balls
        from t20_match_deliveries
        group by bowler
    )
    select bowler,
        round(dot_balls/balls_bowled, 2) as dot_balls_percentage
    from dot_balls
    order by dot_balls_percentage desc
    limit 10;
    '''

    t20_5_df = pd.read_sql(query_t20_5, con=connection)
    st.header('Top 10 Bowlers with Highest Dot Ball % in T20s')
    st.dataframe(t20_5_df)

#visualisation
    plt.figure(figsize=(10,6))
    sns.barplot(
    data=t20_5_df,
    x="dot_balls_percentage",
    y="bowler",
    palette="viridis"
    )
    plt.xlabel("Dot Balls Percentage")
    plt.ylabel("Bowler")
    plt.title("Top 10 Bowlers with Highest Dot Ball % in T20s")
    st.pyplot(plt)



# t20 query 7

    query_t20_7='''

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
        FROM t20_match_deliveries
        GROUP BY match_id, winner, toss_winner, toss_decision, team1, team2
    )
    SELECT 
        batting_first,
        COUNT(*) AS matches_played,
        SUM(CASE WHEN batting_first = winner THEN 1 ELSE 0 END) AS wins_batting_first,
        ROUND(SUM(CASE WHEN batting_first = winner THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS win_pct_batting_first
    FROM team_results
    GROUP BY batting_first
    ORDER BY win_pct_batting_first DESC
    limit 30;
    '''
    t20_7_df=pd.read_sql(query_t20_7,con=connection)
    st.subheader("Effectiveness of Batting First in t20s")
    st.dataframe(t20_7_df)

    # Visualization
    fig, ax = plt.subplots(figsize=(8,6))
    sns.barplot(
        data=t20_7_df,
        x="win_pct_batting_first",
        y="batting_first",
        palette="coolwarm",
        ax=ax
    )
    ax.set_xlabel("Win % When Batting First")
    ax.set_ylabel("Team")
    ax.set_title("Teams Winning % When Batting First in t20s")
    st.pyplot(fig)

# t20 query 8: 
    query_t20_8='''
    with toss_impact as(
    select match_id, max(toss_winner) as toss_winner,
    max(toss_decision) as toss_decision,
    max(winner) as winner
    from t20_match_deliveries
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

    t20_8_df=pd.read_sql(query_t20_8,con=connection)
    st.subheader("Impact of Toss Decision in t20s")
    st.dataframe(t20_8_df)

    # Visualization
    fig, ax = plt.subplots(figsize=(6,4))
    sns.barplot(
        data=t20_8_df,
        x="win_pct",
        y="toss_decision",
        palette="viridis",
        ax=ax
    )
    ax.set_xlabel("Win % When Following Toss Decision")
    ax.set_ylabel("Toss Decision")
    ax.set_title("Toss Decision Impact in t20s")
    st.pyplot(fig)

#t20 query 9 :
    query_t20_9='''
    select wicket_kind,count(*)as dismissals
    from t20_match_deliveries
    where wicket_kind is not null
    group by wicket_kind
    order by dismissals desc;
    '''
    t20_9_df=pd.read_sql(query_t20_9,con=connection)
    st.subheader("Types of Dismissals in t20s")
    st.dataframe(t20_9_df)

    # Visualization
    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(
        data=t20_9_df.head(10), 
        x="dismissals",
        y="wicket_kind",
        palette="magma",
        ax=ax
    )
    ax.set_xlabel("Number of Dismissals")
    ax.set_ylabel("Dismissal Type")
    ax.set_title("Top t20 Dismissal Types")
    st.pyplot(fig)



















elif match_type=='Test':
    st.header('Test Match Analysis')

# Query 1: Top 10 run scorers in Test matches
    query_test_1 = """
        SELECT batsman, SUM(runs_batsman) AS total_runs
        FROM test_match_deliveries
        GROUP BY batsman
        ORDER BY total_runs DESC
        LIMIT 10;
    """
    test_1_df=pd.read_sql(query_test_1,con=connection)
    st.subheader('Top 10 run scorers in Test Matches')
    st.dataframe(test_1_df)

# visualisation 
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(data=test_1_df, x="total_runs", y="batsman", palette="viridis", ax=ax)
    ax.set_title("Top 10 Run Scorers in Test Matches")
    ax.set_xlabel("Total Runs")
    ax.set_ylabel("Batsman")
    st.pyplot(fig)

# Query 2: Top 10 bowlers by wickets in Tests
    query_test_2 = '''
        SELECT bowler, COUNT(*) AS wickets
        FROM test_match_deliveries
        WHERE player_out IS NOT NULL
        GROUP BY bowler
        ORDER BY wickets DESC
        LIMIT 10;
    '''
    test_2_df=pd.read_sql(query_test_2,con=connection)
    st.subheader('Top 10 bowlers in Tests')
    st.dataframe(test_2_df)
#visualisation
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(data=test_2_df, x="wickets", y="bowler", palette="magma", ax=ax)
    ax.set_title("Top 10 Bowlers in Tests (by Wickets)")
    ax.set_xlabel("Wickets Taken")
    ax.set_ylabel("Bowler")
    st.pyplot(fig)


# query 3: Centuries by batsman in Tests
    query_test_3='''
    with batsman_runs as(
    select match_id,innings,batsman,sum(runs_batsman) as total_runs
    from test_match_deliveries
    group by match_id,innings,batsman
    )
    select batsman, count(total_runs) as centuries
    from batsman_runs
    where total_runs>=100
    group by batsman
    order by centuries desc
    limit 20;
    '''

    test_3_df=pd.read_sql(query_test_3,con=connection)
    st.subheader('Centuries by batsman in Tests')
    st.dataframe(test_3_df)
#visualisation
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(data=test_3_df, x="centuries", y="batsman", palette="cubehelix", ax=ax)
    ax.set_title("Centuries by Batsmen in Tests")
    ax.set_xlabel("Number of Centuries")
    ax.set_ylabel("Batsman")
    st.pyplot(fig)


#query 4: single highest individual innings score
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
    st.subheader('single highest individual innings score')
    st.metric(label="Highest Individual Test Score", value=test_4_df['highest_score'].iloc[0])
#visualisation
    st.table(test_4_df)  # Shows batsman + score


# query 5: Top 10 bowlers with the most 5-wicket hauls
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
    st.subheader('Top 10 bowlers with the most 5-wicket hauls')
    st.dataframe(test_5_df)
# visualisation
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(data=test_5_df, x="five_wicket_hauls", y="bowler", palette="coolwarm", ax=ax)
    ax.set_title("Top 10 Bowlers with the Most 5-Wicket Hauls in Tests")
    ax.set_xlabel("Five-Wicket Hauls")
    ax.set_ylabel("Bowler")
    st.pyplot(fig)

#test query 6 :
    query_test_6='''
    select wicket_kind,count(*)as dismissals
    from test_match_deliveries
    where wicket_kind is not null
    group by wicket_kind
    order by dismissals desc;
    '''
    test_6_df=pd.read_sql(query_test_6,con=connection)
    st.subheader("Types of Dismissals in tests")
    st.dataframe(test_6_df)

    # Visualization
    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(
        data=test_6_df.head(10), 
        x="dismissals",
        y="wicket_kind",
        palette="magma",
        ax=ax
    )
    ax.set_xlabel("Number of Dismissals")
    ax.set_ylabel("Dismissal Type")
    ax.set_title("Top test Dismissal Types")
    st.pyplot(fig)


elif match_type=='IPL':
    st.header('IPL Match Analysis')

#ipl query 1 : Top run scorers in IPL
    query_ipl_1='''
    select batsman, sum(runs_batsman) as total_runs
    from ipl_match_deliveries
    group by batsman
    order by total_runs desc
    limit 10;
    '''
    ipl_1_df=pd.read_sql(query_ipl_1,con=connection)
    st.subheader('Top run scorers in IPL')
    st.dataframe(ipl_1_df)

#visualisation
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(data=ipl_1_df, x="total_runs", y="batsman", palette="viridis", ax=ax)
    ax.set_title("Top 10 Run Scorers in IPL")
    ax.set_xlabel("Total Runs")
    ax.set_ylabel("Batsman")
    st.pyplot(fig)


# ipl query 2: Top 10 bowlers by wicket
    query_ipl_2='''
    select bowler, count(player_out) as wickets
    from ipl_match_deliveries
    where player_out is not null
    group by bowler
    order by wickets desc
    limit 10;
    '''
    ipl_2_df=pd.read_sql(query_ipl_2,con=connection)
    st.subheader('Top 10 bowlers by wicket')
    st.dataframe(ipl_2_df)

#visualisation
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(data=ipl_2_df, x="wickets", y="bowler", palette="magma", ax=ax)
    ax.set_title("Top 10 Bowlers in IPL (by Wickets)")
    ax.set_xlabel("Wickets Taken")
    ax.set_ylabel("Bowler")
    st.pyplot(fig)


#ipl query 3: Top batsman with more 6's
    query_ipl_3='''
    select batsman, count(*) as sixes
    from ipl_match_deliveries
    where runs_batsman = 6
    group by batsman
    order by sixes desc
    limit 10;
    '''
    ipl_3_df=pd.read_sql(query_ipl_3,con=connection)
    st.subheader("Top batsman with more 6's")
    st.dataframe(ipl_3_df)

# visualisation
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(data=ipl_3_df, x="sixes", y="batsman", palette="cubehelix", ax=ax)
    ax.set_title("Top 10 Batsmen with Most Sixes in IPL")
    ax.set_xlabel("Number of Sixes")
    ax.set_ylabel("Batsman")
    st.pyplot(fig)


# ipl query 4:Top 10 bowlers based on economy rate
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
    st.subheader('Top 10 bowlers based on economy rate')
    st.dataframe(ipl_4_df)

# visualisation
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(data=ipl_4_df, x="economy_rate", y="bowler", palette="coolwarm_r", ax=ax)
    ax.set_title("Top 10 Bowlers by Economy Rate in IPL")
    ax.set_xlabel("Economy Rate")
    ax.set_ylabel("Bowler")
    st.pyplot(fig)

#ipl query 5:bowler-batsman rivalry
    query_ipl_5 = '''
    select bowler,
        player_out as batsman,
        count(*) as dismissals
    from ipl_match_deliveries
    where player_out is not null
    group by bowler, player_out
    order by dismissals desc
    limit 10;
    '''

    ipl_5_df = pd.read_sql(query_ipl_5, con=connection)


    ipl_5_df["rivalry"] = ipl_5_df["bowler"] + " vs " + ipl_5_df["batsman"]


    st.subheader("Top 10 Bowler vs Batsman Rivalries (Most Dismissals in IPL)")
    st.dataframe(ipl_5_df)

#visualisations

    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(data=ipl_5_df, x="dismissals", y="rivalry", palette="Set2", ax=ax)
    ax.set_title("Top 10 Bowler vs Batsman Rivalries (Most Dismissals in IPL)")
    ax.set_xlabel("Dismissals")
    ax.set_ylabel("Bowler vs Batsman")
    st.pyplot(fig)

#ipl query 6:
    query_ipl_6='''
    with bowler_stats as (
    select
    bowler,
    count(*) as balls_bowled,
    sum(case when wicket_kind is not null then 1 else 0 end) as wickets
    from ipl_match_deliveries
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

    ipl_6_df=pd.read_sql(query_ipl_6,con=connection)
    st.subheader("Bowler Strike Rate (Balls per Wicket)")
    st.dataframe(ipl_6_df)

    # Visualization
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(
        data=ipl_6_df.head(20), 
        x="strike_rate",
        y="bowler",
        palette="viridis",
        ax=ax
    )
    ax.set_title("Top Bowlers by Strike Rate (Lower = Better)")
    ax.set_xlabel("Balls per Wicket")
    ax.set_ylabel("Bowler")
    st.pyplot(fig)

#ipl query 7
    query_ipl_7='''

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
        FROM ipl_match_deliveries
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
    ipl_7_df=pd.read_sql(query_ipl_7,con=connection)
   
    st.subheader("Effectiveness of Batting First in ipls")
    st.dataframe(ipl_7_df)

    # Visualization
    fig, ax = plt.subplots(figsize=(8,6))
    sns.barplot(
        data=ipl_7_df,
        x="win_pct_batting_first",
        y="batting_first",
        palette="coolwarm",
        ax=ax
    )
    ax.set_xlabel("Win % When Batting First")
    ax.set_ylabel("Team")
    ax.set_title("Teams Winning % When Batting First in ipls")
    st.pyplot(fig)

# ipl query 8 : 
    query_ipl_8='''
    with toss_impact as(
    select match_id, max(toss_winner) as toss_winner,
    max(toss_decision) as toss_decision,
    max(winner) as winner
    from ipl_match_deliveries
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

    ipl_8_df=pd.read_sql(query_ipl_8,con=connection)
    st.subheader("Impact of Toss Decision in ipls")
    st.dataframe(ipl_8_df)

    # Visualization
    fig, ax = plt.subplots(figsize=(6,4))
    sns.barplot(
        data=ipl_8_df,
        x="win_pct",
        y="toss_decision",
        palette="viridis",
        ax=ax
    )
    ax.set_xlabel("Win % When Following Toss Decision")
    ax.set_ylabel("Toss Decision")
    ax.set_title("Toss Decision Impact in ipls")
    st.pyplot(fig)

#ipl query 9 :
    query_ipl_9='''
    select wicket_kind,count(*)as dismissals
    from ipl_match_deliveries
    where wicket_kind is not null
    group by wicket_kind
    order by dismissals desc;
    '''
    ipl_9_df=pd.read_sql(query_ipl_9,con=connection)
    st.subheader("Types of Dismissals in ipls")
    st.dataframe(ipl_9_df)

    # Visualization
    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(
        data=ipl_9_df.head(10), 
        x="dismissals",
        y="wicket_kind",
        palette="magma",
        ax=ax
    )
    ax.set_xlabel("Number of Dismissals")
    ax.set_ylabel("Dismissal Type")
    ax.set_title("Top ipl Dismissal Types")
    st.pyplot(fig)

