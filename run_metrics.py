from metric_scripts.arc import evaluate_models_arc
from metric_scripts.boolq import evaluate_models_boolq
from metric_scripts.mmlu import evaluate_models_mmlu
from metric_scripts.openbookqa import evaluate_models_openbookqa
from metric_scripts.piqa import evaluate_models_piqa
from metric_scripts.race import evaluate_models_race
from metric_scripts.siqa import evaluate_models_siqa
from metric_scripts.winogrande import evaluate_models_winogrande
import traceback
import datetime
import os


def run_all_metric(question_per_metric):
    
    datetime_folder = str(datetime.datetime.now().strftime("%d-%m-%y_%H-%M-%S"))
    folders = ['benchmark', 'checkpoints', 'except', 'results']

    for folder in folders:
        os.mkdir(os.path.join(folder, datetime_folder))

    metric_folders = ['arc', 'boolq', 'mmlu', 'openbookqa', 'piqa', 'race', 'siqa', 'winogrande']

    for metric_folder in metric_folders:
        os.mkdir(os.path.join(f"checkpoints/{datetime_folder}", metric_folder))
        
    evaluation_functions = [
        evaluate_models_arc,
        evaluate_models_boolq,
        evaluate_models_mmlu,
        evaluate_models_openbookqa,
        evaluate_models_piqa,
        evaluate_models_race,
        evaluate_models_siqa,
        evaluate_models_winogrande
    ]

    for evaluation_function in evaluation_functions:
        try:
            evaluation_function(question_per_metric, datetime_folder)
        except Exception as e:
            traceback.print_exc()
            print(f"An error occurred while running {evaluation_function.__name__}: {e}")
            return "Exception"
    
    return datetime_folder