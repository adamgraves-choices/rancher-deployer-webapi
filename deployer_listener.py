from flask import Flask, request
import json
import urllib.request
import subprocess
import os
import random

app = Flask(__name__)

rancher_url = os.environ['RANCHER_URL']
rancher_environment = os.environ['RANCHER_ENVIRONMENT']
rancher_secret_key = os.environ['RANCHER_SECRET_KEY']
rancher_access_key = os.environ['RANCHER_ACCESS_KEY']
splunk_hec_token = os.environ['SPLUNK_HEC_TOKEN']

def random_name():
    left=["admiring", "adoring", "affectionate", "agitated", "amazing", "angry", "awesome", "blissful", "boring", "brave", "clever", "cocky", "compassionate", "competent", "condescending", "confident", "cranky", "dazzling", "determined", "distracted", "dreamy", "eager", "ecstatic", "elastic", "elated", "elegant", "eloquent", "epic", "fervent", "festive", "flamboyant", "focused", "friendly", "frosty", "gallant", "gifted", "goofy", "gracious", "happy", "hardcore", "heuristic", "hopeful", "hungry", "infallible", "inspiring", "jolly", "jovial", "keen", "kickass", "kind", "laughing", "loving", "lucid", "mystifying", "modest", "musing", "naughty", "nervous", "nifty", "nostalgic", "objective", "optimistic", "peaceful", "pedantic", "pensive", "practical", "priceless", "quirky", "quizzical", "relaxed", "reverent", "romantic", "sad", "serene", "sharp", "silly", "sleepy", "stoic", "stupefied", "suspicious", "tender", "thirsty", "trusting", "unruffled", "upbeat", "vibrant", "vigilant", "wizardly", "wonderful", "xenodochial", "youthful", "zealous", "zen"]

    right=["albattani", "allen", "almeida", "agnesi", "archimedes", "ardinghelli", "aryabhata", "austin", "babbage", "banach", "bardeen", "bartik", "bassi", "beaver", "bell", "bhabha", "bhaskara", "blackwell", "bohr", "booth", "borg", "bose", "boyd", "brahmagupta", "brattain", "brown", "carson", "chandrasekhar", "shannon", "clarke", "colden", "cori", "cray", "curran", "curie", "darwin", "davinci", "dijkstra", "dubinsky", "easley", "edison", "einstein", "elion", "engelbart", "euclid", "euler", "fermat", "fermi", "feynman", "franklin", "galileo", "gates", "goldberg", "goldstine", "goldwasser", "golick", "goodall", "haibt", "hamilton", "hawking", "heisenberg", "heyrovsky", "hodgkin", "hoover", "hopper", "hugle", "hypatia", "jang", "jennings", "jepsen", "joliot", "jones", "kalam", "kare", "keller", "khorana", "kilby", "kirch", "knuth", "kowalevski", "lalande", "lamarr", "lamport", "leakey", "leavitt", "lewin", "lichterman", "liskov", "lovelace", "lumiere", "mahavira", "mayer", "mccarthy", "mcclintock", "mclean", "mcnulty", "meitner", "meninsky", "mestorf", "minsky", "mirzakhani", "morse", "murdock", "newton", "nightingale", "nobel", "noether", "northcutt", "noyce", "panini", "pare", "pasteur", "payne", "perlman", "pike", "poincare", "poitras", "ptolemy", "raman", "ramanujan", "ride", "montalcini", "ritchie", "roentgen", "rosalind", "saha", "sammet", "shaw", "shirley", "shockley", "sinoussi", "snyder", "spence", "stallman", "stonebraker", "swanson", "swartz", "swirles", "tesla", "thompson", "torvalds", "turing", "varahamihira", "visvesvaraya", "volhard", "wescoff", "wiles", "williams", "wilson", "wing", "wozniak", "wright", "yalow", "yonath"]
    
    return random.choice(left) + "-" + random.choice(right)


@app.route("/deploy_c2s", methods=['POST'])
def RancherDeployC2S():
    payload = request.get_json()

    if payload.get('c2s_image') == None:
        c2s_image = "master"
    else:
        c2s_image = payload['c2s_image']

    if payload.get('nearby-services-api_image') == None:
        nearbyservicesapi_image = "0.2.0-beta"
    else:
        nearbyservicesapi_image = payload['nearby-services-api_image']

    if payload.get('domain') == None:
        domain = 'dev.c2s.nhschoices.net'
    else:
        domain = payload['domain']

    if payload.get('stack_name') == None:
        stack_name = random_name()
    else:
        stack_name = payload['stack_name']

    s = """
traefik_domain=%(domain)s
c2s_docker_image_tag=%(c2s_image)s
nearbyservices_docker_image_tag=%(nearbyservices_image)s
splunk_hec_endpoint=https://splunk-collector.cloudapp.net:8088
splunk_hec_token=%(splunk_hec_token)s
hotjar_id=265857
google_id=UA-67365892-5
webtrends_id=dcs222rfg0jh2hpdaqwc2gmki_9r4q
        """ % {'domain': domain, 'c2s_image': c2s_image, 'nearbyservices_image': nearbyservicesapi_image, 'splunk_hec_token': splunk_hec_token}

    with open("answers.txt", "w") as text_file:
        text_file.write(s)

    try:
        output = subprocess.check_output(["rancher", "--environment", rancher_environment, "--url", rancher_url, "--access-key", rancher_access_key, "--secret-key", rancher_secret_key, "up", "--pull", "--upgrade", "-d", "--stack", stack_name, "--env-file", "answers.txt"])
        return output
    except subprocess.CalledProcessError as grepexc:                                                                                                   
        print ("error code", grepexc.returncode, grepexc.output)
        return grepexc.output

if __name__ == '__main__':
    
    dockercompose = urllib.request.urlopen("https://raw.githubusercontent.com/nhsuk/nhsuk-rancher-templates/master/templates/c2s_traefik/0/docker-compose.yml")
    with open('docker-compose.yml','wb') as output:
        output.write(dockercompose.read())

    ranchercompose = urllib.request.urlopen("https://raw.githubusercontent.com/nhsuk/nhsuk-rancher-templates/master/templates/c2s_traefik/0/rancher-compose.yml")
    with open('rancher-compose.yml','wb') as output:
        output.write(ranchercompose.read())

    app.run(host= '0.0.0.0')
