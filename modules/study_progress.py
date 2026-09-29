import streamlit as st
import json
import datetime
from common.utils import get_user_file

def show_learning_progress(node_id2name, all_node_id_list):
    st.subheader(f"📈 【{st.session_state.login_username}】个人学习进度全维度统计系统")
    st.info("💡 修改知识点得分/学习状态后自动保存并同步至【4 薄弱点智能诊断】；已学习且分数≥60会自动减少对应薄弱数量")
    if not st.session_state.login_username:
        st.warning("请先登录账号查看与修改进度")
        return
    user_data = st.session_state.user_learn_data
    user_file = get_user_file(st.session_state.login_username)
    progress_list = user_data["learning_progress"]
    user = user_data["user_info"]
    total = user["total_nodes"]
    finish = user["finished_nodes"]
    progress_percent = finish / total * 100
    all_score = [i.get("score", 0) for i in progress_list if i.get("status") == "已学习"]
    avg_score = round(sum(all_score) / len(all_score), 2) if len(all_score) > 0 else 0
    st.write(f"总知识点：{total} | 已完成：{finish} | 完成率：{progress_percent:.1f}% | 已学内容平均得分：{avg_score}")
    progress_html = f"""
    <div style="width:100%; height:12px; background:#e8e8e8; border-radius:6px; overflow:hidden;">
        <div style="width:{progress_percent}%; height:100%; background:#2E86AB;"></div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)
    st.divider()
    for item in progress_list:
        name = node_id2name[item["node_id"]]
        status = item.get("status", "未学习")
        score = item.get("score", 0)
        study_cnt = item.get("study_times", 0)
        color = "🟢" if status == "已学习" else "🔘"
        st.write(f"{color} {name} | 状态：{status} | 答题得分：{score} | 累计学习次数：{study_cnt}")
    st.divider()
    st.markdown("### 修改知识点学习状态与答题得分（修改实时同步至薄弱诊断模块）")
    all_names = [node_id2name[item["node_id"]] for item in progress_list]
    select_name = st.selectbox("选择要更新的知识点", all_names)
    input_score = st.number_input("填写答题得分", min_value=0, max_value=100, value=80)
    col1, col2 = st.columns(2)
    with col1:
        save_btn = st.button("确认更新并保存", type="primary")
    with col2:
        cancel_btn = st.button("取消该知识点学习（变回未学习）")
    if save_btn:
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        node_name2id = {v: k for k, v in node_id2name.items()}
        target_nid = node_name2id[select_name]
        for item in progress_list:
            if item["node_id"] == target_nid:
                item["status"] = "已学习"
                item["score"] = input_score
                if "study_times" not in item:
                    item["study_times"] = 0
                item["study_times"] += 1
                item["last_learn_time"] = now_time
        new_finish = sum(1 for i in progress_list if i.get("status") == "已学习")
        user_data["user_info"]["finished_nodes"] = new_finish
        user_data["user_info"]["last_study_date"] = now_time.split(" ")[0]
        with open(user_file, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
        st.session_state.user_learn_data = user_data
        if input_score >= 60:
            st.success("✅ 更新成功！该知识点分数及格，已从薄弱列表移除，数据同步至【4 薄弱点智能诊断】，切换菜单栏4查看更新后薄弱数量")
        else:
            st.success("✅ 更新成功！该知识点分数不足60，仍保留在薄弱列表，数据同步至【4 薄弱点智能诊断】，切换菜单栏4查看")
        st.rerun()
    if cancel_btn:
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        node_name2id = {v: k for k, v in node_id2name.items()}
        target_nid = node_name2id[select_name]
        for item in progress_list:
            if item["node_id"] == target_nid:
                item["status"] = "未学习"
                item["score"] = 0
        new_finish = sum(1 for i in progress_list if i.get("status") == "已学习")
        user_data["user_info"]["finished_nodes"] = new_finish
        with open(user_file, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
        st.session_state.user_learn_data = user_data
        st.success("🔘 取消学习成功！该知识点重新计入薄弱统计，数据同步至【4薄弱点智能诊断】，切换左侧菜单栏4查看最新薄弱分析")
        st.rerun()
