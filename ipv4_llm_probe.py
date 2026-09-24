import os, socket, json
from dotenv import load_dotenv
from openai import OpenAI

# Force IPv4 — IPv6 to dashscope hangs/resets on this machine
_orig = socket.getaddrinfo
def _ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    infos = _orig(host, port, family, type, proto, flags)
    v4 = [i for i in infos if i[0] == socket.AF_INET]
    return v4 or infos
socket.getaddrinfo = _ipv4_only

load_dotenv()
key = os.getenv("DASHSCOPE_API_KEY") or ""
print("key_len", len(key), "prefix", key[:7])

client = OpenAI(
    api_key=key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    timeout=30.0,
)
try:
    r = client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role":"user","content":"只回复一个字：好"}],
        max_tokens=5,
    )
    print("OK:", r.choices[0].message.content)
except Exception as e:
    print(type(e).__name__ + ":", e)
