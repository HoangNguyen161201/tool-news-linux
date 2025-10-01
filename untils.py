import requests
import os
from bs4 import BeautifulSoup
import random
from data import gif_paths, person_img_paths
import asyncio
import cv2
import subprocess
from tqdm import tqdm
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import shutil
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import re
import google.generativeai as genai
import edge_tts
import uuid
import paramiko
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyperclip
from data import data_support
from db_mongodb import get_webiste
from datetime import datetime, timedelta
from moviepy import ImageClip, VideoFileClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip, TextClip, concatenate_audioclips
import numpy as np
import inspect
import xml.etree.ElementTree as ET
from db_mongodb import get_all_sitemap_links 
from itertools import zip_longest

def func_to_string(func):
    return inspect.getsource(func)

# get link in news website -------------------------------------------------------------------------------------
# kenh14 star---
def get_all_link_in_kenh14_star_new():
    url = 'https://kenh14.vn/star.chn'
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    link = []
    

    # Lọc các thẻ <a> thỏa điều kiện
    for a in soup.find_all('a', href=True, class_='ktncli-ava'):
        link.append(f'https://kenh14.vn{a['href']}')
    
    return link

def get_info_new_kenh14_star(url):
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
        meta_tag = soup.find('meta', attrs={'name': 'keywords'})
        if meta_tag:
            tags = meta_tag.get('content', None)
            

        content = soup.find('div', {'class': 'detail-content'}).get_text(strip=True)

        
        # pictures
        pictures = soup.find_all('img', attrs={'type': 'photo'})
        picture_links = [img['src'] for img in pictures if img.has_attr('src')]

        if len(picture_links) == 0 or content is None:
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
# theguardian---
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
            link.append(f'https://www.theguardian.com{a['href']}')
    return link

def get_info_new_theguardian(url):
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
# aljazeera---
def get_all_link_in_aljazeera_new():
    url = 'https://www.aljazeera.com/news/'
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    link = []

    for at in soup.find_all('article'):
        classes = at.get('class', [])
        if all(cls in classes for cls in ['article-card--reset']):
            if at.find(class_='post-icon__text') or 'Live updates' in at.get_text():
                continue
            a_tag = at.find('a', href=True)
            if a_tag:
                link.append(f'https://www.aljazeera.com{a_tag['href']}')
    return link
def get_info_new_aljazeera(url):
    print(url)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }

        response = requests.get('https://www.aljazeera.com/news/2025/8/3/threats-and-intimidation-stalling-top-icc-prosecutors-israel-case-report', headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # title, description and content
        title = None
        meta_tag = soup.select_one('meta[name="pageTitle"]')
        if meta_tag:
            title = meta_tag.get('content')

        print(title)
        print(soup)
        time.sleep(10000)

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
        

# ----------------------------- ------------------------------------------
def get_img_gif_person():
    index_path = random.randint(0, 3)
    return {
        'person_img_path': person_img_paths[index_path],
        'person_gif_path': gif_paths[index_path]    
    } 

# create video by image with ffmpeg----------------------------------------------
def generate_image_ffmpeg(link, out_path, out_blur_path, width=1920, height=1080, crop=150):
    def resize_to_fit(image, max_width, max_height):
        h, w = image.shape[:2]
        scale = min(max_width / w, max_height / h)
        return cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    response = requests.get(link)
    if response.status_code != 200:
        print("Yêu cầu không thành công. Mã trạng thái:", response.status_code)
        return

    with open(out_path, "wb") as f:
        f.write(response.content)

    image = cv2.imread(out_path)
    image = image[crop:-crop, crop:-crop]

    # === ẢNH BLUR ===
    blurred = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
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

def generate_video_by_image_ffmpeg( in_path, out_path, second, is_set_avatar = True):
    width, height = 1920, 1080
    duration = second
    os.makedirs('./temp', exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-framerate", "1", "-loop", "1", "-t", str(duration), "-i", in_path,
        "-framerate", "1", "-loop", "1", "-t", str(duration), "-i", './public/avatar2.png',
        "-filter_complex",
        f"""
        [0:v]scale={width}:{height},setsar=1,setpts=PTS-STARTPTS[bg]; \
        [1:v]scale=200:200,format=rgba,colorchannelmixer=aa={0.7 if is_set_avatar else 0},setsar=1[avatar]; \
        [bg][avatar]overlay={width - 270}:50
        """.replace('\n', ''),
        "-r", "1",                   # Giảm FPS cho nhẹ
        "-crf", "32",                 # Giảm bitrate nhưng giữ duration
        "-c:v", "libx264",            # Codec phổ biến
        "-preset", "ultrafast",       # Encode nhanh
        "-tune", "zerolatency",       # Cho realtime/stream
        "-threads", "1",              # 1 vCPU
        "-pix_fmt", "yuv420p",        # Tương thích
        "-movflags", "+faststart",   # Tốt cho web
        "-t", str(duration),          # ✨ Đảm bảo thời lượng cuối cùng
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

# create video by image with cv2----------------------------------------------
def generate_image_cv2(link, out_path, out_blur_path, width=None, height=None, crop=150):
    print(link)
    import requests

    response = requests.get(link)
    if response.status_code == 200:
        with open(out_path, "wb") as f:
            f.write(response.content)
    else:
        print("Yêu cầu không thành công. Mã trạng thái:", response.status_code)
        return

    image = cv2.imread(out_path)
    h, w, _ = image.shape
    max_w = width - 100
    max_h = height - 100
    scale = min(max_w / w, max_h / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    image= cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    image = image[crop:-crop, crop:-crop]  # crop trung tâm

    blurred_image_edit = None
    if width is not None and height is not None:
        # Resize dãn ra luôn
        blurred_image_edit = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)
    else:
        image = cv2.flip(image, 1)

    border_thickness = 25
    border_color = (255, 255, 255)
    blurred_image_edit_2 = cv2.copyMakeBorder(
        blurred_image_edit if blurred_image_edit is not None else image,
        border_thickness, border_thickness,
        border_thickness, border_thickness,
        cv2.BORDER_CONSTANT, value=border_color
    )
    image = cv2.copyMakeBorder(
        image,
        border_thickness, border_thickness,
        border_thickness, border_thickness,
        cv2.BORDER_CONSTANT, value=border_color
    )

    # Làm mờ hình ảnh
    blurred_image = cv2.GaussianBlur(blurred_image_edit_2, (0, 0), 15)

    cv2.imwrite(out_path, image)
    cv2.imwrite(out_blur_path, blurred_image)
    

def create_video_with_zoom_opencv(image_path, output_path, duration=5, zoom_factor=1.25, fps=15, zoom_in=True):
    image = cv2.imread(image_path)
    h, w, _ = image.shape
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # hoặc 'mp4v'
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
    total_frames = duration * fps
    
    cx, cy = w / 2, h / 2  # tâm ảnh
    
    for i in range(total_frames):
        t = i / total_frames
        zoom = 1 + (zoom_factor - 1) * t if zoom_in else zoom_factor - (zoom_factor - 1) * t

        # Ma trận scale quanh tâm
        M = cv2.getRotationMatrix2D((cx, cy), 0, zoom)
        zoomed_image = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR)

        out.write(zoomed_image)
    out.release()
    
def generate_video_by_image_cv2(zoom_in, in_path, blur_in_path, in_path_draft, blur_in_path_draft, out_path, second):
    create_video_with_zoom_opencv(blur_in_path,blur_in_path_draft, second, zoom_in= True if zoom_in is None else False )
    create_video_with_zoom_opencv(in_path,in_path_draft, second, zoom_in= False if zoom_in is None else True)
    
    command = [
        "ffmpeg", "-y",
        "-i", blur_in_path_draft,    # background video
        "-i", in_path,               # image
        "-i", in_path_draft,         # overlay video
        "-i", "./public/avatar2.png", # avatar image
        "-filter_complex",
        "[1:v]scale=iw+50:ih+50[img_scaled];"
        "[0:v][img_scaled]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2[tmp1];"
        "[tmp1][2:v]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2[tmp2];"
        "[3:v]scale=200:200,format=rgba,colorchannelmixer=aa=0.7[avatar];"
        "[tmp2][avatar]overlay=main_w-overlay_w-50:50[outv]",
        "-map", "[outv]",             # chỉ lấy video từ filter
        "-map", "0:a?",               # lấy audio gốc nếu có (không thì bỏ qua)
        "-c:v", "libx264",            # encoder video
        "-preset", "ultrafast",       # tối ưu tốc độ
        "-crf", "23",                 # chất lượng hợp lý
        "-c:a", "copy",               # copy audio (nhanh nhất)
        out_path
    ]
    
    subprocess.run(command)


# create video by image with moviepy-------------------------------------------------------------
def resize_to_cover(image, target_width, target_height):
    # Get the original dimensions
    original_height, original_width = image.shape[:2]
    
    # Calculate the aspect ratios
    target_aspect = target_width / target_height
    original_aspect = original_width / original_height
    
    # Determine the scaling factor and dimensions to cover the target area
    if original_aspect > target_aspect:
        # Image is wider than target, scale by height
        scale = target_height / original_height
    else:
        # Image is taller than target, scale by width
        scale = target_width / original_width
    
    # Resize the image
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)
    resized_image = cv2.resize(image, (new_width, new_height))
    
    # Calculate the cropping coordinates
    x_center = new_width // 2
    y_center = new_height // 2
    x_crop = target_width // 2
    y_crop = target_height // 2
    
    # Crop the image to the target dimensions
    cropped_image = resized_image[y_center - y_crop:y_center + y_crop, x_center - x_crop:x_center + x_crop]
    
    return cropped_image

