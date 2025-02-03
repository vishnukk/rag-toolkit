import json
import oracledb
import embed_text
import cohere

from dotenv import load_dotenv
from db_utils import cursor
import os

load_dotenv(dotenv_path ="../.env", override=True)

co = cohere.Client( os.getenv("COHERE_TOKEN"))


chunk_size = 95
vectors_list= []

table = os.getenv("EMBEDDING_TABLE")

def create_table():
    cursor.execute(f"""
    	begin
     		execute immediate 'drop table ${table}';
      		exception when others then if sqlcode <> -942 then raise; end if;
    	end;""")
    cursor.execute(f"""
 		create table ${table} (
   	    	id number,
			text varchar2(4000),
    	    vec vector(1024, float64),
        	primary key (id)
		)""")


def insert_data(id, chunk, vec):

    cursor.setinputsizes(None, 4000, oracledb.DB_TYPE_VECTOR)
    cursor.execute(f"insert into ${table} values (:1, :2, :3)", [
        id, chunk, vec])


def read_data():
    cursor.execute(f'select * from ${table}')
    for row in cursor:
        print(f"{row[0]}:{row[1]}")


def dbProcess(vectors):
    # print("creating table")
    create_table()
    for i in range(len(vectors)):
        insert_data(i, serialized_data[i], list(vectors[i]))
    # print("commiting complete")
    connection.commit()


def divide_chunks(serialized_data, n):
    for i in range(0, len(serialized_data), n):
        yield serialized_data[i:i + n]


filename = os.getenv("PROCESSED_FILE_NAME")
f = open(filename)
data = json.load(f)


serialized_data = []
template = '''\
Header: {header}
Title: {title}
Body:\
'''

for record in data:
    for rec in record['context']:
        if len(rec['body']) > 0:
            tmp = template.format(header=record['header'], title=rec['title'])
            tmp += '\n' + '\n'.join(rec['body'])
            serialized_data.append(tmp)



if len(serialized_data) > 95:
    chunk_list = [serialized_data[i:i + chunk_size]
                  for i in range(0, len(serialized_data), chunk_size)]
    for chunk_serialized_data in chunk_list:
        vectors = embed_text.embedText(chunk_serialized_data)
        vectors_list = vectors_list + vectors
    dbProcess(vectors_list)

else:
    vectors = embed_text.embedText(serialized_data)
    print(type(vectors))
    dbProcess(vectors)
