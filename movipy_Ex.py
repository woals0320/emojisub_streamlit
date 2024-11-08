import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import moviepy.editor as mp
from moviepy.video.VideoClip import TextClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.config import change_settings
import pysrt
from PIL import ImageFont, Image, ImageDraw
import numpy as np
from pilmoji import Pilmoji


change_settings({"IMAGEMAGICK_BINARY": "./ImageMagick/ImageMagick-7.1.1-Q16-HDRI/magick.exe"})

# 디자인 가이드 설정
fonts_folder = "./fonts"  # 폰트 파일들이 저장된 폴더

design_guides = {
    'neutral': [
        # {'font': f'{fonts_folder}/Pretendard-Regular.ttf', 'fontsize': 36, 'color': 'white', 'stroke_color': 'black', 'stroke_width': 0},
        {'font': f'{fonts_folder}/BMDOHYEON.ttf', 'fontsize': 36, 'color': 'white', 'stroke_color': 'black', 'stroke_width': 1}
    ],
    'happiness': [
        # {'font': f'{fonts_folder}/Pretendard-Regular.ttf', 'fontsize': 24, 'color': '#FF69B4', 'stroke_color': 'black', 'stroke_width': 1},
        # {'font': f'{fonts_folder}/KyoboHand.ttf', 'fontsize': 36, 'color': 'pink', 'stroke_color': 'black', 'stroke_width': 1},   # 깨지는 폰트
        # {'font': f'{fonts_folder}/KCC-Ganpan.ttf', 'fontsize': 36, 'color': 'pink', 'stroke_color': 'black', 'stroke_width': 1},
        {'font': f'{fonts_folder}/BMDOHYEON.ttf', 'fontsize': 36, 'color': 'pink', 'stroke_color': 'black', 'stroke_width': 1}
    ],
    'anger': [
        # {'font': f'{fonts_folder}/Pretendard-Regular.ttf', 'fontsize': 24, 'color': 'red', 'stroke_color': 'black', 'stroke_width': 1},
        # {'font': f'{fonts_folder}/Shilla_CultureB-Bold.ttf', 'fontsize': 36, 'color': 'red', 'stroke_color': 'black', 'stroke_width': 1}, # 깨지는 폰트
        # {'font': f'{fonts_folder}/Pretendard-Regular.ttf', 'fontsize': 24, 'color': 'red', 'stroke_color': 'yellow', 'stroke_width': 1},
        {'font': f'{fonts_folder}/BMDOHYEON.ttf', 'fontsize': 36, 'color': 'red', 'stroke_color': 'black', 'stroke_width': 1}
    ],
    'sadness': [
        # {'font': f'{fonts_folder}/Pretendard-Regular.ttf', 'fontsize': 24, 'color': 'grey', 'stroke_color': 'black', 'stroke_width': 1},
        {'font': f'{fonts_folder}/SuseongBatang.ttf', 'fontsize': 36, 'color': 'grey', 'stroke_color': 'black', 'stroke_width': 1}
    ],
    'disgust': [
        # {'font': f'{fonts_folder}/Pretendard-Regular.ttf', 'fontsize': 24, 'color': 'brown', 'stroke_color': 'black', 'stroke_width': 1},
        {'font': f'{fonts_folder}/Jeonju_gakR.ttf', 'fontsize': 36, 'color': 'brown', 'stroke_color': 'black', 'stroke_width': 1}
    ],
    'fear': [
        # {'font': f'{fonts_folder}/Pretendard-Regular.ttf', 'fontsize': 24, 'color': 'black', 'stroke_color': 'red', 'stroke_width': 1},
        {'font': f'{fonts_folder}/ChosunCentennial.ttf', 'fontsize': 36, 'color': 'black', 'stroke_color': 'red', 'stroke_width': 0.5}
    ],
    'surprise': [
        # {'font': f'{fonts_folder}/Pretendard-Regular.ttf', 'fontsize': 24, 'color': 'yellow', 'stroke_color': 'black', 'stroke_width': 1},
        # {'font': f'{fonts_folder}/GmarketSansMedium.ttf', 'fontsize': 36, 'color': 'yellow', 'stroke_color': 'black', 'stroke_width': 1} # 깨지는 폰트
        {'font': f'{fonts_folder}/BMDOHYEON.ttf', 'fontsize': 36, 'color': 'yellow', 'stroke_color': 'black', 'stroke_width': 1}
    ]
}

