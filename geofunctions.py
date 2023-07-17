from Bio import Entrez
import pandas as pd
from bs4 import BeautifulSoup as bs
import os


def get_sample_info(sam_id):
    handle = Entrez.efetch(db="biosample", id=sam_id, retmode='xml')
    sample_xml = str(handle.read(), encoding='utf-8')
    parsed_xml = bs(sample_xml, "lxml")
    temp = {}
    temp['title'] = parsed_xml.find('title').text
    attributes = parsed_xml.find_all('attribute')

    for x in attributes:
        temp[x['attribute_name']] = x.text

    lnks = parsed_xml.find_all('id')
    for l in lnks:
        if ('db' in l.attrs.keys()):
            temp[l['db']] = l.text

    return (temp)


#%%
def get_metadata(bioproject):
    handle = Entrez.elink(dbfrom="bioproject",
                          db='biosample',
                          id=bioproject.replace('PRJNA', ''),
                          LinkName="bioproject_biosample")
    records = Entrez.read(handle=handle)
    # print()
    res = []
    if (len(records[0]['LinkSetDb']) > 0):
        for record in records[0]['LinkSetDb'][0]['Link']:
            try:
                res.append(get_sample_info(record['Id']))
            except Exception as E:
                missed = pd.DataFrame([bioproject, record['Id']]).T
                missed.columns = ['bioproject', 'biosample']
                if ('missingsamples.csv' not in os.listdir()):
                    missed.to_csv('missingsamples.csv', index=None)
                else:
                    missed.to_csv('missingsamples.csv',
                                  mode='a',
                                  header=False,
                                  index=False)
                print(E)
                print('Failed for %s' % (record['Id']))
        data = pd.DataFrame(res)
        data['BioProject'] = bioproject
        return data
    else:
        return pd.DataFrame()


def get_prj_summary(bioproject):
    handle = Entrez.esummary(db="bioproject",
                             id=bioproject.replace('PRJNA', ''))
    records = Entrez.read(handle=handle)
    records['DocumentSummarySet']['DocumentSummary'][0]
    data = pd.DataFrame(records['DocumentSummarySet']['DocumentSummary'])
    return data.melt(id_vars=('Project_Id', 'Project_Acc'))


#%%
def get_metadata_geo(geo):
    handle = Entrez.elink(dbfrom="gds",
                          db='bioproject',
                          id=geo.replace('GSE', ''),
                          LinkName="gds_bioproject")

    records = Entrez.read(handle=handle)
    # print()
    res = []
    for record in records[0]['IdList']:
        res.append(get_metadata(record))
    data = pd.DataFrame(res)
    data['geo'] = geo
    return data


def get_metadata_samn(samn):

    handle = Entrez.elink(dbfrom="biosample",
                          db='sra',
                          id=samn.replace('SAMN', ''),
                          LinkName="biosample_sra")
    records = Entrez.read(handle=handle)
    res = []
    for record in records[0]['LinkSetDb'][0]['Link']:
        temp = {}
        temp['BioSample'] = samn
        handle = Entrez.efetch(db="sra", id=record['Id'], retmode='xml')
        sample_xml = str(handle.read(), encoding='utf-8')
        parsed_xml = bs(sample_xml, "lxml")
        temp['srx'] = parsed_xml.find('experiment')['accession']
        temp['gsm'] = parsed_xml.find('sample')['alias']
        temp['gse'] = parsed_xml.find('study')['alias']
        temp['srr'] = parsed_xml.find('run')['accession']
        res.append(temp)
    return res


#%%