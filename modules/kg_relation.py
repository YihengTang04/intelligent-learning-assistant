import streamlit as st
import networkx as nx
import io
from common.utils import FigureCanvasAgg, llm_chat

def show_relation_graph(G, node_id2name, node_name2id, nodes, edges):
    st.subheader("🔗 知识点关联关系图谱 | DAG拓扑结构解析系统 | 支持任意两个知识点互相查询关联逻辑、前置后置、学习先后")
    tab1, tab2 = st.tabs(["全图查看/单点上下游查看", "自定义双知识点关系查询"])
    all_in_degree = dict(G.in_degree())
    all_out_degree = dict(G.out_degree())
    name_all = [n["name"] for n in nodes]
    with tab1:
        select_one = st.selectbox("可选单个知识点，聚焦查看关联链路（不选则展示全图）", ["全部知识点"] + name_all, key="sel1")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(18, 12))
        pos = nx.spring_layout(G, seed=42, k=2.2, iterations=120)
        if select_one == "全部知识点":
            nx.draw(G, pos, ax=ax, with_labels=True, labels=node_id2name, node_color="#87CEEB", node_size=2800, font_size=11,
                    arrows=True, arrowstyle="->", arrowsize=25)
            avg_in = round(sum(all_in_degree.values()) / len(all_in_degree), 2)
            avg_out = round(sum(all_out_degree.values()) / len(all_out_degree), 2)
            st.info(f"全图拓扑指标：总节点{len(nodes)}，总边数{len(edges)}，平均入度{avg_in}，平均出度{avg_out}")
        else:
            target_id = node_name2id[select_one]
            pred_nodes = list(G.predecessors(target_id))
            succ_nodes = list(G.successors(target_id))
            keep_nodes = [target_id] + pred_nodes + succ_nodes
            sub_G = G.subgraph(keep_nodes)
            color_map = []
            for nd in sub_G.nodes():
                if nd == target_id:
                    color_map.append("#ff7f0e")
                elif nd in pred_nodes:
                    color_map.append("#2ca02c")
                else:
                    color_map.append("#d62728")
            sub_label = {k: node_id2name[k] for k in sub_G.nodes()}
            nx.draw(sub_G, pos, ax=ax, with_labels=True, labels=sub_label, node_color=color_map, node_size=3000, font_size=12,
                    arrows=True, arrowstyle="->", arrowsize=25)
            st.info(
                f"橙色：{select_one}；绿色：前置依赖（必须先学，共{len(pred_nodes)}个）；红色：后续进阶（学完本知识点再学，共{len(succ_nodes)}个）")
        edge_labels = {(e["source"], e["target"]): e["relation"] for e in edges if (e["source"], e["target"]) in G.edges()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, label_pos=0.35)
        ax.set_title("深度学习知识点关联图谱", fontsize=20, pad=20)
        buf = io.BytesIO()
        if FigureCanvasAgg:
            FigureCanvasAgg(fig).print_png(buf)
        st.image(buf, use_column_width=True)
        plt.close(fig)
        st.write("关系说明：前置依赖 / 前后衔接 / 并列关系 / 进阶拓展 / 递进关系")
    with tab2:
        st.info("自由任选【知识点A】与【知识点B】，一键查询二者学习先后、依赖、并列等内在关联，基于图论可达性算法解析")
        col_a, col_b = st.columns(2)
        with col_a:
            node_a_name = st.selectbox("选择第一个知识点A", name_all, key="nodeA")
        with col_b:
            node_b_name = st.selectbox("选择第二个知识点B", name_all, key="nodeB")
        aid = node_name2id[node_a_name]
        bid = node_name2id[node_b_name]
        a_to_b = G.has_edge(aid, bid)
        b_to_a = G.has_edge(bid, aid)
        a_ancestor = bid in nx.descendants(G, aid)
        b_ancestor = aid in nx.descendants(G, bid)
        try:
            dist_ab = nx.shortest_path_length(G, source=aid, target=bid)
        except Exception:
            dist_ab = -1
        try:
            dist_ba = nx.shortest_path_length(G, source=bid, target=aid)
        except Exception:
            dist_ba = -1
        st.divider()
        st.info(f"路径量化：A到B最短链路长度：{dist_ab}，B到A最短链路长度：{dist_ba}")
        if a_to_b:
            edge_data = None
            for s, t, e in G.edges(data=True):
                if s == aid and t == bid:
                    edge_data = e
                    break
            rel_type = edge_data["relation"]
            st.success(f"✅ {node_a_name} → {node_b_name} 存在直接关联，关联类型：{rel_type}，学习顺序：优先学【{node_a_name}】再学【{node_b_name}】")
        elif b_to_a:
            edge_data = None
            for s, t, e in G.edges(data=True):
                if s == bid and t == aid:
                    edge_data = e
                    break
            rel_type = edge_data["relation"]
            st.success(f"✅ {node_b_name} → {node_a_name} 存在直接关联，关联类型：{rel_type}，学习顺序：优先学【{node_b_name}】再学【{node_a_name}】")
        elif a_ancestor:
            st.info(f"📌 间接依赖：{node_a_name}是{node_b_name}的前置祖先知识点，需要先学A，经过多层知识点后再学习B")
        elif b_ancestor:
            st.info(f"📌 间接依赖：{node_b_name}是{node_a_name}的前置祖先知识点，需要先学B，经过多层知识点后再学习A")
        else:
            st.warning(f"⚪ {node_a_name}与{node_b_name}无直接/间接依赖关系，属于并列学习内容，无固定先后顺序")
        ai_p = f"结合深度学习课程，{node_a_name}和{node_b_name}两个知识点的学习顺序补充建议，精简描述"
        st.write("🤖大模型补充学习规划：" + llm_chat(ai_p))
