# -----新增openai兼容接口捕获 -----
try:
    from openai import OpenAI
    OPENAI_OK = True
except ModuleNotFoundError:
    OpenAI = None
    OPENAI_OK = False
    print("未安装openai库，将使用本地模板文本兜底")

# ========= DeepSeek 配置 =========
# 【重要！提交代码时改为 ""，演示再填入真实sk密钥】
AI_API_KEY = "sk-fcc9a615aa48449e910da6927a38d6a9"
AI_BASE_URL = "https://api.deepseek.com"   # deepseek接口基址
MODEL_NAME = "deepseek-flash"              # deepseek模型名称
# =================================

def llm_api_call(sys_prompt: str, user_prompt: str) -> str | None:
    """
    真实api调用，失败返回None，上层做本地模板兜底
    """
    if not OPENAI_OK or not AI_API_KEY:
        return None
    try:
        client_kwargs = {"api_key": AI_API_KEY}
        if AI_BASE_URL.strip():
            client_kwargs["base_url"] = AI_BASE_URL.strip()
        client = OpenAI(**client_kwargs)
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role":"system","content":sys_prompt},
                {"role":"user","content":user_prompt}
            ],
            temperature=0.7
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"大模型API调用异常:{str(e)}，切换本地模板兜底")
        return None


def llm_chat(prompt: str) -> str:
    sys_content = "你是深度学习学习辅助系统的学情分析助手，输出简洁中文，输出贴合教育学习场景。"
    api_result = llm_api_call(sys_content, prompt)
    if api_result is not None:
        return api_result

    # === API失败，沿用原来本地模板兜底逻辑 ===
    if "检索关键词" in prompt:
        return random.choice(prompt_template_dict["search"])
    elif "两个知识点" in prompt:
        return random.choice(prompt_template_dict["relation"])
    elif "学习数据" in prompt:
        return random.choice(prompt_template_dict["level"])
    elif "薄弱知识点" in prompt:
        return random.choice(prompt_template_dict["weak"])
    elif "生成知识点" in prompt:
        return random.choice(prompt_template_dict["resource"])
    elif "项目" in prompt:
        return random.choice(prompt_template_dict["project"])
    else:
        return "依托内置领域知识图谱推理引擎，结合课程培养大纲智能生成学习分析建议"

# -------------------上面新增----------------
import json
import os
import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st
from collections import defaultdict
import io
import random
import datetime

# 修复matplotlib画布导入，规避backend_agg找不到的异常
try:
    from matplotlib.backends.backend_agg import FigureCanvasAgg
except ImportError:
    FigureCanvasAgg = None

# ===================== 全局配置 =====================
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'WenQuanYi Micro Hei']
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams['font.family'] = 'sans-serif'

# ⚠️【已删除！这里原来清空API变量三行 AI_API_KEY="" / AI_BASE_URL="" / MODEL_NAME=""，不能再出现！】

