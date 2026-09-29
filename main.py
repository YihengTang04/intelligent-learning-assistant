import streamlit as st
import networkx as nx
from common.utils import load_base_data, init_user_data, fix_old_user_data

# 导入各个功能模块
from modules.kg_struct import show_knowledge_structure
from modules.kg_search import search_knowledge
from modules.kg_relation import show_relation_graph
from modules.weak_diagnose import weak_point_diagnosis
from modules.resource_push import push_resource
from modules.level_navigate import level_navigate
from modules.study_progress import show_learning_progress
from modules.project_analyze import project_trace
from modules.error_manage import error_record_manage

# session初始化
if "login_username" not in st.session_state:
    st.session_state.login_username = ""
if "user_learn_data" not in st.session_state:
    st.session_state.user_learn_data = {}

def main():
    st.set_page_config(page_title="深度学习知识管理系统", layout="wide")
    kg_data, res_data, proj_data = load_base_data()
    nodes = kg_data["knowledge_nodes"]
    edges = kg_data["knowledge_edges"]
    all_node_id_list = [n["id"] for n in nodes]

    G = nx.DiGraph()
    node_id2name = {}
    node_name2id = {}
    name_all = [n["name"] for n in nodes]
    for n in nodes:
        G.add_node(n["id"], name=n["name"], level=n["level"], desc=n["desc"])
        node_id2name[n["id"]] = n["name"]
        node_name2id[n["name"]] = n["id"]
    for e in edges:
        G.add_edge(e["source"], e["target"], relation=e["relation"])

    st.title("知识管理与学习辅助系统")
    with st.sidebar.container():
        st.sidebar.subheader("👤 用户登录 | 独立学习数据库挂载")
        login_name = st.sidebar.text_input("输入用户名登录")
        login_btn = st.sidebar.button("登录系统")
        if login_btn and login_name.strip() != "":
            from common.utils import get_user_file
            userf = get_user_file(login_name.strip())
            import os, json
            if os.path.exists(userf):
                with open(userf, "r", encoding="utf-8") as f:
                    user_data = json.load(f)
                    user_data = fix_old_user_data(user_data)
            else:
                user_data = init_user_data(login_name.strip(), all_node_id_list)
            st.session_state.login_username = login_name.strip()
            st.session_state.user_learn_data = user_data
            st.success(f"欢迎{login_name}登录，个人独立学情数据库已加载挂载！")
        st.sidebar.info("⚙️ 当前加载：深度学习演示知识库\n本系统支持更换知识库JSON，可拓展适配绝大多数知识领域")

    if st.session_state.login_username == "":
        st.warning("请在左侧侧边栏输入用户名登录后使用系统！")
        return

    st.sidebar.title("功能导航栏")
    func_list = [
        "1. 知识点结构化展示",
        "2. 知识点检索查询",
        "3. 知识点关联关系分析",
        "4. 薄弱点智能诊断（联动7学习进度）",
        "5. 配套学习资源推送",
        "6. 知识层级导航",
        "7. 学习进度查看（修改同步4薄弱诊断）",
        "8. 实操项目知识溯源",
        "9. 错题录入与错题汇总"
    ]
    select_func = st.sidebar.selectbox("请选择功能", func_list)

    if select_func == "1. 知识点结构化展示":
        show_knowledge_structure(nodes)
    elif select_func == "2. 知识点检索查询":
        keyword = st.text_input("输入知识点/项目名称检索")
        search_knowledge(keyword, nodes)
    elif select_func == "3. 知识点关联关系分析":
        show_relation_graph(G, node_id2name, node_name2id, nodes, edges)
    elif select_func == "4. 薄弱点智能诊断（联动7学习进度）":
        weak_point_diagnosis(G, nodes, node_id2name, res_data)
    elif select_func == "5. 配套学习资源推送":
        name = st.selectbox("选择知识点", [n["name"] for n in nodes])
        push_resource(name, node_name2id, res_data)
    elif select_func == "6. 知识层级导航":
        level_navigate(nodes, node_id2name)
    elif select_func == "7. 学习进度查看（修改同步4薄弱诊断）":
        show_learning_progress(node_id2name, all_node_id_list)
    elif select_func == "8. 实操项目知识溯源":
        p_id = st.selectbox("选择实操项目ID", list(proj_data.keys()))
        project_trace(p_id, proj_data)
    elif select_func == "9. 错题录入与错题汇总":
        error_record_manage(nodes)


if __name__ == "__main__":
    main()
