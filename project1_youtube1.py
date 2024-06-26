import googleapiclient.discovery
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import streamlit as st
from datetime import datetime, timedelta
import time
from PIL import Image

global youtube_details,fchd,fvd,fcd,mycursor,engine

#api connection
api_service_name = "youtube"
api_version = "v3"
api_key="AIzaSyDoDWM45ZQO2UtAwvBjm_mV9dsDAckiI0E"
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)


#function to obtain the channeldata using channel_id
def channel_data(channel_id):
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()
    data ={
        "channel_name":response["items"][0]['snippet']['title'],
        "channel_thumbnail":response["items"][0]["snippet"]["thumbnails"]["high"]["url"],
    "channel_discription":response["items"][0]['snippet']["description"],
    "channel_view":response['items'][0]["statistics"]["viewCount"],
    "channel_video":response["items"][0]["statistics"]["videoCount"],
    "channel_subscription":response["items"][0]["statistics"]["subscriberCount"],
    "channel_playlist":response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]}
    return data

#function to obtain the video_id from the playlist id
def video_idfun(channel_id):
    request = youtube.channels().list(
            part="contentDetails",
            id=channel_id
            )
    response = request.execute()
    playlist_id=response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    request1=youtube.playlistItems().list(
        part="snippet,contentDetails",playlistId=playlist_id,maxResults=100)
    
    video_title_list=[]
    video_id_list=[]
    video_details=[video_title_list,video_id_list]
    response1=request1.execute()
    for item in range (len(response1['items'])):
        video_title = response1['items'][item]['snippet']['title']
        video_id=response1['items'][item]['snippet']['resourceId']['videoId']
        video_title_list.append(video_title)
        video_id_list.append(video_id)
    request1=youtube.playlistItems().list_next(request1,response1)
    return video_details

#function to obtain the video details
def video_detailsfun(video_id):
    request2 = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    response2 = request2.execute()
    vdu=convert_to_datetime(response2['items'][0]["contentDetails"]["duration"])
    video_detailslist={
        "channel_id":response2['items'][0]["snippet"]["channelId"],
        "channel_name":response2['items'][0]["snippet"]["channelTitle"],
        "video_id":video_id,
        "video_title":response2['items'][0]["snippet"]["title"],
        "video_description":response2["items"][0]["snippet"]["description"],
        "video_thumbnail":response2['items'][0]["snippet"]["thumbnails"]["high"]["url"],
        "video_published_date":response2['items'][0]["snippet"]["publishedAt"],
        "video_comment_count":response2['items'][0]["statistics"]['commentCount'],
        "video_like_count":response2['items'][0]["statistics"]["likeCount"],
        "video_favourite_count":response2['items'][0]["statistics"]["favoriteCount"],
        "video_duration":vdu,
        "video_view_count":response2['items'][0]["statistics"]["viewCount"],
        "caption_status":response2["items"][0]["contentDetails"]["caption"]

    }
    return video_detailslist

