import cv2
import numpy as np

from moviepy import VideoFileClip, CompositeVideoClip

def create_video_with_zoom_opencv(image_path, output_path, duration=5, zoom_factor=1.5, fps=30):
    # Đọc hình ảnh
    image = cv2.imread(image_path)
    h, w, _ = image.shape

    # Tạo đối tượng VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    # Số frame cần tạo cho video
    total_frames = duration * fps

    for i in range(total_frames):
        # Zoom từ to -> nhỏ
        zoom = zoom_factor - (zoom_factor - 1) * (i / total_frames)

        # Tạo vùng ảnh zoomed
        center = (w // 2, h // 2)
        new_w = int(w * zoom)
        new_h = int(h * zoom)

        zoomed_image = cv2.resize(image, (new_w, new_h))
        x1 = max(0, (new_w - w) // 2)
        y1 = max(0, (new_h - h) // 2)
        zoomed_image_cropped = zoomed_image[y1:y1 + h, x1:x1 + w]

        out.write(zoomed_image_cropped)

    out.release()

# create_video_with_zoom_opencv("./videos/image-0.jpg", "output.mp4", 5)



import ffmpeg

background = "./public/intro.mp4"
overlay = "./output.mp4"
output = "final.mp4"

# Overlay ở giữa
ffmpeg.input(background).output(overlay).run()  # đơn giản, nhưng thường cần filter