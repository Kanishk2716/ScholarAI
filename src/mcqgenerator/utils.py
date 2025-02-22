import os 
import json
import PyPDF2
import traceback

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error reading pdf file: {e}")
    
    elif file.name.endswith("txt"):
        return file.read().decode("utf-8")
    
    else:
        raise Exception("Invalid file format. Only .txt and .pdf files are supported")
    
def get_table_data(quiz_str):
    try:
        # convert the quiz from a str to dict
        quiz_dict = json.loads(quiz_str)
        quiz_table_data = []

        #iterate over the quiz dictionary and extract the required information
        
        for key, value in quiz_dict.items():
            mcq = value["mcq"]
            options = " || ".join(
                [
                    f"{option} -> {option_value}" for option, option_value in value["options"].items()
                ]
            )

            correct_value = value["correct"]
            quiz_table_data.append({"MCQ": mcq , "Choices:": options, "Correct": correct_value})

        return quiz_table_data
    
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False