# LangChain Cheat Sheet

## Basic LLM Call

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
response = llm.invoke("Explain Monad blockchain in 2 sentences")
print(response.content)
```

## Prompt Template

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role} agent."),
    ("user", "{input}"),
])
chain = prompt | llm
result = chain.invoke({"role": "researcher", "input": "Find Monad RPC URL"})
```

## Document Loading

```python
from langchain_community.document_loaders import TextLoader, DirectoryLoader

loader = TextLoader("datasets/sample_docs.md")
docs = loader.load()

# Or load directory
loader = DirectoryLoader("datasets/", glob="**/*.md")
docs = loader.load()
```

## Text Splitting

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)
```

## Embeddings + Vector Store

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory="./datasets/chroma")
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
```

## RAG Chain

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
answer = rag_chain.invoke("What is Monad?")
```

## Tools

```python
from langchain_core.tools import tool

@tool
def check_balance(address: str) -> str:
    """Check MON balance for an address."""
    return f"Balance for {address}: 1.25 MON"
```

## Hackathon Tip

Start with this kit's `services/rag_service.py` — swap in LangChain when you need production RAG.
