Abstract—Background: ChatGPT is an Artificial Intelligence that enables the revolution of many fields, which promises the path
toward personalized education. However, the AI models fall short when tackling questions not in English. Thus, we believe investigating
the reliability and robustness of such models in teaching and solving multilingual science questions is the first step toward fully
adopting AI for personalized education.
Approach: We use Korean mathematics questions as a validated dataset, which includes 586 questions. Other than testing the
accuracy of ChatGPT, we evaluate the model’s effectiveness in rating mathematics questions using eleven criteria. We also perform
topic analysis, suggesting effective use of the models.
Results: Out of 586 questions, ChatGPT achieves about 66.72% of accuracy (correctly answer n = 391/586 questions). Besides,
ChatGPT’s rating ability is substantially good and consistent with education theory and test taker’s perspectives.
___

# Project Goal

1. Develop an eco-system of applications for personalized education
    1. K12/Common Core:
        1. Mathematics
        2. Science
        3. English (Verbal)
    2. Undergraduate
        1. Computer science
        2. Information technology
_____
Current app implementation

import streamlit as st
import os
import re
import html

st.set_page_config(page_title="GAIA Mathematics", 
    page_icon="🌐", layout="wide", 
    initial_sidebar_state="expanded")


# Add logo to sidebar
st.sidebar.image("4458ccf6-e0fe-4dd0-adfb-19f302c1f271.jpeg", use_column_width=True)  # Replace "logo.png" with the path to your logo


def escape_html_content(text):
    """
    Escapes HTML special characters in the provided text to prevent rendering issues.
    """
    return html.escape(text)

def get_test_ids(root):
    return [
        folder for folder in os.listdir(root) 
        if os.path.isdir(os.path.join(root, folder))
    ]

def get_test_types(root, test_id):
    test_path = os.path.join(root, test_id)
    return [
        folder for folder in os.listdir(test_path) 
        if os.path.isdir(os.path.join(test_path, folder))
    ]

def get_md_files(root, test_id, test_type):
    test_type_path = os.path.join(root, test_id, test_type)
    return [
        file for file in os.listdir(test_type_path) 
        if file.endswith('.md')
    ]

def read_md_file(root, test_id, test_type, file_name):
    file_path = os.path.join(root, test_id, test_type, file_name)
    with open(file_path, 'r') as file:
        return file.read()

def highlight_translation_pairs(korean_text, english_text):
    """
    Highlights word translation pairs in Korean and English texts using different colors.
    """
    korean_words = korean_text.split()
    english_words = english_text.split()

    colors = ["#FFCDD2", "#F8BBD0", "#E1BEE7", "#D1C4E9", "#C5CAE9", "#BBDEFB", "#B3E5FC", "#B2EBF2", "#B2DFDB", "#C8E6C9", "#DCEDC8", "#F0F4C3"]

    def colorize(word, color):
        return f'<span style="background-color: {color}; padding: 2px 4px; border-radius: 4px;">{word}</span>'

    highlighted_korean = []
    highlighted_english = []

    for i, (k_word, e_word) in enumerate(zip(korean_words, english_words)):
        color = colors[i % len(colors)]
        highlighted_korean.append(colorize(k_word, color))
        highlighted_english.append(colorize(e_word, color))

    return " ".join(highlighted_korean), " ".join(highlighted_english)

# Streamlit App
st.title("GAIA Academy - Mathematics")

root = "mathematics"  # Root directory where the data is stored

# Dropdowns for selecting Test ID and Test Type
test_ids = get_test_ids(root)
test_id = st.sidebar.selectbox("Select Test ID", test_ids)

test_types = get_test_types(root, test_id)
test_type = st.sidebar.selectbox("Select Test Type", test_types)

# Get and display the MD files
md_files = get_md_files(root, test_id, test_type)
selected_md_file = st.sidebar.selectbox("Select MD File", md_files)