def generate_image_moviepy(link, out_path, out_blur_path, width = None, height = None, crop=150):
    response = requests.get(link)
    if response.status_code == 200:
        with open(out_path, "wb") as f:
            f.write(response.content)
    else:
        print("Yêu cầu không thành công. Mã trạng thái:", response.status_code)

    image = cv2.imread(out_path)
    image = image[crop:-crop, crop:-crop]
    blurred_image_edit = None
    if width is not None and height is not None:
        blurred_image_edit  = resize_to_cover(image, width, height)
    else:
        image = cv2.flip(image, 1)
    border_thickness = 25
    border_color = (255, 255, 255)
    blurred_image_edit_2 = cv2.copyMakeBorder(blurred_image_edit if blurred_image_edit is not None else image, border_thickness, border_thickness, border_thickness, border_thickness, cv2.BORDER_CONSTANT, value=border_color)
    image = cv2.copyMakeBorder(image, border_thickness, border_thickness, border_thickness, border_thickness, cv2.BORDER_CONSTANT, value=border_color)

    # Làm mờ hình ảnh bằng Blur
    blurred_image = cv2.GaussianBlur(blurred_image_edit_2, (0, 0), 15)

    cv2.imwrite(out_path, image)
    cv2.imwrite(out_blur_path, blurred_image)

def generate_video_by_image_moviepy(zoom_in, in_path, blur_in_path, out_path, second, gif_path, is_short = False):
    clip_image = ImageClip(in_path).with_duration(second)
    clip_blurred_image = ImageClip(blur_in_path, duration= second).resized((1080, 1920) if is_short else (1920, 1080))
    clip_blurred_image = clip_blurred_image.resized(lambda t: 1 + 0.3 * t/second)

    if not zoom_in:
        w_clip_image, h_clip_image = clip_image.size
        percent = (960 / w_clip_image) if (960 / w_clip_image) * h_clip_image < 720 else (720 / h_clip_image)
        if is_short:
            percent = (720 / w_clip_image) if (720 / w_clip_image) * h_clip_image < 960 else (960 / h_clip_image)
        clip_image = clip_image.resized((percent * w_clip_image, percent * h_clip_image))
        clip_image = clip_image.resized(lambda t: 1 + 0.4 * t/second)
    else:
        w_clip_image, h_clip_image = clip_image.size
        percent = ((1920 - 60) / w_clip_image) if ((1920 - 60) / w_clip_image) * h_clip_image < 1020 else (1020 / h_clip_image)
        if is_short:
            percent = (1020 / w_clip_image) if (1020 / w_clip_image) * h_clip_image < (1920 - 60) else ((1920 - 60) / h_clip_image)
        clip_image = clip_image.resized((percent * w_clip_image, percent * h_clip_image))
        clip_image = clip_image.resized(lambda t: 1 - 0.3 * t/second)
    
    # # add gif
    # gif = VideoFileClip(gif_path, has_mask= True)
    # percent_gif = 0.8 
    # gif = gif.resized((int(1920 * percent_gif), int(1080 * percent_gif)))
    # while gif.duration < second:
    #     gif = concatenate_videoclips([gif, gif])
    # gif = gif.subclipped(0, second)

    
    # Tạo avatar clip
    avatar_clip = ImageClip('./public/avatar2.png').resized((200, 200))
    avatar_clip = avatar_clip.with_opacity(0.7)
    avatar_clip = avatar_clip.with_position((830 if is_short else 1650,  50))

    final_clip = CompositeVideoClip([
        clip_blurred_image.with_position('center'),
        clip_image.with_position('center'),
        # gif.with_position((0, 1080 if is_short else 250)),
        avatar_clip.with_duration(second)
        ])

    final_clip.write_videofile(out_path, fps=10)
    
    


