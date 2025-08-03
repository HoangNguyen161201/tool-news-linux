from untils import upload_yt, check_file_exists_on_vps, download_file_from_vps, delete_remote_folder_vps
import time
import os
from slugify import slugify
import subprocess

# ## dùng để tạo ra 1 user
# chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
# user_data_dir = "C:/Path/To/Chrome/news-us-news-2"
# subprocess.Popen([chrome_path, f'--remote-debugging-port=9223', f'--user-data-dir={user_data_dir}'])
# time.sleep(10000)


def main():
    while True:
        check_exists_file_video = check_file_exists_on_vps('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos/result.mkv')
        check_exists_file_txt = check_file_exists_on_vps('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos/result.txt')
        if(check_exists_file_video and check_exists_file_txt):
            print('download file')
            download_file_from_vps('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos/result.mkv', './result.mkv')
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
            os.rename('./result.mkv', f'./{title_slug}.mkv')
            upload_yt(
                "C:/Path/To/Chrome/news-us-news-2",
                title,
                description,
                tags,
                os.path.abspath(f'./{title_slug}.mkv'),
                os.path.abspath(f"./thumbnail.jpg"),
            )
            os.remove(f'./{title_slug}.mkv')
            time.sleep(1200)
        else: 
            print('chưa tạo video mới')
            time.sleep(20)


if __name__ == "__main__":
    main()