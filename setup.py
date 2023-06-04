import setuptools

setuptools.setup(
    name="summarizer_app",
    version="1.0",
    author="Your Name",
    author_email="your_email@example.com",
    description="A text summarization app using Streamlit",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "streamlit",
        "spacy",
        "en_core_web_sm"
    ],
    python_requires=">=3.6",
)
