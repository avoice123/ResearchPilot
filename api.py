from fastapi import FastAPI, HTTPException
from db import find_all_experiments, find_experiment_by_id, insert_experiment, find_experiment_by_params
from pydantic import BaseModel
from importer import read_result, read_state,merge_experiment
from models import Experiment
app = FastAPI()

def experiment_to_dict(experiment: Experiment) -> dict[str, object]:
    return {
        "id": experiment.id,
        "kf": experiment.kf,
        "kinj": experiment.kinj,
        "acc_i": experiment.acc_i,
        "acc_iq": experiment.acc_iq,
        "acc_p": experiment.acc_p,
        "state_file": experiment.state_file,
        "result_file": experiment.result_file,
        "created_at": experiment.created_at
    }
@app.get("/health")
def health():
    return {"status": "ok"}
@app.get("/experiments")
def get_experiments():
    experiments=find_all_experiments()
    results=[]

    for experiment in experiments:
        results.append(
            experiment_to_dict(experiment)
        )
    return results
@app.get("/experiments/by-params")
def get_experiments_by_params(kf:float,kinj:float):
    experiment=find_experiment_by_params(kf,kinj)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment_to_dict(experiment)
@app.get("/experiments/{experiment_id}")
def get_experiment(experiment_id: int):
   result=find_experiment_by_id(experiment_id)
   if result is None:
       raise HTTPException(status_code=404, detail="Experiment not found")

   return experiment_to_dict(result)
class ImportRequest(BaseModel):
    state_file: str
    result_file: str
@app.post("/experiments/import")
def import_experiment(request: ImportRequest):
    try:
        result_state=read_state(request.state_file)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="State file not found")
    try:
        result_result=read_result(request.result_file)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Result file not found")
    result=merge_experiment(result_state,result_result)
    experiment_id=insert_experiment(result,request.state_file,request.result_file)
    return {"id":experiment_id}

