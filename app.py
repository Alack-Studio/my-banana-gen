import streamlit as st
import requests
import base64
from io import BytesIO

# --- 配置区 (请妥善保管你的 Key) ---
API_KEY = "sk-BS5021722d9245446fa96b948b2794abf1851a27142f8wVe"
API_URL = "https://api.gptsapi.net/v1/chat/completions"
# 优先使用 Pro 预览版以获得 100% 还原效果
MODEL_NAME = "gemini-3-pro-preview" 

# --- 辅助函数：处理图片 ---
def file_to_base64(uploaded_file):
    if uploaded_file:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return None

# --- UI 设计 ---
st.set_page_config(page_title="Banana 智能换主体", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #FFD700; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍌 Nano Banana 专业图像合成")
st.info("模式：主体完美替换 (100% 还原身份一致性)")

# --- 上传区域 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🖼️ 图 1：背景与姿势")
    bg_file = st.file_uploader("上传背景图片", type=['png', 'jpg', 'jpeg'])
    if bg_file:
        st.image(bg_file, use_container_width=True, caption="背景参考")

with col2:
    st.subheader("👤 图 2：目标主体")
    subject_file = st.file_uploader("上传主体图片", type=['png', 'jpg', 'jpeg'])
    if subject_file:
        st.image(subject_file, use_container_width=True, caption="提取主体参考")

st.divider()

# --- 生成逻辑 ---
if st.button("开始 Banana 智能生成"):
    if not bg_file or not subject_file:
        st.warning("请先上传两张图片再进行操作。")
    else:
        with st.spinner("Banana Pro 正在进行 4K 级图像重组..."):
            try:
                # 转换图片
                img1_b64 = file_to_base64(bg_file)
                img2_b64 = file_to_base64(subject_file)

                # 预设提示词 (这就是你说的“提示词提前写入”)
                # 针对 Gemini 3 的 "Thinking" 逻辑进行了优化
                system_prompt = (
                    "我上传了两张图片，分别为图1和图2。请将图2的主体提取出，并将其放置在图1的背景中，"
                    "根据要求完成主体替换。要求：必须100%保持图2主体的身份特征、面部细节和材质；"
                    "同时保持图1的主体姿势与表情。新生成的图片比例不限。请直接返回生成的图像。"
                )

                # 构造符合 Gemini-3-Preview 标准的请求
                payload = {
                    "model": MODEL_NAME,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": system_prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img1_b64}"}},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img2_b64}"}}
                            ]
                        }
                    ],
                    "response_format": { "type": "image" } # 强制要求返回图像格式
                }

                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                }

                response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
                res_data = response.json()

                # --- 结果展示 ---
                st.subheader("✨ 生成结果")
                
                # 处理常见的两种 API 返回结果：链接 或 Base64
                if "choices" in res_data:
                    content = res_data['choices'][0]['message']['content']
                    
                    # 如果返回的是图片链接格式 (Markdown)
                    if "![" in content:
                        st.markdown(content)
                    # 如果返回的是纯 Base64 或特定字段
                    elif "data:image" in content:
                        st.image(content)
                    else:
                        st.write(content)
                else:
                    st.error("API 返回异常，请检查配额或模型状态。")
                    st.json(res_data)

            except Exception as e:
                st.error(f"发生错误: {str(e)}")

# --- 页脚 ---
st.caption("技术支持：Gemini-3-Pro (Banana Pro Mode) | 2026")
