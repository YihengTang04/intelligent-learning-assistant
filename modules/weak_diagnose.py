import streamlit as st
from collections import defaultdict
from common.utils import llm_api_call, llm_chat


def weak_point_diagnosis(G, nodes, node_id2name, res_data):
    # 新增：进入本页面初始化聊天；切走页面自动清空会话，避免DOM残留
    if "weak_chat" not in st.session_state:
        st.session_state["weak_chat"] = [
            {"role": "assistant", "content": "👋你好！AI学情助手已就绪，已读取你的全部学情数据。你可以提问：查看学情汇总、生成学习路径、查询某个知识点资料、生成3天学习计划。\n>提示：大模型接口异常会自动切换本地模板兜底。"}
        ]

    # ============【保留原来完整的薄弱点计算逻辑，全部不变】============
    user_data = st.session_state.user_learn_data
    progress_list = user_data["learning_progress"]
    error_list = user_data.get("error_record", [])
    node_weight_dict = {}
    for nd in nodes:
        nid = nd["id"]
        in_cnt = G.in_degree[nid]
        base_weight = 1.0 + in_cnt * 0.3
        if nd["level"] == "基础理论":
            base_weight *= 1.5
        elif nd["level"] == "进阶模型":
            base_weight *= 1.2
        else:
            base_weight *= 0.8
        node_weight_dict[nid] = base_weight

    error_count_map = defaultdict(int)
    for err in error_list:
        error_count_map[err["node_id"]] += 1

    weak_all_data = []
    for idx, item in enumerate(progress_list):
        n_id = item["node_id"]
        score = item.get("score", 0)
        status = item.get("status", "未学习")
        study_times = item.get("study_times", 0)
        err_cnt = error_count_map.get(n_id, 0)
        kname = node_id2name[n_id]
        weight = node_weight_dict[n_id]
        score_coeff = score / 100 if status == "已学习" else 0
        study_coeff = min(study_times / 3, 1.0) if study_times > 0 else 0
        error_coeff = min(err_cnt / 4, 1.0)
        weak_index = (1 - score_coeff) * weight * (1.1 - study_coeff) * (1 + error_coeff)
        succ_list = [node_id2name[s] for s in G.successors(n_id)]
        pre_list = [node_id2name[p] for p in G.predecessors(n_id)]
        if status == "已学习" and score >= 60:
            continue
        weak_all_data.append({
            "name": kname,
            "nid": n_id,
            "score": score,
            "status": status,
            "study_times": study_times,
            "error_times": err_cnt,
            "weak_index": round(weak_index, 3),
            "pre_depend": pre_list,
            "post_affect": succ_list
        })

    high_risk = [x for x in weak_all_data if x["weak_index"] >= 0.7]
    mid_risk = [x for x in weak_all_data if 0.35 <= x["weak_index"] < 0.7]
    low_risk = [x for x in weak_all_data if 0.15 <= x["weak_index"] < 0.35]
    total_weak_cnt = len(high_risk) + len(mid_risk) + len(low_risk)
    all_learn_score = [i["score"] for i in progress_list if i.get("status") == "已学习"]
    avg_total_score = round(sum(all_learn_score) / len(all_learn_score), 2) if all_learn_score else 0

    # DFS挖掘前置、拓扑排序
    all_weak_nid = set([w["nid"] for w in high_risk + mid_risk + low_risk])
    full_need_repair = set()

    def dfs_pre(node_id):
        preds = list(G.predecessors(node_id))
        for p in preds:
            if p not in full_need_repair:
                full_need_repair.add(p)
                dfs_pre(p)

    for wid in all_weak_nid:
        dfs_pre(wid)

    full_repair_list_id = list(full_need_repair.union(all_weak_nid))
    repair_order = []
    visited = set()

    def topo_sort(nid):
        if nid in visited:
            return
        visited.add(nid)
        for p in G.predecessors(nid):
            if p in full_repair_list_id:
                topo_sort(p)
        repair_order.append(nid)

    for n in full_repair_list_id:
        topo_sort(n)
    repair_name_list = [node_id2name[rid] for rid in repair_order]
    # ============【薄弱计算结束】============

    # 优化错题文本
    if error_list:
        err_text = "\n".join([f"{x['node_name']}：{x['error_content']}" for x in error_list])
    else:
        err_text = "暂无错题记录"

    if repair_name_list:
        repair_str = " → ".join(repair_name_list)
    else:
        repair_str = "暂无薄弱知识点，知识体系掌握良好"

    # 构造给大模型的全局学情上下文（每次对话带上这份背景）
    context_info = f"""
【用户学情上下文】
用户平均分:{avg_total_score}；高危薄弱{len(high_risk)}，中度{len(mid_risk)}，潜力{len(low_risk)}；
全部薄弱知识点：{[i['name'] for i in high_risk+mid_risk+low_risk]}
拓扑排序补全学习顺序：{repair_str}
错题记录：{err_text}
要求：你作为深度学习学情辅导助手，基于上面的学情数据回答用户问题，回答简洁，贴合学习，不要编造不存在知识点。
"""

    # 初始化聊天会话
    if "weak_chat" not in st.session_state:
        st.session_state["weak_chat"] = [
            {"role": "assistant", "content": "👋你好！AI学情助手已就绪，已读取你的全部学情数据。你可以提问：查看学情汇总、生成学习路径、查询某个知识点资料、生成3天学习计划。\n>提示：大模型接口异常会自动切换本地模板兜底。"}
        ]

    # 增加清空聊天按钮
    if st.button("清空AI对话历史"):
        st.session_state["weak_chat"] = [
            {"role": "assistant", "content": "👋你好！AI学情助手已就绪，已读取你的全部学情数据。你可以提问：查看学情汇总、生成学习路径、查询某个知识点资料、生成3天学习计划。\n>提示：大模型接口异常会自动切换本地模板兜底。"}
        ]
        st.rerun()

    # 渲染聊天框
    for msg in st.session_state["weak_chat"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("请向AI学情助手提问...")
    if user_input:
        st.session_state["weak_chat"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        # 调用API，带上完整学情上下文
        sys_prompt = "你是深度学习知识图谱学习助手，严格基于用户提供的学情上下文作答，输出中文，回答精炼。"
        full_user_prompt = context_info + "\n用户提问：" + user_input
        answer = llm_api_call(sys_prompt, full_user_prompt)
        # API调用失败，兜底提示
        if answer is None:
            st.warning("⚠️大模型接口调用失败，启用本地模板推理")
            answer = "⚠️大模型接口暂时不可用，已启用本地推理。\n" + llm_chat(user_input)
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state["weak_chat"].append({"role": "assistant", "content": answer})
