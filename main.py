import shutil
import os
from untils import get_all_link_in_theguardian_new, get_info_new
from untils import get_img_gif_person, get_info_new
from db import check_link_exists, connect_db, insert_link, get_all_links, delete_link 

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
        print(new_info)

        # lấy ngẫu nhiên đường dẫn hình ảnh và hình động người thuyết trình
        person_info = get_img_gif_person()
        
        # tạo ra image gốc và image mờ, sau đó tạo ra video từng phần
        path_videos = []
        print(current_link)
        if(new_info is None):
            raise Exception("Lỗi xảy ra, không có thông tin của content")
        for key, item in enumerate(new_info['picture_links']):
            print(item)   
               
    except Exception as e:
        print(current_link)
        print(f'loi xay ra: {e}')  

if __name__ == "__main__":
    main()