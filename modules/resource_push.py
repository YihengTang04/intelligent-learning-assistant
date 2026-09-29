import streamlit as st
from common.utils import llm_chat

def push_resource(node_name, node_name2id, res_data):
    st.subheader("📦 配套学习资源智能匹配模块")
    if node_name not in node_name2id:
        st.write("⚠️ 该知识点不存在")
        return
    nid = str(node_name2id[node_name])
    if nid not in res_data:
        st.warning("暂无本地资源，调用大模型实时生成学习资料")
        prompt = f"生成深度学习知识点{node_name}的实操代码、教学案例、课后练习题"
        ai_content = llm_chat(prompt)
        st.write(ai_content)
        return
    res = res_data[nid]
    st.write(f"### {res['name']} 资源包")
    st.code(res["code"], language="python")
    st.write(f"**教学案例**：{res['case']}")
    st.write(f"**课后习题**：{res['exercise']}")
