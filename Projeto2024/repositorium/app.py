from flask import Flask, request, jsonify,render_template,url_for, redirect
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
from datetime import datetime

app = Flask(__name__)

# data do sistema em formato ANSI ISO
data_hora_atual = datetime.now()
data_iso_formatada = data_hora_atual.strftime('%Y-%m-%dT%H:%M:%SZ')

# GraphDB endpoint details
graphdb_endpoint = "http://localhost:7200/repositories/repositorium"
prefix = "<http://rpcw.di.uminho.pt/2024/repositorium/>"

limit=50
page = 1
reset = True

current_route = ""

def sparql_get_query(query):
    sparql = SPARQLWrapper(graphdb_endpoint)
    sparql.setMethod("GET")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def sparql_post_query(query):
    sparql = SPARQLWrapper(graphdb_endpoint+"/statements")
    sparql.setMethod("POST")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def search(query):
    pass

def listRecordsGET( page_to_render = 'listRecords.html'):
    global limit
    query = f"""
    PREFIX : {prefix}
SELECT * WHERE {{ 
    {{
        SELECT distinct ?r
        WHERE {{ 
            ?r a :Record.
            ?r :contributed_by ?authors.
        }}LIMIT {limit} OFFSET {(page-1)*limit}
    }}
    ?r :record_id ?id.
    optional{{?r :record_title ?title.}}
    ?r :record_timestamp ?timestamp.
    ?r :contributed_by ?authors.
    optional{{?authors :contributor_name ?name.}}
}}"""
    
    count_query = f"""   
    PREFIX : {prefix}
    SELECT (count(?r) as ?count) where {{
    ?r a :Record.
}}
"""
    jsonReponseCount = sparql_get_query(count_query)
    countResult = jsonReponseCount["results"]["bindings"]

    jsonReponse = sparql_get_query(query)
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
        count = countResult[0].get('count')
        return render_template(page_to_render, listRecords=data, page = page, count=count)
    else:
        return render_template(page_to_render, data=[])


