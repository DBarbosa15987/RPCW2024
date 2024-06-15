from flask import Flask, request, render_template,url_for, redirect,make_response
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import json
from datetime import datetime

app = Flask(__name__)


record_fields = {
    "abstract":("record_abstract","abstract_"),
    "alternativeTitle":("record_alternativeTitle","alternativeTitle_"),
    "articlenumber":("record_articlenumber","articlenumber"),
    "bookTitle":("record_bookTitle","bookTitle"),
    "citation":("record_citation","citation"),
    "citationConferenceDate":("record_citationConferenceDate","citationConferenceDate"),
    "citationConferencePlace":("record_citationConferencePlace","citationConferencePlace"),
    "citationEdition":("record_citationEdition","citationEdition"),
    "citationEndPage":("record_citationEndPage","citationEndPage"),
    "citationIssue":("record_citationIssue","citationIssue"),
    "citationStartPage":("record_citationStartPage","citationStartPage"),
    "citationTitle":("record_citationTitle","citationTitle"),
    "citationVolume":("record_citationVolume","citationVolume"),
    "comments":("record_comments","comments_"),
    "conferencePublication":("record_conferencePublication","conferencePublication_"),
    "dateEmbargo":("record_dateEmbargo","dateEmbargo"),
    "dateIssued":("record_dateIssued","dateIssued"),
    "degre_grade":("record_degre_grade","degre_grade"),
    "degree_grantor":("record_degree_grantor","degree_grantor"),
    "description":("record_description","description"),
    "doi":("record_doi","doi"),
    "eisbn":("record_eisbn","eisbn_"),
    "eissn":("record_eissn","eissn_"),
    "embargoFct":("record_embargoFct","embargoFct"),
    "eventLocation":("record_eventLocation","eventLocation"),
    "eventTitle":("record_eventTitle","eventTitle"),
    "eventType":("record_eventType","eventType"),
    "export":("record_export","export"),
    "fundingAward":("record_fundingAward","fundingAward_"),
    "fundingStream":("record_fundingStream","fundingStream_"),
    "isPartOfSeries":("record_isPartOfSeries","isPartOfSeries"),
    "isbn":("record_isbn","isbn_"),
    "issn":("record_issn","issn_"),
    "language":("record_language","language"),
    "ogUri":("record_ogUri","ogUri"),
    "other":("record_other","other"),
    "pagination":("record_pagination","pagination"),
    "peerReviewed":("record_peerReviewed","peerReviewed"),
    "pmc":("record_pmc","pmc"),
    "pmid":("record_pmid","pmid"),
    "publicationStatus":("record_publicationStatus","publicationStatus"),
    "publicationversion":("record_publicationversion","publicationversion"),
    "publisherVersion":("record_publisherVersion","publisherVersion"),
    "relation":("record_relation","relation"),
    "relationUri":("record_relationUri","relationUri"),
    "rights":("record_rights","rights"),
    "rightsUri":("record_rightsUri","rightsUri"),
    "sponsorship":("record_sponsorship","sponsorship"),
    "tid":("record_tid","tid"),
    "title":("record_title","title"),
    "type":("record_type","type"),
    "uoei":("record_uoei","uoei"),
    "version":("record_version","version"),
    "volume":("record_volume","volume"),
    "file":("record_file","file_"),
}

record_relations = {
    "publisher_": ("published_by","published"),
    "author_": ("authored_by","authored"),
    "advisor_": ("advised_by","advised"),
    "editor_": ("edited_by","edited"),
    "other_": ("contributed_by","contributed"),
    "department_": ("in_dep","dep_has_rec"),
    "journal_": ("in_journal","with_record"),
    "funder_": ("funded_by","funded"),
    "subject_": ("has_subject","is_subject_in")
}

# GraphDB endpoint details
graphdb_endpoint = "http://localhost:7200/repositories/repositorium"
prefix = "<http://rpcw.di.uminho.pt/2024/repositorium/>"

limit=50
page = 1
reset = True

current_route = ""
current_filter_route = ""

def filter_switch():
    global current_route, current_filter_route
    if current_route == "/listRecords":
        current_filter_route = "listRecords"
    elif current_route == "/actionsRecords":
        current_filter_route = "actionsRecords"


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


def listRecordsGET( page_to_render = 'listRecords.html'):
    global limit, current_filter_route
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
        print(query)
        with open("debugDumpQuery.json",'w') as f:
            json.dump(data,f,indent=4,ensure_ascii=False)
        filter_switch()

        return render_template(page_to_render, listRecords=data, page = page, count=count, filter_route=current_filter_route)
    else:
        return render_template(page_to_render, data=[])


