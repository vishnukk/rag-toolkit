
import oci
import cohere
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path =".env", override=True)

co = cohere.Client( os.getenv("COHERE_TOKEN"))


# Setup basic variables
# Auth Config
compartment_id =os.getenv("COMPARTMENT_ID")
CONFIG_PROFILE = os.getenv("PROFILE")
config = oci.config.from_file(os.getenv("CONFIG_FILE_LOCATION"), CONFIG_PROFILE)

# Service endpoint
endpoint = os.getenv("INFERENCE_ENDPOINT")

generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(config=config,
                                                                                         service_endpoint=endpoint,
                                                                                         retry_strategy=oci.retry.NoneRetryStrategy(),
                                                                                         timeout=(10,240))


embed_text_detail = oci.generative_ai_inference.models.EmbedTextDetails()

embed_text_detail.serving_mode = (oci.generative_ai_inference.models
                                  .OnDemandServingMode(model_id=os.getenv("COHERE_EMBEDDING_MODEL")))
embed_text_detail.compartment_id = compartment_id

def embed_text(input):
    embed_text_detail.inputs = input
    if "<compartment_ocid>" in compartment_id:
        print("ERROR:Please update your compartment id in target python file")
        quit()

    embed_text_response = generative_ai_inference_client.embed_text(embed_text_detail)
    return embed_text_response.data.embeddings

def embed_cohere(data):
    response = co.embed(
        model=os.getenv("COHERE_EMBEDDING_MODEL"),
        texts=data,
        input_type='classification',
        truncate='NONE'
    )

    return response.embeddings







