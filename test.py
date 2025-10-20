import asyncio
import edge_tts

async def main():
    # text: nội dung, voice: giọng, output: file mp3
    communicate = edge_tts.Communicate(
        text="Xin chào, tôi tên là Hoàng! Hôm nay chúng ta học Python.",
        voice="vi-VN-HoaiMyNeural"  # giọng nữ tiếng Việt
    )
    await communicate.save("output_edge.mp3")

asyncio.run(main())