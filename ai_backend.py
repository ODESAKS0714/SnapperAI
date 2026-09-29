import ollama
import re
import pytesseract

from PIL import Image, ImageOps
from serpapi_beackend import search_web


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

BACKEND = "ollama"

# Vision model used for screenshot analysis
VISION_MODEL = "qwen2.5vl:3b"

# Smaller text model used for research answers
TEXT_MODEL = "qwen2.5:1.5b"


# --------------------------------------------------
# OCR
# --------------------------------------------------

def extract_text_with_ocr(image_path):

    image = Image.open(image_path)

    # Convert to grayscale
    image = image.convert("L")

    # Make text larger for OCR
    image = image.resize(
        (
            image.width * 2,
            image.height * 2
        )
    )

    # Improve contrast
    image = ImageOps.autocontrast(image)

    # OCR
    text = pytesseract.image_to_string(
        image,
        config="--oem 3 --psm 6"
    )

    return text.strip()


# --------------------------------------------------
# GENERATE RESEARCH QUERY
# --------------------------------------------------

def generate_search_query(image_path):

    ocr_text = extract_text_with_ocr(image_path)

    if not ocr_text:
        return "NO_RESEARCH_TOPIC"

    # Join OCR lines together
    text = " ".join(
        line.strip()
        for line in ocr_text.splitlines()
        if line.strip()
    )

    # Look for quoted question
    match = re.search(
        r'[“"]([^?”"]{3,100})[?”]',
        text
    )

    if match:

        query = match.group(1).strip()

        query = query.strip(
            " ,.:;"
        )

        return query

    # Look for normal question
    match = re.search(
        r'([^.!?]{3,100})\?',
        text
    )

    if match:

        query = match.group(1).strip()

        query = re.split(
            r'[,.:;]',
            query
        )[-1].strip()

        if query:
            return query

    # Use substantial OCR lines
    lines = []

    for line in ocr_text.splitlines():

        line = line.strip()

        if len(line) < 15:
            continue

        if line.lower() in [
            "articles",
            "home",
            "about",
            "contact",
            "menu"
        ]:
            continue

        lines.append(line)

    if not lines:
        return "NO_RESEARCH_TOPIC"

    query = " ".join(
        lines[:2]
    )

    words = query.split()

    if len(words) > 12:

        query = " ".join(
            words[:12]
        )

    return query


# --------------------------------------------------
# GENERATE RESEARCH ANSWER
# --------------------------------------------------

def generate_research_answer(
    image_path,
    query,
    search_results
):

    if not search_results:
        return "No web results were found."

    if search_results == "No useful web results were found.":

        return search_results

    response = ollama.chat(
        model=TEXT_MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    "You are a research assistant.\n\n"

                    "Answer the user's search query using ONLY "
                    "the web search results provided below.\n\n"

                    "Rules:\n"
                    "- Give a concise answer in 2 to 4 sentences.\n"
                    "- Do not mention the screenshot.\n"
                    "- Do not mention OCR.\n"
                    "- Do not invent information.\n"
                    "- If the results don't contain enough information, "
                    "say that clearly.\n\n"

                    f"SEARCH QUERY:\n{query}\n\n"

                    f"WEB SEARCH RESULTS:\n{search_results}\n\n"

                    "Give the answer directly."
                )
            }
        ]
    )

    return response[
        "message"
    ][
        "content"
    ].strip()


# --------------------------------------------------
# MAIN SCREENSHOT ANALYSIS
# --------------------------------------------------

