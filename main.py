# coding=utf-8
# Copyright 2018-2023 EvaDB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from collections import defaultdict
import os
import shutil
from typing import Dict

import pandas as pd

import evadb

DEFAULT_FILE_PATH = "data/user_complaints.txt"
DEFAULT_QUERY = (
    "The keyboard on my laptop is typing the wrong letters and it's driving me crazy!"
)
DEFAULT_STRUCTURE_FORMAT = [
    [
        "Issue Category",
        "What category the issue belongs to",
        "One of (hardware, software)",
    ],
    [
        "Raw Issue String",
        "Raw String containing the exact input given by the user",
        "string",
    ],
    ["Issue Component", "Component that is causing the issue", "string"],
]


def receive_user_input() -> Dict:
    """Receives user input.

    Returns:
        user_input (dict): global configurations
    """
    print(
        "🔮 Welcome to EvaDB-STRUCTURE-GPT! This app lets you provide an unstructured text file and it will generate a structured dataframe for you using that file"
    )

    user_input = dict()
    unstructured_query = str(
        input("Enter the user complaint query you want to structure: ")
    )

    if unstructured_query == "":
        unstructured_query = DEFAULT_QUERY
    user_input["unstructured_query"] = unstructured_query

    # Add input for prompt, right now not needed as such

    # get OpenAI key if needed
    try:
        api_key = os.environ["OPENAI_KEY"]
    except KeyError:
        api_key = str(input("🔑 Enter your OpenAI key: "))
        os.environ["OPENAI_KEY"] = api_key

    return user_input


def create_prompt(extra_prompt_line, user_input):
    # TODO :- Enable storing historical context

    base_prompt = """
        You are given a user query extracted from a customer support chatbot. Your task is to extract the following fields from the text and return the result in json format.

        "Issue Category, What category the issue belongs to, Issue category HAS TO BE one of (hardware, software)"
        "Raw Issue String, Raw String containing the exact input given by the user, string"
        "Issue Component, Component that is causing the issue, string"
        \n

        The query is as follows: 
    """

    if extra_prompt_line == "":
        return base_prompt
    else:
        return base_prompt + extra_prompt_line


def generate_response(cursor, prompt):
    """Generates question response with llm.

    Args:
        cursor (EVADBCursor): evadb api cursor.
        question (str): question to ask to llm.

    Returns
        str: response from llm.
    """

    response = cursor.table("unstructuredtable").select(f"ChatGPT('{prompt}', text)").df()["chatgpt.response"][0]
    print(response)
    return response

    #return cursor.table("unstructuredtable").select(f"ChatGPT({prompt}, text)")


def cleanup():
    """Removes any temporary file / directory created by EvaDB."""
    if os.path.exists("evadb_data"):
        shutil.rmtree("evadb_data")


if __name__ == "__main__":
    # receive input from user
    user_input = receive_user_input()

    try:
        # establish evadb api cursor
        cursor = evadb.connect().cursor()
        cursor.drop_table("unstructuredtable", if_exists=True).execute()
        cursor.query(
            """CREATE TABLE IF NOT EXISTS unstructuredtable (text TEXT(150));"""
        ).execute()
        # TODO : Add back when lifting stuff from a file
        cursor.query(
            """INSERT INTO unstructuredtable (text) VALUES ("{}");""".format(
                user_input["unstructured_query"]
            )
        ).execute()

        # Add something about getting a file and read it
        print("===========================================")
        ready = True
        while ready:
            extra_prompt_line = str(
                input(
                    "If not satisfied by the query add more context. This will be appended to the end of the query (enter 'exit' to exit): "
                )
            )
            prompt = create_prompt(extra_prompt_line, user_input)
            if extra_prompt_line.lower() == "exit":
                ready = False
            else:
                # Generate response with chatgpt udf
                print("⏳ Generating response (may take a while)...")
                response = generate_response(cursor, prompt)
                print("+--------------------------------------------------+")
                print("✅ Answer:")
                print(response)
                print("+--------------------------------------------------+")

        cleanup()
        print("✅ Session ended.")
        print("===========================================")
    except Exception as e:
        cleanup()
        print("❗️ Session ended with an error.")
        print(e)
        print("===========================================")
