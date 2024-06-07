from flask import Flask, request, jsonify,render_template,url_for
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
from datetime import datetime

app = Flask(__name__)

# data do sistema em formato ANSI ISO
data_hora_atual = datetime.now()
data_iso_formatada = data_hora_atual.strftime('%Y-%m-%dT%H:%M:%S')

# GraphDB endpoint details
graphdb_endpoint = "http://localhost:7200/repositories/repositorium"

limit = 50
page = 1

def sparql_get_query(query):
    sparql = SPARQLWrapper(graphdb_endpoint)
    sparql.setMethod("GET")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def sparql_post_query(query):
    sparql = SPARQLWrapper(graphdb_endpoint)
    sparql.setMethod("POST")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def search(query):
    pass

@app.route('/')
def index():
    return render_template('index.html', data = {"data": data_iso_formatada})


def listRecordsGET():

    sparql_query = """
    PREFIX : <http://rpcw.di.uminho.pt/2024/repositorium/>
SELECT * WHERE { 
    {
        SELECT distinct ?r
        WHERE { 
            ?r a :Record.
            ?r :contributed_by ?authors.
        }
    }
    ?r :record_id ?id.
    optional{?r :record_title ?title.}
    ?r :record_timestamp ?timestamp.
    ?r :contributed_by ?authors.
    optional{?authors :contributor_name ?name.}
}"""


    jsonReponse = sparql_get_query(sparql_query)
    result = jsonReponse["results"]["bindings"]

    if result:
        data = []
        curr = {}
        
        for r in result:
            if r.get('name') is None:
                r['name'] = {}
                r['name']["type"] = ""
                r['name']["value"] = ""
            id = r['authors']['value'].split('/')[-1]
            if curr == {}:
                curr=r
                curr['names'] = [(r['name'],id)]
            else:
                if curr['r']['value'] == r['r']['value']:
                    curr['names'].append((r['name'],id))

                else:
                    data.append(curr)
                    curr=r
                    curr['names'] = [(r['name'],id)]

        data.append(curr)            

        return render_template('listRecords.html', listRecords=data)
    else:
        return render_template('empty.html', data=data)

def listRecordsPOST(form):
    record_id = form.get('recordId')
    title = form.get('title')
    contributor = form.get('contributor')
    order_by = form.get('orderBy')

    line_id, line_contributor, line_order_by,line_title  = "", "", "",""
    if record_id and record_id != "":
        line_id = f'?r :record_id "{record_id}"'
    else:
        line_id="?r :record_id ?id."
    if title and title != "":
        line_title = f"""
            FILTER (CONTAINS(LCASE(STR(?title)), "{title}") || CONTAINS(LCASE(STR(?altTitle)), "{title}")).
        """
    if contributor:
        line_contributor = f"""
        ?r :contributed_by ?contributor.
        ?contributor :contributor_name ?nameContributor.
        FILTER (CONTAINS(LCASE(STR(?nameContributor)), "{contributor.lower()}")).
        """
    else:
        line_contributor = """
        ?r :contributed_by ?contributor.
        optional{?contributor :contributor_name ?nameContributor.}
        """
    
    if order_by and order_by != "":
        if order_by == "alc":
            line_order_by = "ORDER BY ASC(?contributor)"
        elif order_by == "ald":
            line_order_by = "ORDER BY DESC(?contributor)"
        elif order_by == "dc":
            line_order_by = "ORDER BY ASC(?timestamp)"
        elif order_by == "dd":
            line_order_by = "ORDER BY DESC(?timestamp)"
        else:
            line_order_by = ""


    sparql_query = f"""
    PREFIX : <http://rpcw.di.uminho.pt/2024/repositorium/>
    SELECT * WHERE {{
        {{
            SELECT distinct ?r WHERE {{
                ?r a :Record.
                {line_contributor}
            }}limit 50
        }}
    {line_id}
    ?r :record_timestamp ?timestamp.
    OPTIONAL {{ ?r :record_title ?title. }}
    OPTIONAL {{ ?r :record_alternativeTitle ?altTitle. }}
    {line_title}
    {line_contributor}
}}  {line_order_by}
    """

    jsonReponse = sparql_get_query(sparql_query)
    result = jsonReponse["results"]["bindings"]
    if result:
        data = []
        curr = {}
        for r in result:
            if r.get('nameContributor') is None:
                r['nameContributor'] = {}
                r['nameContributor']["type"] = ""
                r['nameContributor']["value"] = ""

            id = r['contributor']['value'].split('/')[-1]
            if curr == {}:
                curr=r
                curr['names'] = [(r['nameContributor'],id)]
            
            else:
                if curr['r'] == r['r']:
                    curr['names'].append((r['nameContributor'],id))
                else:
                    data.append(curr)
                    curr=r
                    curr['names'] = [(r['nameContributor'],id)]

        data.append(curr)

        return render_template('listRecords.html', listRecords=data)
    else:
        return render_template('empty.html', data=data)

    

