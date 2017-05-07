import requests
import sys
import os
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, json, jsonify




app = Flask(__name__)

#username = os.environ.get('USERNAME', None)
#password = os.environ.get('PASSWORD', None)
#environment_id = os.environ.get('ENVIRONMENT_ID', None)
#collection_id = os.environ.get('COLLECTION_ID', None)

username= '0c3342f7-4594-4967-baea-0e66b2e25bd4'
password='bzn6Qb1fFDkq'
environment_id='32a11c6d-26fc-497a-a25e-b18e618e951e'
collection_id='c8566c56-d55f-414d-a9a7-a5b3668673fd'
endpoint = "https://gateway.watsonplatform.net/discovery/api/v1/environments/"+environment_id+"/collections/"+collection_id+"/query?version=2016-12-01&"

@app.route('/')
def error():
    return render_template('index.html')


    
    #return "Please specify a search term in your URL"

@app.route('/newHeadlines', methods=['POST'])
def newHeadlines():
    combo = request.json['combo']
    comboWords=combo.replace("\"","").split('|')

    combos=[]
    headlines={}
    
    
    try:
        get_url = endpoint+"query=title:("+combo+")|enrichedTitle.entities.text:("+combo+")&count=50&return=title,url"
        results = requests.get(url=get_url, auth=(username, password)) 
        response = results.json()
    
        for article in response['results']:
            combos[:]=[]
            for word in comboWords:
                if word.upper() in article['title'].upper():
                    combos.append(word)
            comboStr = ''.join(sorted(combos))
            comboLen = len(combos)
            if comboLen not in headlines:
                headlines[comboLen]={}
            if comboStr not in headlines[comboLen]:
                headlines[comboLen][comboStr]={}
            headlines[comboLen][comboStr][article['title']]=article['url']

            
    except Exception as e:
        print e
    output = { 'headlines': headlines }  
    return jsonify(output)

@app.route('/click', methods=['GET', 'POST'])
def click():
   
    
    nodes=request.json['nodes']
    links=request.json['links']
    bigWords=request.json['bigWords']
    index=request.json['current']
    
    x = nodes[index]['x']
    y = nodes[index]['y']
    text = nodes[index]['text']

    length = len(nodes)
    words={}
    headlines={}
    combo=""
    comboWords=[]
    combos=[]
    for node in nodes:
        words[node['text']] = node['index']
        if node['expand'] == 1:
            comboWords.append(node['text'])
    for word in comboWords:
        combo+="\""+word+"\"|"
    combo=combo[:-1]
    try:
        get_url = endpoint+"query=title:("+combo+")|enrichedTitle.entities.text:("+combo+")&count=50&return=title,url"
        results = requests.get(url=get_url, auth=(username, password)) 
        response = results.json()

    
        for article in response['results']:
            combos[:]=[]
            for word in comboWords:
                if word.upper() in article['title'].upper():
                    combos.append(word)
            comboStr = ''.join(sorted(combos))
            comboLen = len(combos)
            if comboLen not in headlines:
                headlines[comboLen]={}
            if comboStr not in headlines[comboLen]:
                headlines[comboLen][comboStr]={}
            headlines[comboLen][comboStr][article['title']]=article['url']

    except Exception as e:
        print e
    
    output = { 'results': { 'nodes': [], 'links': [], 'headlines': headlines, 'combo': combo } }
 
    try:
        get_url = endpoint+"query=title:\""+text+"\"&aggregation=nested(enrichedTitle.entities).filter(enrichedTitle.entities.type:Person).term(enrichedTitle.entities.text,count:100)&count=0"
        results = requests.get(url=get_url, auth=(username, password)) 
        response=results.json()
        
        #add to bigWords
        wordList = []
        for kword in response['aggregations'][0]['aggregations'][0]['aggregations'][0]['results']:
            wordList.append(kword['key'])
        bigWords[text]={'wordList':wordList,'expand':1}  
        output['results']['bigWords']=bigWords    
        count1=0 
        count2=0

        for newWord in bigWords[text]['wordList']:
            if newWord in words:
                    output['results']['links'].append({'source':index,'target':words[newWord]})
                    continue
            if count2 < 5:    
                for bigWord in bigWords:
                    if bigWords[bigWord]['expand']==0:
                        continue
                    if bigWord == text:
                        continue
                    if newWord in bigWords[bigWord]['wordList']:
                        if newWord not in words:
                            output['results']['nodes'].append({'x': x, 'y': y, 'text': newWord, 'size': 1.5, 'color': 'white', 'expand': 0})
                            words[newWord]=length
                            length+=1
                            count2+=1
                        output['results']['links'].append({'source':words[newWord],'target':words[bigWord]})
                        output['results']['links'].append({'source':words[newWord],'target':index})
            if newWord not in words and count1 < 5:
                output['results']['nodes'].append({'x': x, 'y': y, 'text': newWord, 'size': 1.5, 'color': 'white', 'expand': 0})   
                output['results']['links'].append({'source':length,'target':index})
                length+=1
                count1+=1
                    
    except Exception as e:
        print e 
                
    return jsonify(output)

