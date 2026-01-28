import streamlit as st
import os
import asyncio
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
import edge_tts
import tempfile

# Page configuration
st.set_page_config(page_title="AI Video Editor (Upload)", layout="wide")
st.title("🎥 AI Video Editor - Upload & Edit")

# Sidebar settings
st.sidebar.header("ပြင်ဆင်ရန်")
ratio_choice = st.sidebar.selectbox("ဗီဒီယို Ratio ရွေးပါ", ["16:9", "9:16", "4:5"])
dubbing_text = st.sidebar.text_area("မြန်မာအသံအတွက် စာသားထည့်ပါ", "မင်္ဂလာပါ၊ ဒီဗီဒီယိုကို AI နဲ့ တည်းဖြတ်ထားတာပါ။")

# File Uploader
uploaded_file = st.file_uploader("သင့်ဗီဒီယိုကို Upload တင်ပါ (mp4, mov, avi)", type=['mp4', 'mov', 'avi'])

async def generate_voice(text, output_path):
    communicate = edge_tts.Communicate(text, "my-MM-ThihaNeural")
    await communicate.save(output_path)

if uploaded_file is not None:
    # ဗီဒီယိုကို ယာယီသိမ်းဆည်းခြင်း
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    
    st.video(uploaded_file)
    
    if st.button("ဗီဒီယို စတင်တည်းဖြတ်ပါ"):
        with st.status("တည်းဖြတ်နေပါသည်... ခဏစောင့်ပါ") as status:
            try:
                # 1. ဗီဒီယိုကို Load လုပ်ပါ
                clip = VideoFileClip(tfile.name)
                
                # RAM မပြည့်စေရန် ပထမ ၁၂ စက္ကန့်ပဲ ယူပါမည် (စမ်းသပ်ရန်)
                if clip.duration > 12:
                    clip = clip.subclip(0, 12)

                # 2. Ratio ပြောင်းလဲခြင်း (Crop လုပ်ခြင်း)
                st.write("✂️ Ratio ပြောင်းနေသည်...")
                w, h = clip.size
                ratios = {"16:9": 16/9, "9:16": 9/16, "4:5": 4/5}
                target = ratios[ratio_choice]
                
                if w/h > target:
                    clip = clip.crop(x_center=w/2, width=h*target)
                else:
                    clip = clip.crop(y_center=h/2, height=w/target)

                # 3. 3s Play / 3s Freeze-Zoom Effects
                st.write("🎬 Effect များ ထည့်သွင်းနေသည်...")
                final_segments = []
                for i in range(0, int(clip.duration), 6):
                    # 3s regular play
                    p_clip = clip.subclip(i, min(i+3, clip.duration))
                    final_segments.append(p_clip)
                    
                    # 3s freeze & zoom
                    if i+3 < clip.duration:
                        freeze_frame = clip.to_ImageClip(i+3).set_duration(3)
                        # Zoom effect (အရွယ်အစားကို တဖြည်းဖြည်းကြီးအောင်လုပ်ခြင်း)
                        zoomed = freeze_frame.resize(lambda t: 1 + 0.03 * t) 
                        final_segments.append(zoomed)
                
                final_video = CompositeVideoClip(final_segments)

                # 4. မြန်မာအသံ AI နှင့် ထုတ်လုပ်ခြင်း
                st.write("🎙️ မြန်မာအသံ (AI) ဖန်တီးနေသည်...")
                audio_path = "voice.mp3"
                asyncio.run(generate_voice(dubbing_text, audio_path))
                
                # အသံကို ဗီဒီယိုထဲ ထည့်သွင်းခြင်း
                from moviepy.editor import AudioFileClip
                new_audio = AudioFileClip(audio_path)
                final_video = final_video.set_audio(new_audio.set_duration(final_video.duration))

                # 5. ဗီဒီယိုဖိုင်အဖြစ် သိမ်းဆည်းခြင်း
                output_path = "final_output.mp4"
                final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)
                
                st.video(output_path)
                with open(output_path, "rb") as f:
                    st.download_button("ဗီဒီယိုကို ဒေါင်းလုဒ်လုပ်ရန်", f, file_name="ai_edited_video.mp4")
                
                st.success("အားလုံးပြီးစီးပါပြီ!")
                
            except Exception as e:
                st.error(f"အမှားဖြစ်သွားပါသည်: {str(e)}")

# ပိုလျှံနေသော File များကို ရှင်းထုတ်ခြင်း
if os.path.exists("voice.mp3"):
    os.remove("voice.mp3")
