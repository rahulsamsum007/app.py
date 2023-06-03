from setuptools import setup, find_packages

setup(
    name='streamlit-image-captioning-app',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'streamlit',
        'torch',
        'transformers',
        'Pillow',
    ],
)