# 이모지 및 추가 텍스트 매핑
emotion_suffixes = {
    'anger': ' \U0001F4A2',  # 💢    
    'happiness': ' \U0001F495', # 💕
    'surprise': ' !!'
}

def make_emoji_image(emoji, font_path, font_size):
    emoji_font = ImageFont.truetype(font_path, font_size)
    
    # 텍스트 크기 측정
    image = Image.new("RGBA", (1, 1), (0, 0, 0, 0))  # 빈 이미지 생성
    draw = ImageDraw.Draw(image)
    text_bbox = draw.textbbox((0, 0), emoji.strip(), font=emoji_font)
    
    # 바운딩 박스 설정
    padding = 14  # 이모지 주변 여유 공간 설정
    text_size = (text_bbox[2] - text_bbox[0] + padding, text_bbox[3] - text_bbox[1] + padding)
    
    # 이모지 이미지 생성
    image = Image.new("RGBA", text_size, (0, 0, 0, 0))
    with Pilmoji(image) as pilmoji:
        pilmoji.text((padding//2, padding//2), emoji.strip(), (0, 0, 0), emoji_font)

    return np.array(image)

def get_text_width(text, font_path, fontsize):
    font = ImageFont.truetype(font_path, fontsize)
    image = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(image)
    
    # 텍스트 바운딩 박스 측정
    text_bbox = draw.textbbox((0, 0), text, font=font)
    
    # 너비는 바운딩 박스의 가로 길이로 계산
    text_width = text_bbox[2] - text_bbox[0]
    return text_width

# 메인 애플리케이션 클래스 정의
class SubtitleMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emotion-based Subtitle Merger")
        self.root.geometry("400x300")
        self.root.configure(bg='#f0f0f0')

        # 스타일 적용
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')
        self.style.configure('TButton', background='#1E90FF', foreground='white', font=('Helvetica', 12), borderwidth=0, focusthickness=3, focuscolor='none')
        self.style.map('TButton', background=[('active', '#4682B4')])
        self.style.configure('TLabel', foreground='gray', font=('Helvetica', 12))
        self.style.configure('TFrame', background='#f0f0f0')

        # MP4 파일 경로 변수
        self.mp4_path = ""
        # SRT 파일 경로 변수
        self.srt_path = ""

        # MP4 파일 추가 버튼
        self.add_mp4_button = ttk.Button(self.root, text="Add MP4 File", command=self.add_mp4_file)
        self.add_mp4_button.pack(pady=10)

        # SRT 파일 추가 버튼
        self.add_srt_button = ttk.Button(self.root, text="Add SRT File", command=self.add_srt_file)
        self.add_srt_button.pack(pady=10)

        # 시작 버튼
        self.start_button = ttk.Button(self.root, text="Start", command=self.merge_subtitles)
        self.start_button.pack(pady=20)

    def add_mp4_file(self):
        # MP4 파일 선택
        self.mp4_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        if self.mp4_path:
            messagebox.showinfo("File Selected", f"Selected MP4 file: {self.mp4_path}")

    def add_srt_file(self):
        # SRT 파일 선택
        self.srt_path = filedialog.askopenfilename(filetypes=[("SRT files", "*.srt")])
        if self.srt_path:
            messagebox.showinfo("File Selected", f"Selected SRT file: {self.srt_path}")

    def extract_emotion(self, subtitle_text):
        # 자막 텍스트에서 감정을 추출
        if "|emotion=" in subtitle_text:
            text, emotion = subtitle_text.split("|emotion=")
            emotion = emotion.strip()
            return text.strip(), emotion
        return subtitle_text, 'neutral'
    
    

    def merge_subtitles(self):
        if not self.mp4_path or not self.srt_path:
            messagebox.showerror("Error", "Please select both MP4 and SRT files.")
            return

        # 출력 파일 이름
        output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])

        if output_path:
            # MoviePy를 사용하여 동영상에 자막 추가
            video = mp.VideoFileClip(self.mp4_path)

            # SRT 파일을 UTF-8 인코딩으로 읽고 파싱
            subs = pysrt.open(self.srt_path, encoding='utf-8')

            # 자막 클립을 생성하는 함수
            subtitle_clips = []
            for sub in subs:
                start = sub.start.ordinal / 1000  # ms to seconds
                end = sub.end.ordinal / 1000  # ms to seconds
                text, emotion = self.extract_emotion(sub.text)

                if emotion in design_guides:
                    design = design_guides[emotion][0]
                    suffix = emotion_suffixes.get(emotion, "")  # 이모지 또는 텍스트를 추가 
                    
                    if emotion == "surprise":   # '!!'는 텍스트로 추가, 이모지처럼 처리하지 않음
                        full_text = text + suffix
                        txt_clip = TextClip(full_text, font=design['font'], fontsize=design['fontsize'],
                                    color=design['color'], stroke_color=design.get('stroke_color', None),
                                    stroke_width=design.get('stroke_width', 0))
                        
                        # 자막 클립 위치 및 시간 설정
                        txt_clip = txt_clip.set_start(start).set_end(end).set_position(('center', video.h - 100))
                        subtitle_clips.append(txt_clip)

                        
                    else:   # 다른 감정들은 기존대로 처리
                        full_text = text + suffix
                        txt_clip = TextClip(full_text, font=design['font'], fontsize=design['fontsize'],
                                            color=design['color'], stroke_color=design.get('stroke_color', None),
                                            stroke_width=design.get('stroke_width', 0))
                        
                        # 자막 클립 위치 및 시간 설정
                        txt_clip = txt_clip.set_start(start).set_end(end).set_position(('center', video.h - 100))
                        subtitle_clips.append(txt_clip)

                        
                        # 이모지 처리
                        if suffix in emotion_suffixes.values():
                            text_width = get_text_width(text, design['font'], design['fontsize'])
                            emoji_image = make_emoji_image(suffix, design['font'], design['fontsize'])
                            emoji_clip = ImageClip(emoji_image, duration=end - start).set_position((video.w / 2 + text_width / 2 - 30, video.h - 105)).set_start(start)
                            subtitle_clips.append(emoji_clip)

                    # # 자막 텍스트 생성
                    # txt_clip = TextClip(full_text.encode('utf-8').decode('utf-8'), font=design['font'], fontsize=design['fontsize'],
                    #                     color=design['color'], stroke_color=design.get('stroke_color', None),
                    #                     stroke_width=design.get('stroke_width', 0))

                    # 자막 클립 위치 및 시간 설정
                    # txt_clip = txt_clip.set_start(start).set_end(end).set_position(('center', video.h - 100))
                    # subtitle_clips.append(txt_clip)

                    # # 텍스트의 너비 계산
                    # text_width = get_text_width(text, design['font'], design['fontsize'])

                    # # 이모지 이미지 생성
                    # emoji_image = make_emoji_image(emotion_suffixes.get(emotion, ""), design['font'], design['fontsize'])

                    # # 이모지의 가로 위치를 자막 텍스트의 끝부분에 맞춤
                    # emoji_clip = ImageClip(emoji_image, duration=end - start).set_position((video.w / 2 + text_width / 2, video.h - 100)).set_start(start)
                    # subtitle_clips.append(emoji_clip)


            # 자막을 비디오에 오버레이
            final_video = CompositeVideoClip([video] + subtitle_clips)

            # 결과 비디오를 파일로 저장
            final_video.write_videofile(output_path, codec='libx264', temp_audiofile='temp-audio.m4a', remove_temp=True, audio_codec='aac')

            messagebox.showinfo("Success", f"Subtitled video saved to: {output_path}")
            self.mp4_path = ""
            self.srt_path = ""

# Tkinter 애플리케이션 실행
if __name__ == "__main__":
    root = tk.Tk()
    app = SubtitleMergerApp(root)
    root.mainloop()