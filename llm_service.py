import os
import sys

from openai import OpenAI
from dotenv import load_dotenv
from models import Experiment
from db import find_experiment_by_id
load_dotenv()
client=OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://maas.qianwenaiapi.com/compatible-mode/v1"
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

if __name__ == "__main__":
    experiment = find_experiment_by_id(1)
    if experiment is not None:
        print(analyze_experiment_with_llm(experiment))

