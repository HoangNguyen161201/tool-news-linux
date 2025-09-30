import shutil
import os
from untils import get_links_get_content, write_lines_to_file, generate_title_description_improved, generate_video_by_image_ffmpeg, get_all_link_in_theguardian_new
from untils import concat_content_videos_ffmpeg, concat_content_videos_moviepy, get_img_gif_person, generate_image_ffmpeg, generate_image_moviepy, generate_video_by_image_moviepy, generate_content, generate_content_improved
from untils import get_link_in_sitemap, upload_yt, generate_to_voice_edge, generate_thumbnail, generate_thumbnail_moviepy_c2, generate_image_and_video_aff_and_get_three_item, generate_image_and_video_aff_and_get_three_item_amazon
from untils import clear_cache_chrome, check_identity_verification, generate_image_cv2, generate_video_by_image_cv2, open_chrome_to_edit
from db_mongodb import get_all_models, insert_model, delete_model, update_time, insert_time, get_times, get_all_sitemap_links, insert_sitemap_link, delete_sitemap_link, get_func_to_get_info_new, check_link_exists, insert_link, check_authorization, check_not_exist_to_create_ip, find_one_ip, add_gemini_key_to_ip, remove_gemini_key_youtube_to_ip, update_driver_path_to_ip, add_youtube_to_ip, remove_youtube_to_ip
import random
from concurrent.futures import ThreadPoolExecutor, wait
# from slugify import slugify
from django.utils.text import slugify
import time
import shutil
from data import data_ad
import requests
from bs4 import BeautifulSoup

def create_video_by_image(path_folder, key, link, type_run_video = 'ffmpeg', gif_path = None, is_delete = False):
    img_path = f"{path_folder}/image-{key}.jpg"
    img_blur_path = f"{path_folder}/image-blur-{key}.jpg"
    
    if type_run_video == 'ffmpeg':    
        generate_image_ffmpeg(link, img_path, img_blur_path)
        random_number = random.randint(5, 10)
        generate_video_by_image_ffmpeg(
            img_path,
            f'{path_folder}/video-{key}.mkv',
            random_number
        )
        return f"{path_folder}/video-{key}.mkv"
    elif type_run_video == 'moviepy':
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
    elif type_run_video == 'cv2':
        generate_image_cv2(link, img_path, img_blur_path, 1920, 1080, 50)
        random_number = random.randint(5, 10)
        generate_video_by_image_cv2(
            1 if key % 2 == 0 else None,
            img_path,
            img_blur_path,
            f"{path_folder}/image-{key}.mkv",
            f"{path_folder}/image-blur-{key}.mkv",
            f'{path_folder}/video-{key}.mkv',
            random_number,
        )
        
        if is_delete:
            for file_path in [img_path, img_blur_path, f"{path_folder}/image-{key}.mkv", f"{path_folder}/image-blur-{key}.mkv"]:
                if os.path.exists(file_path):
                    os.remove(file_path)

        return f"{path_folder}/video-{key}.mkv"
    

