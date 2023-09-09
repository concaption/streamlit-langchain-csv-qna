"""
This is a simple chatbot app that uses the streamlit_chat library to create a chatbot
for a CSV file.
"""
import sys
import os
from pathlib import Path

import streamlit as st

from streamlit_chat import message
from langchain.document_loaders import CSVLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

__import__("pysqlite3")


sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

os.environ["OPENAI_API_KEY"] = st.secrets["open_ai_api_key"]

st.title("CSV Question and answer ChatBot")

csv_file_uploaded = st.file_uploader(label="Upload your CSV File here")


def save_file_to_folder(uploaded_file):
    """
    This function saves the uploaded file to the "content" folder.

    Args:
        uploaded_file (streamlit.uploaded_file_manager.UploadedFile): The uploaded file

    Returns:
        None
    """
    save_folder = "content"
    save_path = Path(save_folder)
    print(save_path)
    if save_path.is_dir():
        # "content" is already a directory, so we can proceed
        file_path = save_path / uploaded_file.name
        # if the file already exists
        if file_path.exists():
            # remove the file from the directory so we can overwrite it
            file_path.unlink()

        with open(file_path, mode="wb") as file:
            file.write(uploaded_file.getvalue())

        if file_path.exists():
            st.success(f"File {uploaded_file.name} is successfully saved!")
        print(file_path)
    elif save_path.is_file():
        # "content" is a file, you can choose a different name or handle the situation as needed
        st.error(
            'A file named "content" already exists. Please choose a different directory name.'
        )
    else:
        # "content" doesn't exist, so we can create the directory
        save_path.mkdir(parents=True, exist_ok=True)

        file_path = save_path / uploaded_file.name

        with open(file_path, mode="wb") as file:
            file.write(uploaded_file.getvalue())

        if file_path.exists():
            st.success(f"File {uploaded_file.name} is successfully saved!")


def get_text():
    """
    This function gets the text input from the user.

    Args:
        None

    Returns:
        str: The text input from the user
    """
    input_text = st.text_input("You:", "Ask Question From Your Document?", key="input")
    return input_text


def generate_response(user_query):
    """
    This function generates a response from the user input.

    Args:
        user_query (str): The user input

    Returns:
        str: The response generated from the user input
    """
    response = chain({"question": user_query})
    return response.get("result")


if csv_file_uploaded:
    save_file_to_folder(csv_file_uploaded)
    loader = CSVLoader(file_path=os.path.join("content/", csv_file_uploaded.name))
    index_creator = VectorstoreIndexCreator()
    docsearch = index_creator.from_loaders([loader])
    chain = RetrievalQA.from_chain_type(
        llm=OpenAI(),
        chain_type="stuff",
        retriever=docsearch.vectorstore.as_retriever(),
        input_key="question",
    )
    st.title("Chat with your CSV Data")
    if "generated" not in st.session_state:
        st.session_state["generated"] = []
    if "past" not in st.session_state:
        st.session_state["past"] = []
    user_input = get_text()
    if user_input:
        output = generate_response(user_input)
        st.session_state.past.append(user_input)
        if output:
            st.session_state.generated.append(output)

    if st.session_state["generated"]:
        for i in range(len(st.session_state["generated"]) - 1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")
