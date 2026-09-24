import os
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv
from models import Experiment
from db import find_experiment_by_id
load_dotenv()
# Bypass local VPN/system proxy for DashScope (Aliyun China API)
_no_proxy = "dashscope.aliyuncs.com,aliyuncs.com,.aliyuncs.com,aliyun.com,.aliyun.com,localhost,127.0.0.1"
os.environ["NO_PROXY"] = (_no_proxy + ("," + os.environ["NO_PROXY"] if os.environ.get("NO_PROXY") else ""))
os.environ["no_proxy"] = os.environ["NO_PROXY"]
client=OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    timeout=60.0
)
def ask_llm(prompt: str) -> str:
    response=client.chat.completions.create(
        model="qwen-plus",
        messages=[ {"role": "system", "content": "You are an assistant for photonic reservoir computing experiments. Analyze experimental parameters and results accurately and concisely."},
                   {"role": "user", "content": prompt}

        ]
    )
    return response.choices[0].message.content
def analyze_experiment_with_llm(experiment: Experiment) -> str:
    prompt=f"""
    实验参数:
    KF={experiment.kf}
    KINJ={experiment.kinj}
    实验结果:
    ACC_I={experiment.acc_i}
    ACC_P={experiment.acc_p}
    ACC_IQ={experiment.acc_iq}
     请分析当前这组实验结果，比较三种 readout 的表现。
    如果数据中存在值得怀疑或进一步验证的现象，请明确指出。
    不要编造当前数据无法支持的原因。
"""
    return ask_llm(prompt)

def ask_about_experiment(experiment: Experiment, question: str) -> str:
    prompt=f"""实验参数:
    KF={experiment.kf}
    KINJ={experiment.kinj}
    实验结果:
    ACC_I={experiment.acc_i}
    ACC_P={experiment.acc_p}
    ACC_IQ={experiment.acc_iq},
    用户问题是{question}"""
    return ask_llm(prompt)

def analyze_experiment_structured(experiment: Experiment):
    prompt=f"""实验参数:
    KF={experiment.kf}
    KINJ={experiment.kinj}
    实验结果:
    ACC_I={experiment.acc_i}
    ACC_P={experiment.acc_p}
    ACC_IQ={experiment.acc_iq}
    请只返回 JSON，不要返回 Markdown，不要添加其他文字。

    格式必须为：
    {{
        "summary": "简短结论",
      "best_readout": "I、IQ 或 P",
      "best_acc": 数字,
      "needs_verification": true 或 false
    }}    
    """
    result=ask_llm(prompt)
    data=json.loads(result)
    return data


if __name__ == "__main__":
    experiment = find_experiment_by_id(1)
    if experiment is not None:
        result = analyze_experiment_structured(experiment)
        print(result)
        print(type(result))
        print(result["best_readout"])

