
YouTube Data Harvesting and Warehousing using SQL and Streamlit


This project aims in developing a User friendly Streamlit application to harvest and warehouse the YouTube Data using SQL.
This application is used to create a Streamlit application that allows users to access and analyze data from multiple YouTube channels.

## API Reference

#### Get playlist_id

```http
  GET youtube/channel/response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `playlistid` | `string` |playlist_id of the channel  |

#### Get video_id

```http
  GET youtube/playlistItems/response['items'][item]['snippet']['resourceId']['videoId']
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `videoId`      | `string` |video_id of each video |


#### Get comment_id

```http
  GET youtube/commentThread/response["items"][x]["id"]
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `comment_id`      | `string` |  comment_Id of each comment of a particular video |





## Installation

Install the follwing packages for the smooth run of the project

```bash
  pip install google-api-python-client
  pip install datetime
  pip install iso8601
  pip install mysql-connector-python
  pip install sqlalchemy
  pip install streamlit
```
    
## Features

- User friendly
- Able to input and get channel details
- Able to fetch details from API
- Cross platform


## Deployment

To deploy this project run

```bash
   streamlit run project1_youtube.py

```


## Demo

Find the linkedin link of the project demo video
https://www.linkedin.com/feed/update/urn:li:activity:7188454297167175680/

## Skills Takeaway
- Python
- SQL
- Streamlit
- Knowledge on fetching data from API
- Data Collection
- Data Management using SQL