from datasets import load_dataset
import traceback
import re
from .response import generate_model_response
import json


def extract_selected_option(model_response):
    # Define the option labels
    option_labels = ['A', 'B', 'C', 'D']
    
    if len(model_response) > 500:
        return "None"
    
    # Split the model response by sentences to handle complex structures
    response_sentences = model_response.split('\n')
    # Loop through each sentence of the response and check for option labels
    for sentence in response_sentences:
        for option_label in option_labels:
            if re.search(re.escape(option_label) + r'[),.\n].*?', sentence):
                return option_label
            
    # If no option label is found, return None or a default value
    return "None"



def evaluate_models_race(data, datetime_folder):
    
    dataset = load_dataset("race", "high")
    dataset = dataset['test']
    # Access individual columns from the dataset
    articles = dataset['article'][:data]
    questions = dataset['question'][:data]
    options = dataset['options'][:data]
    answers = dataset['answer'][:data]

    miner_scores = dict()

    try:
        que_no = 1
        # Loop through each example in the dataset
        for article, question, option, answer in zip(articles, questions, options, answers):
            # Generate the prompt to ask the model
            
            answer_text = ''
            prompt = f"{article}{question}\nA.{option[0]}\nB.{option[1]}\nC.{option[2]}\nD.{option[3]}"
            
            print(128*'-')
            print(f"Getting question no: {que_no}, Getting this prompt: {prompt}")
            print()
            # Loop through each model and get their responses
            model_input = prompt  # Modify this if your model requires specific input format
            system_prompt = "You are an AI assistant. Your task is to reply correct option from given text and give final answer which has only one character like (A,B,C,D) no other text"

            model_response = generate_model_response(system_prompt, model_input)

            for response in model_response['choices']:
                uid = response['uid']
                model_resp = response['message']['content']
                model_score = 0
                model_accuracy = 0

                if answer in extract_selected_option(model_resp):
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
                    with open(f'checkpoints/{datetime_folder}/race/Race_Miner_Metrics_{que_no}.json', 'w') as chkpnt_file:
                        chkpnt_file.write(json.dumps(miner_scores))
                        
            que_no += 1
            
        with open(f'results/{datetime_folder}/Race_Miner_Metrics.json', 'w') as json_file:
            json_file.write(json.dumps(miner_scores))

    except Exception as e:
        print(f'Exception Occured : {e}')
        print()
        traceback.print_exc()
        with open(f'except/{datetime_folder}/Race_Miner_Metrics_{que_no}.json', 'w') as json_file:
            json_file.write(json.dumps(miner_scores))
            
            
if __name__ == "__main__":
    evaluate_models_race()

