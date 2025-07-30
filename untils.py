import requests
import os
from bs4 import BeautifulSoup
import random
from data import gif_paths, person_img_paths, gemini_keys
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
        scale = min(max_width / w, max_height / h)
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


def generate_video_by_image( in_path, out_path, second):
    width, height = 1920, 1080
    duration = second
    os.makedirs('./temp', exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-framerate", "1", "-loop", "1", "-t", str(duration), "-i", in_path,
        "-framerate", "1", "-loop", "1", "-t", str(duration), "-i", './public/avatar.png',
        "-filter_complex",
        f"""
        [0:v]scale={width}:{height},setsar=1,setpts=PTS-STARTPTS[bg]; \
        [1:v]scale=200:200,format=rgba,colorchannelmixer=aa=0.7,setsar=1[avatar]; \
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

        generate_video_by_image(
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


def generate_content(content, model='gemini-2.0-flash-lite', api_key= gemini_keys[0]):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model)
    response = model.generate_content(content)
    return response.text

def generate_title_description_improved(title, description):
    while True:
        title_des = generate_content(f'''tôi đang có các thông tin như sau:
                                    - title: {title}
                                    - description: {description}
                                    hãy generate lại các thông tin trên cho tôi bằng tiếng anh sao cho hay và nổi bật, chuẩn seo youtube.
                                    Trả ra dưới định dạng như sau:
                                    Dòng 1: là title (trên 50 ký tự và không quá 100 ký tự, không được có dấu : trong title).
                                    Từ dòng thứ 2 trở đi: là description. 
                                    Trả ra kết quả cho tôi luôn, không cần phải giải thích hay ghi thêm gì hết.''',
                                    api_key= gemini_keys[2]
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
def generate_title_description_improved(title, description, gemini_key = gemini_keys[0]):
    while True:
        title_des = generate_content(f'''tôi đang có các thông tin như sau:
                                    - title: {title}
                                    - description: {description}
                                    hãy generate lại các thông tin trên cho tôi bằng tiếng anh sao cho hay và nổi bật, chuẩn seo youtube.
                                    Trả ra dưới định dạng như sau:
                                    Dòng 1: là title (trên 50 ký tự và không quá 100 ký tự, không được có dấu : trong title).
                                    Từ dòng thứ 2 trở đi: là description. 
                                    Trả ra kết quả cho tôi luôn, không cần phải giải thích hay ghi thêm gì hết.''',
                                    api_key= gemini_key
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
def generate_content_improved(content, title, gemini_key = gemini_keys[0]):
    return generate_content(f'''
        Tôi có một bản tin mới. Hãy viết lại bằng tiếng Anh sao cho hấp dẫn, súc tích và phù hợp để đọc lên trong một video tin tức trên YouTube (voice-over). Nội dung cần được viết dưới dạng khách quan ở ngôi thứ ba, không dùng "I", "my", "we", hay bất kỳ đại từ ngôi thứ nhất nào.
        title là: {title},
        Nội dung là: {content}

        Yêu cầu:
        - độ dài ký tự bằng hoặc trên {content.__len__()} ký tự.
        - Viết thành một đoạn văn liền mạch, không chia cảnh, không dùng markdown, không có dấu *, **, hoặc [Scene:].
        - Phong cách giống người dẫn bản tin truyền hình, mang tính tường thuật khách quan nhưng thu hút, gây tò mò và khơi gợi cảm xúc.
        - Không thêm bất kỳ lời giải thích nào. Chỉ trả về nội dung đã viết lại.
        ''', api_key= gemini_key)
        
        
def generate_thumbnail(img_path, img_person_path, draf_path, out_path, text):
    text = text.upper()

    # Mở ảnh thứ hai (ảnh nền phụ) và thay đổi kích thước
    background_2 = Image.open(img_path)
    background_2 = background_2.resize((1920, 1080))

    # Mở ảnh overlay (PNG trong suốt)
    overlay = Image.open(img_person_path)
    overlay = overlay.resize((int(1920 * 0.8), int(1080 * 0.8)))
    overlay2 = Image.open('./public/bar.png')

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
    png_image = Image.open('./public/bg/bg-1.png')
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

def concat_content_videos(intro_path, short_link_path, short_link_out_path, audio_out_path, video_path_list, out_path, draf_out_path, draf_out_path_2, draf_out_path_3):
    # Load âm thanh
    audio_duration = get_media_duration(audio_out_path)
    duration_video = 0
    index = 0
    video_path_list_concat = []


    while duration_video < audio_duration:
        video_path_list_concat.append(video_path_list[index])
        video_duration = get_media_duration(video_path_list[index])
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
    normalize_video(short_link_path, short_link_out_path)


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
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")
    chrome_options.add_argument("profile-directory=Default")  # Nếu bạn muốn sử dụng profile mặc định
    # chrome_options.add_argument("--headless")  # Chạy trong chế độ không giao diện
    # chrome_options.add_argument("--disable-gpu")  # Tắt GPU (thường dùng trong môi trường máy chủ)

    # Sử dụng Service để chỉ định ChromeDriver
    service = Service(ChromeDriverManager().install())


    # Khởi tạo WebDriver với các tùy chọn
    browser = webdriver.Chrome(service=service, options=chrome_options)

    browser.get("https://studio.youtube.com/")
    # await browser load end
    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.ID, 'create-icon'))
    )


    browser.find_element(By.ID, 'create-icon').click()
    time.sleep(1)

    browser.find_element(By.ID, 'text-item-0').click()
    time.sleep(10)

    # upload video
    print('upload video in youtube')
    file_input = browser.find_elements(By.TAG_NAME, 'input')[1]
    file_input.send_keys(video_path)
    time.sleep(3)


    # upload thumbnail
    print('upload thumbnail in youtube')
    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.ID, 'file-loader'))
    )
    thumbnail_input = browser.find_element(By.ID, 'file-loader')
    thumbnail_input.send_keys(video_thumbnail)
    time.sleep(3)


    # enter title
    print('nhập title in youtube')
    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.ID, 'textbox'))
    )
    title_input = browser.find_element(By.ID, 'textbox')
    title_input.clear()
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
    scrollable_element = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "scrollable-content"))
    )
    # Scroll xuống cuối cùng của phần tử scrollable-content
    browser.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable_element)
    time.sleep(2)

    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.ID, 'toggle-button'))
    )
    show_more_btn = browser.find_element(By.ID, 'toggle-button')
    show_more_btn.click()
    time.sleep(2)

    # enter tags
    print('nhập tags in youtube')
    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.ID, 'text-input'))
    )
    tags_input = browser.find_element(By.ID, 'text-input')
    tags_input.send_keys(tags)
    time.sleep(2)

    # next btn
    browser.find_element(By.ID, 'next-button').click()
    time.sleep(2)

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
    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.ID, 'next-button'))
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
    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.ID, 'done-button'))
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
    
