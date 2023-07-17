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

pmids = st.text_area(
    'Enter a PMID or a list of PMIDs separated by commas (e.g. 123456):')
allprj = {}
# st.write(prjs)
if (len(pmids) > 0):
    pmids = list(set([p.strip() for p in pmids.split(',')]))
    with st.spinner('Querying NLM....'):
        for p in pmids:
            try:
                allprj[p] = []
                handle = Entrez.elink(dbfrom="pubmed",
                                      db='bioproject',
                                      id=p,
                                      LinkName="pubmed_bioproject")
                records = Entrez.read(handle=handle)
                for record in records[0]['LinkSetDb'][0]['Link']:
                    allprj[p].append(record['Id'])
            except Exception as e:
                st.write('Can not find bioproject for PMID:' + str(p))

        prj_df = pd.DataFrame(columns=['bioproject', 'pmid'])
        for k in allprj:
            if (len(allprj[k]) == 0):
                temp = pd.DataFrame([['na', 'na']],
                                    columns=['bioproject', 'pmid'])
            else:
                temp = pd.DataFrame(allprj[k], columns=['bioproject'])
            temp['pmid'] = k
            prj_df = pd.concat([prj_df, temp])
        prj_df.reset_index(inplace=True)

        st.write('**Bioproject to PMID**')
        st.write(prj_df)
        prjs = list(
            set([p for p in prj_df.bioproject.tolist() if 'na' not in p]))
        if (len(prjs) > 0):
            with concurrent.futures.ThreadPoolExecutor(4) as exector:
                results1 = exector.map(get_prj_summary, prjs)
                results2 = exector.map(get_metadata, prjs)

        #%%
            prj_summary = pd.DataFrame()
            for result in results1:
                prj_summary = pd.concat([result, prj_summary])

            prj_summary_samn = pd.DataFrame()
            for result in results2:
                if (len(result) > 0):
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

            st.write('**Biosamples without SRA**')
            st.write(misses)
            summary = summary.to_csv(index=None).encode('utf-8')
            prj_summary_samn = prj_summary_samn.to_csv(
                index=None).encode('utf-8')
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
                               "final_srx.csv",
                               "text/csv",
                               key='download-srx-csv')
# summary.to_csv('bioproject_summary.csv', index=None)
