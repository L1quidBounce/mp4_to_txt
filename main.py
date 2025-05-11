import speech_recognition as sr
from moviepy.editor import VideoFileClip
import os
from tqdm import tqdm
from pathlib import Path
import sys

"""
视频转文本(MP4_TO_TXT)
author:Fedal987,L1quidBounce
用于将视频中的音频转换为文本
"""

def check_dependencies():
    """检查依赖"""
    try:
        import speech_recognition as sr
        from moviepy.editor import VideoFileClip
        from tqdm import tqdm
    except ImportError as e:
        print(f"错误：你依赖没装。")
        print("请执行以下cmd命令安装依赖：")
        print("pip install -r requirements.txt")
        sys.exit(1)

def extract_audio_from_video(video_path, audio_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)
    video.close()

def transcribe_audio(audio_path, output_path, language='zh-CN'):
    recognizer = sr.Recognizer()
    text_segments = []
    
    with sr.AudioFile(audio_path) as source:
        duration = source.DURATION
        
        for i in tqdm(range(0, int(duration), 30)):
            audio = recognizer.record(source, duration=min(30, duration-i))
            try:
                text = recognizer.recognize_google(audio, language=language)
                if text.strip():
                    text_segments.append(text.strip())
            except sr.UnknownValueError:
                print(f"无法识别 {i}s - {min(i+30, duration)}s 的音频")
            except sr.RequestError as e:
                print(f"Google API 请求错误: {e}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(text_segments))

def process_video_to_text(video_path, output_path, language='zh-CN'):
    """处理视频并转换为文字"""
    temp_audio = "temp_audio.wav"
    
    try:
        print("正在提取音频...")
        extract_audio_from_video(video_path, temp_audio)
        
        print("正在进行语音识别...")
        transcribe_audio(temp_audio, output_path, language)
        
    finally:
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

def ensure_dir(directory):
    """检查目录"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def get_output_path(input_file, output_dir):
    """输出"""
    filename = Path(input_file).stem
    return os.path.join(output_dir, f"{filename}.txt")

def process_all_videos(input_dir, output_dir, language='zh-CN'):
    """处理目录下的所有MP4文件"""
    ensure_dir(output_dir)
    
    mp4_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.mp4')]
    
    if not mp4_files:
        print("未找到任何MP4文件！")
        return
    
    print(f"找到 {len(mp4_files)} 个MP4文件")
    
    for video_file in mp4_files:
        video_path = os.path.join(input_dir, video_file)
        output_path = get_output_path(video_file, output_dir)
        
        print(f"\n处理文件: {video_file}")
        process_video_to_text(video_path, output_path, language)

if __name__ == "__main__":
    check_dependencies()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "input")
    output_dir = os.path.join(base_dir, "output")
    
    language = input("请输入语言代码(默认zh-CN): ") or "zh-CN"
    
    if os.path.exists(input_dir):
        process_all_videos(input_dir, output_dir, language)
        print("\n所有文件处理完成！")
    else:
        print(f"输入目录 {input_dir} 不存在！")
