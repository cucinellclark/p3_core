import os
import sys
import re
import requests
import io
import urllib.request, urllib.parse, urllib.error
import json
import pandas as pd
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

Debug = False #shared across functions defined here
LOG = sys.stderr
Base_url = "https://www.patricbrc.org/api/"

PatricUser = None

# First iteration: include getFeatureDf, getSubsystemsDf, getPathwaysDf, authenticate functions and getGenomeGroupIds

# splits a list into multiple lists of max size == size
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

# Given a set of genome_ids, returns a pandas dataframe after querying for features
def getFeatureDf(genome_ids, limit=2500000):
    feature_df_list = []
    for gids in chunker(genome_ids, 20):
        batch=""
        genomes = "in(genome_id,({0}))".format(','.join(gids))
        limit = "limit({0})".format(limit)
        select = "sort(+feature_id)&eq(annotation,PATRIC)"
        base = "https://www.patricbrc.org/api/genome_feature/?http_download=true"
        query = "&".join([genomes,limit,select]) 
        headers = {"accept":"text/tsv", "content-type":"application/rqlquery+x-www-form-urlencoded"}
        #query = requests.get(f"https://www.patricbrc.org/api/genome_feature/?in(genome_id,({','.join(gids)}))&eq(annotation,PATRIC)&limit({limit})&sort(+genome_id)&http_download=true&http_accept=text/tsv")

        print('Query = {0}\nHeaders = {1}'.format(base+'&'+query,headers))
        with requests.post(url=base, data=query, headers=headers) as r:
            if r.encoding is None:
                r.encoding = "utf-8"
            if not r.ok:
                logging.warning("Error in API request \n")
            batch_count=0
            for line in r.iter_lines(decode_unicode=True):
                line = line+'\n'
                batch+=line
                batch_count+=1        
        # TODO: set column data types
        feature_df = pd.read_csv(io.StringIO(batch),sep='\t')
        feature_df_list.append(feature_df)
    if len(feature_df_list) > 0:
        return_df = pd.concat(feature_df_list) 
        return return_df
    else:
        return None

# Given a set of genome_ids, returns a pandas dataframe after querying for subsystems
def getSubsystemsDf(genome_ids,limit=2500000):
    subsystem_df_list = []
    for gids in chunker(genome_ids, 20):
        batch=""
        genomes = "in(genome_id,({0}))".format(','.join(gids))
        limit = "limit({0})".format(limit)
        select = "sort(+id)"
        base = "https://www.patricbrc.org/api/subsystem/?http_download=true"
        query = "&".join([genomes,limit,select])
        headers = {"accept":"text/tsv", "content-type":"application/rqlquery+x-www-form-urlencoded"}
        #subsystem_query = requests.get(f"https://patricbrc.org/api/subsystem/?in(genome_id,({','.join(gids)}))&limit({limit})&sort(+genome_id)&http_accept=text/tsv")
        #subsystem_df = pd.read_table(io.StringIO(subsystem_query.text),sep='\t')

        print('Query = {0}\nHeaders = {1}'.format(base+'&'+query,headers))
        with requests.post(url=base, data=query, headers=headers) as r:
            if r.encoding is None:
                r.encoding = "utf-8"
            if not r.ok:
                logging.warning("Error in API request \n")
            batch_count=0
            for line in r.iter_lines(decode_unicode=True):
                line = line+'\n'
                batch+=line
                batch_count+=1
        # TODO: set column data types
        subsystem_df = pd.read_csv(io.StringIO(batch),sep='\t')
        subsystem_df_list.append(subsystem_df)
    if len(subsystem_df_list) > 0:
        return_df = pd.concat(subsystem_df_list)
        return return_df
    else:
        return None

# Given a set of genome_ids, returns a pandas dataframe after querying for pathways 
def getPathwayDf(genome_ids,limit=2500000):
    pathway_df_list = [] 
    for gids in chunker(genome_ids, 20):
        batch=""
        genomes = "in(genome_id,({0}))".format(','.join(gids))
        limit_str = "limit({0})".format(limit)
        select = "eq(annotation,PATRIC)&sort(+id)"
        base = "https://www.patricbrc.org/api/pathway/?http_download=true"
        query = "&".join([genomes,limit_str,select])
        headers = {"accept":"text/tsv", "content-type":"application/rqlquery+x-www-form-urlencoded"}

        print('Query = {0}\nHeaders = {1}'.format(base+'&'+query,headers))
        with requests.post(url=base, data=query, headers=headers) as r:
            if r.encoding is None:
                r.encoding = "utf-8"
            if not r.ok:
                logging.warning("Error in API request \n")
            batch_count=0
            for line in r.iter_lines(decode_unicode=True):
                line = line+'\n'
                batch+=line
                batch_count+=1 
        # TODO: set column data types
        pathway_df = pd.read_csv(io.StringIO(batch),sep='\t')
        pathway_df_list.append(pathway_df)
    if len(pathway_df_list) > 0:
        return_df = pd.concat(pathway_df_list)
        return return_df
    else:
        return None

# athenticates session by searching for token file
def authenticateByFile(tokenFile=None, Session=None):
    if not tokenFile:
        tokenFile = os.path.join(os.environ.get('HOME'), ".patric_token")
    if os.path.exists(tokenFile):
        LOG.write("reading auth key from file %s\n"%tokenFile)
        with open(tokenFile) as F:
            tokenString = F.read().rstrip()
            authenticateByString(tokenString, Session)
        return True
    return False

# authenticates session by looking for KB_AUTH_TOKEN
def authenticateByEnv(Session):
    if "KB_AUTH_TOKEN" in os.environ:
        LOG.write("reading auth key from environment\n")
        authenticateByString(os.environ.get('KB_AUTH_TOKEN'), Session)
        return True
    else:
        return authenticateByFile(None, Session)

# authenticates session by analyzing input string
def authenticateByString(tokenString, Session):
    Session.headers.update({ 'Authorization' : tokenString })
    if "Authorization" in Session.headers:
        global PatricUser
        PatricUser = Session.headers["Authorization"].split(r"|")[3].split("=")[1]
        LOG.write("Patric user = %s\n"%PatricUser)

# Returns a list of genome_ids from the passed in genome group
def getGenomeGroupIds(genomeGroupName, Session, genomeGroupPath=False):
    if genomeGroupPath: #genomeGroupName is assumed to be a full path
        group_path = urllib.parse.quote(genomeGroupName)
        genomeGroupSpecifier = group_path.replace("/", "%2f")
    else: #assume the genome group is in /home/Genome Groups"
        genomeGroupSpecifier = PatricUser+"/home/Genome Groups/"+genomeGroupName
        genomeGroupSpecifier = "/"+urllib.parse.quote(genomeGroupSpecifier)
        genomeGroupSpecifier = genomeGroupSpecifier.replace("/", "%2f")
    query = "in(genome_id,GenomeGroup("+genomeGroupSpecifier+"))"
    query += "&select(genome_id)"
    query += "&limit(10000)"
    ret = Session.get(Base_url+"genome/", params=query)
    data = json.loads(ret.text) 
    ret_ids = [list(x.values())[0] for x in data]
    return ret_ids
