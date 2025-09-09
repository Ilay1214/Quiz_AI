import os
import PyPDF2
import docx

def extract_text_from_file(filepath: str) -> str:
    """
    Extracts text content from a given file path.
    Supports PDF, DOCX, and TXT files.
    """
    _, file_extension = os.path.splitext(filepath)
    file_extension = file_extension.lower()

    if file_extension == '.pdf':
        return _extract_text_from_pdf(filepath)
    elif file_extension == '.docx':
        return _extract_text_from_docx(filepath)
    elif file_extension == '.txt':
        return _extract_text_from_txt(filepath)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def _extract_text_from_pdf(filepath: str) -> str:
    text = ""
    with open(filepath, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text

def _extract_text_from_docx(filepath: str) -> str:
    doc = docx.Document(filepath)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def _extract_text_from_txt(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()
