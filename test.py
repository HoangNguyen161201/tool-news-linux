from untils import generate_to_voice_gtts

generate_to_voice_gtts(
    text="""
    Tối 16-10 tại Hà Nội, Jack trình diễn một ca khúc mới chưa công bố.
    Mạng xã hội tràn ngập tranh luận về phần biểu diễn này.
    """,
    bgm_path="./public/bg.mp3",
    output_path="./final.aac",
    speed=1.3,
    volume_voice=3.0,   # giọng to gấp 3 lần
    volume_bgm=0.25      # nhạc nền nhỏ 40%
)