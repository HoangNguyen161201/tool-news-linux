from untils import check_file_exists_on_vps, download_file_from_vps, delete_remote_folder_vps
import time
def main():
    while True:
        check_exists_file_video = check_file_exists_on_vps('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos/result.mkv')
        check_exists_file_txt = check_file_exists_on_vps('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos/result.txt')
        if(check_exists_file_video and check_exists_file_txt):
            download_file_from_vps('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos/result.mkv', './result.mkv')
            download_file_from_vps('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos/result.txt', './result.txt')
            delete_remote_folder_vps('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos')
        else: 
            print('chưa tạo video mới')
            time.sleep(5)



if __name__ == "__main__":
    main()