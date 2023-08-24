from datasets import load_dataset
import traceback
import re
from .response import generate_model_response
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



def evaluate_models_mmlu(data, datetime_folder):
    
    configs = ['high_school_european_history', 'business_ethics', 'clinical_knowledge', 'medical_genetics', 'high_school_us_history', 'high_school_physics', 'high_school_world_history', 'virology', 'high_school_microeconomics', 'econometrics', 'college_computer_science', 'high_school_biology', 'abstract_algebra', 'professional_accounting', 'philosophy', 'professional_medicine', 'nutrition', 'global_facts', 'machine_learning', 'security_studies', 'public_relations', 'professional_psychology', 'prehistory', 'anatomy', 'human_sexuality', 'college_medicine', 'high_school_government_and_politics', 'college_chemistry', 'logical_fallacies', 'high_school_geography', 'elementary_mathematics', 'human_aging', 'college_mathematics', 'high_school_psychology', 'formal_logic', 'high_school_statistics', 'international_law', 'high_school_mathematics', 'high_school_computer_science', 'conceptual_physics', 'miscellaneous', 'high_school_chemistry', 'marketing', 'professional_law', 'management', 'college_physics', 'jurisprudence', 'world_religions', 'sociology', 'us_foreign_policy', 'high_school_macroeconomics', 'computer_security', 'moral_scenarios', 'moral_disputes', 'electrical_engineering', 'astronomy', 'college_biology']

    mmlu_weights_config = open('weights/mmlu_configs.json')
    dataset_categories = json.load(mmlu_weights_config)

    data_per_config = int(data/len(configs))
    system_prompt = 'You are an AI assistant. Your task is choose an option for multiple fill in the blanks question,  remember only answer in one character like (A,B,C,D) no other text'

    miner_scores = dict()

    try:
        que_no = 1
        for config in configs:
            dataset = load_dataset('lukaemon/mmlu', config)
            dataset = dataset['test']
            questions = dataset['input'][:data_per_config]
            option_labels = ['A', 'B', 'C', 'D']

            # Zip the options columns and the question column
            options_columns = [dataset[option][:data_per_config] for option in option_labels]
            answer_keys = dataset['target'][:data_per_config]
            
            print(128*'-')            
            
            for question, options, answer in zip(questions, zip(*options_columns), answer_keys):
                
                prompt = question + '\n'
                for label, opt in zip(option_labels, options):
                    prompt += f"{label}. {opt}\n"

                
                print(f"Getting question no: {que_no}, Getting this prompt: {prompt}")
                print()
                
                model_response = generate_model_response(system_prompt, prompt)

                for response in model_response['choices']:
                    uid = response['uid']
                    model_resp = response['message']['content']
                    model_score = 0
                    model_accuracy = 0

                    if answer in extract_selected_option(model_resp):
                        model_score = 2 * dataset_categories[config]
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
                    with open(f'checkpoints/{datetime_folder}/mmlu/MMLU_Miner_Metrics_{que_no}.json', 'w') as chkpnt_file:
                        chkpnt_file.write(json.dumps(miner_scores))
                    
                que_no += 1

        with open(f'results/{datetime_folder}/MMLU_Miner_Metrics.json', 'w') as json_file:
            json_file.write(json.dumps(miner_scores))

    except Exception as e:
        print(f'Exception Occured : {e}')
        print()
        traceback.print_exc()
        with open(f'except/{datetime_folder}/MMLU_Miner_Metrics_{que_no}.json', 'w') as json_file:
            json_file.write(json.dumps(miner_scores))

            
if __name__ == "__main__":
    evaluate_models_mmlu()

