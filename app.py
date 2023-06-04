import streamlit as st
import gradio as gr
from datasets import load_dataset
from PIL import Image
import re
import os
import requests

from share_btn import community_icon_html, loading_icon_html, share_js

word_list_dataset = load_dataset("stabilityai/word-list", data_files="list.txt", use_auth_token=True)
word_list = word_list_dataset["train"]["text"]

is_gpu_busy = False


def infer(prompt, negative, scale):
    global is_gpu_busy
    for filter in word_list:
        if re.search(rf"\\b{filter}\\b", prompt):
            raise gr.InterfaceError("Unsafe content found. Please try again with different prompts.")

    images = []
    url = os.getenv("JAX_BACKEND_URL")
    payload = {"prompt": prompt, "negative_prompt": negative, "guidance_scale": scale}
    images_request = requests.post(url, json=payload)
    for image in images_request.json()["images"]:
        image_b64 = f"data:image/jpeg;base64,{image}"
        images.append(image_b64)

    return images


css = """
    /* CSS styles here */
"""

examples = [
    [
        "A high tech solarpunk utopia in the Amazon rainforest",
        "low quality",
        9
    ],
    [
        "A pikachu fine dining with a view to the Eiffel Tower",
        "low quality",
        9
    ],
    [
        "A mecha robot in a favela in expressionist style",
        "low quality, 3d, photorealistic",
        9
    ],
    [
        "an insect robot preparing a delicious meal",
        "low quality, illustration",
         9
    ],
    [
        "A small cabin on top of a snowy mountain in the style of Disney, artstation",
        "low quality, ugly",
        9
    ],
]

st.set_page_config(layout="wide")
st.markdown(
    """
        <div style="text-align: center; margin: 0 auto;">
          <div style="display: inline-flex; align-items: center; gap: 0.8rem; font-size: 1.75rem;">
            <svg width="0.65em" height="0.65em" viewBox="0 0 115 115" fill="none" xmlns="http://www.w3.org/2000/svg">
              <!-- SVG content here -->
            </svg>
            <h1 style="font-weight: 900; margin-bottom: 7px;margin-top:5px">Stable Diffusion 2.1 Demo</h1>
          </div>
          <p style="margin-bottom: 10px; font-size: 94%; line-height: 23px;">
            Stable Diffusion 2.1 is the latest text-to-image model from StabilityAI. <a style="text-decoration: underline;" href="https://huggingface.co/spaces/stabilityai/stable-diffusion-1">Access Stable Diffusion 1 Space here</a><br>For faster generation and API
            access you can try
            <a href="http://beta.dreamstudio.ai/" style="text-decoration: underline;" target="_blank">DreamStudio Beta</a>.</a>
          </p>
        </div>
    """,
    unsafe_allow_html=True
)

# Create input components
prompt_text_input = st.text_input(label="Enter your prompt", max_chars=None, key=None, type='default')
negative_prompt_text_input = st.text_input.