def getAllRelations():

    query_publishers = f"""
    PREFIX : {prefix}
    SELECT DISTINCT ?publishers ?name WHERE {{
        ?r :published_by ?publishers.
        ?publishers :publisher_name ?name.

    }}
    """
    query_contributors = f"""
    PREFIX : {prefix}
    SELECT DISTINCT ?contributors ?name WHERE {{
        ?r :contributed_by ?contributors.
        ?contributors :contributor_name ?name.

    }}
    """
    query_journals = f"""
    PREFIX : {prefix}
    SELECT DISTINCT ?journals ?name WHERE {{
        ?r :in_journal ?journals.
        ?journals :journal_name ?name.
    }}
    """
    query_departments = f"""
    PREFIX : {prefix}
    SELECT DISTINCT ?departments ?name WHERE {{
        ?r :in_dep ?departments.
        ?departments :department_name ?name.
    }}
    """
    query_funders = f"""
    PREFIX : {prefix}
    SELECT DISTINCT ?funders ?name WHERE {{
        ?r :funded_by ?funders.
        ?funders :funding_name ?name.
    }}
    """
    query_subjects = f"""
    PREFIX : {prefix}
    SELECT DISTINCT ?subjects ?name WHERE {{
        ?r :has_subject ?subjects.
        ?subjects :subject_ ?name.
    }}
    """
    
    data = {}
    data["publishers"] = getRelationsLst(query_publishers,"publishers")
    data["subjects"] = getRelationsLst(query_subjects,"subjects")
    data["contributors"] = getRelationsLst(query_contributors,"contributors")
    data["journals"] = getRelationsLst(query_journals,"journals")
    data["departments"] = getRelationsLst(query_departments,"departments")
    data["funders"] = getRelationsLst(query_funders,"funders")
    return data


def listRecordsPOST(form, page_to_render = 'listRecords.html'):
    record_id = form.get('recordId')
    title = form.get('title')
    contributor = form.get('contributor')
    order_by = form.get('orderBy')

    department = form.get('department')
    keyword = form.get('keyword')


    line_id, line_contributor, line_order_by_stamp,line_order_by_cont,line_title  = "", "", "","",""
    line_keyword, line_department = "", ""

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
    if department and department != "":
        line_department = f'''
        ?r :in_dep ?dep.
        ?dep :department_name ?nameDepartment.
        FILTER (CONTAINS(LCASE(STR(?nameDepartment)), "{department}")).'''

    if keyword and keyword != "":
        line_keyword = f'''
        ?r :has_subject ?sub.
        ?sub :subject_ ?nameSubject.
        FILTER (CONTAINS(LCASE(STR(?nameSubject)), "{keyword}")).'''
    
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
                {line_id}
                {line_contributor}
                {line_department}
                {line_keyword}
            }}{line_order_by_stamp} LIMIT {limit} OFFSET {(page-1)*limit}
        }}
    {line_id}
    ?r :record_timestamp ?timestamp.
    {line_title}
    {line_contributor}
    }} {line_order_by_cont}
    """
    print(sparql_query)
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

        filter_switch()
        return render_template(page_to_render, listRecords=data, fr = current_filter_route)
    else:
        return render_template(page_to_render, data=[])


def getTriplosUpdate(id,form):

    triplosInsert = []
    triplosDelete = []

    for field in record_fields:
        fields = [key for key in form if key.startswith(record_fields[field][1])]
        for f in fields:
            triplosInsert.append(f':{id} :{record_fields[field][0]} "{form[f]}".')
            triplosDelete.append(f":{id} :{record_fields[field][0]} ?o.")

    for rel in record_relations:
        rels = [key for key in form if key.startswith(rel)]
        for r in rels:
            if "::" in form[r]: 
                triplosInsert.append(f':{id} :{record_relations[rel][0]} :{form[r].split("::")[0].strip()}.')    
                triplosInsert.append(f':{form[r].split("::")[0].strip()} :{record_relations[rel][1]} :{id}.')
            else:
                if r.startswith("subject_"):
                    t,newsuburi = getNewSubject(form[r])
                    triplosInsert.append(t)
                    triplosInsert.append(f':{id} :{record_relations[rel][0]} :{newsuburi}.')    
                    triplosInsert.append(f':{newsuburi} :{record_relations[rel][1]} :{id}.')
                    
                else:
                    print(f"{r}:{form[r]} not added!!")
                
            triplosDelete.append(f":{id} :{record_relations[rel][0]} ?o.")
            triplosDelete.append(f"?o :{record_relations[rel][1]} :{id}.")

        
    return triplosInsert,triplosDelete

def getNewSubject(s):
    
    query = f"""
