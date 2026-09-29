import streamlit as st
from common.utils import llm_chat

def project_trace(project_id, proj_data):
    st.subheader("🔎 实操项目知识溯源推演+AI原理总结 | 多组对照实验数据分析模块")
    pid = str(project_id)
    if pid not in proj_data:
        st.write("⚠️ 暂无该项目数据")
        return
    proj = proj_data[pid]
    st.write(f"### 项目名称：{proj['project_name']}")
    core_k = ','.join(proj['core_knowledge'])
    st.write(f"**核心知识点**：{core_k}")
    ai_prompt = f"项目{proj['project_name']}依赖知识点{core_k}，简要说明项目实现原理与学习要点"
    st.info("🤖AI项目原理总结：" + llm_chat(ai_prompt))
    st.divider()
    st.write("#### 参数运行效果对比（控制变量法多轮实验汇总）")
    for k, v in proj["param_compare"].items():
        st.write(f"- {k}：{v}")
    st.divider()
    st.write("#### 不同模型效果对比（同等实验环境对照）")
    for k, v in proj["model_effect"].items():
        st.write(f"- {k}：{v}")