# -------------------------------------------------------------------------------------

def download_and_resize_image(url, size=(399, 399), save_path='output.jpg'):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # báo lỗi nếu không tải được
        image = Image.open(BytesIO(response.content)).convert('RGB')
        
        # Resize theo kích thước cố định (có thể méo hình nếu không đúng tỷ lệ)
        image_resized = image.resize(size)

        image_resized.save(save_path)
        print(f"✅ Saved resized image to {save_path}")
    except Exception as e:
        print(f"❌ Error processing {url}: {e}")

def add_rounded_corners(image: Image.Image, radius: int) -> Image.Image:
    # Tạo mặt nạ hình tròn
    rounded_mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(rounded_mask)
    draw.rounded_rectangle([0, 0, *image.size], radius=radius, fill=255)

    # Áp dụng mask vào ảnh
    rounded_image = image.copy()
    rounded_image.putalpha(rounded_mask)

    return rounded_image

def import_audio_to_video(in_path, out_path, audio_path, audio_duration):
    command = [
        "ffmpeg", "-y",
        "-i", in_path,
        "-i", audio_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "copy",
        "-t", str(audio_duration),
        out_path
    ]
    subprocess.run(command)

def generate_image_and_video_aff_and_get_three_item():
    support_randoom = data_support
    random.shuffle(support_randoom)
    support_randoom = random.sample(support_randoom, 3)
    uri = "mongodb+srv://hoangdev161201:Cuem161201@cluster0.3o8ba2h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["news"]
    collection = db["link_affs"]

    path_folder = f'./pic_affs'
    try:
        shutil.rmtree(path_folder)
    except:
        print('next')
    
    os.makedirs(path_folder)

    # Lấy ngẫu nhiên 3 item
    random_items = list(collection.aggregate([
        {"$sample": {"size": 3}}
    ]))


    # In kết quả
    for i, item in enumerate(random_items):
        download_and_resize_image(item['itemMainPic'], save_path= f'{path_folder}/pic_{i}.png')


    try:
        background = Image.open('./public/bg/aff.png').convert("RGB")
        draw = ImageDraw.Draw(background)

        
        font = ImageFont.truetype("./fonts/arial/arial.ttf", 35)
        font2 = ImageFont.truetype("./fonts/arial/arial.ttf", 29)
        font3 = ImageFont.truetype("./fonts/arial/ARIBL0.ttf", 40)
    

        for i, item in enumerate(random_items):
            foreground = Image.open(f'{path_folder}/pic_{i}.png').convert("RGBA")
            foreground = add_rounded_corners(foreground, 11)
            x = 367 + 498 * i
            y = 240
            background.paste(foreground, (x, y), foreground)
            
            title = item['itemTitle']
            if len(title) > 30:
                title = title[:20] + "..."

            
            percent = ''
            match = re.search(r'\d+(\.\d+)?', item['itemOriginPriceMin'])
            match2 = re.search(r'\d+(\.\d+)?', item['itemPriceDiscountMin'])
            if match and match2:
                number1 = float(match.group())
                number2 = float(match2.group())
                percent = f'-{round(number2 / number1 * 100, 0)}%'


            # Vẽ chữ phía dưới ảnh
            draw.text((x, y + foreground.height + 25), title, fill=(0, 0, 0), font=font)
            draw.text((x, y + foreground.height + 80), f'{item['totalTranpro3Semantic']} Sold', fill=(128, 128, 128), font=font2)
            draw.rounded_rectangle(
                [(x + 230, y), (x + 230 + 170, y + 65)],
                radius=15,  # độ cong của góc
                fill=(255, 255, 255),
                outline=(210, 210, 210)
            )
            draw.text((x + 240, y), percent, fill=(255, 0, 0), font=font3)
            
        background.save(f'{path_folder}/pic_result.png')
        audio_duration = get_media_duration('./public/aff.aac')

        generate_video_by_image_ffmpeg(
                        f'{path_folder}/pic_result.png',
                        f'{path_folder}/daft.mkv',
                        audio_duration
                    )

        import_audio_to_video(f'{path_folder}/daft.mkv', f'{path_folder}/aff.mkv',  './public/aff.aac', audio_duration)
        
        print("✅ Done")
        return random_items
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    
# amazon -----------------------------
def process_image_support(
    input_url,
    output_path,
    discount=0,
    fixed_width=410,
    max_height=650,
    border_width=10,
    border_color='#CDCDCD',
    corner_radius=20,
):
    # Tải ảnh
    response = requests.get(input_url)
    img = Image.open(BytesIO(response.content)).convert("RGBA")

    # Tính lại size để KHÔNG CROP và KHÔNG MÉO
    original_width, original_height = img.size
    scale_w = fixed_width / original_width
    scale_h = max_height / original_height
    scale = min(scale_w, scale_h)

    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    img = img.resize((new_width, new_height), Image.LANCZOS)

    # Bo góc
    mask = Image.new('L', (new_width, new_height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, new_width, new_height], radius=corner_radius, fill=255)
    rounded_img = Image.new("RGBA", (new_width, new_height))
    rounded_img = Image.composite(img, rounded_img, mask)

    # Thêm viền ngoài
    bordered_width = new_width + 2 * border_width
    bordered_height = new_height + 2 * border_width
    bordered_img = Image.new("RGBA", (bordered_width, bordered_height), (0, 0, 0, 0))

    draw = ImageDraw.Draw(bordered_img)
    draw.rounded_rectangle(
        [0, 0, bordered_width, bordered_height],
        radius=corner_radius + border_width,
        fill=border_color
    )
    bordered_img.paste(rounded_img, (border_width, border_width), mask=mask)

    # Nếu có discount
   
    badge_radius = 48
    badge_diameter = badge_radius * 2
    badge_position = (bordered_width - badge_diameter - 10, 10)

    # Vẽ hình tròn trắng
    draw.ellipse(
        [badge_position[0], badge_position[1], badge_position[0] + badge_diameter, badge_position[1] + badge_diameter],
        fill="white"
    )

    # Vẽ text
    try:
        font = ImageFont.truetype("./fonts/arial/arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    text = f"-{discount}%" if discount > 0 else 'Hot'
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = badge_position[0] + (badge_diameter - text_width) // 2
    text_y = badge_position[1] + (badge_diameter - text_height) // 2 - 1

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            draw.text((text_x + dx, text_y + dy), text, font=font, fill="red")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    bordered_img.save(output_path)

def generate_image_and_video_aff_and_get_three_item_amazon():
    try:
        support_randoom = data_support
        random.shuffle(support_randoom)
        support_randoom = random.sample(support_randoom, 3)
        link_support_images = [item['link_img'] for item in support_randoom]
        list_discount = [item['discount'] for item in support_randoom]
        content_supports = "\n".join([item['content'] for item in support_randoom])
        
        for index, item in enumerate(link_support_images):
            print(item)
            process_image_support(item, f'./pic_affs/support_{index}.png', list_discount[index])

        # Load ảnh background
        background = Image.open("./public/bg/support.png")  # hoặc background.png

        # Load 3 ảnh sản phẩm
        product1 = Image.open(f'./pic_affs/support_0.png')
        product2 = Image.open(f'./pic_affs/support_1.png')
        product3 = Image.open(f'./pic_affs/support_2.png')

        # Dán các sản phẩm vào ảnh nền tại vị trí mong muốn
        background.paste(product1, (200, 245), product1.convert("RGBA"))
        background.paste(product2, (715, 245), product2.convert("RGBA"))
        background.paste(product3, (1230, 245), product3.convert("RGBA"))

        # Lưu kết quả
        background.save("./pic_affs/drag.png")
        audio_duration = get_media_duration('./public/aff.aac')
        generate_video_by_image_ffmpeg(
                        f'./pic_affs/drag.png',
                        f'./pic_affs/daft.mkv',
                        audio_duration,
                        False
                    )
        import_audio_to_video(f'./pic_affs/daft.mkv', f'./pic_affs/aff.mkv',  './public/aff.aac', audio_duration)
        
        print("✅ Done")
        return content_supports
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def generate_content(content, model='gemini-1.5-flash', api_key = None):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model)
    response = model.generate_content(content)
    return response.text

