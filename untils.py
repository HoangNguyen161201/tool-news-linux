import requests
import os
from bs4 import BeautifulSoup
import random
from data import gif_paths, person_img_paths
import cv2
import subprocess
from tqdm import tqdm

def get_all_link_in_theguardian_new():
    url = 'https://www.theguardian.com/world'
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    link = []
    # Lọc các thẻ <a> thỏa điều kiện
    for a in soup.find_all('a', href=True):
        data_link = a.get('data-link-name', '')
        if 'card-@1' in data_link and 'live' not in data_link:
            link.append(a['href'])
    return link

def get_info_new(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # title, description and content
        title = None
        meta_tag = soup.find('meta', attrs={'property': 'og:title'})
        if meta_tag:
            title = meta_tag.get('content', None)

        description = None
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag:
            description = meta_tag.get('content', None)

        tags = None
        meta_tag = soup.find('meta', attrs={'property': 'article:tag'})
        if meta_tag:
            tags = meta_tag.get('content', None)

        content = soup.find('div', {'id': 'maincontent'}).get_text()

        # pictures
        pictures = soup.find_all('picture', class_='dcr-evn1e9')
        picture_links = []
        for item in pictures:
            source = item.find(['source', 'img'], srcset = True)
            picture_links.append(source['srcset'])
        if(picture_links.__len__() == 0 or content is None or content is None or content is None or content is None):
            return None
        
        return {
            "content": content,
            "title": title,
            "description": description,
            "tags": tags,
            "picture_links": picture_links
        }
    except:
      return None

def get_img_gif_person():
    index_path = random.randint(0, 3)
    return {
        'person_img_path': person_img_paths[index_path],
        'person_gif_path': gif_paths[index_path]    
    } 

def generate_image(link, out_path, out_blur_path, width=1920, height=1080):
    def resize_to_fit(image, max_width, max_height):
        h, w = image.shape[:2]
        scale = min(max_width / w, max_height / h, 1.0)  # chỉ scale nhỏ
        return cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    response = requests.get(link)
    if response.status_code != 200:
        print("Yêu cầu không thành công. Mã trạng thái:", response.status_code)
        return

    with open(out_path, "wb") as f:
        f.write(response.content)

    image = cv2.imread(out_path)
    image = image[150:-150, 150:-150]

    # === ẢNH BLUR ===
    blurred = cv2.resize(image, (1920, 1080), interpolation=cv2.INTER_AREA)
    blurred = cv2.copyMakeBorder(blurred, 25, 25, 25, 25, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    blurred = cv2.GaussianBlur(blurred, (0, 0), 15)

    # === ẢNH CHÍNH ===
    image_resized = resize_to_fit(image, 1840, 1000)
    image_with_border = cv2.copyMakeBorder(image_resized, 25, 25, 25, 25, cv2.BORDER_CONSTANT, value=(255, 255, 255))

    # === GHÉP ẢNH CHÍNH LÊN ẢNH BLUR ===
    # Tính vị trí để canh giữa
    h_blur, w_blur = blurred.shape[:2]
    h_img, w_img = image_with_border.shape[:2]

    x_offset = (w_blur - w_img) // 2
    y_offset = (h_blur - h_img) // 2

    # Dán ảnh chính lên ảnh blur
    combined = blurred.copy()
    combined[y_offset:y_offset + h_img, x_offset:x_offset + w_img] = image_with_border

    # Ghi ảnh kết quả
    cv2.imwrite(out_path, combined)
    cv2.imwrite(out_blur_path, blurred)


def generate_video_by_image( in_path, out_path, second, gif_path):
    width, height = 1920, 1080
    duration = second
    os.makedirs('./temp', exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "0", "-t", str(duration), "-i", in_path,
        "-loop", "0", "-t", str(duration), "-i", './public/avatar.png',
        "-filter_complex",
        f"""
        [0:v]scale={width}:{height},setsar=1,setpts=PTS-STARTPTS[bg]; \
        [1:v]scale=200:200,format=rgba,colorchannelmixer=aa=0.7,setsar=1[avatar]; \
        [bg][avatar]overlay={width - 270}:50
        """.replace('\n', ''),
        "-t", str(duration),
        "-r", "15",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-threads", "1",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        out_path
    ]


    # === Run FFmpeg with progress ===
    process = subprocess.Popen(
        cmd,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    total_frames = duration * 24
    pbar = tqdm(total=total_frames, desc="Rendering", unit="frame")

    for line in process.stderr:
        if "frame=" in line:
            parts = line.strip().split()
            for part in parts:
                if part.startswith("frame="):
                    try:
                        frame_number = int(part.split('=')[1])
                        pbar.n = frame_number
                        pbar.refresh()
                    except:
                        pass
    pbar.close()

    process.wait()
    if process.returncode != 0:
        raise Exception("FFmpeg failed")