@app.route('/listRecords', methods=['POST','GET'])
def listRecords():

    if request.method == 'GET':
        return listRecordsGET()
    elif request.method == 'POST':
        return listRecordsPOST(request.form)



@app.route('/records')
def records(): 
    
    sparql_query = """
    PREFIX : <http://rpcw.di.uminho.pt/2024/repositorium/>
    select * where { 
	?r a :Record.
    optional {?r :record_abstract ?abstract.}
    optional {?r :record_alternativeTitle ?alternativeTitle.}
    optional {?r :record_articlenumber ?articlenumber.}
    optional {?r :record_bookTitle ?bookTitle.}
    optional {?r :record_citation ?citation.}
    optional {?r :record_citationConferenceDate ?citationConferenceDate.}
    optional {?r :record_citationConferencePlace ?citationConferencePlace.}
    optional {?r :record_citationEdition ?citationEdition.}
    optional {?r :record_citationEndPage ?citationEndPage.}
    optional {?r :record_citationIssue ?citationIssue.}
    optional {?r :record_citationStartPage ?citationStartPage.}
    optional {?r :record_citationTitle ?citationTitle.}
    optional {?r :record_citationVolume ?citationVolume.}
    optional {?r :record_comments ?comments.}
    optional {?r :record_conferencePublication ?conferencePublication.}
    optional {?r :record_dateEmbargo ?dateEmbargo.}
    optional {?r :record_dateIssued ?dateIssued.}
    optional {?r :record_degre_grade ?degre_grade.}
    optional {?r :record_degree_grantor ?degree_grantor.}
    optional {?r :record_description ?description.}
    optional {?r :record_doi ?doi.}
    optional {?r :record_eisbn ?eisbn.}
    optional {?r :record_eissn ?eissn.}
    optional {?r :record_embargoFct ?embargoFct.}
    optional {?r :record_eventLocation ?eventLocation.}
    optional {?r :record_eventTitle ?eventTitle.}
    optional {?r :record_eventType ?eventType.}
    optional {?r :record_export ?export.}
    optional {?r :record_exportIdentifier ?exportIdentifier.}
    optional {?r :record_fundingAward ?fundingAward.}
    optional {?r :record_fundingStream ?fundingStream.}
    optional {?r :record_hasVersion ?hasVersion.}
    optional {?r :record_id ?id.}
    optional {?r :record_isBasedOn ?isBasedOn.}
    optional {?r :record_isPartOfSeries ?isPartOfSeries.}
    optional {?r :record_isVersionOf ?isVersionOf.}
    optional {?r :record_isbn ?isbn.}
    optional {?r :record_issn ?issn.}
    optional {?r :record_journal ?journal.}
    optional {?r :record_language ?language.}
    optional {?r :record_number ?number.}
    optional {?r :record_ogUri ?ogUri.}
    optional {?r :record_other ?other.}
    optional {?r :record_pagination ?pagination.}
    optional {?r :record_peerReviewed ?peerReviewed.}
    optional {?r :record_pmc ?pmc.}
    optional {?r :record_pmid ?pmid.}
    optional {?r :record_publicationStatus ?publicationStatus.}
    optional {?r :record_publicationversion ?publicationversion.}
    optional {?r :record_publisherVersion ?publisherVersion.}
    optional {?r :record_relation ?relation.}
    optional {?r :record_relationUri ?relationUri.}
    optional {?r :record_rights ?rights.}
    optional {?r :record_rightsUri ?rightsUri.}
    optional {?r :record_slug ?slug.}
    optional {?r :record_sponsorship ?sponsorship.}
    optional {?r :record_tid ?tid.}
    optional {?r :record_timestamp ?timestamp.}
    optional {?r :record_title ?title.}
    optional {?r :record_type ?type.}
    optional {?r :record_uoei ?uoei.}
    optional {?r :record_version ?version.}
    optional {?r :record_volume ?volume.}
}limit 50
"""
    
    result = sparql_get_query(sparql_query)
    if result["results"]["bindings"]:
        data = result["results"]["bindings"]
        return render_template('teste.html', data=data)
    else:
        return render_template('empty.html', data=data)


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
