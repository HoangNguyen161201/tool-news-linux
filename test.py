from untils import normalize_video, generate_to_voice_edge, check_file_exists_on_vps, download_file_from_vps, delete_remote_folder_vps
import os
import subprocess

# generate_to_voice_edge("If you're looking for an awesome product at a great price, be sure to check out the link in the description!", './public/aff.aac')
normalize_video('./public/intro.mp4', './public/intro.mkv')
normalize_video('./videos/draf2.mkv', './videos/draf3.mkv')

# Tạo file danh sách tạm thời
list_file = "video_list.txt"
    # nối intro với video
with open(list_file, "w", encoding="utf-8") as f:
    f.write(f"file '{os.path.abspath('./public/intro.mkv')}'\n")
    f.write(f"file '{os.path.abspath('./videos/draf3.mkv')}'\n")
    

    command = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        './t.mp4',
        "-progress", "-",
        "-nostats"
    ]


subprocess.run(command)
os.remove(list_file)

# # # check_file_exists_on_vps('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos/result.mkv')
# # # download_file_from_vps('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos/result.mkv', './result.mvk')
# # # delete_remote_folder('207.246.125.31', 'root', '6{zC6v_6!btTCJ=e', '/root/tool-news-linux/videos')