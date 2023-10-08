import openai
import config
import tiktoken
openai.api_key=config.OPENAI_API_KEY
model = "text-davinci-003"

def token_size(text):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def summarize_text(text_to_summarize,tone="normal",size="half of input"):
    if len(text_to_summarize)<5:
        prompt = "The user forgot to give you an input or you could not get this input, ask for another input"
    else:
        if tone or size:
            prompt = f"{text_to_summarize}"+ f"TL;DR. return a detailed summary.{tone} in {size} words "
        else:
            prompt = f"{text_to_summarize}"+"TL;DR"
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        api_key=config.OPENAI_API_KEY,
        temperature=0.7,
        max_tokens = 4096-token_size(prompt)
    )
    summary = response.choices[0].text
    return summary



# print(summarize_text("""Voice assistants have become increasingly popular in recent years, with the rise of devices like Amazon's Alexa and Google Assistant. This project aims to develop a voice assistant application that can perform a wide range of tasks using natural language processing techniques. The voice assistant is designed to be intuitive and user-friendly, allowing users to interact with it in a conversational manner. The application is built using Python and utilizes a number of open-source libraries, including speech recognition, text-to-speech, and natural language processing.
# The voice assistant is capable of performing a range of tasks, including getting reminders, answering questions, and providing weather updates. The application allows users to view their reminders and settings. One of the key features of the application is its ability to understand and respond to natural language input, allowing users to interact with it in a more human-like way. The project represents a significant step forward in the development of voice assistant technology and has the potential to revolutionize the way we interact with our devices. With the increasing importance of natural language processing in the field of artificial intelligence, this project is well-positioned to make a valuable contribution to the field and to the wider community.
# """))




