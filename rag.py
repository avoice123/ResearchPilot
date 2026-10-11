from llm_service import client, ask_llm
import math
import json
def load_document(path):
    with open(path,"r",encoding="utf-8") as f:
        text=f.read()
    return text
def split_text(text,size=200,overlap=50):
    chunks=[]
    for i in range (0,len(text),size-overlap):
        chunks.append(text[i:i+size])

    return chunks

def build_chunk_index(chunks: list[str]):
    result=[]
    for i in range(len(chunks)):
        embedding_vector=get_embedding(chunks[i])
        result.append((chunks[i],i,embedding_vector))
    return result

def get_embedding(text:str)-> list[float]:

    response=client.embeddings.create(model="text-embedding-v4",input=text)
    return response.data[0].embedding

def cosine_similarity(a:list[float],b:list[float])-> float:
    dot=sum(x * y for x,y in zip(a,b))
    norm_a=math.sqrt(sum(x*x for x in a))
    norm_b=math.sqrt(sum(y*y for y in b))
    return dot/(norm_a*norm_b)
def search_chunks(question:str,chunk_index,top_k=3):
    result=[]
    question_vector=get_embedding(question)
    for chunk, i, embedding_vector in chunk_index:
        score = cosine_similarity(question_vector, embedding_vector)

        result.append((chunk,score,i))
    result.sort(key=lambda x:x[1],reverse=True)
    return result[:top_k]

def answer_chunks(question:str,chunk_index)->str:
    search_result=search_chunks(question,chunk_index)
    prompt=f"""
    问题是:{question}
    参考资料1:{search_result[0][0]} 
    参考资料2:{search_result[1][0]}
    参考资料3:{search_result[2][0]}
    请回答问题
    只能使用参考资料中明确出现的信息回答。

不得补充参考资料中没有提供的实验结果、文献结论、
统计显著性、物理机制或数值。

如果参考资料只能提出一种可能性，而不能证明原因，
必须明确写“参考资料不足以确定原因”。

回答中的每个主要结论请注明来自哪一个参考资料。
    """
    ask_result=ask_llm(prompt)
    return ask_result

def save_chunk_index(chunk_index, path):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(chunk_index,f,ensure_ascii=False)

def load_chunk_index(path):
    with open(path,"r",encoding="utf-8") as f:
        data=json.load(f)
        return data


if __name__ == "__main__":
    #text = load_document("C:\\Users\\Administrator\\Desktop\\DFB说明.txt")
    #chunk_index=build_chunk_index(split_text(text))
    #save_chunk_index(chunk_index,"./data/chunk_index.json")
    tem_data=load_chunk_index("./data/chunk_index.json")
    result=answer_chunks("当 XF = 0.029 时，MNIST 的最终分类准确率是多少？",tem_data)
    print(result)


