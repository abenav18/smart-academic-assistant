# 🧠 Smart Academic Assistant
The Smart Academic Assistant is a web-based tool that allows users to upload documents and ask questions to receive structured answers. This project utilizes the Streamlit framework to create a user-friendly interface and leverages the LangChain library to process documents and generate answers. The assistant is designed to help students, researchers, and professionals quickly find relevant information and answers to their questions.

## 🚀 Key Features
- **Document Upload**: Users can upload documents in various formats, including PDF, DOCX, and TXT.
- **Question Answering**: The assistant uses the LangChain library to process the uploaded documents and generate answers to user questions.
- **Customizable Prompts**: Users can customize the prompts and output parsers to suit their specific needs.
- **Efficient Document Representation**: The assistant uses embeddings and vector stores to efficiently represent and retrieve documents.
- **User-Friendly Interface**: The Streamlit framework provides a user-friendly interface for users to interact with the assistant.

## 🛠️ Tech Stack
* **Frontend**: Streamlit
* **Backend**: Python, LangChain
* **Database**: FAISS, Hugging Face Hub
* **AI Tools**: LangChain, Sentence Transformers
* **Build Tools**: Python Dotenv, Pydantic
* **Document Loaders**: PyPDFLoader, Docx2txtLoader, TextLoader
* **Dependencies**: Streamlit, LangChain, LangChain Core, LangChain Community, LangChain Groq, FAISS, Hugging Face Hub, Sentence Transformers, Python Dotenv, Pydantic, Docx2txt, Tiktoken, PyPDF

## 📦 Installation
### Prerequisites
- Python 3.8 or higher
- pip package manager
- Streamlit framework
- LangChain library

### Installation Steps
1. Clone the repository: `git clone https://github.com/your-repo/smart-academic-assistant.git`
2. Navigate to the repository: `cd smart-academic-assistant`
3. Install the dependencies: `pip install -r requirements.txt`
4. Run the application: `streamlit run academic-assistant.py`

## 💻 Usage
1. Upload a document using the file uploader.
2. Enter a question in the question input field.
3. Click the submit button to generate an answer.
4. The answer will be displayed on the web interface.

## 📂 Project Structure
```markdown
smart-academic-assistant/
├── academic-assistant.py
├── requirements.txt
├── document_loaders/
│   ├── PyPDFLoader.py
│   ├── Docx2txtLoader.py
│   ├── TextLoader.py
├── embeddings/
│   ├── HuggingFaceEmbeddings.py
│   ├── FAISS.py
├── prompt_templates/
│   ├── PromptTemplate.py
│   ├── StrOutputParser.py
│   ├── PydanticOutputParser.py
├── utils/
│   ├── utils.py
```

## 📸 Screenshots

## 🤝 Contributing
Contributions are welcome! If you'd like to contribute to the Smart Academic Assistant, please fork the repository and submit a pull request.

## 📝 License
The Smart Academic Assistant is licensed under the MIT License.

## 📬 Contact
For any questions or concerns, please contact us at [your-email@example.com](mailto:your-email@example.com).

## 💖 Thanks Message
A huge thank you to everyone who has contributed to the Smart Academic Assistant! Your support and contributions are greatly appreciated.
This is written by [readme.ai](https://readme-generator-phi.vercel.app/)
