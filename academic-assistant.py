import streamlit as st
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.vectorstores import FAISS
import tempfile
import os
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.schema.output_parser import StrOutputParser

from dotenv import load_dotenv
import json
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Optional
from langchain.tools import BaseTool
from langchain.tools import tool
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

load_dotenv()

# -------------------- Page Configuration --------------------
st.set_page_config(page_title="Smart Academic Assistant", layout="centered")

# -------------------- Title --------------------
st.title("📚 Smart Academic Assistant")
st.write("Upload your documents and ask questions to get structured answers.")

# -------------------- File Upload Section --------------------
uploaded_files = st.file_uploader(
    "Upload documents (PDF, DOCX, or TXT):",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

# -------------------- Question Input --------------------
question = st.text_input("Enter your question:")

# -------------------- Submit Button --------------------
if st.button("Get Answer"):
    if not uploaded_files or not question:
        st.warning("Please upload at least one document and enter a question.")
    else:
        # -------------------- PLACEHOLDER: RAG Pipeline Logic --------------------
        # TODO:
        # 1. Load documents using LangChain document loaders
        documents = []
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                if uploaded_file.name.endswith('.pdf'):
                    loader = PyPDFLoader(tmp_file_path)
                elif uploaded_file.name.endswith('.docx'):
                    loader = Docx2txtLoader(tmp_file_path)
                elif uploaded_file.name.endswith('.txt'):
                    loader = TextLoader(tmp_file_path)
                
                docs = loader.load()

                for doc in docs:
                    doc.metadata['source'] = uploaded_file.name
                
                documents.extend(docs)

            finally:
                os.unlink(tmp_file_path)
    
        # 2. Split documents using RecursiveCharacterTextSplitter or similar
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = splitter.split_documents(documents)

        # 3. Create embeddings and store in vector store (e.g., FAISS, Chroma)
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vectorstore = FAISS.from_documents(chunks, embeddings)

        # 4. Retrieve relevant chunks based on the question
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        retrieved_doc = retriever.invoke(question) # pehle get_relevant_documents tha 

        # 5. Use Groq-hosted LLM via LangChain (e.g., Mixtral, Gemma, Llama3)
        llm = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct")

        class StructuredAnswer(BaseModel):
            answer: str = Field(description="Detailed answer to the question")
            confidence: float = Field(description="Confidence score between 0 and 1")

        parser = PydanticOutputParser(pydantic_object=StructuredAnswer)

        template = PromptTemplate(
            template="""Based on the following context, answer the question. If the question being asked is not from the context, just say so.
    
            {format_instructions}
    
            Context: {context}
            Question: {question}""",   
            input_variables=["context", "question"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        #chain = template|llm|retriever|parser

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type_kwargs={"prompt": template},
            return_source_documents=True
        )

        result = qa_chain.invoke({"query": question})

        # 6. Use Output Parser to format structured response
        
        source_documents = result.get("source_documents", [])

        if source_documents:
            source_document = source_documents[0].metadata.get("source", "Unknown")
        else:
            source_document = "Unknown"


        try:
            structured_response = parser.parse(result["result"])
            answer = structured_response.answer
            confidence_score = structured_response.confidence
        except Exception as e:
            st.error(f"Failed to parse LLM response: {e}")
            answer = result["result"]
            confidence_score = 0.50

        response = {
            "question": question,
            "answer": answer,
            "source_document": source_document,
            "confidence_score": confidence_score
        }
        
        st.subheader("📄 Answer:")
        st.write(answer)
        st.subheader("📄 Confidence:")
        st.write("The mode is",confidence_score*100,"%"," sure that this is the right answer.")
        st.subheader("📄 Source Document:")
        st.write(source_document)

        #st.info("Implement your RAG logic above and display the final structured response here.")

# -------------------- Bonus Section: Agent Tools --------------------
st.markdown("---")
st.subheader("🧠 Bonus Tools")

tab1, tab2, tab3 = st.tabs(["📝 Summarize", "❓ Generate MCQs", "📚 Topic Explanation"])


documents = []
for uploaded_file in uploaded_files:
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
            
    try:
        if uploaded_file.name.endswith('.pdf'):
            loader = PyPDFLoader(tmp_file_path)
        elif uploaded_file.name.endswith('.docx'):
            loader = Docx2txtLoader(tmp_file_path)
        elif uploaded_file.name.endswith('.txt'):
            loader = TextLoader(tmp_file_path)
                
        docs = loader.load()

        for doc in docs:
            doc.metadata['source'] = uploaded_file.name
                
        documents.extend(docs)

    finally:
        os.unlink(tmp_file_path)


def run_ragchain(question, retriever_obj, ans_temp):
    """Execute the pipleine"""
    def clean_text(docs):
        return [doc.page_content.replace("Title:", "").replace("Source:", "")
        for doc in docs]
    prompt = ans_temp
    rag_chain = (
        RunnableParallel({
            "context": retriever_obj | clean_text,
            "question": RunnablePassthrough()
        })
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain.invoke(question)

# For the summary

@tool
def summarize_tool(tool_input: str = "") -> str:
    """Summarizes the give document(s)"""
    prompt = """You are an academic assistant. Create a comprehensive yet concise summary of the documents..."""
    return run_ragchain("Summarize the uploaded documents.", st.session_state["retriever"], prompt)
        
answer_prompt1 = PromptTemplate(
    template="""You are an academic assistant designed to give summary of the documents uploaded. There maybe be more than one, read and give a summary accordingly according to the context provided 
            
    Context: {context}
    """,
    input_variables=['context']
)


# For the MCQs

@tool
def mcq_tool(input: str) -> str:
    """Generates 5 multiple choice questions from the uplaoded documents"""
    prompt = """You are an academic assistant and are to provide us with 5 good multiple choice questions with 4 logical options labeled from A to D. One of these options must be the correct answer. At the end of all the questions, provide the right answer to each question. Below is the text based on which questions should be generated
    
    Context={context}.

    MCQs
    """

answer_prompt2 = PromptTemplate(
    template="""You are an academic assistant designed to give 5 multiple choice questions based on the documents uploaded.
    Context={context}.
    The outline of your response should be:
    Question:
    Option A:
    \nOption B:
    \nOption C:
    \nOption D:

    Answer:
    """,
    input_variables=['context']
)



# For topic explanation
@tool
def topic_explanation_tool(input:str) -> str:
    """Generates the explanation of a topic asked by the user"""
    prompt="""Read the context given and provide a detailed explanation of the topic asked.
    Context={context}.
    Topic={topic}
    Explanation:
    """

answer_prompt3 = PromptTemplate(
    template="""You are a helpful academic assistant, provide a detailed expplanation of {topic} based on the context given. Say you do not know if the question is not from the context.
    Context:{context}
    """,
    input_variables=['topic', 'context']
)


# 2. Split documents using RecursiveCharacterTextSplitter or similar
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)
chunks = splitter.split_documents(documents)

# 3. Create embeddings and store in vector store (e.g., FAISS, Chroma)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
vectorstore = FAISS.from_documents(chunks, embeddings)

# 4. Retrieve relevant chunks based on the question
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})


llm = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct")
llm_with_tools = llm.bind_tools([summarize_tool, mcq_tool, topic_explanation_tool])
full_text = "\n\n".join([doc.page_content for doc in documents])
with tab1:
    if st.button("Summarize Document"):
        # TODO: Implement SummarizeDocumentTool using LangChain agent
        result1 = run_ragchain(full_text, retriever, answer_prompt1)
        st.write(result1)
        st.info("Summary will be shown here.")

with tab2:
    if st.button("Generate MCQs"):
        # TODO: Implement GenerateMCQsTool using LangChain agent
        result2 = run_ragchain(full_text, retriever, answer_prompt2)
        st.write(result2)
        st.info("Generated MCQs will appear here.")

with tab3:
    topic = st.text_input("Enter to topic to be explained")
    if st.button("Topic-wise Explanation"):
        # TODO: Implement TopicWiseExplanationTool using LangChain agent
        result3 = topic_explanation_tool(topic)
        st.write(result3)
        st.info("Topic-wise explanation will be displayed here.")

# -------------------- Footer --------------------
st.markdown("---")
st.caption("Project-1")
