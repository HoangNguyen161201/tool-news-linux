import googleapiclient.discovery
import googleapiclient.discovery

api_key = "AIzaSyCFCtn3uH3kXFwu7HS1-V4iOfjuM1--Ju0"  # API key của bạn
handle = "@05-hot"

youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

# Tìm kênh theo handle
search = youtube.search().list(
    part="snippet",
    q=handle,
    type="channel"
).execute()

channel_id = search['items'][0]['snippet']['channelId']
print(channel_id)

youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

request = youtube.channels().list(
    part="statistics",
    id=channel_id
)
response = request.execute()

stats = response['items'][0]['statistics']

total_views = stats['viewCount']
total_subs = stats.get('subscriberCount', 'Ẩn')
total_videos = stats['videoCount']

print(f"Tổng lượt xem: {total_views}")
print(f"Số subscriber: {total_subs}")
print(f"Số video đã đăng: {total_videos}")