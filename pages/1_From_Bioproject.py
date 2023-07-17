#%%
import streamlit as st
from geofunctions import get_prj_summary, get_metadata, get_metadata_samn
from Bio import Entrez
import concurrent.futures
import pandas as pd
#%%

if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ''

if 'email' not in st.session_state:
    st.session_state['email'] = ''
api_key = st.text_input('Enter API key for NCBI Entrez (required):',
                        key='api_key',
                        value=st.session_state['api_key'])
email = st.text_input('Enter email for NCBI Entrez (required):',
                      key='email',
                      value=st.session_state['email'])

Entrez.email = email
Entrez.api_key = api_key
prjs = st.text_area(
    'Enter a GEO project ID or a list of GEO project IDs separated by commas (e.g. PRJNA858872,858872):'
)
#cchange working directory
#
# st.write(prjs)
if (len(prjs) > 0):
    prjs = list(set([p.strip() for p in prjs.split(',')]))
    with st.spinner('Querying NLM....'):
        with concurrent.futures.ThreadPoolExecutor(4) as exector:
            results1 = exector.map(get_prj_summary, prjs)
            results2 = exector.map(get_metadata, prjs)

        #%%
        prj_summary = pd.DataFrame()
        for result in results1:
            prj_summary = pd.concat([result, prj_summary])

        prj_summary_samn = pd.DataFrame()
        for result in results2:
            prj_summary_samn = pd.concat([result, prj_summary_samn])
        #%%
        summary = prj_summary.pivot(index=['Project_Id', 'Project_Acc'],
                                    columns='variable',
                                    values='value')
        summary.reset_index(inplace=True)

        st.write('**Biorpoject Summary**')
        st.dataframe(summary)

        st.write('**Biosamples from this project**')
        st.dataframe(prj_summary_samn)

        biosamples = list(set(prj_summary_samn.BioSample.tolist()))

        allres = []
        misses = []
        for l in biosamples:
            try:
                allres = allres + get_metadata_samn(l)
            except Exception as e:
                print(l, e)
                misses.append(l)

        final_srx = pd.DataFrame(allres)

        st.write('**SRA Runs**')
        st.write(final_srx)

        st.write('**Biosamples without SRA info**')
        st.write(misses)
        summary = summary.to_csv(index=None).encode('utf-8')
        prj_summary_samn = prj_summary_samn.to_csv(index=None).encode('utf-8')
        final_srx = final_srx.to_csv(index=None).encode('utf-8')
        st.download_button("Press to Download bioproject summary ",
                           summary,
                           "summary.csv",
                           "text/csv",
                           key='download-bio-csv')
        st.download_button("Press to Download biosample metadata ",
                           prj_summary_samn,
                           "prj_summary_samn.csv",
                           "text/csv",
                           key='download-samn-csv')
        st.download_button("Press to Download SRA runs ",
                           final_srx,
                           "prj_summary_samn.csv",
                           "text/csv",
                           key='download-srx-csv')
# summary.to_csv('bioproject_summary.csv', index=None)
