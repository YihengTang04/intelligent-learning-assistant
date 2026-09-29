import streamlit as st
import json
import datetime
from common.utils import get_user_file

def error_record_manage(nodes):
    st.subheader("📝 错题录入与错题汇总管理模块（错题数据纳入薄弱点AI判定权重）")
    if not st.session_state.login_username:
        st.warning("请先登录账号")
        return
    user_data = st.session_state.user_learn_data
    error_list = user_data.get("error_record", [])
    all_kname = [n["name"] for n in nodes]
    st.info("录入错题后自动同步至【4薄弱诊断】，错题越多对应知识点薄弱权重越高")
    st.markdown("### 新增错题记录")
    err_node_name = st.selectbox("错题所属知识点", all_kname)
    err_desc = st.text_area("错题错误描述/错误原因")
    err_btn = st.button("保存错题记录")
    user_file = get_user_file(st.session_state.login_username)
    node_name2id = {n["name"]:n["id"] for n in nodes}
    if err_btn and err_desc.strip() != "":
        nid = node_name2id[err_node_name]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_err = {
            "record_time": now,
            "node_id": nid,
            "node_name": err_node_name,
            "error_content": err_desc
        }
        error_list.append(new_err)
        user_data["error_record"] = error_list
        with open(user_file, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
        st.session_state.user_learn_data = user_data
        st.success("✅ 错题保存成功！数据同步至【4薄弱点智能诊断】，切换菜单栏4查看更新")
        st.rerun()
    st.divider()
    st.markdown("### 全部错题汇总记录")
    if not error_list:
        st.write("暂无错题记录")
    else:
        for idx, err in enumerate(error_list):
            st.write(f"{idx + 1}. 【{err['record_time']}】知识点：{err['node_name']} | 错误描述：{err['error_content']}")