def listRecordsPOST(form):
    record_id = form.get('recordId')
    title = form.get('title')
    contributor = form.get('contributor')
    order_by = form.get('orderBy')

    line_id, line_contributor, line_order_by_stamp,line_order_by_cont,line_title  = "", "", "","",""
    if record_id and record_id != "":
        line_id = f'?r :record_id ?id.\n?r :record_id "{record_id}".'
    else:
        line_id="?r :record_id ?id."
    if title and title != "":
        line_title = f"""
            OPTIONAL {{ ?r :record_title ?title. }}
            OPTIONAL {{ ?r :record_alternativeTitle ?altTitle. }}
            FILTER (CONTAINS(LCASE(STR(?title)), "{title}") || CONTAINS(LCASE(STR(?altTitle)), "{title}")).
        """
    else :
        line_title = f"""
            OPTIONAL {{ ?r :record_title ?title. }}
            OPTIONAL {{ ?r :record_alternativeTitle ?altTitle. }}
        """
    
    if contributor and contributor != "":
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
            line_order_by_cont = "ORDER BY ASC(?contributor)"
        elif order_by == "ald":
            line_order_by_cont = "ORDER BY DESC(?contributor)"
        elif order_by == "dc":
            line_order_by_stamp = "ORDER BY ASC(?timestamp)"
        elif order_by == "dd":
            line_order_by_stamp = "ORDER BY DESC(?timestamp)"
        else:
            line_order_by_stamp = ""
            line_order_by_cont = ""

    sparql_query = f"""
    PREFIX : {prefix}
    SELECT * WHERE {{
        {{
            SELECT distinct ?r ?timestamp WHERE {{
                ?r a :Record.
                ?r :record_timestamp ?timestamp.
                {line_title}
                {line_contributor}
            }}{line_order_by_stamp} LIMIT {limit} OFFSET {(page-1)*limit}
        }}
    {line_id}
    ?r :record_timestamp ?timestamp.
    {line_title}
    {line_contributor}
    }} {line_order_by_cont}
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

        return render_template('actions_records.html', listRecords=data)
    else:
        return render_template('actions_records.html', data=[])


def getRecordById(id):
 
    print(id)

    sparql_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    :{id} a :Record.
    optional {{:{id} :record_abstract ?abstract.}}
    optional {{:{id} :record_alternativeTitle ?alternativeTitle.}}
    optional {{:{id} :record_articlenumber ?articlenumber.}}
    optional {{:{id} :record_bookTitle ?bookTitle.}}
    optional {{:{id} :record_citation ?citation.}}
    optional {{:{id} :record_citationConferenceDate ?citationConferenceDate.}}
    optional {{:{id} :record_citationConferencePlace ?citationConferencePlace.}}
    optional {{:{id} :record_citationEdition ?citationEdition.}}
    optional {{:{id} :record_citationEndPage ?citationEndPage.}}
    optional {{:{id} :record_citationIssue ?citationIssue.}}
    optional {{:{id} :record_citationStartPage ?citationStartPage.}}
    optional {{:{id} :record_citationTitle ?citationTitle.}}
    optional {{:{id} :record_citationVolume ?citationVolume.}}
    optional {{:{id} :record_comments ?comments.}}
    optional {{:{id} :record_conferencePublication ?conferencePublication.}}
    optional {{:{id} :record_dateEmbargo ?dateEmbargo.}}
    optional {{:{id} :record_dateIssued ?dateIssued.}}
    optional {{:{id} :record_degre_grade ?degre_grade.}}
    optional {{:{id} :record_degree_grantor ?degree_grantor.}}
    optional {{:{id} :record_description ?description.}}
    optional {{:{id} :record_doi ?doi.}}
    optional {{:{id} :record_eisbn ?eisbn.}}
    optional {{:{id} :record_eissn ?eissn.}}
    optional {{:{id} :record_embargoFct ?embargoFct.}}
    optional {{:{id} :record_eventLocation ?eventLocation.}}
    optional {{:{id} :record_eventTitle ?eventTitle.}}
    optional {{:{id} :record_eventType ?eventType.}}
    optional {{:{id} :record_export ?export.}}
    optional {{:{id} :record_exportIdentifier ?exportIdentifier.}}
    #optional {{:{id} :record_fundingAward ?fundingAward.}}
    #optional {{:{id} :record_fundingStream ?fundingStream.}}
    optional {{:{id} :record_hasVersion ?hasVersion.}}
    optional {{:{id} :record_id ?id.}}
    optional {{:{id} :record_isBasedOn ?isBasedOn.}}
    optional {{:{id} :record_isPartOfSeries ?isPartOfSeries.}}
    optional {{:{id} :record_isVersionOf ?isVersionOf.}}
    optional {{:{id} :record_isbn ?isbn.}}
    optional {{:{id} :record_issn ?issn.}}
    optional {{:{id} :record_journal ?journal.}}
    optional {{:{id} :record_language ?language.}}
    optional {{:{id} :record_number ?number.}}
    optional {{:{id} :record_ogUri ?ogUri.}}
    optional {{:{id} :record_other ?other.}}
    optional {{:{id} :record_pagination ?pagination.}}
    optional {{:{id} :record_peerReviewed ?peerReviewed.}}
    optional {{:{id} :record_pmc ?pmc.}}
    optional {{:{id} :record_pmid ?pmid.}}
    optional {{:{id} :record_publicationStatus ?publicationStatus.}}
    optional {{:{id} :record_publicationversion ?publicationversion.}}
    optional {{:{id} :record_publisherVersion ?publisherVersion.}}
    optional {{:{id} :record_relation ?relation.}}
    optional {{:{id} :record_relationUri ?relationUri.}}
    optional {{:{id} :record_rights ?rights.}}
    optional {{:{id} :record_rightsUri ?rightsUri.}}
    optional {{:{id} :record_slug ?slug.}}
    optional {{:{id} :record_sponsorship ?sponsorship.}}
    optional {{:{id} :record_tid ?tid.}}
    optional {{:{id} :record_timestamp ?timestamp.}}
    optional {{:{id} :record_title ?title.}}
    optional {{:{id} :record_type ?type.}}
    optional {{:{id} :record_uoei ?uoei.}}
    optional {{:{id} :record_version ?version.}}
    optional {{:{id} :record_volume ?volume.}}
    }}"""


    jsonReponse = sparql_get_query(sparql_query)
    result = jsonReponse["results"]["bindings"]
    return result


