from datasets import load_dataset
import traceback
import re
from .response import generate_model_response
import json

def evaluate_models_boolq(data, datetime_folder):
    dataset = load_dataset("boolq")
    dataset = dataset['train']
    questions = dataset['question'][:data]
    answers = dataset['answer'][:data]
    tasks = []
    
    miner_scores = dict()
    try:
        que_no = 1
        for question, answer in zip(questions, answers):
            
            prompt = question

            print(128*'-')
            print(f"Getting Que No: {que_no} Getting this prompt: {prompt}")
            print()
            
            model_input = prompt  # Modify this if your model requires specific input format
            system_prompt = "You are an AI assistant. Your task is to reply only True/False/None of the given question, 'True' if you consider given statement to be true and 'False' if you consider given statement to be false and 'None' if you don't understand. Dont include other text in your response other than True/False/None"

            model_response = generate_model_response(system_prompt, model_input)
            for response in model_response['choices']:
                uid = response['uid']
                model_resp = response['message']['content']
                model_score = 0
                model_accuracy = 0
                
                #print(f"Getting response from {uid} UID is {response}")
                #print()
                if str(answer).lower() in model_resp.lower():
                    model_score = 4
                    model_accuracy = 1
                    #print("Selecting response as perfectly correct")
                    #print()

                elif 'none' in model_resp.lower():
                    model_score = 2
                    #print("Selecting response as partially correct")
                    #print()

                else:
                    model_score = 1
                    #print("Selecting response as incorrect")
                    #print()

                # Increment the score for the current model
                if uid in miner_scores.keys():
                    miner_scores[uid]['score'] += model_score
                    miner_scores[uid]['accuracy'] += model_accuracy
                else:
                    miner_scores[uid] = {'score': model_score, 'accuracy': model_accuracy}
        
            if que_no%100 == 0:
                with open(f'checkpoints/{datetime_folder}/boolq/Boolq_Miner_Metrics_{que_no}.json', 'w') as chkpnt_file:
                    chkpnt_file.write(json.dumps(miner_scores))
            
            que_no += 1
                
        with open(f'results/{datetime_folder}/Boolq_Miner_Metrics.json', 'w') as json_file:
            json_file.write(json.dumps(miner_scores))

    except Exception as e:
        print(f'Exception Occured : {e}')
        print()
        traceback.print_exc()
        with open(f'except/{datetime_folder}/Boolq_Miner_Metrics_{que_no}.json', 'w') as json_file:
            json_file.write(json.dumps(miner_scores))

if __name__ == "__main__":
    evaluate_models_boolq()