@app.route('/favicon.ico')
def favicon():
   return ""


@app.route('/<keyword>')
def news_page(keyword):
    index=0
    nodes=[]
    links=[]
    headlines={}
    headlines[1]={}
    headlines[1][keyword]={}
    
    bigWords={}
    
    try:
        get_url = endpoint+"query=title:("+keyword+")|enrichedTitle.entities.text:("+keyword+")&count=50&return=title,url"
        results = requests.get(url=get_url, auth=(username, password)) 
        response = results.json()
        print response
        for article in response['results']:
            print article['url']
            headlines[1][keyword][article['title']]=article['url'] 
            

    except Exception as e:
        print e
 
    try:
        get_url = endpoint+"query=title:\""+keyword+"\"&aggregation=nested(enrichedTitle.entities).filter(enrichedTitle.entities.type:Person).term(enrichedTitle.entities.text,count:100)&count=0"
        results = requests.get(url=get_url, auth=(username, password)) 
        response=results.json()

        #add to bigWords
        wordList = []
        for kword in response['aggregations'][0]['aggregations'][0]['aggregations'][0]['results']:
            wordList.append(kword['key'])
        bigWords[keyword]={'wordList':wordList,'expand':1}   
    except Exception as e:
        print e
 
    count=0
    nodes.insert(0, {'x': 300, 'y': 200, 'text': keyword, 'size': 3, 'fixed': 1, 'color': '#0066FF', 'expand': 1})
    for word in bigWords[keyword]['wordList']:
        if count > 9:
            break
        if word == keyword:
            continue
        else:
            nodes.append({'x': 300, 'y': 200, 'text': word, 'size': 1.5, 'color': 'white', 'expand': 0})
            links.append({'source':count + 1,'target':0})
            count+=1
                   
    return render_template('cluster.html', nodes=json.dumps(nodes), links=json.dumps(links), bigWords=json.dumps(bigWords), headlines=json.dumps(headlines))





@app.route('/test/<keyword>')
def sankee_test(keyword):
    index=0 
    headlines={}
    headlines[1]={}
    positiveHeadlines={}
    positiveHeadlines[1]={}
    positiveHeadlines[1][keyword]={}
    negativeHeadlines={}
    negativeHeadlines[1]={}
    positiveResultSet=0
    negativeResultSet=0
    negativeHeadlines[1][keyword]={}

    bigWords={}
    positiveKeys=[]
    negativeKeys=[]
    try:
        get_url = endpoint+"query=title:("+keyword+")|docSentiment.type:positive&count=5"
        results = requests.get(url=get_url, auth=(username, password)) 
        response = results.json()
        
        print json.dumps(response ,indent=4 , sort_keys=True)
        for article in response['results']:
            print article['title']
            positiveKeys.append(article['title'])
           # positiveLinks[1] = article['url']
            #print article['title']
            #positiveHeadlines[1][keyword][article['title']]=article['url']   
        positiveResultSet= response['matching_results']
        print positiveKeys
        get_url = endpoint+"query=title:("+keyword+")|docSentiment.type:negative&count=5"
        results = requests.get(url=get_url, auth=(username, password)) 
        response = results.json()
       # negativeResultSet= response['Matching Results']
        #print response
        for article in response['results']:
            print article['title']
            negativeKeys.append(article['title'])

        negativeResultSet= response['matching_results']
       #     negativeLinks[1] = article['url']
           # print article['title']     
           # negativeHeadlines[1][keyword][article['title']]=article['url'] 
           # negativeHeadlines[1][keyword][article['title']]=article['title']
           # print negativeHeadlines[1][keyword][article['title']]
            

    except Exception as e:
        print e

    return render_template('sankeyGraph.html', key= keyword, negativeLinks=json.dumps(negativeKeys), positiveLinks=json.dumps(positiveKeys), positiveResultSet= positiveResultSet, negativeResultSet=negativeResultSet)

port = os.getenv('VCAP_APP_PORT', '8000')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(port), debug=True)

