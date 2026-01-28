import streamlit as st
import yt_dlp
import os
import asyncio
from moviepy.editor import VideoFileClip, CompositeVideoClip
import edge_tts

st.set_page_config(page_title="MM AI Video Editor", layout="wide")
st.title("🇲🇲 MM AI Video Editor (Myanmar Voice)")

# Input URL
url = st.text_input("YouTube ဗီဒီယို Link ကို ဒီမှာထည့်ပါ")
ratio_choice = st.radio("ဗီဒီယို အချိုးအစား ရွေးပါ", ["16:9", "9:16", "4:5"], index=1)

def download_video(url_link):
    # YouTube က Block တာ သက်သာအောင် header တွေ ထည့်ထားပါတယ်
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'input_video.mp4',
        'noplaylist': True,
        'quiet': False,
    }
    try:
        if os.path.exists("input_video.mp4"):
            os.remove("input_video.mp4")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_link])
        return "input_video.mp4"
    except Exception as e:
        st.error(f"Download Error: {e}")
        return None

async def make_voice(text, output):
    communicate = edge_tts.Communicate(text, "my-MM-ThihaNeural")
    await communicate.save(output)

if st.button("ဗီဒီယို စတင်ဖန်တီးပါ"):
    if url:
        with st.status("ဗီဒီယိုကို ပြုပြင်နေပါသည်..."):
            # 1. Download
            video_file = download_video(url)
            
            if video_file and os.path.exists(video_file):
                try:
                    # 2. Processing (RAM ချွေတာရန် ၅ စက္ကန့်ပဲ အရင်စမ်းပါ)
                    clip = VideoFileClip(video_file).subclip(0, 5)
                    
                    # 3. Ratio Adjustment
                    w, h = clip.size
                    target = {"16:9": 16/9, "9:16": 9/16, "4:5": 4/5}[ratio_choice]
                    if w/h > target:
                        clip = clip.crop(x_center=w/2, width=h*target)
                    else:
                        clip = clip.crop(y_center=h/2, height=w/target)

                    # 4. Myanmar Voice Generation
                    st.write("Generating Myanmar Voice...")
                    asyncio.run(make_voice("မင်္ဂလာပါ၊ ဗီဒီယိုကို မြန်မာဘာသာဖြင့် တင်ဆက်ပေးနေပါသည်။", "mm.mp3"))

                    # 5. Finalize
                    final_clip = clip.set_audio(None) # မူလအသံဖျောက်
                    final_clip.write_videofile("out.mp4", codec="libx264", audio_codec="aac")

                    st.video("out.mp4")
                    st.success("အောင်မြင်စွာ တည်းဖြတ်ပြီးပါပြီ!")
                except Exception as e:
                    st.error(f"Processing Error: {str(e)}")
            else:
                st.error("ဗီဒီယိုကို ဒေါင်းလုဒ်ဆွဲ၍ မရပါ။ Link ကို ပြန်စစ်ပေးပါ။")
    else:
        st.warning("Link အရင်ထည့်ပါ။")
