
def analyze_experiment(csv_path):

# csv_path：实验结果 CSV 文件路径
    import pandas as pd
    df = pd.read_csv(csv_path)
    if "xx" in df.columns and "yy" in df.columns and "zz" in df.columns:
        print("Column  found")
    else:
        print("Column not found")

