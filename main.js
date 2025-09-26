<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>YouTube Channel Views</title>
  <script src="https://apis.google.com/js/api.js"></script>
</head>
<body>
  <h2>Lấy Tổng Lượt Xem Kênh YouTube</h2>
  <button onclick="getChannelViews()">Lấy Lượt Xem</button>
  <p id="result">Đang chờ...</p>

  <script>
    const API_KEY = 'AIzaSyDHQiXe0bLlGqFFelG6mvBe7L2Wrb_MM6M'; // API KEY bạn đã có
    const CHANNEL_ID = 'UC3FjgcZuhLuIu90GiqqObwg'; // Thay bằng CHANNEL ID thật

    function loadClient() {
      gapi.client.setApiKey(API_KEY);
      return gapi.client.load("https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest");
    }

    function getChannelViews() {
        gapi.load("client", async () => {
            try {
                await loadClient();
                alert('dfdf')

          const response = await gapi.client.youtube.channels.list({
            part: 'statistics',
            id: CHANNEL_ID
          });

          const stats = response.result.items[0].statistics;
          const viewCount = stats.viewCount;
          const subs = stats.subscriberCount;
          const videos = stats.videoCount;

          document.getElementById("result").innerText =
            `Tổng lượt xem: ${viewCount}\n` +
            `Tổng số sub: ${subs}\n` +
            `Tổng video: ${videos}`;
        } catch (err) {
          console.error("Lỗi:", err);
          document.getElementById("result").innerText = "Đã xảy ra lỗi khi lấy dữ liệu.";
        }
      });
    }
  </script>
</body>
</html>