def generate_title_description_improved(title, description, gemini_key = None, model = None):
    while True:
        title_des = generate_content(f'''tôi đang có các thông tin như sau:
                                    - title: {title}
                                    - description: {description}
                                    hãy generate lại các thông tin trên cho tôi bằng tiếng việt sao cho hay và nổi bật, chuẩn seo youtube.
                                    Trả ra dưới định dạng như sau:
                                    Dòng 1: là title (trên 50 ký tự và không quá 100 ký tự, không được có các dấu ký hiệu đặt biệt trong title, không có chứa 'dòng 1:').
                                    Từ dòng thứ 2 trở đi: là description. 
                                    Trả ra kết quả cho tôi luôn, không cần phải giải thích hay ghi thêm gì hết.''',
                                    api_key= gemini_key,
                                    model= model
                        )
        
        lines = title_des.splitlines()
        title_line = lines[0].strip()
        if len(title_line) < 100:
            desc = "\n".join(lines[1:]).strip()
            desc = re.sub(r'[ \t]+', ' ', desc)
            return {
                "title": title_line,
                "description": desc
            }

# tạo lại nội dung content
def generate_content_improved(content, title, gemini_key = None, model = None):
    return generate_content(f'''
        Tôi có một bản tin mới. Hãy viết lại bằng tiếng việt sao cho hấp dẫn, súc tích và phù hợp để đọc lên trong một video tin tức trên YouTube (voice-over). Nội dung cần được viết dưới dạng khách quan ở ngôi thứ ba, không dùng tôi, của tôi, chúng ta, hay bất kỳ đại từ ngôi thứ nhất nào.
        title là: {title},
        Nội dung là: {content}

        Yêu cầu:
        - độ dài ký tự bằng hoặc trên {content.__len__()} ký tự.
        - không được viết giống, tránh đạo văn.
        - Viết thành một đoạn văn liền mạch, không chia cảnh, không dùng markdown, không có dấu *, **, hoặc [Scene:].
        - Phong cách giống người dẫn bản tin truyền hình, mang tính tường thuật khách quan nhưng thu hút, gây tò mò và khơi gợi cảm xúc.
        - Không thêm bất kỳ lời giải thích nào. Chỉ trả về nội dung đã viết lại.
        ''', api_key= gemini_key, model= model)
        
        
