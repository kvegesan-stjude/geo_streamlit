import streamlit as st
import pandas as pd
import GEOparse
import os
import base64


# create an app with an about page
def app():
    st.title('Home')
    st.write(
        'Welcome to the GEO Streamlit App. This app is designed to help you search and download GEO data.'
    )
    st.write('You will need an api key from https://www.ncbi.nlm.nih.gov/')
    st.write('To get started, select a page from the sidebar to the left.')
    st.write('The bioproject page is for downloading info from bioprojects.')
    st.write('The GSE page is for downloading info from GSEs.')
    st.write(
        'The PMID page is for downloading info from PMIDs. I first map the pmid to a bioproject, and then download the data.'
    )
    st.write('Some projects have a lot of data so please be patient')

    st.write(
        'The GSE page is a little wasteful because it reruns code multiple times. I will fix it in future versions'
    )


# call the app
app()
