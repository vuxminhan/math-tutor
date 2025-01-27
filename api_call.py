import os
import re
import json
import base64
from dotenv import load_dotenv

# IMPORTANT: This import is different from openai import openai.
# This is the custom import as per your request.
from openai import OpenAI


class MarkdownQuestion:
    """
    A container for storing the path to a Markdown file, 
    the extracted Korean question text, and the image path (if any).
    """

    def __init__(self, md_file_path: str):
        """
        Initialize with a path to a .md file.

        :param md_file_path: Path to the .md file.
        """
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
        """
        self.base_dir = base_dir
        self.questions = []  # Will hold a list of MarkdownQuestion objects
        # Instantiate the custom OpenAI client
        self.client = OpenAI(api_key="sk")

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

                # Start capturing once we see a line containing "문제"
                if not record and "문제" in line_strip:
                    record = True
                
                # Stop capturing if a line contains "정답"
                if record and "정답" in line_strip:
                    break
                
                # if not record and "Question" in line_strip:
                #     record = True
                
                # # Stop capturing if a line contains "정답"
                # if record and "Solution" in line_strip:
                #     break

                if record:
                    lines.append(line_strip)
                    # Check if there's an inline image link in the line
                    match = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', line_strip)
                    if match:
                        rel_path = match.group(2)  # e.g. ../Images/A_11.png
                        # Convert relative path to absolute
                        abs_path = os.path.normpath(
                            os.path.join(os.path.dirname(question_obj.md_file_path), rel_path)
                        )
                        question_obj.image_path = abs_path

        question_obj.korean_question = "\n".join(lines)

    def encode_image(self, question_obj: MarkdownQuestion) -> str:
        """
        Encodes the image (if it exists) in Base64.

        :param question_obj: A MarkdownQuestion with an image_path.
        :return: The Base64-encoded string or None.
        """
        if question_obj.image_path and os.path.exists(question_obj.image_path):
            print(f"Encoding image: {question_obj.image_path}")
            with open(question_obj.image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode("utf-8")
        return None

    def call_api(self, question_text: str, encoded_image: str = None) -> dict:
        """
        Sends the given question (in Korean) and optional encoded image 
        to the custom OpenAI client, exactly as per your snippet. 
        Returns the parsed JSON from the response.

        :param question_text: The extracted Korean question text.
        :param encoded_image: Base64-encoded image string (if any).
        :return: Parsed JSON (Python dict) from the assistant's response.
        """
        # Compose the system message content
        system_message_content = [
            {
                "type": "text",
                "text": (
                    # "You are a math expert. You will be given math problem that might contain an image. "
                    # "Follow the instructions carefully.\n\n"
                    # "Please reason step by step, and put your final answer within \\boxed{}. "
                    # "Each step is placed on a new line, using the following format:\n"
                    # "Step X [Mathematical theorem/basis used]: Detailed solution steps.\n"
                    # "If multiple choice question, return Answer: \\(\\MC: boxed{choice_number}\\), else return Answer: \\(\\boxed{answer}\\).\n\n"
                    # "If there is an image containing image demonstrations. Parse it for the the extra information.\n"
                    # "Provide the solution in both Korean and English. The Korean solution should start with [KR], "
                    # "and the English solution should start with [EN].\n"
                    # "Use the following example as the template.\n\n"
                    # "Input:\n## 문제 4\n"
                    # "그래프와 그 그래프의 각 꼭짓점 사이의 연결 관계를 나타내는 행렬이 다음과 같을 때, $a+b+c+d+e$의 값은? **[3점]**\n\n"
                    # "![A_4](../Images/A_4.png)\n\n"
                    # "1. 5  \n2. 4  \n3. 3  \n4. 2  \n5. 1\n\n"
                    # "Output:\n[KR]  \nStep 1 [인접 행렬의 대각 원소 성질 사용]:  \n"
                    # "- 단순 그래프의 인접 행렬에서는 자기 자신과의 연결(대각 원소)이 0이므로, "
                    # "행렬에서 \\(c\\)가 위치한 대각 원소는 0이 된다. 따라서 \\(c = 0\\).  \n\n"
                    # "Step 2 [그래프 도식 판독]:  \n"
                    # "- 그림에서 \\(A\\)와 \\(E\\)를 직접 잇는 간선이 보이지 않으므로 \\(a = 0\\).  \n"
                    # "- \\(B\\)와 \\(D\\)를 잇는 대각선이 존재하므로 \\(b = 1\\).  \n"
                    # "- 그래프가 무방향이므로 \\(b = 1\\)이면 \\(d = 1\\) 역시 성립한다.  \n"
                    # "- \\(E\\)와 \\(A\\)를 잇는 간선이 보이지 않으므로 \\(e = 0\\).  \n\n"
                    # "Step 3 [값의 합 계산]:  \n\\[\n"
                    # "a + b + c + d + e \\;=\\; 0 + 1 + 0 + 1 + 0 \\;=\\; 2.\n\\]\n\n"
                    # "Answer: \\(\\MC: boxed{4}\\)  \n\n"
                    # "[EN]  \n"
                    # "Step 1 [Using the property of diagonal entries in an adjacency matrix]:  \n"
                    # "- In a simple graph, each diagonal entry (which indicates self-connections) must be 0. "
                    # "Hence, the diagonal entry \\(c\\) is 0.  \n\n"
                    # "Step 2 [Reading the given graph]:  \n"
                    # "- Since there is no direct edge between \\(A\\) and \\(E\\) in the diagram, \\(a = 0\\).  \n"
                    # "- There is a diagonal edge between \\(B\\) and \\(D\\), so \\(b = 1\\).  \n"
                    # "- Because this is an undirected graph, \\(b = 1\\) implies \\(d = 1\\).  \n"
                    # "- There is no direct edge between \\(E\\) and \\(A\\) in the diagram, so \\(e = 0\\).  \n\n"
                    # "Step 3 [Summation]:  \n\\[\n"
                    # "a + b + c + d + e \\;=\\; 0 + 1 + 0 + 1 + 0 \\;=\\; 2.\n\\]\n\n"
                    # "Answer: \\(\\MC: boxed{4}\\)  \n"
                    
                    # "You are a math expert. You will be given math problem that might contain an image. "
                    # "Follow the instructions carefully.\n\n"
                    # "Please reason step by step, and put your final answer within \\boxed{}. "
                    # "Each step is placed on a new line, using the following format:\n"
                    # "Step X [Mathematical theorem/basis used]: Detailed solution steps.\n"
                    # "If multiple choice question, return Answer: \\(\\MC: boxed{choice_number}\\), else return Answer: \\(\\boxed{answer}\\).\n\n"
                    # "If there is an image containing image demonstrations. Parse it for the the extra information.\n"
                    # "Use the following example as the template.\n\n"
                    # "Input:\n"
                    # "Given the following matrix that represents the connection relationship between the vertices of the graph, what is the value of $a+b+c+d+e$? **[3 points]**"
                    # "![A_4](../Images/A_4.png)\n\n"
                    # "1. 5  \n2. 4  \n3. 3  \n4. 2  \n5. 1\n\n"
                    # "Output:\n"   
                    # "Step 1 [Using the property of diagonal entries in an adjacency matrix]:  \n"
                    # "- In a simple graph, each diagonal entry (which indicates self-connections) must be 0. "
                    # "Hence, the diagonal entry \\(c\\) is 0.  \n\n"
                    # "Step 2 [Reading the given graph]:  \n"
                    # "- Since there is no direct edge between \\(A\\) and \\(E\\) in the diagram, \\(a = 0\\).  \n"
                    # "- There is a diagonal edge between \\(B\\) and \\(D\\), so \\(b = 1\\).  \n"
                    # "- Because this is an undirected graph, \\(b = 1\\) implies \\(d = 1\\).  \n"
                    # "- There is no direct edge between \\(E\\) and \\(A\\) in the diagram, so \\(e = 0\\).  \n\n"
                    # "Step 3 [Summation]:  \n\\[\n"
                    # "a + b + c + d + e \\;=\\; 0 + 1 + 0 + 1 + 0 \\;=\\; 2.\n\\]\n\n"
                    # "Answer: \\(\\MC: boxed{4}\\)  \n"
                    
                    
                    "You are a math expert. You will be given math problem that might contain an image. "
                    "Follow the instructions carefully.\n\n"
                    "Please reason step by step, and put your final answer within \\boxed{}. "
                    "Each step is placed on a new line, using the following format:\n"
                    "Step X [Mathematical theorem/basis used]: Detailed solution steps.\n"
                    "If multiple choice question, return Answer: \\(\\MC: boxed{choice_number}\\), else return Answer: \\(\\boxed{answer}\\).\n\n"
                    "If there is an image containing image demonstrations. Parse it for the the extra information.\n"
                    "Use the following example as the template.\n\n"
                    "Input:\n"
                    "Given the following matrix that represents the connection relationship between the vertices of the graph, what is the value of $a+b+c+d+e$? **[3 points]**"
                    "![A_4](../Images/A_4.png)\n\n"
                    "1. 5  \n2. 4  \n3. 3  \n4. 2  \n5. 1\n\n"
                    "Output:\n"   
                    "Step 1 [Using the property of diagonal entries in an adjacency matrix]:  \n"
                    "- In a simple graph, each diagonal entry (which indicates self-connections) must be 0. "
                    "Hence, the diagonal entry \\(c\\) is 0.  \n\n"
                    "Step 2 [Reading the given graph]:  \n"
                    "- Since there is no direct edge between \\(A\\) and \\(E\\) in the diagram, \\(a = 0\\).  \n"
                    "- There is a diagonal edge between \\(B\\) and \\(D\\), so \\(b = 1\\).  \n"
                    "- Because this is an undirected graph, \\(b = 1\\) implies \\(d = 1\\).  \n"
                    "- There is no direct edge between \\(E\\) and \\(A\\) in the diagram, so \\(e = 0\\).  \n\n"
                    "Step 3 [Summation]:  \n\\[\n"
                    "a + b + c + d + e \\;=\\; 0 + 1 + 0 + 1 + 0 \\;=\\; 2.\n\\]\n\n"
                    "Answer: \\(\\MC: boxed{4}\\)  \n"
                )
            }
        ]

        # Build the user content
        user_message_content = [
            {
                "type": "text",
                "text": question_text
            }
        ]

        if encoded_image:
            user_message_content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encoded_image}"
                    }
                }
            )

        # Use the custom client as per your snippet
        response = self.client.chat.completions.create(
            model="o1-preview",
            messages=[
                {
                    "role": "system",
                    "content": system_message_content
                },
                {
                    "role": "user",
                    "content": user_message_content
                }
                    ]
            ,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "math_response",
                    "schema": {
                        "type": "object",
                        "required": [
                            "steps",
                            "final_answer"
                        ],
                        "properties": {
                            "steps": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["explanation", "output"],
                                    "properties": {
                                        "output": {
                                            "type": "string"
                                        },
                                        "explanation": {
                                            "type": "string"
                                        }
                                    },
                                    "additionalProperties": False
                                }
                            },
                            "final_answer": {
                                "type": "string"
                            }
                        },
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            temperature=0.1,
            max_completion_tokens=10000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # The raw response from the server is typically in response.body or response.choices
        # depending on how the custom library is implemented. We'll assume there's a .body:

        # If your library provides a different property name, adjust accordingly.
        # For demonstration, assume `response.body` is a JSON string we can parse.
        # response_json = json.loads(response)
        return response

    def process_files(self) -> None:
        """
        Main routine that:
        1) Finds .md files
        2) Parses them for Korean questions
        3) Encodes any linked image
        4) Sends question + image to the API
        5) Saves response to a .json file
        """
        # 1) Gather .md files
        self.discover_markdown_files()

        for question_obj in self.questions:
            print(f"Processing: {question_obj.md_file_path}")

            # 2) Parse the markdown file
            self.parse_markdown_korean(question_obj)

            # If there's no Korean question text, skip
            if not question_obj.korean_question.strip():
                print("No Korean question found. Skipping...")
                continue

            # 3) Encode image, if any
            encoded_img = self.encode_image(question_obj)

            # 4) Call the API
            response_obj = self.call_api(question_obj.korean_question, encoded_img)

            # 5) Save response to .json
            json_output_path = os.path.splitext(question_obj.md_file_path)[0] + ".json"
            with open(json_output_path, "w", encoding="utf-8") as output_file:
                # Example: If 'response_obj' is already a dict-like object:
                json.dump(response_obj.to_dict(), output_file, ensure_ascii=False, indent=2)

            print(f"Saved raw response to {json_output_path}")



def main():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    print(openai_api_key)
    base_directory = "mathematics-retry-o1/last"

    # Create the processor and run
    processor = MarkdownQuestionProcessor(base_directory, openai_api_key)
    processor.process_files()
    # Parent directory (contains 13-11-08, 14-11-15, etc.)
    # base_parent_dir = "mathematics-retry-o1"

    # # Loop through every item in 'mathematics-retry-o1'
    # for item in os.listdir(base_parent_dir):
    #     subpath = os.path.join(base_parent_dir, item)

    #     # Only process subdirectories (skip files) and ignore "13-11-08"
    #     if os.path.isdir(subpath):
    #         print(f"Now processing subfolder: {subpath}")
    #         processor = MarkdownQuestionProcessor(subpath)
    #         processor.process_files()

if __name__ == "__main__":
    main()
