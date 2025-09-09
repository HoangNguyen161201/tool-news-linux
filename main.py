import shutil
import os
from untils import write_lines_to_file, generate_title_description_improved, generate_video_by_image_ffmpeg, get_all_link_in_theguardian_new
from untils import concat_content_videos_ffmpeg, concat_content_videos_moviepy, get_img_gif_person, generate_image_ffmpeg, generate_image_moviepy, generate_video_by_image_moviepy, generate_content_improved
from untils import generate_to_voice_edge, generate_thumbnail, generate_image_and_video_aff_and_get_three_item, generate_image_and_video_aff_and_get_three_item_amazon
from untils import get_func_Website_to_create
from db import check_link_exists, insert_link
import random
from concurrent.futures import ThreadPoolExecutor, wait
# from slugify import slugify
from django.utils.text import slugify
import time
from data import gemini_keys

def create_video_by_image(path_folder, key, link, is_moviepy = False, gif_path = None):
    img_path = f"{path_folder}/image-{key}.jpg"
    img_blur_path = f"{path_folder}/image-blur-{key}.jpg"
    
    if is_moviepy is False:    
        generate_image_ffmpeg(link, img_path, img_blur_path)
        random_number = random.randint(5, 10)
        generate_video_by_image_ffmpeg(
            img_path,
            f'{path_folder}/video-{key}.mkv',
            random_number
        )
        return f"{path_folder}/video-{key}.mkv"
    else:
        generate_image_moviepy(link, img_path, img_blur_path)
        random_number = random.randint(5, 10)
        generate_video_by_image_moviepy(
            1 if key % 2 == 0 else None,
            img_path,
            img_blur_path,
            f'{path_folder}/video-{key}.mp4',
            random_number,
            gif_path
        )
        return f"{path_folder}/video-{key}.mp4"

def main(is_moviepy = False):
    gemini_key_index = 0
    current_link = None
    while True:
        try:
            start_time = time.time()
            current_link = None
            
            # tạo folder để chứa video
            path_folder = './videos'
            try:
                shutil.rmtree(path_folder)
            except Exception:
                print('next')
            os.makedirs(path_folder)

            # lấy tất cả link tin tức
            website = get_func_Website_to_create()
            link_news = website['get_links']()

            # kiểm tra link nào chưa xử lý
            for link in link_news:
                if not check_link_exists(link):
                    current_link = link
                    break

            print(current_link)
            if current_link is None:
                raise Exception("Lỗi xảy ra, không tồn tại link hoặc đã hết tin tức")

            # lấy thông tin tin tức
            new_info = website['get_info'](current_link)
            if new_info is None:
                raise Exception("Lỗi xảy ra, không có thông tin của content")

            # ảnh người thuyết trình
            person_info = get_img_gif_person()
            
            path_videos = []
            products = None
            
            # chạy song song các task: xử lý title/desc, content, ảnh aff, video từng ảnh
            with ThreadPoolExecutor(max_workers=6) as executor:
                future1 = executor.submit(generate_title_description_improved, new_info['title'], new_info['description'], gemini_keys[gemini_key_index])
                future2 = executor.submit(generate_content_improved, new_info['content'], new_info['title'], gemini_keys[gemini_key_index])
                # future3 = executor.submit(generate_image_and_video_aff_and_get_three_item)
                # future3 = executor.submit(generate_image_and_video_aff_and_get_three_item_amazon)
                
                future_videos = [
                    executor.submit(create_video_by_image, path_folder, key, link, is_moviepy, person_info['person_gif_path'])
                    for key, link in enumerate(new_info['picture_links'])
                ]

                # wait([future1, future2, future3] + future_videos)
                wait([future1, future2] + future_videos )

                result1 = future1.result()
                result2 = future2.result()
                # products = future3.result()

                for fut in future_videos:
                    path_videos.append(fut.result())

                # cập nhật nội dung mới vào new_info
                new_info['title'] = result1['title']
                new_info['description'] = result1['description']
                new_info['content'] = result2
                new_info['title_slug'] = slugify(new_info['title'])
                

            # if products is None:
            #     raise Exception("Lỗi xảy ra, không thể tạo và lấy ra 3 product ngẫu nhiên")

            # tạo thumbnail, voice, file txt — vẫn song song nhưng nhẹ hơn
            with ThreadPoolExecutor(max_workers=3) as executor:
                future1 = executor.submit(
                    generate_thumbnail,
                    f"{path_folder}/image-0.jpg",
                    person_info['person_img_path'],
                    f"{path_folder}/draf-thumbnail.jpg",
                    f"{path_folder}/thumbnail.jpg",
                    new_info['title'].replace('*', '')
                )

                future2 = executor.submit(
                    generate_to_voice_edge,
                    new_info['content'],
                    f"{path_folder}/content-voice.aac",
                    'vi-VN-HoaiMyNeural'
                )

                future3 = executor.submit(
                    write_lines_to_file,
                    f"{path_folder}/result.txt",
                    [
                        new_info['title'],
                        f"news,{new_info['tags']},breaking news,current events,",
                        f"{new_info['description']}\n\n{products}\n\n(tags):\n{', '.join(new_info['tags'].split(','))}"
                    ]
                )

                future1.result()
                future2.result()
                future3.result()

            if is_moviepy is False:
                concat_content_videos_ffmpeg(
                    './public/intro.mkv',
                    # './pic_affs/aff.mkv',
                    None,
                    f"{path_folder}/aff.mkv",
                    f"{path_folder}/content-voice.aac",
                    path_videos,
                    f"{path_folder}/result.mkv",
                    f"{path_folder}/draf.mkv",
                    f"{path_folder}/draf2.mkv",
                    f"{path_folder}/draf3.mkv",
                )
            else:
                concat_content_videos_moviepy(f"{path_folder}/content-voice.aac", path_videos, f"{path_folder}/result.mp4")

            end_time = time.time()
            print(f"Thời gian chạy: {end_time - start_time:.2f} giây")
            insert_link(current_link)  # Mở lại khi cần lưu vào DB
            # chờ cho đến khi file bị xoá thủ công để tiếp tục
            while os.path.exists(f"{path_folder}/result.mkv"):
                print('Đợi xóa file result.mp4...')
                time.sleep(5)
            print('Tiếp tục...')
        except Exception as e:
            message = str(e)

            if "Lỗi xảy ra, không tồn tại link hoặc đã hết tin tức" in message:
                print(f"{message} → Đợi 20 phút rồi thử lại...")
                data = 5
                while data < 1200:
                    print('đợi 20 giây vì hết link')
                    time.sleep(5)
                    data += 5
            elif "Lỗi xảy ra, không có thông tin của content" in message:
                insert_link(current_link)
                print(f"Lỗi xảy ra, không có thông tin của content")
            else:
                print(f"[LỖI KHÁC] {message}")
                gemini_key_index += 1
                if gemini_key_index > 2:
                    gemini_key_index = 0
                time.sleep(60)

if __name__ == "__main__":
    main(True)