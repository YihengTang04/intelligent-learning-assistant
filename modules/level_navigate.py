import streamlit as st
from collections import defaultdict
import json
from common.utils import llm_chat

def level_navigate(nodes, node_id2name):
    st.subheader("🧭 智能知识体系层级导航（基于个人学习数据AI定制学习路线 | 多维度学情加权分析）")
    if not st.session_state.login_username:
        st.warning("请先登录账号查看数据")
        return
    user_data = st.session_state.user_learn_data
    progress = user_data["learning_progress"]
    level_info = defaultdict(lambda: {"all": 0, "learned": 0, "unlearn": [], "avg_score": 0.0, "total_score": 0})
    for n in nodes:
        lid = n["id"]
        lev = n["level"]
        level_info[lev]["all"] += 1
        up = [p for p in progress if p["node_id"] == lid][0]
        status_up = up.get("status", "未学习")
        score_up = up.get("score", 0)
        if status_up == "已学习":
            level_info[lev]["learned"] += 1
            level_info[lev]["total_score"] += score_up
        else:
            level_info[lev]["unlearn"].append(n["name"])
    for k in level_info:
        if level_info[k]["learned"] > 0:
            level_info[k]["avg_score"] = round(level_info[k]["total_score"] / level_info[k]["learned"], 2)
        else:
            level_info[k]["avg_score"] = 0
    level_summary = str(dict(level_info))
    ai_prompt = f"用户深度学习三层级学习数据{level_summary}，依据掌握程度，智能推荐接下来优先学习的层级与知识点顺序，简短建议"
    st.info("🤖AI智能学习层级推荐：" + llm_chat(ai_prompt))
    st.info("📊层级学情汇总：" + json.dumps(dict(level_info), ensure_ascii=False))
    levels = ["基础理论", "进阶模型", "项目实战"]
    select_level = st.radio("选择浏览层级", levels)
    st.markdown(
        f"### {select_level} ｜本层总知识点{level_info[select_level]['all']}个，已掌握{level_info[select_level]['learned']}个，已学内容平均分：{level_info[select_level]['avg_score']}")
    for n in nodes:
        if n["level"] == select_level:
            nid = n["id"]
            p_data = [p for p in progress if p["node_id"] == nid][0]
            tag = "🟢已学习" if p_data.get("status") == "已学习" else "🔘未学习"
            st.write(f'{tag} ID:{n["id"]} | {n["name"]}：{n["desc"]}')
    st.divider()
    un_list = level_info[select_level]['unlearn']
    st.warning(f"本层级待攻克知识点：{','.join(un_list) if un_list else '本层级全部学完'}")
