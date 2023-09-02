import gradio as gr
import json
import ssl
import http.client

def generate_top_response(system_prompt,model_input):
    payload = json.dumps(
            {"top_n": 30, "messages": [{"role": "system", "content": system_prompt},{"role": "user", "content": model_input}]}
        )

    headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer 7DhS7husq5VqSx8H1ZsVYvtx2IXYET9jM5iOJM0hwMZTkJpqBIE-n-zmFgZIkLyq",
            "Endpoint-Version": "2023-05-19",
    }
        
    context = ssl.create_default_context()
    context.check_hostname = True

    conn = http.client.HTTPSConnection("test.neuralinternet.ai", context=context)
    conn.request("POST", "/chat", payload, headers)
    response = conn.getresponse()
    utf_string = response.read().decode("utf-8").replace("\n", "").replace("\t", "")
    json_resp = json.loads(utf_string)
    conn.close()
    for choice in json_resp['choices']:
        return choice['message']['content']

def generate_benchmark_response(system_prompt,model_input):
    payload = json.dumps(
            {"uids": [86,294,519,387,938,198,40,292,509], "messages": [{"role": "system", "content": system_prompt},{"role": "user", "content": model_input}]}
        )

    headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer 7DhS7husq5VqSx8H1ZsVYvtx2IXYET9jM5iOJM0hwMZTkJpqBIE-n-zmFgZIkLyq",
            "Endpoint-Version": "2023-05-19",
    }
        
    context = ssl.create_default_context()
    context.check_hostname = True

    conn = http.client.HTTPSConnection("test.neuralinternet.ai", context=context)
    conn.request("POST", "/chat", payload, headers)
    response = conn.getresponse()
    utf_string = response.read().decode("utf-8").replace("\n", "").replace("\t", "")
    json_resp = json.loads(utf_string)
    #print(utf_string)
    conn.close()
    for choice in json_resp['choices']:
        return choice['message']['content']
def dynamic_function(prompt):
    system_prompt = "You are an AI assistant, Your task is to provide accurate response based on user prompt"
    
    top_response = generate_top_response(system_prompt, prompt) 
    benchmark_response = generate_benchmark_response(system_prompt, prompt)
    
    return f"TOP: {top_response}\n\n\nBenchmark:{benchmark_response}"

interface = gr.Interface(
    fn=dynamic_function,
    inputs= gr.inputs.Textbox(label="Enter Prompt"),
    outputs=gr.outputs.Textbox(label="Responses"),
    title="Bittensor Compare Util",
)


# Launch the Gradio Interface
interface.launch(share=True, enable_queue=True)
 