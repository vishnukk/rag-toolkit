import argparse
import os
import oci

def make_security_token_signer(oci_config):
    pk = oci.signer.load_private_key_from_file(oci_config.get("key_file"), None)
    with open(oci_config.get("security_token_file")) as f:
        st_string = f.read()
    return oci.auth.signers.SecurityTokenSigner(st_string, pk)

def get_generative_ai_dp_client(endpoint, profile, use_session_token):
    config = oci.config.from_file(os.getenv("CONFIG_FILE_LOCATION"), profile)
    if use_session_token:
        signer = make_security_token_signer(oci_config=config)
        return oci.generative_ai_inference.GenerativeAiInferenceClient(config=config, signer=signer, service_endpoint=endpoint, timeout=(10,240))
    else:
        return oci.generative_ai_inference.GenerativeAiInferenceClient(config=config, service_endpoint=endpoint, timeout=(10,240))

def initArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--st", action="store_true", help="use session token")
    return parser.parse_args()


def getEnvVariables():
    region = "us-chicago-1"
    profile = "DEFAULT"
    compartment = "<compartment_ocid>"
    stage = "prod"
    if os.getenv("REGION") != None:
        region = os.getenv("REGION")

    if os.getenv("STAGE") != None:
        stage = os.getenv("STAGE")

    if os.getenv("PROFILE") != None:
        profile = os.getenv("PROFILE")

    if os.getenv("COMPARTMENT_ID") != None:
        compartment = os.getenv("COMPARTMENT_ID")

    return (region, stage, profile, compartment)


def getEndpoint(region, stage):
    if stage == "prod":
        return f"https://inference.genai.{region}.oci.oracle.com" #Dummy URLs
    elif stage == "dev":
        return f"https://dev.inference.genai.{region}.oci.oracle.com" #Dummy URLs
    elif stage == "ppe":
        return f"https://ppe.inference.genai.{region}.oci.oracle.com" #Dummy URLs
    else:
        print("Provide stage via env variable GENAI_STAGE: dev/ppe/prod")
        quit()

def checkCompartmentPresent(compartment_id):
    if "<compartment_ocid>" in compartment_id:
        print("ERROR:Please update your compartment id via env variable GENAI_COMPARMENT")
        quit()
