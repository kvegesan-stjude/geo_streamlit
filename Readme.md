This streamlit app is for downloading Bioproject and biosample metadata from NCBI. I also added functionality to download Geo Series(GSE) data from GEO.
The Geo part is a little buggy, but will still download the data.

The first thing you will need is an api key from NCBI to use the Entrez API. This is needed for downloading data from PMID/BioProject. GSE data can be downloaded without the key.

You can get the API key from https://support.nlm.nih.gov/knowledgebase/article/KA-05317/en-us

Once you have the API key, create a python virtual environment and activate it. https://docs.python.org/3/library/venv.html

Install the requirements using

```

pip install -r requirements.txt
```

Run the app using

```
streamlit run Home.py
```
