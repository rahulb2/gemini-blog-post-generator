import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    # safety_settings = Adjust safety settings
    # See https://ai.google.dev/gemini-api/docs/safety-settings
    system_instruction="Act as an experienced blogger who knows about all the topics in this world. You will be receiving a blog post topic as an input and you have to write a crisp and humanly toned blog post. Do not make up fake stuff and try to be very factual and quote stats related to that topic if possible to make the end result accurate. Keep the word count at around 150 words. Do not cross this word limit. "
)



st.header('JRP Blog Post Generator')
st.write("Enter either a topic as a text or upload an image and then wait for the JRP AI Magic")

if "chat" not in st.session_state:
    st.session_state.chat = []
    st.session_state.inputType = ""

class Message:
    def __init__(self, message, type):
        self.message = message
        self.type = type

def process_gemini_response(prompt):
    user_message = Message("User : "+ prompt, type = 'text')
    st.session_state.chat.append(user_message)
    # Gemini Integration here
    chat_session = model.start_chat()
    response = chat_session.send_message(prompt)
    gemini_message = Message("Gemini : " + response.text, type = 'text')
    st.session_state.chat.append(gemini_message)
    show_messages()
    return


def process_image_gemini_response(image):

    if image is not None:
        image_message = Image.open(image)
        i_message = Message(image, type = 'image')
        st.session_state.chat.append(i_message)
        response = model.generate_content([image_message])
        reply = response.text
        gemini_reply = Message(reply, type = 'text')
        st.session_state.chat.append(gemini_reply)
        show_messages()
        return



def show_messages():

    for i in range(len(st.session_state.chat)):
        if i%2 == 0:
            with st.chat_message("user"):
                if st.session_state.chat[i].type == "text":
                    st.write(st.session_state.chat[i].message)
                elif st.session_state.chat[i].type == "image":
                    st.image(st.session_state.chat[i].message, caption="Uploaded Image", use_column_width=True)
        else:
            with st.chat_message("assistant"):
                st.write(st.session_state.chat[i].message)

    return


def input_type_text():
    st.session_state.inputType = 'text'


def input_type_image():
    st.session_state.inputType = 'image'



prompt = st.chat_input("Enter any topic", on_submit=input_type_text)
uploaded_image = st.file_uploader("Choose an image for our JRP AI to write a blog post on.", type = ["jpg", "jpeg", "png"], accept_multiple_files =False, on_change=input_type_image)


if st.session_state.inputType == "text":
    process_gemini_response(prompt)
    prompt = None
elif st.session_state.inputType == "image" and uploaded_image is not None:
    process_image_gemini_response(uploaded_image)
    uploaded_image
