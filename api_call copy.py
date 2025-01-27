import os
import re
import json
import base64
from dotenv import load_dotenv

# IMPORTANT: This import is different from `import openai`.
# This is the custom import as per your request.
from openai import OpenAI


class MarkdownQuestion:
    """
    A container for storing the path to a Markdown file, 
    the extracted Korean question text, and the image path (if any).
    """
    def __init__(self, md_file_path: str):
        self.md_file_path = md_file_path
        self.korean_question = ""
        self.image_path = None


class MarkdownQuestionProcessor:
    """
    A class to handle parsing .md files for Korean questions,
    encoding images, sending API requests, and saving the responses.
    """

    def __init__(self, base_dir: str, key: str):
        """
        :param base_dir: Directory to search for .md files.
        :param key: API key for custom OpenAI client.
        """
        self.base_dir = base_dir
        self.questions = []  
        # Instantiate the custom OpenAI client with your key
        self.client = OpenAI(api_key=key)

    def discover_markdown_files(self) -> None:
        """
        Walks through the base directory, finds .md files,
        and creates MarkdownQuestion objects for them.
        """
        for root, dirs, files in os.walk(self.base_dir):
            for filename in files:
                if filename.endswith(".md"):
                    md_file_path = os.path.join(root, filename)
                    self.questions.append(MarkdownQuestion(md_file_path))

    def parse_markdown_korean(self, question_obj: MarkdownQuestion) -> None:
        """
        Reads a markdown file and extracts:
        - The Korean question text (between '## 문제' and '## 해설'/'## Question')
        - The path to the image (if present).
        Updates question_obj fields in-place.
        """
        lines = []
        record = False

        with open(question_obj.md_file_path, "r", encoding="utf-8") as f:
            for line in f:
                line_strip = line.strip()

                if not record and "Question" in line_strip:
                    record = True
                if record and "Solution" in line_strip:
                    break

                if record:
                    lines.append(line_strip)
                    # Check for inline image link
                    match = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', line_strip)
                    if match:
                        rel_path = match.group(2)
                        abs_path = os.path.normpath(
                            os.path.join(os.path.dirname(question_obj.md_file_path), rel_path)
                        )
                        question_obj.image_path = abs_path

        question_obj.korean_question = "\n".join(lines)


    def call_api(self, question_text: str) -> dict:
        """
        Sends the given question (in Korean) and optional encoded image 
        to the custom OpenAI client for a math response.
        
        Key changes for o1 usage:
        - Use a developer message (instead of system).
        - Keep the prompt simple; no chain-of-thought instructions.
        - Omit unsupported parameters like temperature, top_p, etc. 
        """
        # Developer message: "Formatting re-enabled" if you DO want any markdown 
        # in the answer. Keep instructions short and direct.
        developer_message_content = """
        Formatting re-enabled
        You are a math expert. Please provide a detailed solution in JSON 
        using the required format, and place the final answer in \\(\\boxed{}\\). 
        """.strip()

        # The user message is simply the question text
        # user_message_content = question_text
        user_message_content = '''
        Suppose that Y1, Y2, ..., Y10
iid
âˆ¼ N (2, 9) with the average Â¯Y1 and variance S2
1 , and
Y1, Y2, ..., Y15
iid
âˆ¼ N (1, 4) with the average Â¯Y2 and variance S2
2 . If the samples are independent,
find the followings stating reasons and graphs P
 S2
1
S2
2
< 1'''

        # Create the completion request using the o1 model
        response = self.client.chat.completions.create(
            model="o1-preview",  # or "o1-preview", "o1-2024-12-17", whichever is correct for your environment
            messages=[
                {
                    "role": "user",
                    "content": developer_message_content +  user_message_content
                }],
            max_completion_tokens=10000
            
            # Note: Omit unsupported parameters for o1 (like temperature, top_p, etc.)
        )

        return response

    def process_files(self) -> None:
        """
        Main routine that:
        1) Finds .md files
        2) Parses them for Korean questions
        3) (Optionally) encodes images
        4) Makes the "o1" call for a structured math response
        5) Feeds the JSON content to "gpt-4o-mini" for validation
        6) Saves combined output (including usage info) to .json
        """
        self.discover_markdown_files()

        for question_obj in self.questions:
            print(f"Processing: {question_obj.md_file_path}")

            # Extract question text
            self.parse_markdown_korean(question_obj)
            if not question_obj.korean_question.strip():
                print("No Korean question found. Skipping...")
                continue

            # Encode image if you want to pass it (optional)

            # 1) FIRST CALL: "o1" for the math response
            o1_response_obj = self.call_api(
                question_text=question_obj.korean_question,
            )
            
            response_dict = o1_response_obj.to_dict() if hasattr(o1_response_obj, "to_dict") else dict(o1_response_obj)

            # Save response as JSON
            json_output_path = os.path.splitext(question_obj.md_file_path)[0] + "-o1-MA.json"
            with open(json_output_path, "w", encoding="utf-8") as output_file:
                json.dump(response_dict, output_file, ensure_ascii=False, indent=2)

            print(f"Saved o1 response to {json_output_path}")
            
def main():
    load_dotenv()
    # openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_api_key = "sk"
    print("Using key:", openai_api_key)
    base_directory = "mathematics-retry-o1/23-11-20/A-test" #CHCHAY

    processor = MarkdownQuestionProcessor(base_directory, openai_api_key)
    processor.process_files()
    
        # Parent directory (contains 13-11-08, 14-11-15, etc.)
    # base_parent_dir = "mathematics-retry-o1"

    # # Loop through every item in 'mathematics-retry-o1'
    # for item in os.listdir(base_parent_dir):
    #     subpath = os.path.join(base_parent_dir, item)

    #     # Only process subdirectories (skip files) and ignore "13-11-08"
    #     if os.path.isdir(subpath) and item != "13-11-08" and item != "19-11-15":
    #         try:
    #             print(f"Now processing subfolder: {subpath}")
    #             processor = MarkdownQuestionProcessor(subpath, openai_api_key)
    #             processor.process_files()
    #         except Exception as e:
    #             # append error to a file log
    #             with open("error_log.txt", "a") as f:
    #                 f.write(f"Error processing {subpath}: {str(e)}\n")

if __name__ == "__main__":
    main()