#function to obtain the comment details
def comment_detailsfun(video_id):
    request3= youtube.commentThreads().list(
        part="snippet",videoId=video_id,maxResults=50
    )
    response3 = request3.execute()
    video_comment_details_count=[]
    if len(response3['items'])==0:
        video_comment_details={
                "video_id":video_id,
                "comment_id":"No Comments",
                "comment_author":"No Comments",
                "comment_text":"No Comments",
                "comment_likes":"No Comments",
                "comment_published_date":"No Comments"
            }
        video_comment_details_count.append(video_comment_details)
    else:
        for x in range (len(response3["items"])):
            video_comment_details={
                "video_id":response3["items"][x]["snippet"]["videoId"],
                "comment_id":response3["items"][x]["id"],
                "comment_author":response3['items'][x]["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                "comment_text":response3['items'][x]["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                "comment_likes":response3['items'][x]["snippet"]["topLevelComment"]["snippet"]["likeCount"],
                "comment_published_date":response3['items'][x]["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
            }
            video_comment_details_count.append(video_comment_details)
    return video_comment_details_count


from datetime import datetime, timedelta

# function to convert duration to seconds format
def convert_to_datetime(time_str):
    if 'H' in time_str and 'M' in time_str and 'S' in time_str:
        # Format: PT1H30M56S (1 hour 30 minutes 56 seconds)
        hours = int(time_str.split('H')[0][2:])*3600
        minutes = int(time_str.split('M')[0].split('H')[1])*60
        seconds = int(time_str.split('S')[0].split('M')[1])
        duration_timedelta = hours+minutes+seconds
        return duration_timedelta

    # Parse the input time string
    elif 'H' in time_str and 'M' in time_str:
        # Format: PT1H30M (1 hour 30 minutes)
        hours = int(time_str.split('H')[0][2:])*3600
        minutes = int(time_str.split('M')[0].split('H')[1])*60
        seconds=0
        duration_timedelta = hours+minutes+seconds
        return duration_timedelta
    
    elif 'M' in time_str and 'S' in time_str:
        # Format: PT13M56S (13 minutes 56 seconds)
        hours=0
        minutes = int(time_str.split('M')[0][2:])*60
        seconds = int(time_str.split('S')[0].split('M')[1])
        duration_timedelta = hours+minutes+seconds
        return duration_timedelta
    elif 'H' in time_str and 'S' in time_str:
        # Format: PT1H56S (1 hour 56 seconds)
        hours = int(time_str.split('H')[0][2:])*3600
        minutes=0
        seconds = int(time_str.split('S')[0].split('H')[1])
        duration_timedelta = hours+minutes+seconds
        return duration_timedelta
    elif 'H' in time_str:
        hours = int(time_str.split('H')[0][2:])*3600
        minutes=0
        seconds=0
        duration_timedelta = hours+minutes+seconds
        return duration_timedelta
    elif 'M' in time_str:
        hours=0
        minutes = int(time_str.split('M')[0][2:])*60
        seconds=0
        duration_timedelta = hours+minutes+seconds
        return duration_timedelta
    elif 'S' in time_str:
        hours=0
        minutes=0
        seconds=int(time_str.split('S')[0][2:])
        duration_timedelta = hours+minutes+seconds
        return duration_timedelta
    else:
        raise ValueError("Invalid time format")
    

#Function to connect all the sub functions and creating table in database using dataframe
def control(n):
    global youtube_details,fchd,fvd,fcd,mycursor,engine,mydb
#n="UCoRaQCW7NuCVifjecs86noQ"
    cdt=channel_data(n)
    fchd=pd.DataFrame(cdt,index=[1])
    cd=video_idfun(n)
    vl=[]
    for i in cd[1]:
        a=video_detailsfun(i)
        a1=pd.DataFrame(a,index=[i])
        vl.append(a1)
    fvd=pd.concat(vl,axis=0)
    cd1=[]
    for i in cd[1]:
        a=comment_detailsfun(i)
        n1=len(a)
        a1=pd.DataFrame(a,index= range(n1))
        cd1.append(a1)
    fcd=pd.concat(cd1,axis=0)
    youtube_details=pd.merge(fchd,fvd, on="channel_name").merge(fcd, on="video_id")




    connection = mysql.connector.connect(
  host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
  port = 4000,
  user = "3Pq3bYuANQHnv9P.root",
  password = "M2U9mJayT54djDpU",
  database = "test",
  
    )
    print(connection)
    mycursor = connection.cursor(buffered=True)
    mycursor.execute("use project01")

    engine=create_engine('mysql+mysqlconnector://3Pq3bYuANQHnv9P.root:M2U9mJayT54djDpU@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/project01')

    youtube_details.to_sql(name="youtube_details",con=engine,index=False,if_exists='append')
    fchd.to_sql(name="Channel_details",con=engine,index=False,if_exists='append')
    fvd.to_sql(name="Video_details",con=engine,index=False,if_exists='append')
    fcd.to_sql(name="Comment_details",con=engine,index=False,if_exists='append')




# Function to display the details with connection to SQL
def subdisplay_details(i):
    global out
    connection = mysql.connector.connect(
  host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
  port = 4000,
  user = "3Pq3bYuANQHnv9P.root",
  password = "M2U9mJayT54djDpU",
  database = "test",
  
    )
    print(connection)
    mycursor = connection.cursor(buffered=True)
    mycursor.execute("use project01")
    

    engine=create_engine('mysql+mysqlconnector://3Pq3bYuANQHnv9P.root:M2U9mJayT54djDpU@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/project01')
    if i==1:
        mycursor.execute("SELECT * from project01.youtube_details")
        out=mycursor.fetchall()
    if i==2:
        mycursor.execute("SELECT  DISTINCT Video_details.channel_id, Channel_details.channel_name from Channel_details JOIN Video_details ON Channel_details.channel_name=Video_details.channel_name")
        out=mycursor.fetchall()
    if i==3:
        mycursor.execute("SELECT * from  Channel_details")
        out=mycursor.fetchall()
    return out

#Query part with connection to SQL Server
def query_display(i):
    global out1
    connection = mysql.connector.connect(
  host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
  port = 4000,
  user = "3Pq3bYuANQHnv9P.root",
  password = "M2U9mJayT54djDpU",
  database = "test",
  
    )
    print(connection)
    mycursor = connection.cursor(buffered=True)
    mycursor.execute("use project01")

    engine=create_engine('mysql+mysqlconnector://3Pq3bYuANQHnv9P.root:M2U9mJayT54djDpU@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/project01')
    if i==1:
        mycursor.execute("SELECT  DISTINCT Channel_details.channel_name, Video_details.video_title from Channel_details JOIN Video_details ON Channel_details.channel_name=Video_details.channel_name ORDER BY channel_name ")
        out1=mycursor.fetchall()
    elif i==2:
        mycursor.execute("SELECT  DISTINCT channel_name, CAST(channel_video as SIGNED) as Maximum_video_count from Channel_details ORDER BY Maximum_video_count DESC limit 1 ")
        out1=mycursor.fetchall()
    elif i==3:
        mycursor.execute("SELECT DISTINCT channel_name,video_title,CAST(video_view_count AS SIGNED) as Video_view_count from Video_details ORDER BY Video_view_count DESC  limit 10")
        out1=mycursor.fetchall()
    elif i==4:
        mycursor.execute("SELECT DISTINCT channel_name,video_title, video_comment_count  from Video_details ORDER BY channel_name ")
        out1=mycursor.fetchall()
    elif i==5:
        mycursor.execute("SELECT channel_name,video_title, CAST(video_like_count as SIGNED) as Video_like_count from Video_details ORDER BY Video_like_count DESC limit 1")
        out1=mycursor.fetchall()
    elif i==6:
        mycursor.execute("SELECT  DISTINCT channel_name,video_title,video_like_count  from Video_details ORDER BY channel_name ")
        out1=mycursor.fetchall()
    elif i==7:
        mycursor.execute("SELECT DISTINCT channel_name,channel_view  from Channel_details ORDER BY channel_name ")
        out1=mycursor.fetchall()
    elif i==8:
        mycursor.execute("SELECT DISTINCT channel_name, video_title,video_published_date from Video_details where video_published_date =2022  ORDER BY channel_name")
        out1=mycursor.fetchall()
    elif i==9:
        mycursor.execute("SELECT  channel_name, SEC_TO_TIME(avg(video_duration)) FROM Video_details group by channel_name")
        out1=mycursor.fetchall()
    elif i==10:
        mycursor.execute("SELECT channel_name, video_title, CAST(video_comment_count AS SIGNED) as max from Video_details order by max desc  limit 1")
        out1=mycursor.fetchall()
    return out1

#Streamlit part
st.title('YouTube Data Harvesting and Warehousing using SQL and Streamlit')
st.write("Welcome to the User friendly Streamlit Application")
col1,col2,col3 = st.tabs(['Home','Details','Query'])
with col1:
    user_input=st.text_input("Enter the channelID")
    try:
        if st.button("Extract"):
            subdisplay_details(2)
            detail=pd.DataFrame(out)
            if user_input in detail[0].values:
                st.warning("Channel data already exists,Please enter a different channelID")
                subdisplay_details(1)
                details=pd.DataFrame(out,columns=['Channel_name','Channel_thumbnail','Channel_discription','Channel_view','Channel_video','Channel_subsription','Channel_playlist','Channel_ID','Video_id','Video_title','Video_discription','Video_thumbnail','Video_published_date','Video_comment_count','Video_like_count','Video_favourite_count','Video_duration','Video_view_count','Caption_status','Comment_id','Comment_author','Comment_text','Comment_likes','Comment_published_date'])
                subdisplay_details(3)
                channeld=pd.DataFrame(out,columns=['Channel_name','Channel_thumbnail','Channel_discription','Channel_view','Channel_video','Channel_subsription','Channel_playlist'])
                filtered_df=details[details['Channel_ID'].str.contains(user_input, case=False)]
                filtered_df1 = details[details['Channel_name'].isin(filtered_df['Channel_name'])]
                filtered_df01 = filtered_df1.drop_duplicates(subset=['Channel_name'])
                st.write('Please find the details of the channel')
                for _, row in filtered_df01.iterrows():
                    st.write(row['Channel_name'])
                    st.image(row['Channel_thumbnail'], use_column_width=True)
                x=filtered_df01.T
                st.dataframe(x)
                st.dataframe(filtered_df)
    
            else:
                control(user_input)
                st.success("Channel data obtained successfully")
        
                for _, row in fchd.iterrows():
                    st.image(row['channel_thumbnail'], use_column_width=True)
                x=fchd.T
                st.dataframe(x)
                st.write("Please find the details of the youtube Channel")
                st.dataframe(youtube_details)
    except:
        st.warning('The given channel did not meet the required format,please try another channel.')
        pass
with col2:

    st.write("Please find the details of all the youtube channels with video and comment details")
    add_selectbox=st.selectbox("Please select what to be displayed",("DISPLAY ALL CHANNEL DETAILS","DISPLAY THE LIST OF CHANNELS"))
    if add_selectbox=="DISPLAY ALL CHANNEL DETAILS":
        subdisplay_details(1)
        details=pd.DataFrame(out,columns=['Channel_name','Channel_thumbnail','Channel_discription','Channel_view','Channel_video','Channel_subsription','Channel_playlist','Channel_ID','Video_id','Video_title','Video_discription','Video_thumbnail','Video_published_date','Video_comment_count','Video_like_count','Video_favourite_count','Video_duration','Video_view_count','Caption_status','Comment_id','Comment_author','Comment_text','Comment_likes','Comment_published_date'])
        details.index+=1
        st.dataframe(details)
    if add_selectbox=="DISPLAY THE LIST OF CHANNELS":
        subdisplay_details(2)
        details=pd.DataFrame(out,columns=['Channel_id','Channel_Name'])
        details.index+=1
        st.dataframe(details)
    if add_selectbox=="DISPLAY THE DETAILS OF SPECIFIED CHANNEL":
        subdisplay_details(1)
        details=pd.DataFrame(out,columns=['Channel_name','Channel_thumbnail','Channel_discription','Channel_view','Channel_video','Channel_subsription','Channel_playlist','Channel_ID','Video_id','Video_title','Video_discription','Video_thumbnail','Video_published_date','Video_comment_count','Video_like_count','Video_favourite_count','Video_duration','Video_view_count','Caption_status','Comment_id','Comment_author','Comment_text','Comment_likes','Comment_published_date'])
        subdisplay_details(3)
        channeld=pd.DataFrame(out,columns=['Channel_name','Channel_thumbnail','Channel_discription','Channel_view','Channel_video','Channel_subsription','Channel_playlist'])
        sd=st.selectbox('Select the channel',details['Channel_name'].unique())
        filtered_df=details[details['Channel_name']==sd]
        filtered_df1=channeld[channeld['Channel_name']==sd]
        st.write('Please find the details of the channel')
        for _, row in filtered_df1.iterrows():
                st.write(row['Channel_name'])
                st.image(row['Channel_thumbnail'], use_column_width=True)
        x=filtered_df1.T
        st.dataframe(x)
        st.dataframe(filtered_df)
with col3:
    st.write("Please select the query you wish to display")
    add_selectbox = st.selectbox(
                    "SQL Query Output need to displayed as table in Streamlit Application",
                    ('What are the names of all the videos and their corresponding channels?','Which channels have the most number of videos, and how many videos do they have?',
                'What are the top 10 most viewed videos and their respective channels?',
                'How many comments were made on each video, and what are their corresponding video names?',
                'Which videos have the highest number of likes, and what are their corresponding channel names?',
                'What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
                'What is the total number of views for each channel, and what are their corresponding channel names?','What are the names of all the channels that have published videos in the year 2022?','What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                'Which videos have the highest number of comments, and what are their corresponding channel names?'
                )
                )
    if add_selectbox=='What are the names of all the videos and their corresponding channels?':
        query_display(1)
        try1=pd.DataFrame(out1,columns=["Channel Name","Video_title"])
        try1.index+=1
        st.dataframe(try1)
    elif add_selectbox=='Which channels have the most number of videos, and how many videos do they have?':
        query_display(2)
        try1=pd.DataFrame(out1,columns=["Channel Name","Maximum_Video_Count"])
        try1.index+=1
        st.dataframe(try1)
    elif add_selectbox =='What are the top 10 most viewed videos and their respective channels?':
        query_display(3)
        try1=pd.DataFrame(out1,columns=["Channel Name","Video_title","Video_view_count"])
        try1.index+=1
        st.dataframe(try1)
    elif add_selectbox=='How many comments were made on each video, and what are their corresponding video names?':
        query_display(4)
        try1=pd.DataFrame(out1,columns=["Channel Name","Video_title","Video_comment_count"])
        try1.index+=1
        st.dataframe(try1)
    elif add_selectbox=='Which videos have the highest number of likes, and what are their corresponding channel names?':
        query_display(5)
        try1=pd.DataFrame(out1,columns=["Channel Name","Video_title","MAXimum_Video_like_count"])
        try1.index+=1
        st.dataframe(try1)
    elif add_selectbox=='What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        query_display(6)
        try1=pd.DataFrame(out1,columns=["Channel Name","Video_title","Video_like_count"])
        try1.index+=1
        st.dataframe(try1)
    elif add_selectbox=='What is the total number of views for each channel, and what are their corresponding channel names?':
        query_display(7)
        try1=pd.DataFrame(out1,columns=["Channel Name","Channel_viewcount"])
        try1.index+=1
        st.dataframe(try1)
    elif add_selectbox=='What are the names of all the channels that have published videos in the year 2022?':
        query_display(8)
        try1=pd.DataFrame(out1,columns=["Channel Name","Video_title","Video_published_date"])
        try1.index+=1
        st.dataframe(try1)
    elif add_selectbox=='What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        query_display(9)
        try1=pd.DataFrame(out1,columns=["Channel Name","Average_Duration"])
        try1.index+=1
        st.dataframe(try1)
    elif add_selectbox=='Which videos have the highest number of comments, and what are their corresponding channel names?':
        query_display(10)
        try1=pd.DataFrame(out1,columns=["Channel Name","Video_title","Maximum_comment_count"])
        try1.index+=1
        st.dataframe(try1)


