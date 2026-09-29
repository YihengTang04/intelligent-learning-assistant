import streamlit as st
from collections import defaultdict
import json

def show_knowledge_structure(nodes):
    st.subheader("📚 知识本体层级量化分析模块｜演示案例：深度学习知识点整体结构")
    st.info("💡 本平台为通用知识学习辅助框架，可替换知识库适配各类学科领域，当前仅以深度学习作为演示样例。")

    level_group = defaultdict(list)
    level_stat = defaultdict(lambda: {"count": 0, "desc_avg_len": 0})
    for n in nodes:
        level_group[n["level"]].append(n)
        level_stat[n["level"]]["count"] += 1
        level_stat[n["level"]]["desc_avg_len"] += len(n["desc"])
    for k in level_stat:
        level_stat[k]["desc_avg_len"] = round(level_stat[k]["desc_avg_len"] / level_stat[k]["count"], 2)

    # 替换原来的 st.info("📊 全知识库层级量化统计：" + json.dumps(dict(level_stat), ensure_ascii=False))
    import pandas as pd
    stat_table = []
    for lev, data in level_stat.items():
        stat_table.append({
            "知识层级": lev,
            "知识点数量": data["count"],
            "描述平均字符长度": data["desc_avg_len"]
        })
    df = pd.DataFrame(stat_table)
    st.info("📊 全知识库层级量化统计")
    st.dataframe(df, use_container_width=True)

    if "selected_know_node" not in st.session_state:
        st.session_state.selected_know_node = None

    for level, node_list in level_group.items():
        st.markdown(f"### {level} （知识点总数：{level_stat[level]['count']}，知识点释义平均字符长度：{level_stat[level]['desc_avg_len']}）")
        cols = st.columns(4)
        for idx, node in enumerate(node_list):
            with cols[idx % 4]:
                btn_text = f"【{node['id']}】{node['name']}"
                if st.button(btn_text, key=f"k_btn_{node['id']}"):
                    st.session_state.selected_know_node = node
        st.divider()

    if st.session_state.selected_know_node is not None:
        sel_node = st.session_state.selected_know_node
        with st.expander("🔍 当前选中知识点详情", expanded=True):
            st.markdown(f"**ID**: {sel_node['id']}")
            st.markdown(f"**知识点名称**: {sel_node['name']}")
            st.markdown(f"**所属层级**: {sel_node['level']}")
            st.markdown(f"**知识点描述**: {sel_node['desc']}")
            if st.button("清空选择"):
                st.session_state.selected_know_node = None
                st.rerun()
