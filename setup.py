from setuptools import setup, find_packages

setup(
    name="aicrewdev",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "crewai>=0.1.0",
        "langchain-openai>=0.0.2",
        "python-dotenv>=1.0.0"
    ],
    python_requires=">=3.9",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered development team simulator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aicrewdev",
)
