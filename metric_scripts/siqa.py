from datasets import load_dataset
import traceback
import re
from .response import generate_model_response
import json

def extract_selected_option(model_response):
    # Define the option labels
    option_labels = ['A', 'B', 'C']
    
    if len(model_response) > 350:
        return "None"
    
    # Split the model response by sentences to handle complex structures
    response_sentences = re.split(r'[.!?]', model_response)

    # Loop through each sentence of the response and check for option labels
    for sentence in response_sentences:
        for option_label in option_labels:
            if re.search(r'\b' + re.escape(option_label) + r'[),.\n]?', sentence):
                return option_labels.index(option_label) + 1
            
    # If no option label is found, return None or a default value
    return "None"


def evaluate_models_siqa(data, datetime_folder):
    
    dataset = load_dataset("social_i_qa")
    dataset = dataset['train']
    # Access individual columns from the dataset
    contexts = dataset['context'][:data]
    questions = dataset['question'][:data]
    answerA = dataset['answerA'][:data]
    answerB = dataset['answerB'][:data]
    answerC = dataset['answerC'][:data]
    
    label = dataset['label'][:data]

    miner_scores = dict()
    try:
        que_no = 1
        # Loop through each example in the dataset
        for context, question, answerA, answerB, answerC, label in zip(contexts, questions, answerA, answerB, answerC, label):
            # Generate the prompt to ask the model
                            
            prompt = f"{context}{question}\nA. {answerA}\nB. {answerB}\nC. {answerC}" 

            print(128*'-')
            print(f"Getting question no: {que_no}, Getting this prompt: {prompt}")
            print()
            # Loop through each model and get their responses
            model_input = prompt  # Modify this if your model requires specific input format
            system_prompt = "You are an AI assistant. Your task is to reply correct option from given text and remember only answer in one character like (A,B,C), no other text"

            model_response = generate_model_response(system_prompt, model_input)
            for response in model_response['choices']:
                uid = response['uid']
                model_resp = response['message']['content']
                model_score = 0
                model_accuracy = 0

                if str(label) in str(extract_selected_option(model_resp)):
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
                    with open(f'checkpoints/{datetime_folder}/siqa/Siqa_Miner_Metrics_{que_no}.json', 'w') as chkpnt_file:
                        chkpnt_file.write(json.dumps(miner_scores))
                        
            que_no += 1
            
        with open(f'results/{datetime_folder}/Siqa_Miner_Metrics.json', 'w') as json_file:
            json_file.write(json.dumps(miner_scores))

    except Exception as e:
        print(f'Exception Occured : {e}')
        print()
        traceback.print_exc()
        with open(f'except/{datetime_folder}/Siqa_Miner_Metrics_{que_no}.json', 'w') as json_file:
            json_file.write(json.dumps(miner_scores))
            
if __name__ == "__main__":
    evaluate_models_siqa()