def getRelationsLst(query,rel):

    jsonReponse = sparql_get_query(query)
    res = jsonReponse["results"]["bindings"]
    l = [{"id": f"{r[rel]['value'].split('/')[-1]}","name": r['name']['value'] if 'name' in r else ""} for r in res]
    return l 


def getRecordRelations(id):

    authors_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    ?authors a :Author.
    optional{{?authors :contributor_name ?name}}.
    ?authors :authored :{id}.
    }}
"""
    editors_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    ?editors a :Editor.
    optional{{?editors :contributor_name ?name}}.
    ?editors :edited :{id}.
    }}
"""
    advisors_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    ?advisors a :Advisor.
    optional{{?advisors :contributor_name ?name}}.
    ?advisors :advised :{id}.
    }}
"""
    publisher_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    ?publisher a :PublisherEntity.
    optional{{?publisher :publisher_name ?name}}.
    ?publisher :published :{id}.
    }}
"""
    others_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    ?others a :Other.
    optional{{?others :contributor_name ?name}}.
    ?others :contributed :{id}.
    }}
"""
    journals_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    ?journals a :Journal.
    optional{{?journals :journal_name ?name}}
    ?journals :with_record :{id}.
    }}
"""
    departments_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    ?departments a :Department.
    optional{{?departments :department_name ?name}}
    ?departments :dep_has_rec :{id}.
    }}
"""
    funders_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    ?funders a :FundingEntity.
    optional{{?funders :funding_name ?name}}
    ?funders :funded :{id}.
    }}
"""
    
    data = {}
    data['authors'] = getRelationsLst(authors_query,'authors')
    data['editors'] = getRelationsLst(editors_query,'editors')
    data['advisors'] = getRelationsLst(advisors_query,'advisors')
    data['publisher'] = getRelationsLst(publisher_query,'publisher')
    data['others'] = getRelationsLst(others_query,'others')
    data['journals'] = getRelationsLst(journals_query,'journals')
    data['departments'] = getRelationsLst(departments_query,'departments')
    data['funders'] = getRelationsLst(funders_query,'funders')

    return data

@app.route('/record/<id>', methods=['GET'])
def records(id):

    id_to_query = f"record_{id}"

    result = getRecordById(id_to_query)

    if result:
        recordFields = [(k,r['value']) for k,r in result[0].items()]
        data = getRecordRelations(id_to_query)
        data['recordFields'] = recordFields
        
        return render_template('record.html', data=data)
    else:

        return render_template('empty.html', data=[])

#/recordDelete/${recordId}
@app.route('/recordDelete/<id>', methods=['DELETE'])
#@app.route('/record/<id>', methods=['GET'])
def deleteRecord(id):
    id_to_delete = f"record_{id}"
    print(f"DELETED ID:{id_to_delete}")
    query = f"""
    PREFIX : {prefix}
    DELETE {{
        :{id_to_delete} ?p ?o .
        ?s ?p2 :{id_to_delete}.
    }}
    WHERE {{
        ?s ?p2 :{id_to_delete}.
        :{id_to_delete} ?p ?o .
    }}
"""
    sparql_post_query(query)
    return redirect(url_for('actionsRecords'), code=303)

def createRecordGET():
    return render_template("createRecord.html")