def main(type_run_video = 'ffmpeg', is_not_run_parallel_create_child_video = False):
    index_youtube = 0
    gemini_key_index = 0
    gemini_model_index = 0
    current_link = None
    while True:
        # lấy data
        data_by_ip = find_one_ip()
        times = get_times()
        models = get_all_models()
        
        # check authorization
        is_authorization = check_authorization()
        if is_authorization is False or is_authorization is False:
            raise Exception("Lỗi xảy ra")
        
        try:
            start_time = time.time()
            current_link = None
            name = None
            
            # tạo folder để chứa video
            path_folder = './videos'
            try:
                shutil.rmtree(path_folder)
            except Exception:
                print('next')
            os.makedirs(path_folder)
            
            # clear cache chrome
            clear_cache_chrome(f"./youtubes/{data_by_ip['youtubes'][index_youtube]}")

            # lấy tất cả link tin tức
            links = get_links_get_content()
            
           
            for data_link in links:
                if not check_link_exists(data_link['link']):
                    current_link = data_link['link']
                    name = data_link['name']
                    insert_link(current_link)
                    break

            print(current_link, name)
            if current_link is None:
                raise Exception("Lỗi xảy ra, không tồn tại link hoặc đã hết tin tức")
            
            # lấy thông tin tin tức
            funcs = get_func_to_get_info_new()
            namespace = {}
            exec(funcs[0]['func'], globals(), namespace)                
            new_info = namespace['get_info_new'](current_link)
            if new_info is None:
                raise Exception("Lỗi xảy ra, không có thông tin của content")
            
            print(new_info)

            # ảnh người thuyết trình
            person_info = get_img_gif_person()
            
            path_videos = []
            products = None
            
            # not run parallel create child --------------------------------------------------------------------------------
            if is_not_run_parallel_create_child_video is True:
                for key, link in enumerate(new_info['picture_links']):
                    link_child_video = create_video_by_image(path_folder, key, link, type_run_video, person_info['person_gif_path'], True if key > 0 else False)
                    path_videos.append(link_child_video)
                    
            # chạy song song các task: xử lý title/desc, content, ảnh aff, video từng ảnh
            with ThreadPoolExecutor(max_workers=6) as executor:
                future1 = executor.submit(generate_title_description_improved, new_info['title'], new_info['description'], data_by_ip['geminiKeys'][gemini_key_index], models[gemini_model_index])
                future2 = executor.submit(generate_content_improved, new_info['content'], new_info['title'], data_by_ip['geminiKeys'][gemini_key_index],  models[gemini_model_index])
                # future3 = executor.submit(generate_image_and_video_aff_and_get_three_item)
                # future3 = executor.submit(generate_image_and_video_aff_and_get_three_item_amazon)
                
                # not run parallel create child -----------------------------------------------------------------------------
                future_videos = None if is_not_run_parallel_create_child_video is True else [
                    executor.submit(create_video_by_image, path_folder, key, link, type_run_video, person_info['person_gif_path'])
                    for key, link in enumerate(new_info['picture_links'])
                ]

                # wait([future1, future2, future3] + future_videos)
                wait(([future1, future2] + future_videos) if is_not_run_parallel_create_child_video is False else [future1, future2])

                result1 = future1.result()
                result2 = future2.result()
                # products = future3.result()

                if is_not_run_parallel_create_child_video is False:
                    for fut in future_videos:
                        path_videos.append(fut.result())

                # cập nhật nội dung mới vào new_info
                new_info['title'] = result1['title']
                new_info['description'] = result1['description']
                new_info['content'] = result2
                new_info['title_slug'] = slugify(new_info['title'])
                
            # if products is None:
            #     raise Exception("Lỗi xảy ra, không thể tạo và lấy ra 3 product ngẫu nhiên")
            
            # random ad
            index_ad = random.randint(0, 1)
            ad = data_ad[index_ad]
            
            # tạo thumbnail, voice, file txt — vẫn song song nhưng nhẹ hơn
            with ThreadPoolExecutor(max_workers=3) as executor:
                future1 = executor.submit(
                    generate_thumbnail,
                    f"{path_folder}/image-0.jpg",
                    person_info['person_img_path'],
                    f"{path_folder}/draf-thumbnail.jpg",
                    f"{path_folder}/thumbnail.jpg",
                    new_info['title'].replace('*', '')
                ) if type_run_video == 'ffmpeg' else executor.submit(
                    generate_thumbnail_moviepy_c2,
                    f"{path_folder}/image-0.jpg",
                    f"{path_folder}/image-blur-0.jpg",
                    None,
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
                        f"tin hot,{','.join(new_info['tags'])},tin nóng,tin tức mỗi ngày,",
                        f"[Nguồn: {name}] {new_info['description']}\n\n{ad['des']}\n\n(tags):\n{', '.join(new_info['tags'])}"
                    ]
                )

                future1.result()
                future2.result()
                future3.result()
        
            
            if type_run_video == 'ffmpeg' or type_run_video == 'cv2':
                concat_content_videos_ffmpeg(
                    './public/intro.mkv',
                    ad['video'],
                    f"{path_folder}/ad.mkv",
                    f"{path_folder}/content-voice.aac",
                    path_videos,
                    f"{path_folder}/result.mkv",
                    f"{path_folder}/draf.mkv",
                    f"{path_folder}/draf2.mkv",
                    f"{path_folder}/draf3.mkv",
                )
            elif type_run_video == 'moviepy':
                concat_content_videos_moviepy(f"{path_folder}/content-voice.aac", path_videos, f"{path_folder}/result.mp4")

            end_time = time.time()
            print(f"Thời gian chạy: {end_time - start_time:.2f} giây")
            
            title = ''
            tags = ''
            description = ''
            with open(f"{path_folder}/result.txt", 'r', encoding='utf-8') as f:
                lines = f.readlines()
                title = lines[0].strip() if len(lines) >= 1 else ''
                tags = lines[1].strip() if len(lines) >= 2 else ''
                description = ''.join(lines[2:]).strip() if len(lines) >= 3 else ''
            title_slug = slugify(title)
            os.rename(f"{path_folder}/result.mkv", f"{path_folder}/{title_slug}.mkv")
            upload_yt(
                f"./youtubes/{data_by_ip['youtubes'][index_youtube]}",
                title,
                description,
                tags,
                os.path.abspath(f"{path_folder}/{title_slug}.mkv"),
                os.path.abspath(f"{path_folder}/thumbnail.jpg"),
            )
            if data_by_ip['youtubes'].__len__() > 1:
                index_youtube += 1
                if(data_by_ip['youtubes'].__len__() <= index_youtube):
                    index_youtube = 0
                print(f'chờ {times[0]['time3']} phút')
                time.sleep(60 * times[0]['time3'])
            else:
                print(f'chờ {times[0]['time2']} phút')
                time.sleep(60 * times[0]['time2'])
            print('Tiếp tục...')
        except Exception as e:
            message = str(e)

            if "Lỗi xảy ra, không tồn tại link hoặc đã hết tin tức" in message:
                print(f"{message} → Đợi {times[0]['time1']} phút rồi thử lại...")
                data = 5
                while data < (60 * times[0]['time1']):
                    print(f'đợi {times[0]['time1']} phút vì hết link')
                    time.sleep(5)
                    data += 5
            elif "Lỗi xảy ra, không có thông tin của content" in message:
                insert_link(current_link)
                print(f"Lỗi xảy ra, không có thông tin của content")
            else:
                print(f"[LỖI KHÁC] {message}")
                gemini_model_index += 1
                if gemini_model_index > models.__len__() - 1:
                    gemini_model_index = 0
                    gemini_key_index += 1
                    if gemini_key_index > data_by_ip['geminiKeys'].__len__() - 1:
                        gemini_key_index = 0
                print('Cập nhật model và key của gemini')
                print(f'Model của bạn là: {models[gemini_model_index]}')
                print(f'key của bạn là: {data_by_ip['geminiKeys'][gemini_key_index]}')
                
                time.sleep(60)

