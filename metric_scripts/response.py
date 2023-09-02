import json
import http.client
import ssl


def generate_model_response(system_prompt,model_input):
    payload = json.dumps(
            {"top_n": 200, "messages": [{"role": "system", "content": system_prompt},{"role": "user", "content": model_input}]}
        )
    
    headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer EDsO2sTnDxMTFc8dXVYLLs75ItTOePt942QfgMjyDPIXCZH8u8nDfa8MnVeKD-A_",
            "Endpoint-Version": "2023-05-19",
    }
        
    context = ssl.create_default_context()
    context.check_hostname = True

    #conn = http.client.HTTPSConnection("test.neuralinternet.ai", context=context)
    conn = http.client.HTTPConnection("localhost", 8000)
    conn.request("POST", "/chat", payload, headers)
    response = conn.getresponse()
    utf_string = response.read().decode("utf-8").replace("\n", "").replace("\t", "")
    json_resp = json.loads(utf_string)
    #print(utf_string)
    conn.close()
    return json_resp