def generate_thumbnail(img_path, img_person_path, draf_path, out_path, text):
    text = text.upper()

    # Mở ảnh thứ hai (ảnh nền phụ) và thay đổi kích thước
    background_2 = Image.open(img_path)
    background_2 = background_2.resize((1920, 1080))

    # Mở ảnh overlay (PNG trong suốt)
    overlay = Image.open(img_person_path)
    overlay = overlay.resize((int(1920 * 0.8), int(1080 * 0.8)))
    overlay2 = Image.open('./public/bar-2.png')

    # Đảm bảo ảnh overlay có kênh alpha
    if overlay.mode != 'RGBA':
        overlay = overlay.convert('RGBA')

    # Tính toán vị trí để đặt ảnh nền chính vào giữa ảnh nền phụ
    bg2_w, bg2_h = background_2.size

    # Dán ảnh overlay lên ảnh nền chính
    background_2.paste(overlay, (0, 250), overlay)
    background_2.paste(overlay2, (0, 0), overlay2)
    
       # Thêm văn bản vào ảnh
    draw = ImageDraw.Draw(background_2)
    font = ImageFont.truetype("./fonts/arial/arial.ttf", 55)  # Đặt font và kích thước font
    max_width = 1350
    lines = []

    # Tách văn bản thành các dòng có độ dài tối đa là 1000 pixel
    words = text.split()
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = bbox[2] - bbox[0]
        if test_width <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    # Tính tổng chiều cao của tất cả các dòng văn bản
    total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines) + (len(lines) - 1) * 5

    # Tính toán vị trí y ban đầu để căn giữa theo chiều dọc
    box_height = 380
    y_text_start = bg2_h - box_height + (box_height - total_text_height) // 2

    # Vẽ các dòng văn bản vào ảnh
    x_text = 480  # Khoảng cách từ trái sang
    y_text = y_text_start

    for line in lines:  # Vẽ từ trên xuống dưới
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        # Vẽ văn bản nhiều lần để làm đậm chữ
        for offset in [
            (0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1),
            (2, 0), (0, 2), (2, 2), (-2, 0), (0, -2), (-2, -2), (2, -2), (-2, 2)
        ]:
            draw.text((x_text + offset[0], y_text + offset[1]), line, font=font, fill="white")
        y_text += int(line_height * 1.8)

    # Lưu ảnh draf 
    background_2.save(draf_path)

    # lưu ảnh với bg 
    jpg_image = Image.open(draf_path)  
    png_image = Image.open('./public/bg/bg-2.png')
    png_image = png_image.convert("RGBA")
    jpg_image.paste(png_image, (0, 0), png_image)
    jpg_image.save(out_path)

def generate_to_voice_edge(content: str, output_path: str, voice: str = "en-US-AriaNeural", rate="+5%", pitch="-5Hz", chunk_size=500):
    def split_text_by_dot(text, max_length):
        sentences = text.split(".")
        chunks = []
        current = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if len(current) + len(sentence) + 1 <= max_length:
                current += sentence + ". "
            else:
                chunks.append(current.strip())
                current = sentence + ". "
        if current:
            chunks.append(current.strip())
        return chunks

    async def _run():
        temp_dir = "__temp_voice_edge__"
        os.makedirs(temp_dir, exist_ok=True)
        temp_files = []

        chunks = split_text_by_dot(content, chunk_size)

        for i, chunk in enumerate(tqdm(chunks, desc="TTS Chunks")):
            file_path = os.path.join(temp_dir, f"chunk_{i}_{uuid.uuid4().hex}.mp3")
            tts = edge_tts.Communicate(text=chunk, voice=voice, rate=rate, pitch=pitch)
            await tts.save(file_path)
            temp_files.append(file_path)

        # Tạo concat list
        concat_path = os.path.join(temp_dir, "concat.txt")
        with open(concat_path, "w", encoding="utf-8") as f:
            for file in temp_files:
                f.write(f"file '{os.path.abspath(file).replace('\\', '/')}'\n")

        print("🔊 Merging audio files...")
        process = subprocess.Popen(
            [
                "ffmpeg", "-f", "concat", "-safe", "0",
                "-i", concat_path,
                "-c:a", "aac", "-b:a", "192k", "-y", output_path
            ],
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        for line in tqdm(process.stderr, desc="Merging", unit="line"):
            pass

        process.wait()

        # Cleanup
        for file in temp_files + [concat_path]:
            try: os.remove(file)
            except: pass
        try: os.rmdir(temp_dir)
        except: pass

        print(f"✅ Done! Saved to {output_path}")

    asyncio.run(_run())

# concat video by ffmpeg ----------------------------------------------
def add_thumbnail_to_video(input_video, input_image, output_image, output_video):
    # Kích thước mong muốn
    width = 177
    height = 85
    bottom_margin = 40
    right_margin = 27
    
    img = Image.open(input_image)
    img = img.resize((width, height))
    img.save(output_image)

    # Lệnh ffmpeg
    cmd = [
        "ffmpeg",
        "-i", input_video,
        "-i", output_image,
        "-filter_complex",
        f"[0:v][1:v]overlay=W-w-{right_margin}:H-h-{bottom_margin}",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "28",
        "-c:a", "copy",
        output_video
    ]

    subprocess.run(cmd, check=True)
    
def concat_content_videos_ffmpeg(intro_path, short_link_path, short_link_out_path, audio_out_path, video_path_list, out_path, draf_out_path, draf_out_path_2, draf_out_path_3):
    if short_link_path is not None:
        print('tạo thumb trong ad')
        add_thumbnail_to_video(short_link_path, './videos/thumbnail.jpg', './videos/thumbnail-tiny.jpg', short_link_out_path)
        
    # Load âm thanh
    audio_duration = get_media_duration(audio_out_path)
    duration_video = 0
    index = 0
    video_path_list_concat = []


    while duration_video < audio_duration:
        video_path_list_concat.append(video_path_list[index])
        video_duration = get_media_duration(video_path_list[index])
        print(video_path_list[index])
        print(video_duration)
        duration_video += video_duration
        if(index + 1 == video_path_list.__len__()):
            index = 0
        else:
            index += 1

    # Tạo file danh sách tạm thời
    list_file = "video_list.txt"
    
    with open(list_file, "w", encoding="utf-8") as f:
        for path in video_path_list_concat:
            f.write(f"file '{os.path.abspath(path)}'\n")

    # nối các video lại với nhau
    command = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        draf_out_path,
        "-progress", "-",
        "-nostats"
    ]

    # Chạy và hiển thị tiến trình
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        line = line.strip()
        if line.startswith("frame=") or "out_time=" in line or "progress=" in line:
            print(line)

    process.wait()

    # cắt đúng duration và gắn âm thanh
    import_audio_to_video(draf_out_path, draf_out_path_2, audio_out_path, audio_duration)
    normalize_video(draf_out_path_2, draf_out_path_3)

    # nối intro với video
    with open(list_file, "w", encoding="utf-8") as f:
        f.write(f"file '{os.path.abspath(intro_path)}'\n")
        if short_link_path is not None:
            f.write(f"file '{os.path.abspath(short_link_out_path)}'\n")
        f.write(f"file '{os.path.abspath(draf_out_path_3)}'\n")

    command = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        out_path,
        "-progress", "-",
        "-nostats"
    ]

    subprocess.run(command)
    os.remove(list_file)

