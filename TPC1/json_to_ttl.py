from datetime import datetime
import json
import re

def getDataXSD(data):
    try:
        if len(data) > 10:
            # Parse datetime with time component
            date_obj = datetime.strptime(data, '%d/%m/%Y %H:%M:%S')
            formatted_date = date_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            # Parse date without time component
            date_obj = datetime.strptime(data, '%d/%m/%Y')
            formatted_date = date_obj.strftime('%Y-%m-%dT00:00:00Z')

        return formatted_date
    except ValueError:
        return ""


f = open("plantas.json")
bd = json.load(f)
f.close()

f = open("ontology_plantas.owl")
ttl = f.read()
f.close()

ttl = ""
i = 0
ontologia = "http://rpcw.di.uminho.pt/2024/plantas"

pIndividuo = re.compile(r'[\(\)\'"ºª/]')
pNumeros = re.compile(r'^\d*$')

entidadesSet = set()
estadosSet = set()
plantasSet = set()
localizacaoSet = set()

ttl+="""

#################################################################
#    Individuals
#################################################################
"""

for reg in bd:

    plantado_por = ""
    gerido_por = ""
    localizado_em = ""
    tem = ""
    e = ""
    e_de = ""

    ### ORIGEM
    registoOrigem = ""

    if(reg['Origem'] != ""):

        origem = reg['Origem'].replace(' ','_')

        individuo = f"<{ontologia}#{origem}>" if pIndividuo.search(origem) is not None else f":{origem}"
        plantado_por = f":plantado_por {individuo} ;"


        if(origem not in entidadesSet):

            registoOrigem = f"""
###  {ontologia}#{origem}
    {individuo} rdf:type owl:NamedIndividual ,
            :Empresa ;
    :Nome_Empresa "{reg['Origem']}"^^xsd:string .
"""
            
            entidadesSet.add(origem)

    ###GESTOR
    registoGestor = ""

    if(reg['Gestor'] != ""):

        gestor = reg['Gestor'].replace(' ','_')
        
        individuo = f"<{ontologia}#{gestor}>" if pIndividuo.search(gestor) is not None else f":{gestor}"
        gerido_por = f":gerido_por {individuo} ;"

        if(gestor not in entidadesSet):

            registoGestor = f"""
###  {ontologia}#{gestor}
    {individuo} rdf:type owl:NamedIndividual ,
            :Empresa ;
    :Nome_Empresa "{reg['Gestor']}"^^xsd:string .
"""
            
            entidadesSet.add(gestor)

    ### ESTADO
    registoEstado = ""

    if(reg['Estado'] != ""):

        estado = reg['Estado']
        e = f":é :{estado} ;"

        if(estado not in estadosSet):
           
            registoEstado = f"""
###  {ontologia}#{estado}
    :{estado} rdf:type owl:NamedIndividual ,
            :Estado ;
    :Tipo_Estado "{reg['Estado']}"^^xsd:string .
"""

            estadosSet.add(estado)


    ### LOCALIZAÇÃO
    registoLocalizacao = ""
    listaLocalizacao = []
    listaLocalizacao += [reg['Freguesia']] if reg['Freguesia'] != "" else []
    listaLocalizacao += [reg['Rua']] if reg['Rua'] != "" else []
    listaLocalizacao += [reg['Local']] if reg['Local'] != "" else []
    
    localizacao = f"{'-'.join(listaLocalizacao)}".replace(' ','_')

    if(localizacao != ""):
        
        individuo = f"<{ontologia}#{localizacao}>" if pIndividuo.search(localizacao) is not None else f":{localizacao}"
        localizado_em = f":localizado_em {individuo} ;"

        if(localizacao not in localizacaoSet):

            rua = reg['Rua'].replace('"','\\"')
          
            registoLocalizacao = f"""
###  {ontologia}#{localizacao}
    {individuo} rdf:type owl:NamedIndividual ,
            :Localização ;
    :Código_de_rua "{ str(reg['Código de rua']) }"^^xsd:int ;
    :Freguesia "{reg['Freguesia']}"^^xsd:string ;
    :Local "{reg['Local']}"^^xsd:string ;
    :Rua "{rua}"^^xsd:string .
"""
            
            localizacaoSet.add(localizacao)

    ### PLANTA
    registoPlanta = ""
    #TODO
    planta = f"{reg['Nome Científico']}-{reg['Espécie']}".replace(' ','_').replace('.','')
    if(planta != ""):

        individuo = f"<{ontologia}#{planta}>" if pIndividuo.search(planta) is not None else f":{planta}"

        e_de = f":é_de {individuo} ;"

        if(planta not in plantasSet):

            registoPlanta = f"""
###  {ontologia}#{planta}
    {individuo} rdf:type owl:NamedIndividual ,
            :Planta ;
    :Espécie "{ reg['Espécie'] }"^^xsd:string ;
    :Nome_Científico "{ reg['Nome Científico'] }"^^xsd:string .

"""
            plantasSet.add(planta)
    
    ### PLANTAÇÃO
    plantacao = f"p{reg['Id']}"
    
    registoPlantacao = f"""
###  {ontologia}#{plantacao}
    :{plantacao} rdf:type owl:NamedIndividual ,
            :Plantação ;
    {plantado_por}
    {e}
    {e_de}
    :Caldeira "{reg['Caldeira']}"^^xsd:string ;
    :Data_de_Plantação "{getDataXSD(reg["Data de Plantação"])}"^^xsd:dateTime ;
    :Implantação "{reg['Implantação']}"^^xsd:string ;
    :Tutor "{reg['Tutor']}"^^xsd:string .
"""

    
    ### REGISTOS
    registo = f"r{reg['Id']}"
    numeroDeIntervencoes = ""
    if(pNumeros.search(str(reg["Número de intervenções"])) is not None):
        numeroDeIntervencoes = str(reg["Número de intervenções"])
        
    registoRegisto = f"""
### {ontologia}#{registo}
    :{registo} rdf:type owl:NamedIndividual ,
            :Registo ;
    {gerido_por}
    {localizado_em}
    {tem}
    :Data_de_atualização "{getDataXSD(reg["Data de actualização"])}"^^xsd:dateTime ;
    :Número_de_intervenções "{numeroDeIntervencoes}"^^xsd:int ;
    :Número_de_registo "{reg["Número de Registo"]}"^^xsd:int ;
    :id "{reg["Id"]}"^^xsd:int .

"""
    

    registoTurtle = f"""{registoOrigem}{registoGestor}{registoEstado}{registoLocalizacao}{registoPlanta}{registoPlantacao}{registoRegisto}"""

    ttl += registoTurtle
    i+=1


f = open("ontology_plantas_output.owl","w")
f.write(ttl)
f.close()
