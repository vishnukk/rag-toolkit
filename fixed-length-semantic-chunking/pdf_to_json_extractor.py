
from unstructured.partition.pdf import partition_pdf # version unstructured 0.11.5

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path ="../.env", override=True)


# Define parameters for Unstructured's library

## include_page_breaks
# include page breaks
include_page_breaks = False

## strategy
# The strategy to use for partitioning the PDF. Valid strategies are "hi_res", "ocr_only", and "fast".
# When using the "hi_res" strategy, the function uses a layout detection model to identify document elements.
# hi_res" is used for analyzing PDFs and extracting table structure (default is "auto")
strategy = "hi_res"

## infer_table_structure
# Only applicable if `strategy=hi_res`.
# If True, any Table elements that are extracted will also have a metadata field named "text_as_html" where the table's text content is rendered into an html string.
# I.e., rows and cells are preserved.
# Whether True or False, the "text" field is always present in any Table element and is the text content of the table (no structure).

if strategy == "hi_res": infer_table_structure = True
else: infer_table_structure = False

## extract_element_types
# Get images of tables
if infer_table_structure == True: extract_element_types=['Table']
else: extract_element_types=None

## max_characters
# The maximum number of characters to include in a partition (document element)
# If None is passed, no maximum is applied.
# Only applies to the "ocr_only" strategy (default is 1500)
# max_characters = 2000
if strategy != "ocr_only": max_characters = None

## languages
# The languages to use for the Tesseract agent.
# To use a language, you'll first need to install the appropriate Tesseract language pack.
languages = ["eng"] # example if more than one "eng+por" (default is "eng")

## model_name
# @requires_dependencies("unstructured_inference")
# yolox: best model for table extraction. Other options are yolox_quantized, detectron2_onnx and chipper depending on file layout
# source: https://unstructured-io.github.io/unstructured/best_practices/models.html
hi_res_model_name = "yolox"



filename = os.getenv("PDF_FILE_NAME")

# Returns a List[Element] present in the pages of the parsed pdf document
elements = partition_pdf(
    filename=filename,

    include_page_breaks=include_page_breaks,
    strategy=strategy,
    infer_table_structure=infer_table_structure,
    extract_element_types=extract_element_types,
    max_characters=max_characters,
    languages=languages,
    hi_res_model_name=hi_res_model_name,
    starting_page_number=9,
)

# get output as json
from unstructured.staging.base import elements_to_json
elements_to_json(elements, filename=os.getenv("FILE_NAME"))