# concat video by moviepy ------------------------------------------------
def concat_content_videos_moviepy(audio_path, video_path_list, out_path):
    # Load âm thanh
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    # intro video
    intro = VideoFileClip('./public/intro.mp4')
    intro_audio = AudioFileClip('./public/intro.mp4')
    intro = intro.resized((1920, 1080))
    intro_duration =  intro.duration
    final_duration = audio_duration + intro_duration

    duration_video = 0
    index = 0
    videos = [intro]

    bg_mobile_img = Image.open('./public/bg/bg-mobile-1.png').convert("RGBA")
    bg_mobile_array = np.array(bg_mobile_img)
    bg_mobile = ImageClip(bg_mobile_array, duration= 5, is_mask = False, transparent = True)  # Không cố định thời gian ở đây
    bg_mobile = bg_mobile.with_position((0, -700))
 
    bg_mobile = bg_mobile.with_duration(intro.duration)

    while duration_video < final_duration:
        video = VideoFileClip(video_path_list[index])
        if(duration_video + video.duration > final_duration):
            duration_end_video =  duration_video + video.duration - final_duration
            video = video.subclipped(0, duration_end_video)
            duration_video += duration_end_video
        else:
            duration_video += video.duration
        videos.append(video)
        if(index + 1 == video_path_list.__len__()):
            index = 0
        else:
            index += 1

    # Nối video lại với nhau
    final_video = concatenate_videoclips(videos).subclipped(0, final_duration)
    # Ghép video và âm thanh lại với nhau
    final_video = final_video.with_audio(concatenate_audioclips([intro_audio, audio]))
    final_video.write_videofile(out_path)
    final_video.close()

# -------------------------------------------------------------------

def normalize_video(input_path, output_path):
    command = [
        "ffmpeg", "-y",
        "-threads", "1",                  # Chỉ dùng 1 CPU
        "-i", input_path,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "32",                    # Tăng CRF để giảm dung lượng + RAM
        "-c:a", "aac",
        "-b:a", "96k",                   # Bitrate âm thanh thấp hơn nữa
        "-ar", "22050",                  # Giảm sample rate âm thanh
        "-ac", "1",                      # Mono
        "-movflags", "+faststart",
        output_path
    ]
    subprocess.run(command)

def get_media_duration(audio_path):
    result = subprocess.run(
        ["ffmpeg", "-i", audio_path],
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        text=True
    )
    match = re.search(r'Duration: (\d+):(\d+):([\d.]+)', result.stderr)
    if match:
        hours, minutes, seconds = match.groups()
        duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        return duration
    return 0

def write_lines_to_file(filepath, contents):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for line in contents:
            f.write(line.rstrip() + "\n")  # đảm bảo mỗi dòng kết thúc bằng \n

