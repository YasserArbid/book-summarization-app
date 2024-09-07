import streamlit as st
import openai
import os
import PyPDF2
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
from langchain import PromptTemplate
from langchain import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from dotenv import load_dotenv


# Functions to process the book and interact with OpenAI
def get_book_text(pdf_file_path):
    """Extracts text from PDF file using PyPDF2"""
    if not pdf_file_path:
        return ""

    try:
        with open(pdf_file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in range(len(reader.pages)):
                page = reader.pages[page]
                text += str(page.extract_text())
            return text
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        return ""

def get_openai_response(prompt, engine="gpt-3.5-turbo-instruct"):
    """Fetches response from OpenAI using the specified prompt and engine"""
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

def summarize_pdf(pdf_file_path):
    """
    Summarizes a PDF using a custom prompt with OpenAI.

    Args:
        pdf_file_path: Path to the PDF file.

    Returns:
        The custom summary generated by OpenAI.
    """
    loader = PyPDFLoader(pdf_file_path)
    docs = loader.load_and_split()
    prompt_template = """ please make a custom summary for
    {text}
    SUMMARY:"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])

    #llm = ChatOpenAI()  # Initialize the OpenAI model  model="gpt-3.5-turbo"
    load_dotenv()

    
    llm = OpenAI(temperature=0, openai_api_key = os.getenv("OPENAI_API_KEY"))
    chain = load_summarize_chain(llm, chain_type="map_reduce", map_prompt=PROMPT)
    custom_summary = chain({"input_documents": docs}, return_only_outputs=True)["output_text"]
    return custom_summary

# Define the four prompts for book summarization
prompt_get_chapters = """This book is titled "{title}", Act as a professional book summarizer and provide the exact list of chapter titles of the uploaded book."""
prompt_summarize_chapter = """This book is titled "{title}", Act as a professional book summarizer and summarize each Chapter separately."""
prompt_extract_keywords = """This book is titled "{title}", Act as a professional book summarizer and extract the key words from each Chapter."""

def main():
    st.title("Book Summarizer")
    st.subheader("Summarize your book")

    # Option 1: Text input for file path
    pdf_file_path = st.text_input("Enter the path to your book:")

    # Option 2: File uploader to get the file path
    uploaded_file = st.file_uploader("Or upload your Book...", type=["pdf"])
    if uploaded_file:
        pdf_file_path = uploaded_file.name
        with open(pdf_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded file: {pdf_file_path}")

    text_content = ""

    if pdf_file_path:
        st.write("PDF path set successfully!")

    # Buttons for different functionalities
    submit_chapters = st.button("Get Chapters Titles")
    submit_summarize_chapter = st.button("Summarize Each And Every Chapter")
    submit_keywords = st.button("Extract Chapters Keywords")
    submit_custom_summary = st.button("Full Book Summary")

    if submit_chapters:
        if pdf_file_path:
            text_content = get_book_text(pdf_file_path)
            response = get_openai_response(
                prompt_get_chapters.format(title=os.path.splitext(os.path.basename(pdf_file_path))[0])
            )
            st.subheader("Chapter Titles:")
            st.write(response)
        else:
            st.write("Please provide a PDF file path to proceed.")

    elif submit_summarize_chapter:
        if pdf_file_path:
            text_content = get_book_text(pdf_file_path)
            response = get_openai_response(
                prompt_summarize_chapter.format(title=os.path.splitext(os.path.basename(pdf_file_path))[0])
            )
            st.subheader("Summary of each Chapter:")
            st.write(response)
        else:
            st.write("Please provide a PDF file path to proceed.")

    elif submit_keywords:
        if pdf_file_path:
            text_content = get_book_text(pdf_file_path)
            response = get_openai_response(
                prompt_extract_keywords.format(title=os.path.splitext(os.path.basename(pdf_file_path))[0])
            )
            st.subheader("Keywords from each Chapter:")
            st.write(response)
        else:
            st.write("Please provide a PDF file path to proceed.")

    elif submit_custom_summary:
        if pdf_file_path:
            custom_summary = summarize_pdf(pdf_file_path)
            st.write(custom_summary)
        else:
            st.error("Please provide a PDF file path to proceed.")

if __name__ == "__main__":
    main()
    
footer = """
---
#### Made By [Yasser Arbid](https://www.linkedin.com/in/yasser-arbid/)    *AI Expert* 
For Queries, Reach out on [LinkedIn](https://www.linkedin.com/in/yasser-arbid/)   
*Making books summarization easier*
"""

st.markdown(footer, unsafe_allow_html=True)
