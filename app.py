import streamlit as st
import requests
import base64
import json

# --- API 配置 ---
API_KEY = "sk-BS5021722d9245446fa96b948b2794abf1851a27142f8wVe"

# 1. "大脑"模型：负责看图并生成指令
# 使用你提供的官方原生接口路径
BRAIN_URL = "https://api.gptsapi.net/v1beta/models/gemini-3-pro-preview:generateContent"

# 2. "画师"模型：负责根据指令直接出图
# 使用你截图中发现的专业生图接口
PAINTER_URL = "https://api.gptsapi.net/api/v3/google/gemini-3-pro-image-preview/text-to-image"

def file_to_base64(uploaded_file):
    if uploaded_file:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return None

# --- 网页 UI ---
st.set_page_config(page_title="Banana Pro 图像合成", layout="centered")
st.title("🎨 模块：换主体 (专业版)")

c1, c2 = st.columns(2)
with c1:
    f1 = st.file_uploader("上传图 1 (背景)", type=['png', 'jpg', 'jpeg'])
with c2:
    f2 = st.file_uploader("上传图 2 (主体)", type=['png', 'jpg', 'jpeg'])

st.divider()

# --- 核心自动化流程 ---
if st.button("开始生成", use_container_width=True, type="primary"):
    if f1 and f2:
        # 使用 status 组件让过程对用户透明，只显示最终结果
        with st.status("正在进行像素级合成...", expanded=False) as status:
            try:
                b1 = file_to_base64(f1)
                b2 = file_to_base64(f2)
                prompt = "我上传了两张图片，分别为图1和图2。请将图2的主体提取出，并将其放置在图1的背景中，根据要求完成主体替换。要求：保持图1的主体姿势与表情。新生成的图片比例不限"
                
                # --- 第一步：大脑分析 (用户无感) ---
                brain_payload = {
                    "contents": [{"role": "user", "parts": [
                        {"text": prompt},
                        {"inlineData": {"mimeType": "image/jpeg", "data": b1}},
                        {"inlineData": {"mimeType": "image/jpeg", "data": b2}}
                    ]}]
                }
                # 注意：大脑模型使用 x-goog-api-key
                res_brain = requests.post(BRAIN_URL, headers={"x-goog-api-key": API_KEY}, json=brain_payload)
                raw_text = res_brain.json()['candidates'][0]['content']['parts'][0]['text']
                
                # 自动解析 JSON 指令，提取提示词
                action_data = json.loads(raw_text)
                inner_input = json.loads(action_data['action_input'])
                final_prompt = inner_input.get('prompt', '')

                # --- 第二步：画师生图 (核心步骤) ---
                # 直接调用你截图中的专业接口
                painter_payload = {
                    "prompt": final_prompt,
                    "aspect_ratio": "3:4", # 可以根据需要调整
                    "output_format": "png"
                }
                # 注意：画师模型使用 Authorization: Bearer
                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                }
                
                res_painter = requests.post(PAINTER_URL, headers=headers, json=painter_payload)
                painter_data = res_painter.json()

                # --- 第三步：展示结果 ---
                if painter_data.get("code") == 200:
                    # 从返回结果中提取图片链接
                    img_url = painter_data["data"]["urls"]["get"]
                    st.subheader("生成结果")
                    st.image(img_url, use_container_width=True)
                    status.update(label="处理完成！", state="complete", expanded=True)
                else:
                    st.error(f"生图失败: {painter_data.get('message', '未知错误')}")
                    status.update(label="处理失败", state="error")

            except Exception as e:
                st.error(f"发生错误: {str(e)}")
                # 仅在调试时取消注释下面这行，查看原始错误信息
                # st.write("Debug Info:", raw_text if 'raw_text' in locals() else "Brain request failed")
                status.update(label="发生错误", state="error")
    else:
        st.warning("请先上传两张图片。")

st.markdown("<p style='text-align:center; color:grey; margin-top:50px;'>输出图片窗口</p>", unsafe_allow_html=True)
