import shutil
import os
from untils import write_lines_to_file, generate_title_description_improved, generate_video_by_image, get_all_link_in_theguardian_new, get_info_new
from untils import concat_content_videos, get_img_gif_person, generate_image, generate_content_improved
from untils import generate_to_voice_edge, generate_thumbnail, generate_image_and_video_aff_and_get_three_item
from db import check_link_exists, insert_link
import random
from concurrent.futures import ThreadPoolExecutor, wait
from slugify import slugify
import time

def create_video_by_image(path_folder, key, link):
    img_path = f"{path_folder}/image-{key}.jpg"
    img_blur_path = f"{path_folder}/image-blur-{key}.jpg"
    generate_image(link, img_path, img_blur_path)
    random_number = random.randint(5, 10)
    generate_video_by_image(
        img_path,
        f'{path_folder}/video-{key}.mkv',
        random_number
    )
    return f"{path_folder}/video-{key}.mkv"

def main():
    while True:
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
        link_news = get_all_link_in_theguardian_new()

        # kiểm tra link nào chưa xử lý
        for link in link_news:
            full_link = f'https://www.theguardian.com{link}'
            if not check_link_exists(full_link):
                current_link = full_link
                break

        print(current_link)
        if current_link is None:
            raise Exception("Lỗi xảy ra, không tồn tại link hoặc đã hết tin tức")

        # lấy thông tin tin tức
        new_info = get_info_new(current_link)
        if new_info is None:
            raise Exception("Lỗi xảy ra, không có thông tin của content")

        # ảnh người thuyết trình
        person_info = get_img_gif_person()
        
        path_videos = []
        products = None

        # chạy song song các task: xử lý title/desc, content, ảnh aff, video từng ảnh
        with ThreadPoolExecutor(max_workers=6) as executor:
            future1 = executor.submit(generate_title_description_improved, new_info['title'], new_info['description'])
            future2 = executor.submit(generate_content_improved, new_info['content'], new_info['title'])
            future3 = executor.submit(generate_image_and_video_aff_and_get_three_item)
            future_videos = [
                executor.submit(create_video_by_image, path_folder, key, link)
                for key, link in enumerate(new_info['picture_links'])
            ]

            wait([future1, future2, future3] + future_videos)

            result1 = future1.result()
            result2 = future2.result()
            products = future3.result()

            for fut in future_videos:
                path_videos.append(fut.result())

            # cập nhật nội dung mới vào new_info
            new_info['title'] = result1['title']
            new_info['description'] = result1['description']
            new_info['content'] = result2
            new_info['title_slug'] = slugify(new_info['title'])

        if products is None:
            raise Exception("Lỗi xảy ra, không thể tạo và lấy ra 3 product ngẫu nhiên")

        print(new_info)

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
                f"{path_folder}/content-voice.aac"
            )

            future3 = executor.submit(
                write_lines_to_file,
                f"{path_folder}/result.txt",
                [
                    new_info['title'],
                    f"news,{new_info['tags']},breaking news,current events,",
                    f"{new_info['description']}\n\n(tags):\n{', '.join(new_info['tags'].split(','))}"
                ]
            )

            future1.result()
            future2.result()
            future3.result()

        # nối video final
        concat_content_videos(
            './public/intro.mkv',
            './pic_affs/aff.mkv',
            f"{path_folder}/aff.mkv",
            f"{path_folder}/content-voice.aac",
            path_videos,
            f"{path_folder}/result.mkv",
            f"{path_folder}/draf.mkv",
            f"{path_folder}/draf2.mkv",
            f"{path_folder}/draf3.mkv",
        )

        end_time = time.time()
        print(f"Thời gian chạy: {end_time - start_time:.2f} giây")
        insert_link(current_link)  # Mở lại khi cần lưu vào DB
        # chờ cho đến khi file bị xoá thủ công để tiếp tục
        while os.path.exists(f"{path_folder}/result.mkv"):
            print('Đợi xóa file result.mp4...')
            time.sleep(5)
        print('Tiếp tục...')

if __name__ == "__main__":
    main()