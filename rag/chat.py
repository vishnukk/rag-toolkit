import os

from request import RequestBody
import requests
import search
import oci

from rag.oci_utils import initArgs, getEnvVariables, get_generative_ai_dp_client, getEndpoint, checkCompartmentPresent

args = initArgs()

def fetch_config():
    url = f"http://127.0.0.1:4119/get_config"
    resp = requests.request("GET", url).json()
    return resp


def get_info_from_guide(tool_result, rerank):
    question = tool_result.call.parameters["question"]
    answer = search.handle_chat_request(question, rerank)
    tool_result.outputs = [
        {
            "question": question,
            "answer": answer
        }
    ]



def vector_tool():
    param = oci.generative_ai_inference.models.CohereParameterDefinition()
    param.description = "question to look up in the guide"
    param.type = "str"
    param.is_required = True

    tool = oci.generative_ai_inference.models.CohereTool()
    tool.name = "get_info_from_guide"
    tool.description = "Retrieves information from the guide"
    tool.parameter_definitions = {
        "question": param
    }
    return tool

def config_tool():

    tool = oci.generative_ai_inference.models.CohereTool()
    tool.name = "get_config"
    tool.description = "Get the  configuration"
    return tool


def get_config(tool_result):
    config = fetch_config()
    tool_result.outputs = [
        {
            "config": config
        }
    ]

region, stage, profile, compartment_id = getEnvVariables()
generative_ai_inference_client = get_generative_ai_dp_client(
    endpoint=getEndpoint(region, stage),
    profile=profile,
    use_session_token=args.st)

checkCompartmentPresent(compartment_id)


chat_request = oci.generative_ai_inference.models.CohereChatRequest()
chat_request.max_tokens = 600
chat_request.is_stream = False
chat_request.is_force_single_step = False
chat_request.tools = [
    config_tool(),
    vector_tool()
]

chat_detail = oci.generative_ai_inference.models.ChatDetails()
chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
    model_id=os.getenv("CONFIG_FILE_LOCATION"))
chat_detail.compartment_id = compartment_id
chat_detail.chat_request = chat_request

map = {}

def generate_chat(request: RequestBody, conversation_id: str):
    chat_request.chat_history = None

    prompt = request.question
    re_rank = request.rerank
    chat_request.message = prompt
    chat_request.tool_results = None
    chat_response = generative_ai_inference_client.chat(chat_detail)

    tool_results = []
    tool_steps = []

    chat_request.message = ""
    while chat_response.data.chat_response.tool_calls is not None:
        for call in chat_response.data.chat_response.tool_calls:
            tool_result = oci.generative_ai_inference.models.CohereToolResult()
            tool_result.call = call
            if call.name == "get_config":
                get_config(tool_result)
            elif call.name == "get_info_from_guide":
                get_info_from_guide(tool_result, re_rank)
            tool_results.append(tool_result)
            tool_steps.append(chat_response.data.chat_response._text)

        chat_request.chat_history = chat_response.data.chat_response.chat_history
        # if conversation_id:
        #     map[conversation_id] = map[conversation_id] + chat_response.data.chat_response.chat_history

        chat_request.tool_results = tool_results
        chat_response = generative_ai_inference_client.chat(chat_detail)

        # print(chat_response.data.chat_response.text)
    return search.buildResponse(chat_response.data.chat_response.text,
                                cleanup(chat_response.data.chat_response.chat_history), tool_steps)



def cleanup(chat_history):
    for history in chat_history:
        history.swagger_types = None
        history.attribute_map = None

    return chat_history


# res = generateChat("What is the capital of India")
# print(res)
