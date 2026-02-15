import streamlit as st
import requests
import base64
import re

# --- 1. API 配置 ---
API_KEY = "sk-BS5021722d9245446fa96b948b2794abf1851a27142f8wVe"
# 尝试使用官方示例的路径
API_URL = "https://api.gptsapi.net/v1beta/models/gemini-3-pro-preview:generateContent"

def file_to_base64(uploaded_file):
    if uploaded_file:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return None

st.set_page_config(page_title="Banana 调试版", layout="centered")
st.title("🎨 模块：换主体 (Debug)")

f1 = st.file_uploader("上传图 1 (背景)", type=['png', 'jpg', 'jpeg'])
f2 = st.file_uploader("上传图 2 (主体)", type=['png', 'jpg', 'jpeg'])

if st.button("开始生成", use_container_width=True):
    if f1 and f2:
        with st.status("Banana 引擎重组中...", expanded=True) as status:
            try:
                b1 = file_to_base64(f1)
                b2 = file_to_base64(f2)

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

                headers = {
                    "x-goog-api-key": API_KEY, 
                    "Content-Type": "application/json"
                }

                # 发送请求
                response = requests.post(API_URL, headers=headers, json=payload, timeout=300)
                
                # --- 核心调试代码：检查返回状态 ---
                if response.status_code != 200:
                    st.error(f"❌ API 请求失败！状态码: {response.status_code}")
                    st.text("后台返回内容:")
                    st.code(response.text) # 这里会显示具体的错误信息（比如余额不足或模型不支持）
                    status.update(label="处理失败", state="error")
                    st.stop()

                # 只有状态码为 200 才尝试解析 JSON
                res_data = response.json()

                # --- 结果过滤：只看图片 ---
                if "candidates" in res_data:
                    parts = res_data['candidates'][0]['content']['parts']
                    found = False
                    for part in parts:
                        if "text" in part:
                            # 提取图片链接
                            urls = re.findall(r'!\[.*?\]\((https?://.*?)\)', part["text"])
                            for url in urls:
                                st.image(url, caption="生成结果")
                                found = True
                        elif "inlineData" in part:
                            st.image(f"data:image/jpeg;base64,{part['inlineData']['data']}")
                            found = True
                    
                    if found:
                        status.update(label="生成成功！", state="complete")
                    else:
                        st.warning("模型返回了消息，但没找到图片链接。")
                        st.write(res_data) # 显示完整 JSON 方便排查

            except Exception as e:
                st.error(f"程序运行崩溃: {str(e)}")
                # 如果是 JSON 解析错误，打印原始 text
                if 'response' in locals():
                    st.text("原始返回文本:")
                    st.code(response.text)

st.markdown("<p style='text-align:center; color:grey; margin-top:50px;'>输出图片窗口</p>", unsafe_allow_html=True)
