from untils import upload_yt, check_file_exists_on_vps, download_file_from_vps, delete_remote_folder_vps
import time
import os
from slugify import slugify

def main():
    while True:
        check_exists_file_video = check_file_exists_on_vps('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos/result.mp4')
        check_exists_file_txt = check_file_exists_on_vps('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos/result.txt')
        if(check_exists_file_video and check_exists_file_txt):
            download_file_from_vps('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos/result.mp4', './result.mp4')
            download_file_from_vps('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos/result.txt', './result.txt')
            download_file_from_vps('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos/thumbnail.jpg', './thumbnail.jpg')
            delete_remote_folder_vps('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos')

            title = ''
            tags = ''
            description = ''
            with open('./result.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                title = lines[0].strip() if len(lines) >= 1 else ''
                tags = lines[1].strip() if len(lines) >= 2 else ''
                description = ''.join(lines[2:]).strip() if len(lines) >= 3 else ''
            title_slug = slugify(title)
            os.rename('./result.mp4', f'./{title_slug}.mp4')
            upload_yt(
                "C:/Path/To/Chrome/news-us-news",
                title,
                description,
                tags,
                os.path.abspath(f'./{title_slug}.mp4'),
                os.path.abspath(f"./thumbnail.jpg"),
            )
            time.sleep(1200)
        else: 
            print('chưa tạo video mới')
            time.sleep(5)


if __name__ == "__main__":
    main()