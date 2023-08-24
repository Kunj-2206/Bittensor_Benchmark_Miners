from datasets import load_dataset
import traceback
import re
from .response import  generate_model_response
import json

def extract_selected_option(model_response, sol1, sol2):
    
    if sol1.lower() in model_response.lower() and sol2.lower() not in model_response.lower():
        return "0"
    
    elif sol1.lower() in model_response.lower() and sol2.lower() not in model_response.lower():
        return "1"
    
    # Define the option labels
    option_labels = ['0','1']
    
    if len(model_response) > 200 or (sol1.lower() in model_response.lower() and sol2.lower() in model_response.lower()):
        return "None"
    
    # Split the model response by sentences to handle complex structures
    response_sentences = re.split(r'[.!?]', model_response)

    # Loop through each sentence of the response and check for option labels
    for sentence in response_sentences:
        for option_label in option_labels:
            if re.search(r'\b' + re.escape(option_label) + r'[),.\n]?', sentence):
                return option_label
            
    # If no option label is found, return None or a default value
    return "None"



def evaluate_models_piqa(data, datetime_folder):
    
    dataset = load_dataset("piqa")
    dataset = dataset['train']
    # Access individual columns from the dataset
    goal = dataset['goal'][:data]
    sol1 = dataset['sol1'][:data]
    sol2 = dataset['sol2'][:data]
    answer = dataset['label'][:data]

    miner_scores = dict()

    try:
        que_no = 1
        # Loop through each example in the dataset
        for goal, sol1, sol2, answer in zip(goal, sol1, sol2, answer):
            # Generate the prompt to ask the model
                            
            prompt = f"{goal}?\n0. {sol1}\n1. {sol2}" 

            print(128*'-')
            print(f"Getting question no: {que_no}, Getting this prompt: {prompt}")
            print()
            # Loop through each model and get their responses
            model_input = prompt  # Modify this if your model requires specific input format
            system_prompt = "You are an AI assistant. Your task is to reply correct option from given text and remember only answer in one character like (1,2), no other text"

            model_response = generate_model_response(system_prompt, model_input)
            for response in model_response['choices']:
                uid = response['uid']
                model_resp = response['message']['content']
                model_score = 0
                model_accuracy = 0

                if str(answer) in extract_selected_option(model_resp,sol1,sol2):
                    model_score = 3
                    model_accuracy = 1
                else:
                    model_score = 0

                # Increment the score for the current model
                if uid in miner_scores.keys():
                    miner_scores[uid]['score'] += model_score
                    miner_scores[uid]['accuracy'] += model_accuracy
                else:
                    miner_scores[uid] = {'score': model_score, 'accuracy': model_accuracy}
            
            if que_no%100 == 0:
                    with open(f'checkpoints/{datetime_folder}/piqa/Piqa_Miner_Metrics_{que_no}.json', 'w') as chkpnt_file:
                        chkpnt_file.write(json.dumps(miner_scores))
                        
            que_no += 1
            
        with open(f'results/{datetime_folder}/Piqa_Miner_Metrics.json', 'w') as json_file:
            json_file.write(json.dumps(miner_scores))

    except Exception as e:
        print(f'Exception Occured : {e}')
        print()
        traceback.print_exc()
        with open(f'except/{datetime_folder}/Piqa_Miner_Metrics_{que_no}.json', 'w') as json_file:
            json_file.write(json.dumps(miner_scores))
            
if __name__ == "__main__":
    evaluate_models_piqa()

