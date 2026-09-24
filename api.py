from fastapi import FastAPI, HTTPException
from db import find_all_experiments, find_experiment_by_id, insert_experiment, find_experiment_by_params
from pydantic import BaseModel,Field
from importer import read_result, read_state,merge_experiment
from models import Experiment
from llm_service import analyze_experiment_with_llm, ask_about_experiment

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
class ExperimentResponse(BaseModel):
    id: int
    kf: float
    kinj:float
    acc_i: float
    acc_iq: float
    acc_p: float
    state_file:str
    result_file:str
    created_at:str|None
class BestAnalysisResponse(BaseModel):
    best_id: int
    best_kf: float
    best_kinj: float
    metric: str
    best_acc: float
@app.get("/health")
def health():
    return {"status": "ok"}
@app.get("/experiments",response_model=list[ExperimentResponse])
def get_experiments():
    experiments=find_all_experiments()
    results=[]

    for experiment in experiments:
        results.append(
            experiment_to_dict(experiment)
        )
    return results
@app.get("/experiments/by-params",response_model=ExperimentResponse)
def get_experiments_by_params(kf:float,kinj:float):
    experiment=find_experiment_by_params(kf,kinj)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment_to_dict(experiment)
@app.get("/experiments/{experiment_id}",response_model=ExperimentResponse)
def get_experiment(experiment_id: int):
   result=find_experiment_by_id(experiment_id)
   if result is None:
       raise HTTPException(status_code=404, detail="Experiment not found")

   return experiment_to_dict(result)

class ImportRequest(BaseModel):
    state_file: str=Field(min_length=1)
    result_file: str=Field(min_length=1)

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
@app.get("/experiments/{experiment_id}/analysis")
def get_analysis(experiment_id: int):
    result=find_experiment_by_id(experiment_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    best_acc=max(result.acc_i,result.acc_iq,result.acc_p)
    if best_acc==result.acc_i:
        best_readout="I"
    elif best_acc==result.acc_iq:
        best_readout="IQ"
    else:
        best_readout="P"
    return {"id":experiment_id,
        "best_readout":best_readout,
            "best_acc":best_acc}
@app.get("/analysis/best",response_model=BestAnalysisResponse)
def get_analysis_best(metric: str):
    experiments = find_all_experiments()
    if not experiments :
        raise HTTPException(status_code=404, detail="Experiment not found")
    if metric=="acc_iq":
        best=max(experiments,key=lambda experiment:experiment.acc_iq)
        best_value=best.acc_iq
    elif metric=="acc_i":
        best=max(experiments,key=lambda experiment:experiment.acc_i)
        best_value=best.acc_i
    elif metric=="acc_p":
        best=max(experiments,key=lambda experiment:experiment.acc_p)
        best_value=best.acc_p
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid metric"
        )
    return {"best_id":best.id,
            "best_kf":best.kf,
            "best_kinj":best.kinj,
            "best_acc":best_value,
            "metric":metric}

class AIAnalysisResponse(BaseModel):
    id: int
    analysis: str
@app.get("/experiments/{experiment_id}/ai-analysis",response_model=AIAnalysisResponse)
def get_ai_analysis(experiment_id: int):
    experiment=find_experiment_by_id(experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    try:
        result=analyze_experiment_with_llm(experiment)
    except Exception :
        raise HTTPException(status_code=502, detail="LLM service failed")
    return {"id":experiment.id,"analysis":result}


class AskExperimentResponse(BaseModel):
    id: int
    result:str=Field(min_length=1)
class AskExperimentRequest(BaseModel):
    quest:str=Field(min_length=1)
@app.post("/experiments/{experiment_id}/ask",response_model=AskExperimentResponse)
def ask_experiment(quest:AskExperimentRequest,experiment_id: int):
    experiment=find_experiment_by_id(experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    try:
        result=ask_about_experiment(experiment,quest.quest)
    except Exception :
        raise HTTPException(status_code=502, detail="LLM service failed")
    return {"id":experiment.id,"result":result}