if selected_md_file:
    content = read_md_file(root, test_id, test_type, selected_md_file)
    
    # Split the content into Korean and English sections
    korean_section, english_section = content.split("## Question", 1)
    korean_problem, korean_solution = korean_section.split("### 해설", 1)
    english_problem, english_solution = english_section.split("### Solution", 1)

    # Escape HTML special characters
    escaped_korean_problem = escape_html_content(korean_problem)
    escaped_korean_solution = escape_html_content(korean_solution)
    escaped_english_problem = escape_html_content(english_problem)
    escaped_english_solution = escape_html_content(english_solution)

    # Highlight translation pairs
    highlighted_korean_problem, highlighted_english_problem = highlight_translation_pairs(
        escaped_korean_problem, escaped_english_problem
    )

    # Extract options
    korean_lines = korean_section.splitlines()
    english_lines = english_section.splitlines()

    def extract_options(lines):
        options = [line.strip() for line in lines if line.strip().startswith(tuple(str(i) + '.' for i in range(1, 10)))]
        return options

    korean_options = extract_options(korean_lines)
    english_options = extract_options(english_lines)

    # Show/Hide solution buttons
    show_korean_solution = st.sidebar.checkbox("Show Korean Solution", value=False)
    show_english_solution = st.sidebar.checkbox("Show English Solution", value=False)

    # Display content in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h2>Korean</h2>", unsafe_allow_html=True)
        st.markdown(korean_problem, unsafe_allow_html=True)
        if korean_options:
            korean_buttons_html = "".join([
                f'<button style="margin: 5px; padding: 5px 10px;">{option}</button>' for option in korean_options
            ])
            st.markdown(korean_buttons_html, unsafe_allow_html=True)
        if show_korean_solution:
            st.markdown("<h3>해설</h3>", unsafe_allow_html=True)
            st.markdown(escaped_korean_solution, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h2>English</h2>", unsafe_allow_html=True)
        st.markdown(english_problem, unsafe_allow_html=True)
        if english_options:
            english_buttons_html = "".join([
                f'<button style="margin: 5px; padding: 5px 10px;">{option}</button>' for option in english_options
            ])
            st.markdown(english_buttons_html, unsafe_allow_html=True)
        if show_english_solution:
            st.markdown("<h3>Solution</h3>", unsafe_allow_html=True)
            st.markdown(escaped_english_solution, unsafe_allow_html=True)
____

currently I have had a knowledge base in markdown files, that look like this

## 문제 1 
$\left( 8^{\frac{2}{3}} \times 9^{\frac{1}{2}} \right)$의 값은? **[2점]**

1. 12  
2. 10  
3. 8  
4. 6  
5. 4  

### 해설  
주어진 식 $\left( 8^{\frac{2}{3}} \times 9^{\frac{1}{2}} \right)$의 값을 계산해봅시다.

1. $8^{\frac{2}{3}}$은 $8 = 2^3$이므로 $8^{\frac{2}{3}} = \left(2^3\right)^{\frac{2}{3}} = 2^2 = 4$입니다.
2. $9^{\frac{1}{2}}$는 $9 = 3^2$이므로 $9^{\frac{1}{2}} = \sqrt{9} = 3$입니다.
3. 따라서, $\left( 8^{\frac{2}{3}} \times 9^{\frac{1}{2}} \right) = 4 \times 3 = 12$입니다.

정답은 **1번: 12**입니다.

## Question 1  
What is the value of $\left( 8^{\frac{2}{3}} \times 9^{\frac{1}{2}} \right)$? **[2 points]**

1. 12  
2. 10  
3. 8  
4. 6  
5. 4  

## Solution  
Let's calculate the value of the expression $\left( 8^{\frac{2}{3}} \times 9^{\frac{1}{2}} \right)$.

1. $8^{\frac{2}{3}}$: Since $8 = 2^3$, we have $8^{\frac{2}{3}} = \left(2^3\right)^{\frac{2}{3}} = 2^2 = 4$.
2. $9^{\frac{1}{2}}$: Since $9 = 3^2$, we have $9^{\frac{1}{2}} = \sqrt{9} = 3$.
3. Therefore, $\left( 8^{\frac{2}{3}} \times 9^{\frac{1}{2}} \right) = 4 \times 3 = 12$.

The correct answer is **1: 12**.%  

____

My question is, how can I apply RAG in this project whether we should use an existing one (if that's the more reasonable way) or build it ourselves because I haven't done much research on how people usually implement RAG