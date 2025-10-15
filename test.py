from untils import generate_content

data = generate_content('''
                            "a channel dedicated to empowering people over 60 to live with strength, dignity, and emotional freedom.
                            Here on Strong Elderly Life, you’ll find heartfelt advice on living alone, healing relationships with adult children, and building a life rooted in kindness, self-worth, and respect.
                            We share uplifting lessons on how to rediscover joy, find inner peace, and communicate more meaningfully in your golden years. Whether you feel forgotten or simply want to live with more purpose and independence, this is your space.
                            🌿 Aging isn’t about fading away—it’s about becoming wiser, freer, and stronger.
                            Strong Elderly Life is more than just a channel—it’s a community built for and by elders embracing a vibrant and self-directed life."
                            đây là thông tin kênh của tôi, hãy tạo ra 1 content, ngôi thứ nhất, bằng tiếng việt, thu hút, hấp dẫn, có độ dài trên 8000 ký tự, không nhắc tới kênh.
                            hãy đưa ra 1 vấn đề của tuổi già trên mạng và viết lại sao cho hay và dẫn
                          
                            chọn ngẫu nhiên ra 1 vấn đề thôi,
                            phải liên quan đến cuộc sống của nhân vật đang thoại, cách đối mặt và giải quyết.
                        ''', api_key= 'AIzaSyC4ZvI-VjW3GPf9DMzZT4iOMmT6DvjUH-8', model= 'gemini-2.5-flash-lite')

print(data)