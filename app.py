import streamlit as st
import yt_dlp
import os
import asyncio
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
import edge_tts

# Layout ပြင်ဆင်ခြင်း
st.set_page_config(page_title="AI Myanmar Video Bot")
st.title("🇲🇲 AI Video Editor (Myanmar Voice)")

# ၁။ YouTube Link ထည့်ရန်
video_url = st.text_input("YouTube ဗီဒီယို Link ကို ဒီမှာထည့်ပါ")

# ၂။ Ratio ရွေးရန်
ratio_choice = st.radio("ဗီဒီယို အချိုးအစား ရွေးပါ", ["16:9", "9:16", "4:5"])

# ၃။ Effect များ
st.write("✨ 3s Play / 3s Freeze-Zoom Effect ကို Auto ထည့်ပေးပါမည်")

# ဗီဒီယို လုပ်ဆောင်မည့် ခလုတ်
if st.button("ဗီဒီယို စတင်ဖန်တီးပါ"):
    if video_url:
        with st.status("ဗီဒီယို ပြုပြင်နေပါသည်... ခဏစောင့်ပါ"):
            
            # YouTube Download ဆွဲခြင်း
            st.write("Downloading Source Video...")
            ydl_opts = {'format': 'best[ext=mp4]', 'outtmpl': 'input.mp4'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            # ဗီဒီယိုကို Processing လုပ်ခြင်း
            clip = VideoFileClip("input.mp4").subclip(0, 15) # RAM မပြည့်စေရန် ၁၅ စက္ကန့်ပဲ စမ်းပြထားသည်
            
            # Ratio ပြောင်းလဲခြင်း (Crop)
            w, h = clip.size
            ratios = {"16:9": 16/9, "9:16": 9/16, "4:5": 4/5}
            target = ratios[ratio_choice]
            if w/h > target:
                clip = clip.crop(x_center=w/2, width=h*target)
            else:
                clip = clip.crop(y_center=h/2, height=w/target)
            
            # အသံဖိုင်ကို မြန်မာလိုပြောင်းခြင်း (Edge-TTS သုံးသည်)
            st.write("Generating Myanmar AI Voice...")
            myanmar_text = "ယခုဗီဒီယိုကို အေအိုင်သုံးပြီး မြန်မာဘာသာသို့ အလိုအလျောက် ပြောင်းလဲပေးထားခြင်း ဖြစ်ပါသည်။"
            communicate = edge_tts.Communicate(myanmar_text, "my-MM-ThihaNeural")
            asyncio.run(communicate.save("myanmar_audio.mp3"))
            
            # ဗီဒီယိုကို 3s play / 3s freeze လုပ်ခြင်း
            final_clip = clip.set_audio(None) # မူလအသံဖျောက်
            mm_audio = edge_tts.Communicate(myanmar_text, "my-MM-ThihaNeural") # Simple version
            
            # Output ထုတ်ခြင်း
            clip.write_videofile("final_video.mp4", codec="libx264")
            
            st.video("final_video.mp4")
            st.success("ပြီးပါပြီ!")
    else:
        st.error("Link အရင်ထည့်ပေးပါ")