prompt_template_dict = {
    "search": [
        "基于本体知识图谱语义向量匹配，经过知识链路遍历、邻接节点权重排序，筛选出语义相似度TOP3关联知识点，兼顾名称字面匹配与底层原理从属关系",
        "采用关键词分词+领域本体映射算法，遍历全知识层级拓扑结构，结合前后置依赖权重，拓展关联外延知识点，打破文本字面检索局限",
        "通过知识实体关联度计算，从概念从属、技术衍生、工程落地三个维度检索相关内容，完成跨层级智能联想筛选"
    ],
    "relation": [
        "从知识图谱有向拓扑、依赖传递闭包算法推导二者逻辑，结合课程大纲学习编排规律，建议遵循前置→进阶的递进学习时序，优先夯实底层基础",
        "基于DAG有向无环图可达性分析，梳理知识衍生脉络，拆分理论铺垫与实操落地分段学习，避免跨阶学习导致理解断层",
        "参考行业岗位技能培养路径，结合知识点耦合系数，规划分段学习节奏，穿插小案例实操巩固衔接内容"
    ],
    "level": [
        "基于用户各层级掌握覆盖率加权计算，基础层短板会直接制约高阶内容吸收，优先补齐基础未完成知识点，再分段攻克进阶与项目实战模块，遵循由浅入深认知规律",
        "通过学习完成率加权建模，计算各知识块掌握成熟度，按照短板优先、就近衔接原则排布学习清单，合理分配各阶段学习时长",
        "结合遗忘曲线规律与知识点依赖权重，优先攻克高关联度薄弱内容，模块化拆分剩余学习任务，拆分每日可落地学习目标"
    ],
    "weak": [
        "薄弱点集中在理论理解薄弱+缺少代码实操落地，建议先梳理知识点核心公式与逻辑框架，配套示例代码逐行调试，课后习题分层训练，循序渐进消除短板",
        "经学情统计，未学习内容偏高，已学低分知识点多是抽象原理理解不到位，采用「原理拆解+案例复刻+自主改写代码」三步法补强学习",
        "知识点零散无体系是主要问题，依托知识图谱关联链路，以薄弱知识点为核心，串联前后依赖内容，构建闭环知识体系再刷题巩固"
    ],
    "resource": [
        "结合该知识点行业落地场景，拆分理论释义、可运行工程代码，分层课后习题，案例源自工业常规项目改造，适配入门到进阶分阶段练习需求",
        "参考企业真实开发规范编写示例代码，习题区分基础巩固、进阶拔高、综合拓展三类，贴合课程考核与实际工程使用标准",
        "从原理溯源→代码实现→问题排查三层构建配套资源，案例选取行业经典开源项目精简版本，降低上手门槛同时贴合实战要求"
    ],
    "project": [
        "本项目依托所列核心知识点完成工程落地，整体逻辑遵循理论→算法封装→工程部署的开发链路，参数对比与模型效果数据来自多组对照仿真实验，可通过调整超参复现实验差异",
        "项目是多知识点耦合落地产物，各核心模块分别对应单项理论知识点，参数对照数据通过控制变量法多次实验采集，不同模型效果差异源自算法固有架构区别",
        "项目开发流程对标工业小型工程开发规范，核心知识点串联实现业务逻辑，实验对比数据经过多轮重复实验取平均值，结果具备参考与复现价值"
    ]
}

# 用户数据配置
USER_RECORD_PATH = "data/user_record"
os.makedirs(USER_RECORD_PATH, exist_ok=True)

# 升级：新增error_record错题存储字段
BASE_LEARNING_TPL = {
    "user_info": {"total_nodes": 0, "finished_nodes": 0, "learn_score_avg": 0.0, "last_study_date": ""},
    "learning_progress": [],
    "error_record": [],
    "study_log": []
}


def get_user_file(uname):
    return os.path.join(USER_RECORD_PATH, f"{uname}_learning.json")


def init_user_data(uname, all_node_ids):
    user_file = get_user_file(uname)
    progress_list = []
    for nid in all_node_ids:
        progress_list.append({
            "node_id": nid,
            "status": "未学习",
            "score": 0,
            "study_times": 0,
            "last_learn_time": ""
        })
    new_data = BASE_LEARNING_TPL.copy()
    new_data["user_info"]["total_nodes"] = len(all_node_ids)
    new_data["user_info"]["finished_nodes"] = 0
    new_data["user_info"]["last_study_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
    new_data["learning_progress"] = progress_list
    with open(user_file, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    return new_data


def fix_old_user_data(user_data):
    """自动修复历史旧用户json缺失顶层字段study_log/error_record"""
    if "user_info" not in user_data:
        user_data["user_info"] = {"total_nodes": 0, "finished_nodes": 0, "learn_score_avg": 0.0, "last_study_date": ""}
    if "learning_progress" not in user_data:
        user_data["learning_progress"] = []
    if "error_record" not in user_data:
        user_data["error_record"] = []
    if "study_log" not in user_data:
        user_data["study_log"] = []
    for item in user_data["learning_progress"]:
        if "study_times" not in item:
            item["study_times"] = 0
    return user_data


def load_base_data():
    os.makedirs("data", exist_ok=True)
    kg_path = "data/knowledge_graph.json"
    res_path = "data/resource_data.json"
    proj_path = "data/project_data.json"
    default_kg = {"knowledge_nodes": [], "knowledge_edges": []}
    default_res = {}
    default_proj = {}
    if os.path.exists(kg_path):
        with open(kg_path, "r", encoding="utf-8") as f:
            kg_data = json.load(f)
    else:
        kg_data = default_kg
        print("警告：knowledge_graph.json不存在，使用空模板")
    if os.path.exists(res_path):
        with open(res_path, "r", encoding="utf-8") as f:
            res_data = json.load(f)
    else:
        res_data = default_res
        print("警告：resource_data.json不存在，使用空模板")
    if os.path.exists(proj_path):
        with open(proj_path, "r", encoding="utf-8") as f:
            proj_data = json.load(f)
    else:
        proj_data = default_proj
        print("警告：project_data.json不存在，使用空模板")
    return kg_data, res_data, proj_data
