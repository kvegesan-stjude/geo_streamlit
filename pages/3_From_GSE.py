import streamlit as st
import pandas as pd
import GEOparse
from numpy import random
import os
import shutil
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ''

if 'email' not in st.session_state:
    st.session_state['email'] = ''
# api_key = st.text_input('Enter API key for NCBI Entrez (required):',
#                         key='api_key',
#                         value=st.session_state['api_key'])
# email = st.text_input('Enter email for NCBI Entrez (required):',
#                       key='email',
#                       value=st.session_state['email'])

# st.write(api_key, email)

gse = st.text_area(
    'Enter a GSE or a list of GSE separated by commas (e.g. GSE121636,121636):'
)
gse_list = list(set([p.strip() for p in gse.split(',')]))

st.session_state.gse = gse


# generate a 8 digit random number
def random_number():
    return random.randint(10000000, 99999999)


# call the function
random_number = random_number()
# create a directory with that name
gsedir = 'tempdir_gse_' + str(random_number)


def delete_tempdir():
    tempdirs = [d for d in os.listdir('.') if d.startswith('tempdir')]
    for t in tempdirs:
        if (os.path.exists(t)):
            shutil.rmtree(t)


@st.cache_data
def load_gse_data(gse_list, gsedir):
    if (len(gse_list) > 0):

        if (not os.path.exists(gsedir)):
            os.mkdir(gsedir)

        with st.spinner('Querying GEO....'):
            # download geo soft.gz files
            sample_metadata = pd.DataFrame()
            for geo in gse_list:
                try:

                    gse = GEOparse.get_GEO(geo=geo, destdir=gsedir)
                    sample_metadata = pd.concat(
                        [sample_metadata, gse.phenotype_data])
                except Exception as e:
                    print(geo, ' ', e)
            sample_metadata.to_csv(os.path.join(gsedir, 'sample_metadata.tsv'),
                                   sep='\t',
                                   index=None)
            # get the bioproject and pubmed ids where available
            project_data = pd.DataFrame()
            for geo in os.listdir(gsedir):
                if (geo.endswith('soft.gz')):
                    meta_data = {}
                    gse = GEOparse.get_GEO(filepath=os.path.join(gsedir, geo))
                    meta_data['gse'] = [geo.split('_')[0]]
                    bioproject = gse.get_metadata_attribute('relation')
                    if (type(bioproject) == list):
                        meta_data['bioproject'] = ','.join([
                            f.split('/')[-1] for f in bioproject
                            if 'BioProject' in f
                        ])
                    else:
                        meta_data['bioproject'] = ','.join([
                            f.split('/')[-1] for f in [bioproject]
                            if 'BioProject' in f
                        ])

                    try:
                        pubmed = gse.get_metadata_attribute('pubmed_id')
                    except:
                        pubmed = ''
                    if (type(pubmed) == list):
                        meta_data['pubmed'] = [','.join(pubmed)]
                    else:
                        meta_data['pubmed'] = [pubmed]
                    project_data = pd.concat(
                        [project_data, pd.DataFrame(meta_data)])
            #%%
            project_data.to_csv(os.path.join(gsedir, 'gse_metadata.tsv'),
                                sep='\t',
                                index=None)
            # st.success('Done!')
            st.write('**Writing to cache:** ' + gsedir)
            st.write('**Sample metadata:**')
            st.write(sample_metadata)
            st.write('**GSE metadata:**')
            st.write(project_data)
            return sample_metadata, project_data


if (len(gse) > 0):
    sample_metadata, project_data = load_gse_data(gse_list, gsedir)
    sample_metadata = sample_metadata.to_csv(index=None).encode('utf-8')
    project_data = project_data.to_csv(index=None).encode('utf-8')
    st.download_button("Press to Download sample metadata ",
                       sample_metadata,
                       "sample_metadata.csv",
                       "text/csv",
                       key='download-sample-csv')
    st.download_button("Press to Download project metadata ",
                       project_data,
                       "project_data.csv",
                       "text/csv",
                       key='download-project-csv')
clear_cache = st.button('Clear cache')
# st.write(os.getcwd())
if (clear_cache):
    # gse_list = []
    #remove directory
    delete_tempdir()
    st.write('Cache cleared')