def upload_yt( user_data_dir, title, description, tags, video_path, video_thumbnail, comment = None):
    ### dùng để tạo ra 1 user
    # chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    # user_data_dir = "C:/Path/To/Chrome/news-us"
    # subprocess.Popen([chrome_path, f'--remote-debugging-port=9223', f'--user-data-dir={user_data_dir}'])
    # time.sleep(5)

    # Tạo đối tượng ChromeOptions
    chrome_options = Options()
    
    # Chỉ định đường dẫn đến thư mục user data
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    user_data_dir_abspath = os.path.abspath(user_data_dir)
    chrome_options.add_argument(f"user-data-dir={user_data_dir_abspath}")
    chrome_options.add_argument("profile-directory=Default")  # Nếu bạn muốn sử dụng profile mặc định
    # chrome_options.add_argument("--headless")  # Chạy trong chế độ không giao diện
    # chrome_options.add_argument("--disable-gpu")  # Tắt GPU (thường dùng trong môi trường máy chủ)

    # Sử dụng Service để chỉ định ChromeDriver
    service = Service(ChromeDriverManager().install())

    # Khởi tạo WebDriver với các tùy chọn
    browser = webdriver.Chrome(service=service, options=chrome_options)

    browser.get("https://studio.youtube.com/")
    # await browser load end
    element = WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.XPATH, '//ytcp-button[@icon="yt-sys-icons:video_call"]'))
    )
    element.click()
    time.sleep(1)


    WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.ID, 'text-item-0'))
    )

    browser.find_element(By.ID, 'text-item-0').click()
    time.sleep(10)
    
    # upload video
    print('upload video in youtube')
    WebDriverWait(browser, 100).until(
        lambda d: len(d.find_elements(By.TAG_NAME, 'input')) > 1  # Đảm bảo có ít nhất 2 input
    )
    
    file_input = browser.find_elements(By.TAG_NAME, 'input')[1]
    file_input.send_keys(video_path)
    time.sleep(3)


    # upload thumbnail
    print('upload thumbnail in youtube')
    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.ID, 'file-loader'))
    )
    thumbnail_input = browser.find_element(By.ID, 'file-loader')
    thumbnail_input.send_keys(video_thumbnail)
    time.sleep(3)


    # enter title
    print('nhập title in youtube')
    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.ID, 'textbox'))
    )
    
    title_input = browser.find_element(By.ID, 'textbox')
    
    
    check_clean_title = False
    while check_clean_title is False:
        # Xoá bằng Ctrl+A + Delete
        title_input.send_keys(Keys.CONTROL, "a")
        title_input.send_keys(Keys.DELETE)
        title_input.clear()
        time.sleep(1)
        if title_input.text.strip() == "":
            check_clean_title = True
            
    time.sleep(1)
    title_input.send_keys(title)
    time.sleep(1)

    # enter description
    print('nhập description in youtube')
    des_input = browser.find_elements(By.ID, 'textbox')[1]
    des_input.clear()
    time.sleep(1)
    # Copy vào clipboard
    pyperclip.copy(description)
    des_input.click()
    time.sleep(1)
    des_input.send_keys(Keys.CONTROL, 'v')
    time.sleep(1)

    # enter hiển thị thêm
    # Đợi cho phần tử scrollable-content xuất hiện
    scrollable_element = WebDriverWait(browser, 100).until(
        EC.presence_of_element_located((By.ID, "scrollable-content"))
    )
    # Scroll xuống cuối cùng của phần tử scrollable-content
    browser.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable_element)
    time.sleep(2)

    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.ID, 'toggle-button'))
    )
    show_more_btn = browser.find_element(By.ID, 'toggle-button')
    show_more_btn.click()
    time.sleep(2)
    

    # enter tags
    print('nhập tags in youtube')
    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.ID, 'text-input'))
    )
    tags_input = browser.find_element(By.ID, 'text-input')
    tags_input.send_keys(tags)
    time.sleep(2)

    # next btn
    browser.find_element(By.ID, 'next-button').click()
    time.sleep(10)

    # # add end screens
    # WebDriverWait(browser, 10).until(
    #     EC.presence_of_all_elements_located((By.ID, 'endscreens-button'))
    # )
    # browser.find_element(By.ID, 'endscreens-button').click()
    # time.sleep(2)
    # canvas_element = WebDriverWait(browser, 10).until(
    #     EC.element_to_be_clickable((By.TAG_NAME, "canvas"))
    # )
    # browser.execute_script("arguments[0].click();", canvas_element)
    # time.sleep(2)
    # browser.find_element(By.ID, 'save-button').click()
    # time.sleep(4)

    # next
    WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.ID, 'next-button'))
    )
    browser.find_element(By.ID, 'next-button').click()
    time.sleep(2)

    while True:
        element = browser.find_elements(By.XPATH, '//*[@check-status="UPLOAD_CHECKS_DATA_COPYRIGHT_STATUS_COMPLETED" or @check-status="UPLOAD_CHECKS_DATA_COPYRIGHT_STATUS_STARTED"]')
        
        if element:
            break  # Thoát vòng lặp nếu tìm thấy

        print("Chưa tìm thấy, tiếp tục kiểm tra...")
        time.sleep(2)  # Đợi 2 giây trước khi kiểm tra lại

    browser.find_element(By.ID, 'next-button').click()
    time.sleep(2)


    # done
    print('upload video in youtube thành công')
    WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.ID, 'done-button'))
    )
    browser.find_element(By.ID, 'done-button').click()

    # vào youtube để nhập bình luận
    if comment is not None:
        WebDriverWait(browser, 100).until(
            EC.presence_of_all_elements_located((By.ID, 'share-url'))
        )
        link_redirect = browser.find_element(By.ID, 'share-url')
        href = link_redirect.get_attribute('href')
        browser.get(href)
        WebDriverWait(browser, 100).until(
            EC.presence_of_all_elements_located((By.ID, 'above-the-fold'))
        )
        time.sleep(5)
        is_Find_comment = False
        while  is_Find_comment is False:
            try:
                browser.execute_script("window.scrollBy(0, 50);")
                time.sleep(1)
                comment_box = browser.find_element(By.ID, 'simplebox-placeholder')
                if(comment_box):
                    is_Find_comment = True
                time.sleep(3)
            except:
                time.sleep(3)

        comment_box = browser.find_element(By.ID, 'simplebox-placeholder')
        comment_box.click()
        textarea = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#contenteditable-root[contenteditable='true']"))
        )
        pyperclip.copy(comment)
        textarea.click()
        time.sleep(1)
        textarea.send_keys(Keys.CONTROL, 'v')
        time.sleep(2)
        submit_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "submit-button"))
        )
        submit_button.click()

    time.sleep(10)
    WebDriverWait(browser, 100).until(
            EC.presence_of_all_elements_located((By.ID, 'share-url'))
        )
    browser.quit()


def download_file_from_vps(host, username, password, remote_path, local_path, port = 22):
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)

    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.get(remote_path, local_path)

    sftp.close()
    transport.close()
    print(f"✅ Tải file thành công: {remote_path} → {local_path}")

def delete_remote_folder_vps(host, username, password, folder_path, port=22):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, username=username, password=password, port=port)

        # Lệnh xóa thư mục
        command = f"rm -rf '{folder_path}'"
        stdin, stdout, stderr = ssh.exec_command(command)

        error = stderr.read().decode()
        if error:
            print(f"❌ Lỗi khi xóa thư mục: {error}")
        else:
            print(f"🗑️ Đã xóa thư mục thành công: {folder_path}")

        ssh.close()
    except Exception as e:
        print(f"❌ Lỗi khi kết nối SSH hoặc xóa thư mục: {e}")

def check_file_exists_on_vps(host, username, password, remote_path, port=22):
    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        sftp.stat(remote_path)  # Gây lỗi nếu file không tồn tại

        sftp.close()
        transport.close()
        print(f"✅ File tồn tại: {remote_path}")
        return True
    except FileNotFoundError:
        print(f"❌ File không tồn tại: {remote_path}")
        return False
    except Exception as e:
        print(f"⚠️ Lỗi kiểm tra file: {e}")
        return False
    

