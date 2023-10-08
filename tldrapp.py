import tkinter as tk
from tkinter import filedialog
import tldr
from tldr import summarize_text
import PyPDF2
import docx
import requests
from bs4 import BeautifulSoup
import tiktoken
import time
from youtubeapi import yt_transcript

# Define the rate limit and cooldown time in seconds
RATE_LIMIT = 3  # Number of API calls allowed per minute
COOLDOWN_TIME = 60 / RATE_LIMIT  # Cooldown time in seconds

# Initialize a timestamp for the last API call
last_api_call_time = 0

def rate_limited_summarize(chunk, tone_type, max_tokens):
    global last_api_call_time
    
    # Calculate time elapsed since the last API call
    time_since_last_call = time.time() - last_api_call_time
    
    # If less than the cooldown time has passed, wait before making the next call
    if time_since_last_call < COOLDOWN_TIME:
        time.sleep(COOLDOWN_TIME - time_since_last_call)
    
    # Make the API call
    summary = summarize_text(chunk, tone_type, max_tokens)
    
    # Update the timestamp for the last API call
    last_api_call_time = time.time()
    
    return summary


# Create the main application window
app = tk.Tk()
app.title("TL;DR")

def token_size(text):
    encoding = tiktoken.encoding_for_model(tldr.model)
    return len(encoding.encode(text))

def read_txt_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()



def read_pdf_file(file_path):
    pdf_text = ""
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_text += page.extract_text()

    return pdf_text

def read_docx_file(file_path):
    doc = docx.Document(file_path)
    doc_text = ""
    for paragraph in doc.paragraphs:
        doc_text += paragraph.text

    return doc_text




def open_file_dialog():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("PDF Files", "*.pdf"), ("DOCX Files", "*.docx")])
    if file_path:
        input_text.delete(1.0, tk.END)
        if ".pdf" in file_path:
            text = read_pdf_file(file_path)
        elif ".docx" in file_path:
            text = read_docx_file(file_path)
        else:
            text = read_txt_file(file_path)
        input_text.insert(tk.END, text)


def extract_text_from_url(url):
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if there's an error

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the text content from the parsed HTML
        # This example assumes that the article text is inside <p> tags.
        article_text = ""
        for paragraph in soup.find_all('p'):
            article_text += paragraph.get_text() + "\n"

        return article_text

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def get_url():
    try:
        url = input_text.get(1.0, tk.END).strip()
        if "youtube.com" in url:
            videoID = url.split("=")[1]
            text = yt_transcript(videoID)
        else:
            text = extract_text_from_url(url)  # Extract text from the URL
        tone_type = tone_type_entry.get()  # Get the selected tone/type
        size_input = size_entry.get()
    

    
        size = int(size_input) if size_input else 2048
    
    
        tnum = token_size(text)
        if tnum>2048:
            input_text.delete(1.0,tk.END)
            input_text.insert(tk.END,text)
            summarize_large_text()
        else:
            summary = summarize_text(text, tone_type, size)  # Summarize the extracted text
            result_text.delete(1.0, tk.END)  # Clear previous result
            result_text.insert(tk.END, summary)  # Display the summary
    except Exception as e:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Error: {str(e)}")

def get_text():
    input_data = input_text.get(1.0, tk.END)
    tone_type = tone_type_entry.get()  # Get the selected tone/type
    size_input = size_entry.get()
    
    size = int(size_input) if size_input else 2048
    
    try:
        summary = summarize_text(input_data, tone_type, size)  # Pass the tone/type as an argument
        result_text.delete(1.0, tk.END)  # Clear previous result
        result_text.insert(tk.END, summary)  # Display the summary
    except Exception as e:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Error: {str(e)}")




def summarize_large_text():
    summaries = []
    chunk_size = 2048
    input_data = input_text.get(1.0, tk.END)
    tone_type = tone_type_entry.get()  # Get the selected tone/type
    encoding = tiktoken.encoding_for_model(tldr.model)
    size_input = size_entry.get()
    encoded_input = encoding.encode(input_data)

    size = int(size_input) if size_input else 2048


    # Split the input text into chunks
    chunks = [encoded_input[i:i + chunk_size] for i in range(0, len(encoded_input), chunk_size)]

    # Summarize each chunk and append to the summaries list
    for chunk in chunks:
        chunk = encoding.decode(chunk)
        chunk_summary = rate_limited_summarize(chunk, tone_type,size)
        summaries.append(chunk_summary)

    # Combine the individual summaries into the final summary
    summary = '\n'.join(summaries)

    result_text.delete(1.0, tk.END)  # Clear previous result
    result_text.insert(tk.END, summary)


def summarize():
    input_data = input_text.get(1.0, tk.END)
    tnum = token_size(input_data)
    if "http" in input_data:
        get_url()
    else:
        if tnum>3800:
            summarize_large_text()
        else:
            get_text()


input_label = tk.Label(app, text="Enter Text, URL, or Upload File:")
input_label.pack(pady=10)

input_text = tk.Text(app, height=5, width=40)
input_text.pack()

file_button = tk.Button(app, text="Upload File", command=open_file_dialog)
file_button.pack()

tone_type_label = tk.Label(app, text="What kind of summary?")
tone_type_label.pack()

tone_type_entry = tk.Entry(app)
tone_type_entry.pack()

size_label = tk.Label(app, text="how long? leave empty for default")
size_label.pack()

size_entry = tk.Entry(app)
size_entry.pack()

summarize_button = tk.Button(app, text="Summarize", command=summarize)
summarize_button.pack(pady=10)

result_label = tk.Label(app, text="Summary:")
result_label.pack()

result_text = tk.Text(app, height=350, width=700)
result_text.pack()

# Start the main application loop
app.mainloop()

