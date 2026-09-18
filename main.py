from importer import read_state,read_result,merge_experiment
from db import create_table, insert_experiment, find_experiment_by_id, find_all_experiments, find_experiment_by_params
from models import Experiment

create_table()
while  True:
    print("欢迎,按1是输入数据,2是按照id查询,3是直接全部查询,4是根据kf和kinj查询,0是退出")
    choice= input("输入你的选择")
    if choice=="1":
        state_path=input("输入你的state文件路径")
        result_path=input("输入你的result文件路径")
        state_info = read_state(state_path)
        result_info = read_result(result_path)
        merged_info=merge_experiment(state_info,result_info)

        experiment_id=insert_experiment(merged_info,state_path,result_path)
        print(f"完毕,实验id={experiment_id}")
    elif choice=="2":
        try:
            experiment_id=int(input("查询你想要看的id\n"))
        except ValueError:
            print("你应该输入整数")
            continue

        experiment=find_experiment_by_id(experiment_id)
        if experiment is not None:
            experiment.show_experiment()
        else:
            print("无数据")
    elif choice=="3":
        experiments=find_all_experiments()
        if not experiments:
            print("无数据")
        else:
            for experiment in experiments:
                experiment.show_experiment()
    elif choice=="4":
        kf,kinj=map(float,input("请输入kf和kinj,用空格隔开:").split())
        experiment=find_experiment_by_params(kf, kinj)
        if experiment is not None:
            experiment.show_experiment()
        else:
            print("无数据")
    elif choice == "0":
        break
    else:
        print("输入不合法")