def generate_thumbnail_moviepy_c2(img_path, img_blur_path, img_person_path, draf_path, out_path, text):
    text = text.upper()
    # Mở ảnh thứ nhất (ảnh nền chính)
    background = Image.open(img_path)
    bg_w, bg_h = background.size
    percent = ((1920 - 60) / bg_w) if ((1920 - 60) / bg_w) * bg_h < 1020 else (1020 / bg_h)
    background = background.resize((int(bg_w * percent),int(bg_h * percent)))

    # Mở ảnh thứ hai (ảnh nền phụ) và thay đổi kích thước
    background_2 = Image.open(img_blur_path)
    background_2 = background_2.resize((1920, 1080))

    overlay = None
    # Mở ảnh overlay (PNG trong suốt)
    if img_person_path is not None:
        overlay = Image.open(img_person_path)
        overlay = overlay.resize((int(1920 * 0.8), int(1080 * 0.8)))
    overlay2 = Image.open('./public/bar-2.png')

    # Đảm bảo ảnh overlay có kênh alpha
    if img_person_path is not None and overlay.mode != 'RGBA':
        overlay = overlay.convert('RGBA')

    # Tính toán vị trí để đặt ảnh nền chính vào giữa ảnh nền phụ
    bg2_w, bg2_h = background_2.size
    x = (bg2_w - int(bg_w * percent)) // 2
    y = (bg2_h - int(bg_h * percent)) // 2

    # Dán ảnh nền chính vào giữa ảnh nền phụ
    background_2.paste(background, (x, y))

    # Dán ảnh overlay lên ảnh nền chính
    if img_person_path is not None:
        background_2.paste(overlay, (0, 250), overlay)
    background_2.paste(overlay2, (0, 0), overlay2)
    
       # Thêm văn bản vào ảnh
    draw = ImageDraw.Draw(background_2)
    font = ImageFont.truetype("./fonts/arial/arial.ttf", 55)  # Đặt font và kích thước font
    max_width = 1350
    lines = []

    # Tách văn bản thành các dòng có độ dài tối đa là 1000 pixel
    words = text.split()
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = bbox[2] - bbox[0]
        if test_width <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    # Tính tổng chiều cao của tất cả các dòng văn bản
    total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines) + (len(lines) - 1) * 5

    # Tính toán vị trí y ban đầu để căn giữa theo chiều dọc
    box_height = 380
    y_text_start = bg2_h - box_height + (box_height - total_text_height) // 2

    # Vẽ các dòng văn bản vào ảnh
    x_text = 480  # Khoảng cách từ trái sang
    y_text = y_text_start

    for line in lines:  # Vẽ từ trên xuống dưới
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        # Vẽ văn bản nhiều lần để làm đậm chữ
        for offset in [
    (0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1),
    (2, 0), (0, 2), (2, 2), (-2, 0), (0, -2), (-2, -2), (2, -2), (-2, 2)
]:
            draw.text((x_text + offset[0], y_text + offset[1]), line, font=font, fill="white")
        y_text += int(line_height * 1.8)

    # Lưu ảnh draf 
    background_2.save(draf_path)

    # lưu ảnh với bg 
    jpg_image = Image.open(draf_path)  
    png_image = Image.open('./public/bg/bg-2.png')
    png_image = png_image.convert("RGBA")
    jpg_image.paste(png_image, (0, 0), png_image)
    jpg_image.save(out_path)


def open_chrome_to_edit(name_chrome_yt, driver_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"):
    user_data_dir = os.path.abspath(f"./youtubes/{name_chrome_yt}")
    process = subprocess.Popen([driver_path, f'--remote-debugging-port=9223', f'--user-data-dir={user_data_dir}'])
    input('nhấn bất kì để đóng chrome:')
    process.terminate()  # gửi tín hiệu terminate
    try:
        process.wait(timeout=30)  # đợi chrome tắt
    except subprocess.TimeoutExpired:
        process.kill()  # nếu không tắt thì kill hẳn là sao không hiểu

def check_identity_verification(name_chrome_yt):
    try:
        video_path = os.path.abspath(f"./public/kokoro.mp4"),
        thumb_path = os.path.abspath(f"./public/bg/bg-2.png"),
        user_data_dir = os.path.abspath(f"./youtubes/{name_chrome_yt}")
        
        # Tạo đối tượng ChromeOptions
        chrome_options = Options()
        
        # Chỉ định đường dẫn đến thư mục user data
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        user_data_dir_abspath = os.path.abspath(user_data_dir)
        chrome_options.add_argument(f"user-data-dir={user_data_dir_abspath}")
        chrome_options.add_argument("profile-directory=Default")  # Nếu bạn muốn sử dụng profile mặc định
        # chrome_options.add_argument("--headless")  # Chạy trong chế độ không giao diện
        # chrome_options.add_argument("--disable-gpu")  # Tắt GPU (thường dùng trong môi trường máy chủ)

        # Sử dụng Service để chỉ định ChromeDriver
        service = Service(ChromeDriverManager().install())


        # Khởi tạo WebDriver với các tùy chọn
        browser = webdriver.Chrome(service=service, options=chrome_options)

        browser.get("https://studio.youtube.com/")
        # await browser load end
        element = WebDriverWait(browser, 100).until(
            EC.element_to_be_clickable((By.XPATH, '//ytcp-button[@icon="yt-sys-icons:video_call"]'))
        )
        element.click()
        time.sleep(1)

        WebDriverWait(browser, 100).until(
            EC.element_to_be_clickable((By.ID, 'text-item-0'))
        )
            
        browser.find_element(By.ID, 'text-item-0').click()
        time.sleep(10)

        # upload video
        print('upload video in youtube')
        # chờ tối đa 100 giây cho ít nhất 2 input xuất hiện
        WebDriverWait(browser, 100).until(
            lambda d: d.find_elements(By.TAG_NAME, 'input') if len(d.find_elements(By.TAG_NAME, 'input')) > 1 else False
        )
        file_input = browser.find_elements(By.TAG_NAME, 'input')[1]
        file_input.send_keys(video_path)
        time.sleep(3)


        # upload thumbnail
        print('upload thumbnail in youtube')
        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'file-loader'))
        )
        thumbnail_input = browser.find_element(By.ID, 'file-loader')
        thumbnail_input.send_keys(thumb_path)
        time.sleep(3)
    except:
        print('error')
    
    input('nhấn bất kì để đóng chrome:')
    browser.quit()
    

def get_link_in_sitemap(data):
    # tải sitemap
    response = requests.get(data['link'])
    response.raise_for_status()  # báo lỗi nếu request fail

    # parse xml
    root = ET.fromstring(response.content)

    # namespace trong file XML (thường có trong <urlset>)
    namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    # lấy toàn bộ <loc>
    links = [{'link': loc.text, 'name': data['name']} for loc in root.findall(".//ns:loc", namespace)]
    return links

def get_links_get_content():
    data = get_all_sitemap_links(True)
    all_links = []
    for sitemap_url in data:
        links = get_link_in_sitemap(sitemap_url)
        all_links.append(links)
    
    merged = []
    for group in zip_longest(*all_links):  # group sẽ là tuple (link1_site1, link1_site2, link1_site3, ...)
        for link in group:
            if link:  # tránh None khi list ngắn hơn
                merged.append(link)
    return merged

def clear_cache_chrome(yt_path):
    paths = ['/Default/Cache', '/Default/GPUCache', '/ShaderCache', '/Default/Code Cache', '/GrShaderCache']
    for item in paths:
        try:
            shutil.rmtree(f'{yt_path}{item}')
            print(f'đã xóa cache {item}')
        except:
            print(f'Đã xóa folder hoặc không tồn tại folder {item}')
    