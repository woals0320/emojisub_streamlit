import streamlit as st
import moviepy.editor as mp
from moviepy.editor import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.config import change_settings
import pysrt
from PIL import ImageFont, Image, ImageDraw
import numpy as np
from pilmoji import Pilmoji

# 디자인 가이드 설정
fonts_folder = "./fonts"

design_guides = {
    'neutral': [{'font': f'{fonts_folder}/BMDOHYEON.ttf', 'fontsize': 36, 'color': 'white', 'stroke_color': 'black', 'stroke_width': 1}],
    'happiness': [{'font': f'{fonts_folder}/BMDOHYEON.ttf', 'fontsize': 36, 'color': 'pink', 'stroke_color': 'black', 'stroke_width': 1}],
    'anger': [{'font': f'{fonts_folder}/BMDOHYEON.ttf', 'fontsize': 36, 'color': 'red', 'stroke_color': 'black', 'stroke_width': 1}],
    'sadness': [{'font': f'{fonts_folder}/SuseongBatang.ttf', 'fontsize': 36, 'color': 'grey', 'stroke_color': 'black', 'stroke_width': 1}],
    'disgust': [{'font': f'{fonts_folder}/Jeonju_gakR.ttf', 'fontsize': 36, 'color': 'brown', 'stroke_color': 'black', 'stroke_width': 1}],
    'fear': [{'font': f'{fonts_folder}/ChosunCentennial.ttf', 'fontsize': 36, 'color': 'black', 'stroke_color': 'red', 'stroke_width': 0.5}],
    'surprise': [{'font': f'{fonts_folder}/BMDOHYEON.ttf', 'fontsize': 36, 'color': 'yellow', 'stroke_color': 'black', 'stroke_width': 1}],
}

emotion_suffixes = {
    'anger': ' \U0001F4A2',
    'happiness': ' \U0001F495',
    'surprise': ' !!',
}

def make_emoji_image(emoji, font_path, font_size):
    emoji_font = ImageFont.truetype(font_path, font_size)
    image = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    text_bbox = draw.textbbox((0, 0), emoji.strip(), font=emoji_font)
    padding = 14
    text_size = (text_bbox[2] - text_bbox[0] + padding, text_bbox[3] - text_bbox[1] + padding)
    image = Image.new("RGBA", text_size, (0, 0, 0, 0))
    with Pilmoji(image) as pilmoji:
        pilmoji.text((padding // 2, padding // 2), emoji.strip(), (0, 0, 0), emoji_font)
    return np.array(image)

def extract_emotion(subtitle_text):
    if "|emotion=" in subtitle_text:
        text, emotion = subtitle_text.split("|emotion=")
        return text.strip(), emotion.strip()
    return subtitle_text, 'neutral'

def get_text_width(text, font_path, fontsize):
    font = ImageFont.truetype(font_path, fontsize)
    image = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(image)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    return text_bbox[2] - text_bbox[0]

def main():
    # Streamlit 인터페이스
    st.title("감정기반 이모지 자막 프로그램")
    st.markdown("MP4 파일과 SRT 파일을 업로드하세요. 자막은 감정에 맞는 디자인으로 작성됩니다.")
    
    mp4_file = st.file_uploader("동영상 파일 업로드", type=["mp4"])
    srt_file = st.file_uploader("srt 자막 파일 업로드", type=["srt"])
    
    if mp4_file and srt_file:
        output_name = st.text_input("저장할 파일 이름 입력 (예: output.mp4)")
        if st.button("시작"):
            with st.spinner("비디오에 자막을 추가 중입니다..."):
                # 임시 파일 저장
                video_path = f"./temp_{mp4_file.name}"  # 임시 파일 경로
                with open(video_path, "wb") as f:
                    f.write(mp4_file.getbuffer())
            
                video = VideoFileClip(mp4_file.name)
                subs = pysrt.from_string(srt_file.read().decode("utf-8"))
    
                subtitle_clips = []
                for sub in subs:
                    start = sub.start.ordinal / 1000
                    end = sub.end.ordinal / 1000
                    text, emotion = extract_emotion(sub.text)
                    design = design_guides.get(emotion, design_guides['neutral'])[0]
                    suffix = emotion_suffixes.get(emotion, "")
    
                    if emotion == "surprise":
                        full_text = text + suffix
                        txt_clip = TextClip(full_text, font=design['font'], fontsize=design['fontsize'],
                                            color=design['color'], stroke_color=design.get('stroke_color'),
                                            stroke_width=design.get('stroke_width', 0))
                        txt_clip = txt_clip.set_start(start).set_end(end).set_position(('center', video.h - 100))
                        subtitle_clips.append(txt_clip)
                    else:
                        full_text = text + suffix
                        txt_clip = TextClip(full_text, font=design['font'], fontsize=design['fontsize'],
                                            color=design['color'], stroke_color=design.get('stroke_color'),
                                            stroke_width=design.get('stroke_width', 0))
                        txt_clip = txt_clip.set_start(start).set_end(end).set_position(('center', video.h - 100))
                        subtitle_clips.append(txt_clip)
    
                        if suffix in emotion_suffixes.values():
                            text_width = get_text_width(text, design['font'], design['fontsize'])
                            emoji_image = make_emoji_image(suffix, design['font'], design['fontsize'])
                            emoji_clip = ImageClip(emoji_image, duration=end - start).set_position((video.w / 2 + text_width / 2 - 30, video.h - 105)).set_start(start)
                            subtitle_clips.append(emoji_clip)
    
                final_video = CompositeVideoClip([video] + subtitle_clips)
                final_video.write_videofile(output_name, codec='libx264', audio_codec='aac')
    
            st.success(f"비디오가 성공적으로 저장되었습니다: {output_name}")


if __name__ == "__main__":
    main()

