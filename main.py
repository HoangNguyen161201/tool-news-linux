from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


import time
import random
import os
# from untils import generate_content, generate_voice_kokoro, generate_image, generate_video_by_image, concact_content_videos, count_folders, generate_thumbnail, upload_yt
import concurrent.futures
from data import gif_paths, person_img_paths
from slugify import slugify
from db import connect_db, check_link_exists, insert_link,delete_link, get_all_links
from pathlib import Path
import subprocess
from datetime import datetime
import pyglet

connect_db()
print(get_all_links())
# delete_link('https://www.theguardian.com/world/2025/feb/15/uk-based-lawyers-for-hong-kong-activist-jimmy-lai-targeted-by-chinese-state')
# # # # insert_link('https://www.theguardian.com/world/article/2024/may/21/gove-accuses-uk-university-protests-of-antisemitism-repurposed-for-instagram-age')
# time.sleep(60)
