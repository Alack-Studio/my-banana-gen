import streamlit as st
import requests
import base64
import re

# --- 1. API 配置 ---
API_KEY = "sk-BS5021722d9245446fa96b948b2794abf1851a27142f8wVe"
API_URL = "https://api.gptsapi.net/v1beta/models/gemini-3-pro-preview:generateContent"

def file_to_base64(uploaded_file):
    if uploaded_file:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return None

# --- 2. 页面布局 ---
st.set_page_config(page_title="Banana 合成器", layout="centered")
st.title("🎨 模块：换主体")

# 上传组件
c1, c2 = st.columns(2)
with c1:
    f1 = st.file_uploader("上传图 1 (背景)", type=['png', 'jpg', 'jpeg'])
with c2:
    f2 = st.file_uploader("上传图 2 (主体)", type=['png', 'jpg', 'jpeg'])

st.divider()

# --- 3. 生成与过滤逻辑 ---
if st.button("开始生成", use_container_width=True, type="primary"):
    if f1 and f2:
        with st.status("正在处理...", expanded=False) as status:
            try:
                b1 = file_to_base64(f1)
                b2 = file_to_base64(f2)

                # 保持原本提示词不变
                prompt = "我上传了两张图片，分别为图1和图2。请将图2的主体提取出，并将其放置在图1的背景中，根据要求完成主体替换。要求：保持图1的主体姿势与表情。新生成的图片比例不限"

                payload = {
                    "contents": [{
                        "role": "user",
                        "parts": [
                            {"text": prompt},
                            {"inlineData": {"mimeType": "image/jpeg", "data": b1}},
                            {"inlineData": {"mimeType": "image/jpeg", "data": b2}}
                        ]
                    }]
                }

                headers = {"x-goog-api-key": API_KEY, "Content-Type": "application/json"}
                response = requests.post(API_URL, headers=headers, json=payload, timeout=180)
                res_data = response.json()

                # --- 4. 核心：只提取图片 ---
                st.empty() # 清空之前的状态
                if "candidates" in res_data:
                    parts = res_data['candidates'][0]['content']['parts']
                    
                    found_image = False
                    for part in parts:
                        # 识别方式 1：提取 Markdown 中的图片链接
                        if "text" in part:
                            # 使用正则匹配 ![] (url)
                            urls = re.findall(r'!\[.*?\]\((.*?)\)', part["text"])
                            for url in urls:
                                st.subheader("生成结果")
                                st.image(url, use_container_width=True)
                                found_image = True
                        
                        # 识别方式 2：直接返回的 Base64 数据
                        elif "inlineData" in part:
                            img_data = part["inlineData"]["data"]
                            st.subheader("生成结果")
                            st.image(f"data:image/jpeg;base64,{img_data}", use_container_width=True)
                            found_image = True
                    
                    if not found_image:
                        st.error("模型未返回有效图片，请重试。")
                
                status.update(label="处理完成！", state="complete")

            except Exception as e:
                st.error(f"处理出错: {e}")
    else:
        st.warning("请上传图片")

st.markdown("<br><br><p style='text-align:center; color:grey;'>输出图片窗口</p>", unsafe_allow_html=True)
