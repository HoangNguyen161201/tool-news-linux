import shutil
import os
from untils import generate_title_description_improved, generate_video_by_image, get_all_link_in_theguardian_new, get_info_new
from untils import concat_content_videos, get_img_gif_person, get_info_new, generate_image, generate_content_improved
from untils import generate_to_voice_edge, generate_thumbnail, generate_image_and_video_aff_and_get_three_item
from db import check_link_exists, connect_db, insert_link, get_all_links, delete_link 
import random
from concurrent.futures import ProcessPoolExecutor, wait
from slugify import slugify

def main():
    current_link = None
    try:
        # tạo folder để chứa video
        path_folder = f'./videos'
        try:
            shutil.rmtree(path_folder)
        except:
            print('next')
        
        os.makedirs(path_folder)
        # lấy tất cả link tin tức
        link_news = get_all_link_in_theguardian_new()
        
        # kết nối db và kiểm tra có link tồn tại chưa, chưa thì lấy và làm video
        connect_db()
        for link in link_news:
            if not check_link_exists(f'https://www.theguardian.com/{link}'):
                current_link = link
                break

        # nếu không có link thì bắn lỗi
        if (current_link is None):
            raise Exception("Lỗi xảy ra, không tồn tại link hoặc đã hết tin tức")

        current_link = f'https://www.theguardian.com/{current_link}'
        print(current_link)

        # lấy thông tin của video
        new_info = get_info_new(current_link)

        # lấy ngẫu nhiên đường dẫn hình ảnh và hình động người thuyết trình
        person_info = get_img_gif_person()
        
        # tạo ra image gốc và image mờ, sau đó tạo ra video từng phần
        path_videos = []
        print(current_link)
        if(new_info is None):
            raise Exception("Lỗi xảy ra, không có thông tin của content")
        for key, item in enumerate(new_info['picture_links']):
            img_path = f"{path_folder}/image-{key}.jpg"
            img_blur_path = f"{path_folder}/image-blur-{key}.jpg"
            generate_image(item, img_path, img_blur_path)
            random_number = random.randint(5, 10)
            generate_video_by_image(
                img_path,
                f'{path_folder}/video-{key}.mkv',
                random_number
            )
            path_videos.append(f"{path_folder}/video-{key}.mkv")
            
        products = generate_image_and_video_aff_and_get_three_item()
        if(products is None):
            raise Exception("Lỗi xảy ra, không thể tạo và lấy ra 3 product ngẫu nhiên")

        # chuyển đổi title và description lại, tạo mới lại content
        with ProcessPoolExecutor() as executor:
            future1 = executor.submit(generate_title_description_improved, new_info['title'], new_info['description'])
            future2 = executor.submit(generate_content_improved, new_info['content'], new_info['title'])

            wait([future1, future2])

            result1 = future1.result()
            result2 = future2.result()

            # Gán lại kết quả vào new_info
            new_info['title'] = result1['title']
            new_info['description'] = result1['description']
            new_info['content'] = result2
            new_info['title_slug'] = slugify(new_info['title'])

        print(new_info)
        # tạo thumbnail video
        generate_thumbnail(
            f"{path_folder}/image-0.jpg",
            person_info['person_img_path'],
            f"{path_folder}/draf-thumbnail.jpg",
            f"{path_folder}/thumbnail.jpg",
            new_info['title'].replace('*', '')
        )

        # tạo âm thanh video
        print('generate voice-----------------')
        generate_to_voice_edge(new_info['content'], f"{path_folder}/content-voice.aac")

        concat_content_videos(
            './public/intro_ffmpeg.mp4',
            f'./pic_affs/aff.mp4',
            f"{path_folder}/content-voice.aac",
            path_videos,
            f'{path_folder}/{new_info['title_slug']}.mkv',
            f'{path_folder}/draf.mkv',
            f'{path_folder}/draf2.mkv',
        )
        
    except Exception as e:
        print(current_link)
        print(f'loi xay ra: {e}')  

if __name__ == "__main__":
    main()