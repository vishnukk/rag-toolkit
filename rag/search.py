import array
import os
from db_utils import cursor as cur

import oracledb
import embed_text
import cohere
from langchain.prompts import PromptTemplate


co = cohere.Client( os.getenv("COHERE_TOKEN"))
template = ("Given the following context: {result}. \n "
            "Answer the question the question based only on the context."
            " If no mentions found, return 'Unable to find the answer.' \n Question:\n {question}")

oracledb.init_oracle_client()

def search_data(cursor, vec):
    docs = []
    cursor.setinputsizes(oracledb.DB_TYPE_VECTOR)
    cursor.execute(f"""
		select  text, vector_distance(vec, to_vector(:1), COSINE) as similarity
		from {os.getenv("EMBEDDING_TABLE")}
		order by similarity 
		fetch first 5 rows only where
	""", vec)
    #count = 1
    for index, row in enumerate(cursor):
        docs.append(f"{index+1}) distance - {row[1]}"  f"\\n{row[0]}\\n")

    return docs


def rerank(query, docs):
    context_documents = []
    rerank_results = co.rerank(
        query=query, documents=docs, top_n=3, model='rerank-english-v3.0', return_documents=True)
    print("**************************Reranking started**************************")
    for index, rerank_result in enumerate(rerank_results.results):
        context_documents.append(f"{index+1}. Relevance score of re-ranking - {rerank_result.relevance_score}")
        context_documents.append(f"{rerank_result.document.text[rerank_result.document.text.find('distance'):]}")

    print("**************************Reranking completed**************************")
    return context_documents


def get_formatted_context(records):
    res = ''
    for record in records:
        res += ' \n\n ' + record

    return res


def get_context(question, result):
    prompt = PromptTemplate(
        input_variables=["question", "result"],
        template=template)
    prompts = prompt.format(question=question, result=get_formatted_context(result))
    return prompts


def buildResponse(response, context, tool_steps):
    data = {}
    data['response'] = response
    data['steps'] = tool_steps
    data['context'] = context

    return data

def handle_chat_request(query, is_rerank):
    context = search_query(query, is_rerank)
    prompts = get_context(query, context)
    return prompts


def search_query(query, is_rerank):
    q = []
    q.append(query)
    vec = list(embed_text.embedText(q)[0])
    vec2 = array.array('d', vec)
    context = search_data(cur, [vec2])
    if is_rerank:
        context = rerank(query, context)
    return context