if __name__ == "__main__":
    is_exit = False
    while is_exit is False:
        check_not_exist_to_create_ip()
        print('|-----------------------------------------------|')
        print('|-------       tool youtube linux        -------|')
        print('|-0. Thoát chương trình                  -------|')
        print('|-1. Chỉnh sửa danh sách chrome youtube  -------|')
        print('|-2. Chỉnh sửa danh sách gemini          -------|')
        print('|-3. Chỉnh sửa chrome driver             -------|')
        print('|-4. chỉnh sitemap website (chỉnh toàn bộ vps) -|')
        print('|-5. chỉnh thời gian chạy (chỉnh toàn bộ vps) --|')
        print('|-6. Chạy youtube                        -------|')
        
        func = int(input("Nhập chọn chức năng: "))
        
        if func == 1:
            while func == 1:
                data = find_one_ip()
                print('|-----------------------------------------------|')
                print('|---   Chỉnh sửa danh sách chrome youtube   ----|')
                print('|- DANH SÁCH YOUTUBE:                    -------|')
                if(data.get('youtubes') is not None and data['youtubes'].__len__() > 0):
                    print(data['youtubes'])
                else:    
                    print('Trống vui lòng thêm youtube mới')
                print('|-0. Quay lại                            -------|')
                print('|-1. Thêm youtube mới (nhập 1-name)      -------|')
                print('|-2. Xóa youtube (nhập 2-name)           -------|')
                print('|-3. Mở để chỉnh sửa (nhập 3-name)       -------|')
                print('|-4. Check xác minh danh tính (nhập 4-name)  ---|')
                print('|- Lưu ý: name chrome ghi liền mạch không cách -|')
                func1 = input("Nhập chọn chức năng: ")
                
                if (' ' in func1):
                    print('lỗi cú pháp, không được chứa dấu cách')
                elif func1 == 0 or func1 == '0':
                    func= 'exit' 
                elif func1.startswith("1-"):
                    text = func1[2:]
                    if(data.get('youtubes') is not None and text in data.get("youtubes", [])):
                        print('đã tồn tại chrome youtube này rồi')
                    else:
                        add_youtube_to_ip(text)
                        open_chrome_to_edit(text, data.get('driverPath'))
                elif func1.startswith("2-"):
                    text = func1[2:]
                    if(data.get('youtubes') is not None and text in data.get("youtubes", [])):
                        remove_youtube_to_ip(text)
                        try:
                            shutil.rmtree(f"./youtubes/{text}")
                        except:
                            print('')    
                    else:
                        print('Không thể xóa vì chưa tồn tại chrome youtube này')
                elif func1.startswith("3-"):
                    text = func1[2:]
                    if(data.get('youtubes') is not None and text in data.get("youtubes", [])):
                        open_chrome_to_edit(text, data.get('driverPath'))
                    else:
                        print('Chưa tồn tại trình duyệt này')
                elif func1.startswith("4-"):
                    text = func1[2:]
                    if(data.get('youtubes') is not None and text in data.get("youtubes", [])):
                        check_identity_verification(text)
                    else:
                        print('Chưa tồn tại trình duyệt này')
                
                
        elif func == 2:
            while func == 2:
                data = find_one_ip()
                models = get_all_models()
                print('|-----------------------------------------------|')
                print('|---    Chỉnh sửa danh sách gemini keys     ----|')
                print('|- DANH SÁCH GEMINI KEYS:                -------|')
                if(data.get('geminiKeys') is not None and data['geminiKeys'].__len__() > 0):
                    print(data['geminiKeys'])
                else:    
                    print('Trống vui lòng thêm gemini key mới')
                print('|- DANH SÁCH GEMINI MODEL:               -------|')
                if(models is not None and models.__len__() > 0):
                    print(models)
                else:    
                    print('Trống vui lòng thêm model mới')
                print('|-0. Quay lại                            -------|')
                print('|-1. Thêm key mới (nhập 1-key)           -------|')
                print('|-2. Xóa key (nhập 2-key)                -------|')
                print('|-3. Thêm model (nhập 3-model, toàn bộ vps)   --|')
                print('|-4. xóa model (nhập 4-model, toàn bộ vps)    --|')
                print('|-5. xem các models trong gemini              --|')
                print('|-6. test chạy key (nhập 6-key)               --|')
                print('|-7. test chạy (nhập 7-model)                 --|')
                print('|- Lưu ý: key ghi liền mạch không cách   -------|')
                func2 = input("Nhập chọn chức năng: ")
                
                if func2 == 0 or func2 == '0':
                    func= 'exit' 
                elif func2.startswith("1-"):
                    text = func2[2:]
                    if(data.get('geminiKeys') is not None and text in data.get("geminiKeys", [])):
                        print('đã tồn tại key này rồi')
                    else:
                        add_gemini_key_to_ip(text)
                elif func2.startswith("2-"):
                    text = func2[2:]
                    if(data.get('geminiKeys') is not None and text in data.get("geminiKeys", [])):
                        remove_gemini_key_youtube_to_ip(text)
                    else:
                        print('Không thể xóa vì chưa tồn tại key này')
                elif func2.startswith("3-"):
                    text = func2[2:]
                    if(models is not None and text in models):
                        print('đã tồn tại model này rồi')
                    else:
                        insert_model(text)
             
                elif func2.startswith("4-"):
                    text = func2[2:]
                    if(models is not None and text in models):
                        delete_model(text)
                    else:
                        print('Không thể xóa vì chưa tồn tại model này')
                elif func2.startswith("5"):
                    if(data.get('geminiKeys') is not None and data['geminiKeys'].__len__() > 0):
                        import google.generativeai as genai
                        genai.configure(api_key=data['geminiKeys'][0])
                        models = genai.list_models()
                        for m in models:
                            if 'generateContent' in m.supported_generation_methods:
                                print(m.name, m.description, m.supported_generation_methods)
                    else:
                        print('chưa có key để search model')
                    
        
                elif func2.startswith("6-"):
                    text = func2[2:]
                    data = generate_content("hãy tạo ra 1 câu truyện cổ tích", api_key= text)
                    print(data)
                elif func2.startswith("7-"):
                    if(data.get('geminiKeys') is not None and data['geminiKeys'].__len__() > 0):
                        text = func2[2:]
                        data = generate_content("hãy tạo ra 1 câu truyện cổ tích", model= text, api_key= data['geminiKeys'][0])
                        print(data)
                    else:
                        print('chưa có key để test model')
                        
        elif func == 4:
            while func == 4:
                data = get_all_sitemap_links()
                print('|-----------------------------------------------|')
                print('|---    Chỉnh sửa danh sách sitemap link    ----|')
                print('|- DANH SÁCH SITEMAP:                    -------|')
                if(data.__len__() > 0):
                    print(data)
                else:    
                    print('Trống vui lòng thêm sitemap link mới')
                print('|-0. Quay lại                            -------|')
                print('|-1. Thêm name và link mới (nhập 1@name@link) --|')
                print('|-2. Xóa link (nhập 2-link)              -------|')
                print('|-3. test chạy lấy nội dung link (nhập 3-link) -|')
                func4 = input("Nhập chọn chức năng: ")
                
                if func4 == 0 or func4 == '0':
                    func= 'exit' 
                elif func4.startswith("1@"):
                    arr = func4.split("@")
                    print(arr)
                    if arr.__len__() != 3:
                        print('không đúng cú pháp')
                    elif(arr[2] in data):
                        print('đã tồn tại link này rồi')
                    else:
                        insert_sitemap_link(arr[1], arr[2])
                elif func4.startswith("2-"):
                    text = func4[2:]
                    if(text in data):
                        delete_sitemap_link(text)
                    else:
                        print('Không thể xóa vì chưa tồn tại key này')
                elif func4.startswith("3-"):
                    text = func4[2:]
                    links = get_link_in_sitemap({"link": text, "name": "test"})
                    if(links.__len__() > 0):
                        funcs = get_func_to_get_info_new()
                        namespace = {}
                        exec(funcs[0]['func'], globals(), namespace)   
                        print(links[0]['link'])
                        index = 0
                        while index < 3:                 
                            new_info = namespace['get_info_new'](links[index]['link'])
                            print(new_info)
                            index += 1
            
        elif func == 3:
            while func == 3:
                data = find_one_ip()
                print('|-----------------------------------------------|')
                print('|---         Chỉnh sửa chrome driver        ----|')
                print('|- DRIVER CỦA BẠN LÀ:                    -------|')
                print(data['driverPath'])
                print('|-1. Thay driver (nhập 1-driver path     -------|')
                print('|-0. Quay lại                            -------|')
                
                func3 = input("Nhập chọn chức năng: ")
                if func3 == 0 or func3 == '0':
                    func= 'exit' 
                elif func3.startswith("1-"):
                    text = func3[2:]
                    update_driver_path_to_ip(text)
                
        elif func == 5:
            while func == 5:
                data = get_times()
                print('|-----------------------------------------------|')
                print('|---         Chỉnh sửa thời gian            ----|')
                print('|- THÔNG TIN CHI TIẾT:                   -------|')
                if(data.__len__() == 0):
                    print('Chưa có thông tin thời gian, vui lòng cập nhật')
                else:
                    print(f'Thời gian đợi khi hết link: {data[0]['time1']} phút')
                    print(f'Thời gian đợi khi upload thành công nếu chỉ 1 kênh: {data[0]['time2']} phút')
                    print(f'Thời gian đợi khi upload thành công nếu có nhiều kênh: {data[0]['time3']} phút')
    
                print('|-1. thời gian đợi khi hết link, thời gian chờ -|')
                print('| khi úp yt thành công nếu chỉ 1 kênh, thời    -|')
                print('| gian khi úp yt thành công nếu có nhiều kênh  -|')
                print('| (nhập 1-time1-time2-time3) (phút)            -|')
                print('|-0. Quay lại                            -------|')
                
                func3 = input("Nhập chọn chức năng: ")
                if func3 == 0 or func3 == '0':
                    func= 'exit'
                elif func3.startswith("1-"):
                    arr = func3.split('-')
                    if(arr.__len__() != 4):
                        print('Không đúng cú pháp')
                    elif not arr[1].isdigit() or not arr[2].isdigit() or not arr[3].isdigit():
                        print('Không đúng cú pháp')
                    elif int(arr[1]) <= 0 or int(arr[2]) <= 0 or int(arr[3]) <= 0:
                        print('Thời gian không được nhỏ hơn hoặc bằng 0')
                    else:
                        if(data.__len__() == 0):
                            insert_time(int(arr[1]), int(arr[2]), int(arr[3]))
                        else:
                            update_time(data[0]['_id'], int(arr[1]), int(arr[2]), int(arr[3]))
                        
                 
        elif func == 6:
            data = find_one_ip()
            times = get_times()
            link_sitemaps = get_all_sitemap_links()
            
            if(data.get('geminiKeys') is None or data['geminiKeys'].__len__() == 0):
                print('bạn chưa thể chạy vì chưa thêm gemini key')
            elif(data.get('youtubes') is None or data['youtubes'].__len__() == 0):
                print('bạn chưa thể chạy vì chưa thêm youtube chrome')
            elif(times.__len__() == 0):
                print('bạn chưa thể chạy vì chưa chỉnh thời gian')
            elif(link_sitemaps.__len__() == 0):
                print('bạn chưa thể chạy vì chưa tồn tại link sitemap nào')
            else:
                # type: 'ffmpeg' 'moviepy' 'cv2'
                type = 'cv2'
                main(type, True) 
        elif func == 0:
            is_exit = True
        else:
            print('Thoát thành công')
    
   