def getTriplosMultiplos(type,record_uri,type_uri):
    # "authors","editors","advisors","journals","departments","publishers","fundingEnts"]
    query = ""
    match type:
        case "journals":
            query = f"""
{record_uri} :in_journal :{type_uri}.
:{type_uri} :with_record {record_uri}.
    """
        case "publishers":
            query = f"""
{record_uri} :published :{type_uri}.
:{type_uri} :published_by {record_uri}.
    """
        case "authors":
            query = f"""
{record_uri} :authored_by :{type_uri}.
:{type_uri} :authored {record_uri}.
"""
        case "advisors":
            query = f"""
{record_uri} :advised_by :{type_uri}.
:{type_uri} :advised {record_uri}.
"""

        case "editors":
            query = f"""
{record_uri} :edited_by :{type_uri}.
:{type_uri} :edited {record_uri}.
"""
        case "others":
            query = f"""
{record_uri} :contributed_by :{type_uri}.
:{type_uri} :contributed {record_uri}.
"""
        case "departments":
            query = f"""
{record_uri} :in_dep :{type_uri}.
:{type_uri} :dep_has_rec {record_uri}.
    """
        case "fundingEnts":
            query = f"""
{record_uri} :funded_by :{type_uri}.
:{type_uri} :funded {record_uri}.
    """
    return query        
    
def createRecordPOST(form):
    title = form.get("title")
    alTitle = form.get("alTitle")
    issn = form.get("issn")
    doi = form.get("doi")

    id_query = f"""
    PREFIX : {prefix}
    SELECT ?id WHERE {{
    ?s :record_id ?id.
    FILTER (regex(?id, "^0000/\\\\d$")).
    }}
"""
    jsonReponse = sparql_get_query(id_query)
    result = jsonReponse["results"]["bindings"]
    i=0
    if result:
        i = max([int(r['id']['value'].split("/")[-1]) for r in result]) + 1
    
    uri = f":record_0000_{i}"
    id = f"0000/{i}"
    line_alTitle,line_issn,line_doi = "","",""
    
    relations = ["authors","editors","advisors","journals","departments","publishers","fundingEnts"]
    triplos = []
    for rel in relations:
        relLst = form.get(rel) #contributor_0; contributor_1; contributor_2
        if relLst:
            l = relLst.split(";")
            for r in l:
                triplos.append(getTriplosMultiplos(rel,uri,r))


    if alTitle and alTitle != "":
        line_alTitle = f'{uri} :record_alternativeTitle "{alTitle}".'
        triplos.append(line_alTitle)
    if issn and issn != "":
        line_issn = f'{uri} :record_issn "{issn}".'
        triplos.append(line_issn)
    if doi and doi != "":
        line_doi = f'{uri} :record_doi "{doi}".'
        triplos.append(line_doi)

    data_hora_atual = datetime.now()
    data_iso_formatada = data_hora_atual.strftime('%Y-%m-%dT%H:%M:%S+00:00')

    nl = "\n"
    query = f"""
PREFIX : {prefix}
PREFIX owl: <http://www.w3.org/2002/07/owl#>
INSERT DATA {{

    {uri} a :Record, owl:NamedIndividual.
    {uri} :record_id "{id}".
    {uri} :record_title "{title}".
    {uri} :record_timestamp "{data_iso_formatada}"^^xsd:dateTime.
    {nl.join(triplos)}
    
    }}

"""
    sparql_post_query(query)
    return redirect(url_for('actionsRecords'), code=303)


def listContributorsGET():
    query = """
    PREFIX : <http://rpcw.di.uminho.pt/2024/repositorium/>
    SELECT * WHERE {
        ?dep a :Contributor.
        ?dep :contributor_name ?name
    }
    LIMIT 50
    """

    jsonReponse = sparql_get_query(query)
    result = jsonReponse["results"]["bindings"]
    if result:
        data = [( item["dep"]["value"].split("/")[-1], item["name"]["value"]) for item in result]
        return render_template('listContributors.html', listContributors = data)
    else:
        return render_template('listContributors.html', data=[])


