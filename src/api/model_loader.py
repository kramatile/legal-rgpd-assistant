from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_neo4j import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_neo4j import Neo4jGraph

class GraphRag():
    def __init__(self,model_name,api_key,url,username,password):
        self.graph = Neo4jGraph( url=url, username=username, password=password)
        self.vector_graph = Neo4jVector.from_existing_graph( HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),    
                                        url=url,    
                                        username=username,    
                                        password=password,    
                                        node_label="article",    
                                        text_node_properties=["text"],    
                                        embedding_node_property="embedding",    
                                        index_name="articles",
                                        ).as_retriever()
        self.llm = ChatOpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1",
                    model=model_name,
                    default_headers={
                        "HTTP-Referer": "http://localhost",   
                        "X-Title": "LegalGraphRAG",            
                    },
                )
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(""" 
                You are an expert Neo4j developer. Use the following database schema to write a Cypher statement to answer the user's question. Only generate the Cypher statement, no pre-amble. Do not return any Markdown.
            STRICT RULES:
            - NEVER use CONTAINS inside property maps {{}}
            - NEVER write: {{property: CONTAINS "..."}}
            - ALWAYS use WHERE for string filtering
            - Only generate READ-ONLY Cypher (MATCH, WHERE, RETURN)
            - Do NOT use DELETE, SET, CREATE, MERGE
            - Return only the Cypher query, nothing else

            Schema: 
            {schema}
            
            Question: {input}""", 
            partial_variables={"schema": self.graph.schema})
        ])

        self.graph_qa_prompt = ChatPromptTemplate.from_messages([  
            SystemMessagePromptTemplate.from_template("""    You are a helpful legal assistant answering questions about General Data Protection Regulation GDPR the European Union regulation on information privacy in the European Union (EU law in french.    
                                                    You are given a question and a context.    
                                                    Question: {input}    
                                                    """
                                                    ),
            SystemMessagePromptTemplate.from_template("""    The following context has been retrieved from the database using vector search to help    
                                                    you answer the question:     
                                                    {vectors}   
                                                    """),
            SystemMessagePromptTemplate.from_template("""    The following data has been retrieved from the knowledge graph using Cypher to    
                                                    answer the question.      
                                                    {records}    
                                                    You can treat any information contained from the knowledge graph as authoritative.    
                                                    If the information does not exist in this answer, fall back to vector search results.    
                                                    If the answer is not included in either just say that you don't know and don't rely    
                                                    on pre-existing knowledge."""),
            ])
        



    def invoke(self,query):
        text_to_cypher_chain = self.prompt | self.llm | StrOutputParser()
        graphrag_qa_chain = RunnablePassthrough.assign(    
            vectors=RunnableLambda(lambda x: self.vector_graph.invoke(x["input"])),    
            records=text_to_cypher_chain | self.graph.query) | self.graph_qa_prompt    | self.llm    | StrOutputParser()
        
        return graphrag_qa_chain.invoke({"input":query})
