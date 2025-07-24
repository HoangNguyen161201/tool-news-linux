import requests
import os
from bs4 import BeautifulSoup
import random
from data import gif_paths, person_img_paths, gemini_keys

import cv2
import subprocess
from tqdm import tqdm
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import shutil
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import re
from moviepy import AudioFileClip, concatenate_audioclips
import google.generativeai as genai

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


def generate_video_by_image( in_path, out_path, second):
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

def import_audio_to_video(in_path, out_path, audio_duration, audio_path):
    command = [
        "ffmpeg", "-y",
        "-i", in_path,               # Đường dẫn video đầu vào
        "-i", audio_path,            # Đường dẫn âm thanh đầu vào
        "-t", str(audio_duration),   # Đặt thời gian cho video theo độ dài âm thanh
        "-filter:v", "scale=1920:1080,fps=30",  # Bộ lọc video
        "-c:v", "libx264",           # Sử dụng codec video h.264
        "-c:a", "aac",               # Sử dụng codec âm thanh AAC
        "-b:a", "192k",              # Cài đặt bitrate âm thanh
        "-preset", "fast",           # Cài đặt preset nhanh
        "-map", "0:v:0",             # Chỉ định video từ stream đầu tiên (video)
        "-map", "1:a:0",             # Chỉ định audio từ stream thứ hai (audio)
        out_path                     # Đường dẫn đầu ra
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
        audio = AudioFileClip('./public/aff.aac')

        generate_video_by_image(
                        f'{path_folder}/pic_result.png',
                        f'{path_folder}/daft.mp4',
                        audio.duration
                    )

        import_audio_to_video(f'{path_folder}/daft.mp4', f'{path_folder}/aff.mp4', audio.duration,  './public/aff.aac')
        print(audio.duration)
        
        audio.close()
        print("✅ Done")

        return random_items
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def generate_content(content, model='gemini-1.5-flash', api_key= gemini_keys[0]):
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
def generate_content_improved(content, title):
    return generate_content(f'''
        Tôi có một bản tin mới. Hãy viết lại bằng tiếng Anh sao cho hấp dẫn, súc tích và phù hợp để đọc lên trong một video tin tức trên YouTube (voice-over). Nội dung cần được viết dưới dạng khách quan ở ngôi thứ ba, không dùng "I", "my", "we", hay bất kỳ đại từ ngôi thứ nhất nào.
        title là: {title},
        Nội dung là: {content}

        Yêu cầu:
        - độ dài ký tự bằng hoặc trên {content.__len__()} ký tự.
        - Viết thành một đoạn văn liền mạch, không chia cảnh, không dùng markdown, không có dấu *, **, hoặc [Scene:].
        - Phong cách giống người dẫn bản tin truyền hình, mang tính tường thuật khách quan nhưng thu hút, gây tò mò và khơi gợi cảm xúc.
        - Không thêm bất kỳ lời giải thích nào. Chỉ trả về nội dung đã viết lại.
        ''', api_key= gemini_keys[2])
        
        
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
