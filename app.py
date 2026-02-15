import streamlit as st
import requests
import base64
import json
import re

# --- 1. API 配置 ---
API_KEY = "sk-BS5021722d9245446fa96b948b2794abf1851a27142f8wVe"
# Gemini 指挥官地址
GEMINI_URL = "https://api.gptsapi.net/v1beta/models/gemini-3-pro-preview:generateContent"
# DALL-E 3 执行引擎地址 (通常是这个路径，请根据你后台示例确认)
DALLE_URL = "https://api.gptsapi.net/v1/images/generations"

def file_to_base64(uploaded_file):
    if uploaded_file:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return None

# --- 2. 网页 UI ---
st.set_page_config(page_title="Banana 换主体", layout="centered")
st.markdown("<style>div.stButton > button {background-color: #ff4b4b; color: white; width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold;}</style>", unsafe_allow_html=True)
st.title("🎨 模块：换主体")

c1, c2 = st.columns(2)
with c1:
    f1 = st.file_uploader("上传图 1 (背景)", type=['png', 'jpg', 'jpeg'])
with c2:
    f2 = st.file_uploader("上传图 2 (主体)", type=['png', 'jpg', 'jpeg'])

st.divider()

# --- 3. 核心自动化工作流 ---
if st.button("开始生成"):
    if f1 and f2:
        with st.status("Banana 引擎重组中...", expanded=True) as status:
            try:
                b1 = file_to_base64(f1)
                b2 = file_to_base64(f2)

                # 第一步：调用 Gemini 获取生图指令
                prompt = "我上传了两张图片，分别为图1和图2。请将图2的主体提取出，并将其放置在图1的背景中，根据要求完成主体替换。要求：保持图1的主体姿势与表情。新生成的图片比例不限"
                
                gemini_payload = {
                    "contents": [{"role": "user", "parts": [
                        {"text": prompt},
                        {"inlineData": {"mimeType": "image/jpeg", "data": b1}},
                        {"inlineData": {"mimeType": "image/jpeg", "data": b2}}
                    ]}]
                }
                
                res = requests.post(GEMINI_URL, headers={"x-goog-api-key": API_KEY}, json=gemini_payload)
                res_data = res.json()

                # 解析 Gemini 返回的内容
                raw_text = res_data['candidates'][0]['content']['parts'][0]['text']
                
                # 第二步：检测是否包含生图指令 (img_gen)
                if '"action": "img_gen"' in raw_text:
                    status.write("✨ 已生成精准合成指令，正在渲染图像...")
                    
                    # 提取指令里的 Prompt
                    action_data = json.loads(raw_text)
                    inner_input = json.loads(action_data['action_input'])
                    final_prompt = inner_input.get('prompt', '')

                    # 第三步：调用 DALL-E 3 进行物理生图
                    dalle_payload = {
                        "model": "dall-e-3",
                        "prompt": final_prompt,
                        "n": 1,
                        "size": "1024x1024" # 或者根据 inner_input['aspect_ratio'] 换算
                    }
                    
                    # 注意：DALL-E 3 通常使用 Authorization Bearer 鉴权
                    dalle_res = requests.post(
                        DALLE_URL, 
                        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                        json=dalle_payload
                    )
                    dalle_data = dalle_res.json()

                    # 展示最终图片
                    if "data" in dalle_data:
                        img_url = dalle_data['data'][0]['url']
                        st.subheader("生成结果")
                        st.image(img_url, use_container_width=True)
                        status.update(label="处理完成！", state="complete")
                    else:
                        st.error("DALL-E 3 渲染失败")
                        st.json(dalle_data)
                else:
                    # 如果没有指令，看看是不是直接给了图片链接
                    urls = re.findall(r'https?://[^\s)"]+(?:\.jpg|\.png|\.jpeg)', raw_text)
                    if urls:
                        st.image(urls[0], use_container_width=True)
                        status.update(label="处理完成！", state="complete")
                    else:
                        st.warning("未能触发合成引擎，请重试。")
                        st.write(raw_text)

            except Exception as e:
                st.error(f"发生错误: {str(e)}")
    else:
        st.warning("请上传图片")

st.markdown("<p style='text-align:center; color:grey; margin-top:50px;'>输出图片窗口</p>", unsafe_allow_html=True)