def listJournalsGET():
    query = """
    PREFIX : <http://rpcw.di.uminho.pt/2024/repositorium/>
    SELECT * WHERE {
        ?dep a :Journal.
        ?dep :journal_name ?name
    }
    LIMIT 50
    """

    jsonReponse = sparql_get_query(query)
    result = jsonReponse["results"]["bindings"]
    if result:
        data = [( item["dep"]["value"].split("/")[-1], item["name"]["value"]) for item in result]
        return render_template('listJournals.html', listJournals = data)
    else:
        return render_template('listJournals.html', data=[])

def listDepartmentsGET():
    query = """
    PREFIX : <http://rpcw.di.uminho.pt/2024/repositorium/>
    SELECT * WHERE {
        ?dep a :Department.
        ?dep :department_name ?name
    }
    LIMIT 50
    """

    jsonReponse = sparql_get_query(query)
    result = jsonReponse["results"]["bindings"]
    if result:
        data = [( item["dep"]["value"].split("/")[-1], item["name"]["value"]) for item in result]
        return render_template('listDepartments.html', listDepartments = data)
    else:
        return render_template('listDepartments.html', data=[])


def listPublishersGET():
    query = """
    PREFIX : <http://rpcw.di.uminho.pt/2024/repositorium/>
    SELECT * WHERE {
        ?dep a :PublisherEntity.
        ?dep :publisher_name ?name.  
    }
    LIMIT 50
    """

    jsonReponse = sparql_get_query(query)
    result = jsonReponse["results"]["bindings"]
    if result:
        data = [( item["dep"]["value"].split("/")[-1], item["name"]["value"]) for item in result]
        return render_template('listPublishers.html', listPublishers = data)
    else:
        return render_template('listPublishers.html', data=[])

@app.route('/nextPage', methods=['POST'])
def nextPage():
    global current_route, page, reset
    page = page + 1
    reset = False

    if current_route == "/listRecords":
        return redirect(url_for('listRecords'), code=303)
    elif current_route == "/actionsRecords":
        return redirect(url_for('actionsRecords'), code=303)

@app.route('/previousPage', methods=['POST'])
def previousPage():
    global current_route, page, reset
    page = page - 1
    reset = False
    
    if current_route == "/listRecords":
        return redirect(url_for('listRecords'), code=303)
    elif current_route == "/actionsRecords":
        return redirect(url_for('actionsRecords'), code=303)

    #return redirect(url_for(current_route), code=303)

@app.route('/listRecords', methods=['POST','GET'])
def listRecords():
    global current_route, page, reset

    if not reset:
        reset = True
    else:    
        page = 1

    if request.method == 'GET':
        current_route = "/listRecords"
        return listRecordsGET()
    elif request.method == 'POST':
        return listRecordsPOST(request.form)

@app.route("/listJournals", methods=['GET'])
def listJournals():
    global current_route, page
    if request.method == 'GET':
        current_route = "/createRecord"
        return listJournalsGET()

@app.route("/listPublishers", methods=['GET','POST'])
def listPublishers():
    global current_route, page
    if request.method == 'GET':
        current_route = "/createRecord"
        return listPublishersGET()

@app.route("/listDepartments", methods=['GET'])
def listDepartments():
    global current_route, page
    if request.method == 'GET':
        current_route = "/createRecord"
        return listDepartmentsGET()

@app.route("/listContributors", methods=['GET'])
def listContributors():
    global current_route, page
    if request.method == 'GET':
        current_route = "/createRecord"
        page = 1
        return listContributorsGET()

@app.route("/createRecord", methods=['GET','POST'])
def createRecord():
    global current_route, page
    if request.method == 'GET':
        current_route = "/createRecord"
        return createRecordGET()
    elif request.method == 'POST':
        return createRecordPOST(request.form)

@app.route("/actionsRecords",methods={'GET','POST'})
def actionsRecords():
    global current_route, page
    if request.method == 'GET':
        current_route = "/actionsRecords"
        return listRecordsGET(page_to_render='actions_records.html')
    elif request.method == 'POST':
        return listRecordsPOST(request.form)


@app.route('/')
def index():
    return render_template('index.html', data = {"data": data_iso_formatada})


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
