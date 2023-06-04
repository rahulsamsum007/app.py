import streamlit as st
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch

model_name = "google/pegasus-xsum"
tokenizer = PegasusTokenizer.from_pretrained(model_name)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = PegasusForConditionalGeneration.from_pretrained(model_name).to(device)

st.title("Text Summarization")

inputtext = st.text_area("Enter the input text:")

if st.button("Summarize"):
    input_text = "summarize: " + inputtext

    tokenized_text = tokenizer.encode(input_text, return_tensors='pt', max_length=512).to(device)
    summary_ = model.generate(tokenized_text, min_length=30, max_length=300)
    summary = tokenizer.decode(summary_[0], skip_special_tokens=True)

    st.subheader("Summary:")
    st.write(summary)
