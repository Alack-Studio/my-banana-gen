import streamlit as st
import requests
import base64
import json

# --- 1. 严格根据官方示例配置 API ---
API_KEY = "sk-BS5021722d9245446fa96b948b2794abf1851a27142f8wVe"
# 官方端点地址
API_URL = "https://api.gptsapi.net/v1beta/models/gemini-3-pro-preview:generateContent"

def file_to_base64(uploaded_file):
    if uploaded_file:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return None

# --- 2. UI 界面 ---
st.set_page_config(page_title="Banana 官方接口版", layout="centered")
st.title("🍌 Nano Banana 图像合成")
st.caption("使用 gemini-3-pro-preview 官方原生接口")

col1, col2 = st.columns(2)
with col1:
    file1 = st.file_uploader("上传图 1 (背景)", type=['png', 'jpg', 'jpeg'])
    if file1: st.image(file1, caption="背景参考")

with col2:
    file2 = st.file_uploader("上传图 2 (主体)", type=['png', 'jpg', 'jpeg'])
    if file2: st.image(file2, caption="主体参考")

# --- 3. 核心生成逻辑 ---
if st.button("🚀 执行 Banana 智能合成", use_container_width=True):
    if file1 and file2:
        with st.spinner("正在通过原生接口进行 100% 还原合成..."):
            try:
                # 转换图片为 Base64
                b1 = file_to_base64(file1)
                b2 = file_to_base64(file2)

                # 【保持不变】你的原始提示词
                user_prompt = "我上传了两张图片，分别为图1和图2。请将图2的主体提取出，并将其放置在图1的背景中，根据要求完成主体替换。要求：保持图1的主体姿势与表情。新生成的图片比例不限"

                # --- 4. 构造符合官方示例的 Payload ---
                payload = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {"text": user_prompt},
                                {
                                    "inlineData": {
                                        "mimeType": "image/jpeg",
                                        "data": b1
                                    }
                                },
                                {
                                    "inlineData": {
                                        "mimeType": "image/jpeg",
                                        "data": b2
                                    }
                                }
                            ]
                        }
                    ]
                }

                # --- 5. 构造符合官方示例的 Headers ---
                headers = {
                    "x-goog-api-key": API_KEY,  # 注意这里不是 Authorization
                    "Content-Type": "application/json"
                }

                # 发送请求
                response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
                res_data = response.json()

                st.markdown("---")
                st.subheader("✨ 输出图片窗口")

                # --- 6. 解析原生返回格式 ---
                if "candidates" in res_data:
                    # 获取模型输出的内容部分
                    parts = res_data['candidates'][0]['content']['parts']
                    
                    for part in parts:
                        # 如果返回的是文字（包含生图链接）
                        if "text" in part:
                            st.write(part["text"])
                        # 如果返回的是直接的图片数据（Banana 原生输出）
                        elif "inlineData" in part:
                            img_data = part["inlineData"]["data"]
                            st.image(f"data:image/jpeg;base64,{img_data}")
                else:
                    st.error("接口调用失败，请检查 API Key 或余额。")
                    st.json(res_data) # 打印错误日志方便调试

            except Exception as e:
                st.error(f"发生异常: {str(e)}")
    else:
        st.warning("请上传完整图片。")
