import streamlit as st
import requests
import base64
import json

# --- 配置区 ---
API_KEY = "sk-BS5021722d9245446fa96b948b2794abf1851a27142f8wVe"
API_URL = "https://api.gptsapi.net/v1/chat/completions"
# 提示：如果这个模型返回 JSON，尝试确认 API 是否有后缀，如 "gemini-3-pro-preview-image"
MODEL_NAME = "gemini-3-pro-preview" 

def file_to_base64(uploaded_file):
    if uploaded_file:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return None

st.set_page_config(page_title="Banana 智能合成", layout="centered")
st.title("🍌 Nano Banana 图像合成工具")

# --- UI 模块 ---
col1, col2 = st.columns(2)
with col1:
    bg_file = st.file_uploader("上传图 1 (背景)", type=['png', 'jpg', 'jpeg'])
    if bg_file: st.image(bg_file, caption="图 1")

with col2:
    subject_file = st.file_uploader("上传图 2 (主体)", type=['png', 'jpg', 'jpeg'])
    if subject_file: st.image(subject_file, caption="图 2")

# --- 核心逻辑 ---
if st.button("开始生成", use_container_width=True):
    if bg_file and subject_file:
        with st.spinner("Banana 正在执行生图指令..."):
            try:
                img1_b64 = file_to_base64(bg_file)
                img2_b64 = file_to_base64(subject_file)

                # 【保持不变】你的原始提示词
                user_prompt = "我上传了两张图片，分别为图1和图2。请将图2的主体提取出，并将其放置在图1的背景中，根据要求完成主体替换。要求：保持图1的主体姿势与表情。新生成的图片比例不限"

                payload = {
                    "model": MODEL_NAME,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img1_b64}"}},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img2_b64}"}}
                            ]
                        }
                    ],
                    # 关键配置：尝试关闭工具调用，迫使模型在当前 turn 直接渲染
                    "tool_choice": "none" 
                }

                response = requests.post(
                    API_URL, 
                    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                    json=payload
                )
                res_data = response.json()

                st.subheader("输出图片窗口")

                # 解析逻辑
                if "choices" in res_data:
                    content = res_data['choices'][0]['message']['content']
                    
                    # 情况 A：模型返回了 JSON（即你刚才遇到的情况）
                    if '"arguments"' in content or '"name"' in content:
                        st.info("模型正在通过 Nano Banana 引擎进行像素级合成...")
                        # 在某些中转 API 中，这种 JSON 其实是后台生图的『排队凭证』
                        # 我们直接把 JSON 解析出来，看看里面有没有直接能用的链接
                        try:
                            # 尝试美化显示，或者根据接口文档看是否需要第二次请求
                            st.json(content)
                            st.warning("如果此处未直接显示图片，请确认 WildCard 的该模型是否需要单独的 -image 后缀。")
                        except:
                            st.write(content)
                    
                    # 情况 B：模型直接返回了 Markdown 链接或 Base64
                    elif "![" in content:
                        st.markdown(content)
                    else:
                        # 尝试将 content 作为图片 URL 或文字直接显示
                        st.write(content)
                else:
                    st.error("API 未能按预期返回结果")
                    st.json(res_data)

            except Exception as e:
                st.error(f"处理出错: {str(e)}")
    else:
        st.warning("请上传完整图片。")
