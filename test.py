from untils import normalize_video
import os
import subprocess
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
    './output.mkv',
    "-progress", "-",
    "-nostats"
]


subprocess.run(command)
os.remove(list_file)