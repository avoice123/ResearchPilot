import json
from db import find_experiment_by_id, find_experiment_by_params
from llm_service import client
from rag import search_chunks, load_chunk_index
import logging
logging.basicConfig(level=logging.INFO,format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
def search_research_knowledge(question: str, chunk_index, top_k=3):
    result = search_chunks(question, chunk_index, top_k)
    return result
chunk_index = load_chunk_index("./data/chunk_index.json")
tools = [
    {
        "type": "function",
        "function": {
            "name": "find_experiment_by_id",
            "description": "根据实验ID查询一个实验的数据",
            "parameters": {
                "type": "object",
                "properties": {
                    "experiment_id":
                        {"type": "integer",
                         "description": "实验的ID"
                         }
                },
                "required": ["experiment_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_experiment_by_params",
            "description": "根据 KF 和 KINJ 查询实验数据",
            "parameters": {
                "type": "object",
                "properties": {
                    "kf": {
                        "type": "number",
                        "description": "实验参数 KF"
                    },
                    "kinj": {
                        "type": "number",
                        "description": "实验参数 KINJ"
                    }
                },
                "required": ["kf", "kinj"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_research_knowledge",
            "description": "从科研知识库中检索与问题相关的资料",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "需要检索的科研问题"
                    }
                },
                "required": ["question"]
            }
        }
    }
]
def ask_with_tools(question):
    messages = [
        {
            "role": "system",
            "content": """
    你是 ResearchPilot 科研助手。
    规则：
    1. 查询具体实验数据时，必须使用实验数据库工具。
    2. 涉及实验结果的原因、物理机制、科研解释时，
       不能只依赖你自己的知识，必须检索科研知识库。
    3. 如果问题同时需要实验数据和科研解释，
       应先查询实验数据，再检索科研知识库，然后综合回答。
    4. 如果科研知识库没有提供足够证据解释原因，
   必须明确回答“当前资料不足以确定原因”。

   不得继续列举基于模型自身知识推测出的潜在原因、
   物理机制、参数范围或实验结论。

   可以提出“下一步应进行哪些实验或检索来验证原因”，
   但必须明确这些是验证建议，而不是已经得到证据支持的结论。
   5. 没有重复实验、误差范围或统计检验时，
   不得使用“显著”“统计显著”等表述。
   只能客观描述数值差异。

6. 提出后续验证方案时，不得自行编造具体参数、
   阈值、步长或实验条件。
   如果这些设置没有来源，应只提出验证方向。

7. 生成知识库检索问题时，应优先保持中性，
   使用用户问题和已确认事实进行检索，
   不得把未经证实的候选机制预先写入检索问题。
    """
        },
        {
            "role": "user",
            "content": question
        }
    ]
    for _ in range(5):
        try:
            response = client.chat.completions.create(
                model="qwen-plus",
                messages=messages,
                tools=tools,
            )
        except Exception:
            logger.exception("LLM request failed")
            raise
        assistant_message = response.choices[0].message
        messages.append(assistant_message)
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:

                arguments = json.loads(tool_call.function.arguments)
                tool_name = tool_call.function.name
                logger.info("Agent selected tool: %s", tool_name)
                logger.debug("Tool arguments: %s", arguments)

                if tool_name == "find_experiment_by_id":
                    experiment_id = arguments["experiment_id"]
                    result = find_experiment_by_id(experiment_id)

                    if result is None:
                        tool_result = json.dumps(
                            {"error": "experiment not found"},
                            ensure_ascii=False
                        )
                    else:
                        tool_result = json.dumps(
                            result.__dict__,
                            ensure_ascii=False
                        )

                elif tool_name == "find_experiment_by_params":
                    kf = arguments["kf"]
                    kinj = arguments["kinj"]
                    result = find_experiment_by_params(kf, kinj)

                    if result is None:
                        tool_result = json.dumps(
                            {"error": "experiment not found"},
                            ensure_ascii=False
                        )
                    else:
                        tool_result = json.dumps(
                            result.__dict__,
                            ensure_ascii=False
                        )

                elif tool_name == "search_research_knowledge":
                    retrieval_question = arguments["question"]
                    result = search_research_knowledge(
                        retrieval_question,
                        chunk_index,
                        top_k=3
                    )

                    tool_result = json.dumps(
                        result,
                        ensure_ascii=False
                    )

                else:
                    tool_result = json.dumps(
                        {"error": f"unknown tool call: {tool_name}"},
                        ensure_ascii=False
                    )


                messages.append(
                {
                    "role": "tool",
                    "content": tool_result,
                    "tool_call_id": tool_call.id,
                })
        else:
            return assistant_message.content
    raise RuntimeError("Agent exceeded maximum rounds")
if __name__=="__main__":
    print(ask_with_tools("实验1的 IQ accuracy 为什么比 I accuracy 低？"))
