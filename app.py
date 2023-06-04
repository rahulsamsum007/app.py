import streamlit as st
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest

def summarizer(rawdocs):
    stopwords = list(STOP_WORDS)

    nlp = spacy.load('en_core_web_sm')
    doc = nlp(rawdocs)
    tokens = [token.text for token in doc]

    word_freq = {}

    for word in doc:
        if word.text.lower() not in stopwords and word.text.lower() not in punctuation:
            if word.text.lower() not in word_freq:
                word_freq[word.text.lower()] = 1
            else:
                word_freq[word.text.lower()] += 1

    max_freq = max(word_freq.values())

    for word in word_freq.keys():
        word_freq[word] += word_freq[word] / max_freq

    sent_tokens = [sent for sent in doc.sents]

    sent_scores = {}

    for sent in sent_tokens:
        for word in sent:
            if word.text.lower() in word_freq.keys():
                if sent not in sent_scores.keys():
                    sent_scores[sent] = word_freq[word.text.lower()]
                else:
                    sent_scores[sent] += word_freq[word.text.lower()]

    select_len = int(len(sent_tokens) * 0.3)

    summary = nlargest(select_len, sent_scores, key=sent_scores.get)

    final_summary = [word.text for word in summary]
    summary = ' '.join(final_summary)

    return summary, doc, len(rawdocs.split(' ')), len(summary.split(' '))


def main():
    st.title("Text Summarizer")

    text = st.text_area("Enter text")

    if st.button("Summarize"):
        summary, doc, original_len, summary_len = summarizer(text)

        st.subheader("Original Text")
        st.write(text)

        st.subheader("Summary")
        st.write(summary)

        st.subheader("Length of Original Text")
        st.write(original_len)

        st.subheader("Length of Summary")
        st.write(summary_len)


if __name__ == "__main__":
    main()
