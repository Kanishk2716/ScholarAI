import os
import json
import PyPDF2
import pandas as pd
import traceback
from dotenv import load_dotenv

from src.mcqgenerator.utils import read_file , get_table_data
from src.mcqgenerator.logger import logging

import langchain_google_genai as genai
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain , SequentialChain

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

llm = genai.ChatGoogleGenerativeAI(google_api_key=api_key , model = "gemini-1.5-pro")

template = """
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz of {number} multiple choice questions for {subject} students in {tone} tone.
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your responses like RESPONSE_JSON below and use it as a guide. \
Ensure to make {number} MCQs.
### RESPONSE_JSON
{response_json}

"""

quiz_generation_prompt = PromptTemplate(
    input_variables= ["text" , "number" , "subject" , "tone" , "response_json"],
    template = template
)

quiz_chain = LLMChain(llm = llm , prompt = quiz_generation_prompt , output_key = "quiz" , verbose = True)

template2 = """
You are an expert English grammarian and writer. Given a Multiple Choice Quiz for {subject} students, you need to evaluate the complexity of the questions and provide a complete analysis of the quiz. Use a maximum of 50 words for complexity analysis.

If the quiz does not align with the cognitive and analytical abilities of the students, update the necessary questions and adjust the tone to ensure it perfectly suits their level.

Quiz_MCQs:
{quiz}

Review and refine the quiz to ensure it aligns with the students' cognitive and analytical abilities, making necessary adjustments to question complexity and tone.
"""

quiz_evaluation_prompt = PromptTemplate(
    input_variables= ["subject" , "quiz"],
    template = template2
)

review_chain = LLMChain(llm = llm , prompt = quiz_evaluation_prompt , output_key = "review" , verbose = True)

generate_evaluate_chain = SequentialChain(
    chains=[quiz_chain, review_chain],
    input_variables=["text", "number", "subject", "tone", "response_json"],
    output_variables=["quiz", "review"],
    verbose=True
)