def analyze_screenshot(
    image_path,
    action,
    question=""
):

    # --------------------------------------------------
    # RESEARCH
    # --------------------------------------------------

    if action == "Research":

        query = generate_search_query(
            image_path
        )

        if query == "NO_RESEARCH_TOPIC":

            return (
                "There is no useful subject "
                "to research in this screenshot."
            )

        try:

            search_results = search_web(
                query
            )

        except Exception:

            return (
                "RESEARCH ERROR\n\n"
                "Unable to perform the web search. "
                "Please check your internet connection "
                "and SerpApi setup."
            )

        if (
            search_results == "No useful web results were found."
            or
            search_results == "SerpApi API key is not configured."
        ):

            return (
                "RESEARCH ERROR\n\n"
                f"{search_results}"
            )

        answer = generate_research_answer(
            image_path,
            query,
            search_results
        )

        return (
            "RESEARCH ANSWER\n\n"
            f"{answer}\n\n\n"

            "SOURCES\n\n"
            f"{search_results}\n\n\n"

            "SEARCH QUERY\n"
            f"{query}"
        )

    # --------------------------------------------------
    # OCR
    # --------------------------------------------------

    ocr_text = extract_text_with_ocr(
        image_path
    )

    if not ocr_text:

        ocr_text = (
            "No readable text was detected "
            "by OCR."
        )

    # --------------------------------------------------
    # EXPLAIN
    # --------------------------------------------------

    elif action == "Explain":

        prompt = (
            "You are an AI screenshot assistant.\n\n"

            "Explain what is shown in the screenshot "
            "clearly and simply.\n\n"

            "Use BOTH the screenshot and the OCR text "
            "below to understand the content.\n\n"

            "If the screenshot contains code, explain "
            "what the code is doing.\n"

            "If it contains an error message, explain "
            "what the error means.\n"

            "If it contains a webpage, explain the "
            "important information shown.\n\n"

            "Do not invent information that is not "
            "visible in the screenshot.\n\n"

            "OCR TEXT:\n"
            f"{ocr_text}\n\n"

            "Give a clear and useful explanation."
        )

    # --------------------------------------------------
    # SUMMARIZE
    # --------------------------------------------------

    elif action == "Summarize":

        prompt = (
            "You are an AI screenshot assistant.\n\n"

            "Summarize the important information "
            "visible in this screenshot.\n\n"

            "Use BOTH the screenshot and the OCR text "
            "below.\n\n"

            "Focus only on information that is actually "
            "visible.\n\n"

            "If the screenshot contains code, summarize "
            "what the code does.\n"

            "If it contains an article or webpage, "
            "summarize its main points.\n"

            "If it contains an error message, summarize "
            "the problem.\n\n"

            "Do not invent information.\n\n"

            "OCR TEXT:\n"
            f"{ocr_text}\n\n"

            "Give a concise but useful summary."
        )

    # --------------------------------------------------
    # FIND ERROR
    # --------------------------------------------------

    elif action == "Find Error":

        prompt = (
            "You are an expert programming debugger.\n\n"

            "Carefully inspect the screenshot and identify "
            "any actual errors or problems.\n\n"

            "If the screenshot contains code, check for:\n"
            "1. Syntax errors\n"
            "2. Compilation errors\n"
            "3. Runtime errors\n"
            "4. Incorrect variable names\n"
            "5. Missing brackets, semicolons, or symbols\n"
            "6. Incorrect logic\n"
            "7. Warnings or obvious mistakes\n\n"

            "Use the OCR text below as additional information, "
            "but verify it against the screenshot because OCR "
            "may contain mistakes.\n\n"

            "OCR TEXT:\n"
            f"{ocr_text}\n\n"

            "IMPORTANT:\n"
            "- Do not invent errors.\n"
            "- If an error exists, explain exactly what is wrong.\n"
            "- Mention the relevant line or code when possible.\n"
            "- If there is no obvious error, say exactly:\n"
            "'No obvious error found in the screenshot.'\n\n"

            "Give a useful debugging answer."
        )

    # --------------------------------------------------
    # EXTRACT
    # --------------------------------------------------

    elif action == "Extract":

        prompt = (
            "You are an OCR and information extraction assistant.\n\n"

            "Extract the important text and information "
            "visible in this screenshot.\n\n"

            "Use BOTH the screenshot and the OCR text below.\n\n"

            "Preserve the original wording as much as possible.\n"

            "If the screenshot contains code, preserve "
            "the code structure and symbols.\n"

            "If there are headings, lists, numbers, URLs, "
            "or important values, include them.\n\n"

            "OCR TEXT:\n"
            f"{ocr_text}\n\n"

            "Correct obvious OCR mistakes by checking "
            "the screenshot.\n\n"

            "Return the extracted information clearly."
        )

    # --------------------------------------------------
    # CUSTOM QUESTION
    # --------------------------------------------------

    elif question:

        prompt = (
            "You are an AI screenshot assistant.\n\n"

            "Answer the user's question about the screenshot.\n\n"

            "Use BOTH the screenshot and the OCR text below "
            "to answer accurately.\n\n"

            "Do not invent information that cannot be "
            "supported by the screenshot.\n\n"

            "OCR TEXT:\n"
            f"{ocr_text}\n\n"

            "USER QUESTION:\n"
            f"{question}\n\n"

            "Answer the question directly and clearly."
        )

    # --------------------------------------------------
    # DEFAULT
    # --------------------------------------------------

    else:

        prompt = (
            "Describe and analyze this screenshot clearly.\n\n"

            "Use both the screenshot and the OCR text.\n\n"

            "OCR TEXT:\n"
            f"{ocr_text}"
        )

    # --------------------------------------------------
    # OLLAMA
    # --------------------------------------------------

    if BACKEND == "ollama":

        response = ollama.chat(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [
                        image_path
                    ]
                }
            ]
        )

        return response[
            "message"
        ][
            "content"
        ].strip()

    # --------------------------------------------------
    # SNAPDRAGON
    # --------------------------------------------------

    

    else:

        return (
            "ERROR\n\n"
            f"Unknown backend: {BACKEND}"
        )