import sqlite3
from models import Experiment
from datetime import datetime
def row_to_experiment(row:tuple)->Experiment:
    experiment=Experiment(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
    return experiment

def create_table()->None:
    conn = sqlite3.connect("research_pilot.db")
    cursor = conn.cursor()
    sql = """
    
    
          CREATE TABLE IF NOT EXISTS experiments
          (
              id          INTEGER PRIMARY KEY AUTOINCREMENT,
              KF          REAL,
              KINJ        REAL,
              ACC_I       REAL,
              ACC_IQ      REAL,
              ACC_P      REAL,
              state_file  TEXT,
              result_file TEXT,
              created_at  TEXT
    
          );"""
    cursor.execute(sql)
    conn.commit()
    conn.close()

def insert_experiment(merged_data,state_file,result_file)->int:
    conn = sqlite3.connect("research_pilot.db")
    cursor = conn.cursor()
    check_sql = """
    SELECT id FROM experiments
    WHERE KF = ? and KINJ = ? 
                  
                """
    cursor.execute(check_sql,(merged_data["KF"],merged_data["KINJ"]))
    existing=cursor.fetchone()
    sql = """
            INSERT INTO experiments
            ( KF, KINJ, ACC_I,ACC_IQ,ACC_P,state_file,result_file,created_at)  
            
            
            VALUES(?,?,?,?,?,?,?,?)    
            """
    if existing is None:
        created_at = datetime.now().isoformat(timespec="seconds")
        cursor.execute(sql,(merged_data["KF"],merged_data["KINJ"], merged_data["ACC_I"],merged_data["ACC_IQ"],merged_data["ACC_P"],state_file,result_file,created_at))
        experiment_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return experiment_id
    else:
        existing_id=existing[0]
        print(f"已存在,id为{existing_id}")
        conn.close()
        return existing_id

def find_experiment_by_id(experiment_id:int)->Experiment|None:
    conn = sqlite3.connect("research_pilot.db")
    cursor = conn.cursor()
    find_sql = """
    SELECT * FROM experiments WHERE id = ?
    """
    cursor.execute(find_sql,(experiment_id,))
    result = cursor.fetchone()
    if result is None:
        conn.close()
        return None
    experiment=row_to_experiment(result)
    conn.close()
    return experiment
def find_all_experiments()->list[Experiment]:
    conn = sqlite3.connect("research_pilot.db")
    cursor = conn.cursor()
    find_all_sql = """
    SELECT * FROM experiments
        
    """
    cursor.execute(find_all_sql)
    rows = cursor.fetchall()
    experiments=[]
    for row in rows:
        experiment=row_to_experiment(row)
        experiments.append(experiment)
    conn.close()
    return experiments
def find_experiment_by_params(kf:float, kinj:float)->Experiment|None:
    conn = sqlite3.connect("research_pilot.db")
    cursor = conn.cursor()
    find_kf_kinj_sql = """
    SELECT * FROM experiments WHERE KF = ? and KINJ = ?
    """
    cursor.execute(find_kf_kinj_sql,(kf,kinj))
    result = cursor.fetchone()
    if result is None:
        conn.close()
        return None
    experiment=row_to_experiment(result)
    conn.close()
    return experiment
