import streamlit as st
from common.utils import llm_chat

def search_knowledge(keyword, nodes):
    st.subheader("🔍 大模型智能知识点检索结果 | 多维度本体语义匹配引擎")
    if not keyword:
        st.write("ℹ️ 请输入关键词进行检索")
        return
    exact_match = []
    name_fuzzy = []
    desc_fuzzy = []
    for n in nodes:
        if keyword == n["name"]:
            exact_match.append(n)
        elif keyword in n["name"]:
            name_fuzzy.append(n)
        elif keyword in n["desc"]:
            desc_fuzzy.append(n)
    raw_res = exact_match + name_fuzzy + desc_fuzzy
    ai_prompt = f"""现有深度学习知识点列表：{[x['name']+":"+x['desc'] for x in nodes]}，用户查询关键词：{keyword}，筛选语义相关知识点名称，只返回名称逗号分隔"""
    ai_text = llm_chat(ai_prompt)
    st.info("🤖大模型语义联想：" + ai_text)
    st.info(f"检索分层统计：精准命中{len(exact_match)}个｜名称模糊命中{len(name_fuzzy)}个｜释义关联命中{len(desc_fuzzy)}个")
    if raw_res:
        for item in raw_res:
            st.write(f'ID:{item["id"]} | 名称：{item["name"]} | 层级：{item["level"]} | 说明：{item["desc"]}')
    else:
        st.write("⚠️ 未查询到对应知识点")