PREFIX : {prefix}
SELECT ?s (REPLACE(STR(?s), "^.*subject_", "") as ?id)
WHERE {{
?s a :Subject .
?s :subject_ ?name.
}}"""
    
    jsonReponse = sparql_get_query(query)
    result = jsonReponse["results"]["bindings"]
    i=0
    if result:
        i=max([int(x['id']['value']) for x in result]) + 1
    newuri = f"subject_{i}"
    return f':{newuri} :subject_ "{s}".',newuri
        



def getRecordById(id):
 
    print(id)
    triplos = []
    for k,(a,_) in record_fields.items():
        triplos.append(f"optional {{:{id} :{a} ?{k}.}}")

    nl = "\n"
    sparql_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    :{id} a :Record.
    :{id} :record_id ?id.
    :{id} :record_timestamp ?timestamp.
    optional {{:{id} :record_title ?title.}}
    {nl.join(triplos)}
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
    ?authors :contributor_name ?name.
    ?authors :authored :{id}.
    }}
"""
    editors_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    ?editors a :Editor.
    ?editors :contributor_name ?name.
    ?editors :edited :{id}.
    }}
"""
    advisors_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    ?advisors a :Advisor.
    ?advisors :contributor_name ?name.
    ?advisors :advised :{id}.
    }}
"""
    publisher_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    ?publisher a :PublisherEntity.
    ?publisher :publisher_name ?name.
    ?publisher :published :{id}.
    }}
"""
    others_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    ?others a :Other.
    ?others :contributor_name ?name.
    ?others :contributed :{id}.
    }}
"""
    journals_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    ?journals a :Journal.
    ?journals :journal_name ?name.
    ?journals :with_record :{id}.
    }}
"""
    departments_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    ?departments a :Department.
    ?departments :department_name ?name.
    ?departments :dep_has_rec :{id}.
    }}
"""
    funders_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    ?funders a :FundingEntity.
    ?funders :funding_name ?name.
    ?funders :funded :{id}.
    }}
"""
    subjects_query = f"""
    PREFIX : {prefix}
    select * where {{ 
    ?subjects a :Subject.
    ?subjects :subject_ ?name.
    ?subjects :is_subject_in :{id}.
    }}
"""

    data = {}
    data['authors'] = getRelationsLst(authors_query,'authors')
    data['editors'] = getRelationsLst(editors_query,'editors')
    data['advisors'] = getRelationsLst(advisors_query,'advisors')
    data['publisher'] = getRelationsLst(publisher_query,'publisher')
    data['subjects'] = getRelationsLst(subjects_query,'subjects')
    data['others'] = getRelationsLst(others_query,'others')
    data['journals'] = getRelationsLst(journals_query,'journals')
    data['departments'] = getRelationsLst(departments_query,'departments')
    data['funders'] = getRelationsLst(funders_query,'funders')

    return data


def createRecordGET():

    recordFields = [r for r in record_fields if r.lower()!= "oguri" and r.lower()!= "other"]
    data = {}
    data['recordFields'] = recordFields
    allData = getAllRelations()

    return render_template("createRecord.html",allData=allData,data=data)


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
    
    uri = f"record_0000_{i}"
    id = f"0000/{i}"
    
    triplos,_ = getTriplosUpdate(uri,form)

    data_hora_atual = datetime.now()
    data_iso_formatada = data_hora_atual.strftime('%Y-%m-%dT%H:%M:%S+00:00')

    nl = "\n"
    query = f"""
PREFIX : {prefix}
PREFIX owl: <http://www.w3.org/2002/07/owl#>
INSERT DATA {{

    :{uri} a :Record, owl:NamedIndividual.
    :{uri} :record_id "{id}".
    :{uri} :record_timestamp "{data_iso_formatada}"^^xsd:dateTime.
    {nl.join(triplos)}
    
    }}

