from datasets import load_dataset
import traceback
import re
from .response import  generate_model_response
import json

def extract_selected_option(model_response):
    # Define the option labels
    option_labels = ['A', 'B', 'C', 'D']
    
    if len(model_response) > 400:
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



def evaluate_models_openbookqa(data, datetime_folder):
    
    dataset = load_dataset("openbookqa")
    dataset = dataset['train']
    # Access individual columns from the dataset
    question_stems = dataset['question_stem'][:data]
    choices_list = dataset['choices'][:data]
    answer_keys = dataset['answerKey'][:data]

    miner_scores = dict()

    try:
        que_no = 1
        # Loop through each example in the dataset
        for question_stem, choice, answer_key in zip(question_stems, choices_list, answer_keys):
            # Generate the prompt to ask the model
            choices_text = choice['text']

            answer_text = ''
            prompt = f"{question_stem}?\n"
            for choice_text, label in zip(choices_text, choice['label']):
                if answer_key == label:
                    answer_text = choice_text
                    optn_max_len = len(choice_text)

                prompt += f"{label}. {choice_text}\n"

            print(128*'-')
            print(f"Getting question no: {que_no}, Getting this prompt: {prompt}")
            print()
            # Loop through each model and get their responses
            model_input = prompt  # Modify this if your model requires specific input format
            system_prompt = "You are an AI assistant. Your task is to reply correct option from given text and remember only answer in one character like (A,B,C,D) no other text"

            model_response = generate_model_response(system_prompt, model_input)

            for response in model_response['choices']:
                uid = response['uid']
                model_resp = response['message']['content']
                model_score = 0
                model_accuracy = 0

                if answer_key in extract_selected_option(model_resp):
                    model_score = 3
                    model_accuracy = 1
                else:
                    model_score = 1

                # Increment the score for the current model
                if uid in miner_scores.keys():
                    miner_scores[uid]['score'] += model_score
                    miner_scores[uid]['accuracy'] += model_accuracy
                else:
                    miner_scores[uid] = {'score': model_score, 'accuracy': model_accuracy}
            
            if que_no%100 == 0:
                    with open(f'checkpoints/{datetime_folder}/openbookqa/Openbook_Miner_Metrics_{que_no}.json', 'w') as chkpnt_file:
                        chkpnt_file.write(json.dumps(miner_scores))
                        
            que_no += 1
            
        with open(f'results/{datetime_folder}/Openbook_Miner_Metrics.json', 'w') as json_file:
            json_file.write(json.dumps(miner_scores))

    except Exception as e:
        print(f'Exception Occured : {e}')
        print()
        traceback.print_exc()
        with open(f'except/{datetime_folder}/Openbook_Miner_Metrics_{que_no}.json', 'w') as json_file:
            json_file.write(json.dumps(miner_scores))
            
            
if __name__ == "__main__":
    evaluate_models_openbookqa()

