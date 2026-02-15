import streamlit as st
import requests
import base64
import re
import json

# --- 1. API 配置 (严格按照你的截图) ---
API_KEY = "sk-BS5021722d9245446fa96b948b2794abf1851a27142f8wVe"
API_URL = "https://api.gptsapi.net/v1beta/models/gemini-3-pro-preview:generateContent"

def file_to_base64(uploaded_file):
    if uploaded_file:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return None

# --- 2. 网页 UI ---
st.set_page_config(page_title="Banana 换主体", layout="centered")

st.markdown("""
    <style>
    div.stButton > button {
        background-color: #ff4b4b !important;
        color: white !important;
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎨 模块：换主体")

c1, c2 = st.columns(2)
with c1:
    f1 = st.file_uploader("上传图 1 (背景)", type=['png', 'jpg', 'jpeg'])
with c2:
    f2 = st.file_uploader("上传图 2 (主体)", type=['png', 'jpg', 'jpeg'])

st.divider()

# --- 3. 生成与深度解析逻辑 ---
if st.button("开始生成"):
    if f1 and f2:
        status_box = st.status("Banana 引擎处理中...", expanded=True)
        try:
            b1 = file_to_base64(f1)
            b2 = file_to_base64(f2)

            # 保持你的原始提示词
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
            response = requests.post(API_URL, headers=headers, json=payload, timeout=300)
            res_data = response.json()

            # --- 4. 暴力提取图片 ---
            found_image = False
            
            if "candidates" in res_data:
                parts = res_data['candidates'][0]['content']['parts']
                
                # 创建一个结果容器，只放图
                result_container = st.container()
                
                for part in parts:
                    # 识别 A：Base64 数据
                    if "inlineData" in part:
                        img_b64 = part["inlineData"]["data"]
                        result_container.image(f"data:image/jpeg;base64,{img_b64}", caption="生成结果")
                        found_image = True
                    
                    # 识别 B：提取文字中的所有 URL
                    elif "text" in part:
                        text_content = part["text"]
                        
                        # 匹配 Markdown 图片: ![..](url)
                        md_urls = re.findall(r'!\[.*?\]\((https?://.*?)\)', text_content)
                        # 匹配 纯文本中的图片链接 (jpg, png, webp 等)
                        raw_urls = re.findall(r'(https?://[^\s)"]+(?:\.jpg|\.png|\.jpeg|\.webp))', text_content)
                        
                        all_urls = list(set(md_urls + raw_urls))
                        for url in all_urls:
                            result_container.image(url, caption="生成结果")
                            found_image = True

                if not found_image:
                    status_box.update(label="未找到生成图片", state="error")
                    st.warning("⚠️ 模型返回了文字但没出图。以下是模型返回的原始信息，请检查是否包含图片链接：")
                    st.info(parts[0].get("text", "无文本返回"))
                else:
                    status_box.update(label="处理完成！", state="complete")
            else:
                st.error("接口未返回有效 candidate 数据")
                st.json(res_data)

        except Exception as e:
            st.error(f"发生错误: {str(e)}")
    else:
        st.warning("请上传图片")

st.markdown("<p style='text-align:center; color:grey; margin-top:50px;'>输出图片窗口</p>", unsafe_allow_html=True)