"""
    sparql_post_query(query)
    return redirect(url_for('actionsRecords'), code=303)


def updateRecordGET(id):
    id_to_query = f"record_{id}"
    result = getRecordById(id_to_query)

    recordFields = {}
    if result:
        for r in result:
            for k,v in r.items():
                if k in recordFields:
                    recordFields[k].add(v['value'])
                else:
                    recordFields[k] = set([v['value']])
        #recordFields = [(k,list(r)) for k,r in recordFields.items()]
        data = getRecordRelations(id_to_query)
        data['recordFields'] = recordFields.items()

    # if result:
    #     recordFields = [(k, r['value']) for k, r in result[0].items()]
    #     data = getRecordRelations(id_to_query)
    #     data['recordFields'] = recordFields
    #     print(id_to_query)
        allData = getAllRelations()
        return render_template('updateRecord.html', data=data, allData=allData,id=id)
    else:
        return render_template('empty.html')

        
def updateRecordPOST(id,form):

    nl = "\n"
    id_to_query = f"record_{id}"
    triplosInserir,triplosApagar = getTriplosUpdate(id_to_query,form)
    data_hora_atual = datetime.now()
    data_iso_formatada = data_hora_atual.strftime('%Y-%m-%dT%H:%M:%S+00:00')
    triplosInserir.append(f':{id_to_query} :record_timestamp "{data_iso_formatada}"^^xsd:dateTime.')
    triplosApagar.append(f':{id_to_query} :record_timestamp ?o.')

    query = f"""
    PREFIX : {prefix}
    DELETE {{
        {nl.join(triplosApagar)}
    }}
    INSERT {{
        {nl.join(triplosInserir)}
    }}
    WHERE {{
        :{id_to_query} ?p ?o .
}}
"""

    sparql_post_query(query)
    print(query)
    return redirect(url_for('actionsRecords'), code=303)


def listContributorsGET():
    query = f"""
    PREFIX : {prefix}
    SELECT * WHERE {{
        ?dep a :Contributor.
        ?dep :contributor_name ?name
    }}
    LIMIT {limit}
    """

    jsonReponse = sparql_get_query(query)
    result = jsonReponse["results"]["bindings"]
    if result:
        data = [( item["dep"]["value"].split("/")[-1], item["name"]["value"]) for item in result]
        return render_template('listContributors.html', listContributors = data)
    else:
        return render_template('listContributors.html', data=[])


def listJournalsGET():
    query = f"""
    PREFIX : {prefix}
    SELECT * WHERE {{
        ?dep a :Journal.
        ?dep :journal_name ?name
    }}
    LIMIT {limit}
    """

    jsonReponse = sparql_get_query(query)
    result = jsonReponse["results"]["bindings"]
    if result:
        data = [( item["dep"]["value"].split("/")[-1], item["name"]["value"]) for item in result]
        return render_template('listJournals.html', listJournals = data)
    else:
        return render_template('listJournals.html', data=[])


def listDepartmentsGET():
    query = f"""
    PREFIX : {prefix}
    SELECT * WHERE {{
        ?dep a :Department.
        ?dep :department_name ?name
    }}
    LIMIT {limit}
    """

    jsonReponse = sparql_get_query(query)
    result = jsonReponse["results"]["bindings"]
    if result:
        data = [( item["dep"]["value"].split("/")[-1], item["name"]["value"]) for item in result]
        return render_template('listDepartments.html', listDepartments = data)
    else:
        return render_template('listDepartments.html', data=[])


def listPublishersGET():
    query = f"""
    PREFIX : {prefix}
    SELECT * WHERE {{
        ?dep a :PublisherEntity.
        ?dep :publisher_name ?name.  
    }}
    LIMIT {limit}
    """

    jsonReponse = sparql_get_query(query)
    result = jsonReponse["results"]["bindings"]
    if result:
        data = [( item["dep"]["value"].split("/")[-1], item["name"]["value"]) for item in result]
        return render_template('listPublishers.html', listPublishers = data)
    else:
        return render_template('listPublishers.html', data=[])

@app.route('/record/<id>', methods=['GET'])
def records(id):

    id_to_query = f"record_{id}"

    result = getRecordById(id_to_query)
    recordFields = {}
    if result:
        for r in result:
            for k,v in r.items():
                if k in recordFields:
                    recordFields[k].add(v['value'])
                else:
                    recordFields[k] = set([v['value']])
        #recordFields = [(k,list(r)) for k,r in recordFields.items()]
        data = getRecordRelations(id_to_query)
        data['recordFields'] = recordFields.items()
        
        return render_template('record.html', data=data)
    else:
        return render_template('empty.html', data=[])

@app.route('/recordDelete/<id>', methods=['DELETE'])
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

@app.route("/actionsRecords",methods=['GET','POST'])
def actionsRecords():
    global current_route, page
    current_route = "/actionsRecords"
    if request.method == 'GET':
        return listRecordsGET(page_to_render='actions_records.html')
    elif request.method == 'POST':
        return listRecordsPOST(request.form, page_to_render='actions_records.html')

@app.route("/updateRecord/<id>", methods=['GET','POST'])
def updateRecord(id):
   if request.method == 'GET':
       return updateRecordGET(id)
   elif request.method == 'POST':
       return updateRecordPOST(id,request.form)
    
@app.route("/recordEdit/<id>",methods={'POST'})
def recordEdit(id):
    global current_route, page
    current_route = "/updateRecord"
    if request.method == 'POST':
        return redirect(url_for(f'updateRecord/{id}'), code=303)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
