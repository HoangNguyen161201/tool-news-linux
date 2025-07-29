import subprocess
import json

def check_mkv_youtube_compatible(file_path):
    try:
        # Lấy thông tin media bằng ffprobe
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=format_name:stream=index,codec_type,codec_name",
                "-of", "json",
                file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        info = json.loads(result.stdout)

        # Kiểm tra container format
        format_ok = 'matroska' in info.get('format', {}).get('format_name', '')

        # Tìm video & audio stream
        video_codecs = {"h264", "vp9"}
        audio_codecs = {"aac", "vorbis", "opus"}

        has_valid_video = False
        has_valid_audio = False

        for stream in info.get("streams", []):
            if stream["codec_type"] == "video" and stream["codec_name"] in video_codecs:
                has_valid_video = True
            elif stream["codec_type"] == "audio" and stream["codec_name"] in audio_codecs:
                has_valid_audio = True

        if format_ok and has_valid_video and has_valid_audio:
            return True, "✅ File MKV hợp lệ để upload lên YouTube."
        else:
            return False, f"❌ Không hợp lệ: Format: {format_ok}, Video: {has_valid_video}, Audio: {has_valid_audio}"

    except Exception as e:
        return False, f"❌ Lỗi khi kiểm tra file: {e}"

# Ví dụ sử dụng
file_path = "result.mkv"
is_valid, message = check_mkv_youtube_compatible(file_path)
print(message)