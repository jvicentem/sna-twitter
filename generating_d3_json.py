# -*- coding: utf-8 -*-
from pymongo import MongoClient
import re
import networkx as nx
from networkx.readwrite import json_graph
import community

REAL_MADRID_PLAYERS = {
    "keylor,navas": "navaskeylor",
    "ramos": "sergioramos",
    "nacho": "nachofi1990",
    "carvajal": "danicarvajal92",
    "marcelo": "marcelom12",
    "casemiro": "casemiro",
    "kroos": "tonikroos",
    "modric": "lm19official", 
    "bale": "garethbale11",
    "cristiano,ronaldo": "cristiano",
    "karim,benzema": "benzema",
    "kova": "mateokova16",
    "asensio": "marcoasensio10",
    "james": "jamesdrodriguez",
    "casilla": "kikocasilla13",
    "pepe": "officialpepe",
    "varane": "raphaelvarane",    
    "danil": "2daniluiz", 
    "morata": "alvaromorata",
    "coentrao": "fabio_coentrao",
    "vazquez": "lucasvazquez91",
    "isco": "isco_alarcon",
    "zinedine,zidane": "zidane"
}

BARCELONA_PLAYERS = {
    "stegen": "mterstegen1",
    "piqu[e|é]": "3gerardpique",
    "umtiti": "umtitisam",
    "alba": "jordialba",
    "roberto": "sergiroberto10",
    "rakitic": "ivanrakitic",
    "busquets": "busquets",
    "iniesta": "andresiniesta8",
    "alc[a|á]cer": "paco93alcacer",
    "su[a|á]rez": "luissuarez9",
    "leo,messi": "messi",
    "gomes": "aftgomes",
    "arda,turan": "ardaturan",
    "neymar": "neymarjr",
    "mascherano": "mascherano",
    "mathieu": "iamathieujeremy",
    "rafinha": "rafinha",
    "enrique": "luisenrique21"
}

if __name__ == "__main__":
    client = MongoClient("localhost", 27017)
    db = client.tweetsAGRS

    nodes = {"nodes": []}
    links = {"links": []}

    player_objs = {}

    for player in REAL_MADRID_PLAYERS.keys():
        nodes["nodes"].append({"id": REAL_MADRID_PLAYERS[player], 
                               "count": 0, 
                               "type": "player-rm",
                               "graph": 0
                              })

    for player in BARCELONA_PLAYERS.keys():
        nodes["nodes"].append({"id": BARCELONA_PLAYERS[player], 
                               "count": 0, 
                               "type": "player-bcn",
                               "graph": 1
                              })        

    nodes["nodes"].append({"id": "referee", "count": 0, "type": "referee"})

    for document in db.RMABCN.find({}):
        player_idx = 0

        tweet_text = document["text"].lower()

        for player in REAL_MADRID_PLAYERS.keys():
            player_names = player.split(",")

            if len(player_names) == 1:
                if player_names[0] != "modric":
                    if re.search(player_names[0], tweet_text):
                        nodes["nodes"][player_idx]["count"] += 1

                        if document["user"]["verified"]:
                            account = {"id": str(document["user"]["screen_name"]), 
                                       "type": "account"
                                      }

                            if account not in nodes["nodes"]:
                                nodes["nodes"].append(account)

                            links["links"].append({"source": nodes["nodes"].index(account), 
                                                   "target": player_idx,
                                                   "type": "rm"
                                                  })
                else:
                    if re.search(player_names[0] + "|" + REAL_MADRID_PLAYERS[player], tweet_text):
                        nodes["nodes"][player_idx]["count"] += 1     

                        if document["user"]["verified"]:
                            account = {"id": str(document["user"]["screen_name"]), 
                                       "type": "account"
                                      }

                            if account not in nodes["nodes"]:
                                nodes["nodes"].append(account)

                            links["links"].append({"source": nodes["nodes"].index(account), 
                                                   "target": player_idx,
                                                   "type": "rm"
                                                  })
            else:
                if re.search(player_names[0] + "|" + player_names[1], tweet_text):
                    nodes["nodes"][player_idx]["count"] += 1

                    if document["user"]["verified"]:
                        account = {"id": str(document["user"]["screen_name"]), 
                                   "type": "account"
                                  }

                        if account not in nodes["nodes"]:
                            nodes["nodes"].append(account)

                        links["links"].append({"source": nodes["nodes"].index(account), 
                                               "target": player_idx,
                                               "type": "rm"
                                              })

            player_idx += 1

        for player in BARCELONA_PLAYERS.keys():
            player_names = player.split(",")

            if len(player_names) == 1:
                if re.search(player_names[0], tweet_text):
                    nodes["nodes"][player_idx]["count"] += 1

                    if document["user"]["verified"]:
                        account = {"id": str(document["user"]["screen_name"]), 
                                   "type": "account"
                                  }

                        if account not in nodes["nodes"]:
                            nodes["nodes"].append(account)

                        links["links"].append({"source": nodes["nodes"].index(account), 
                                               "target": player_idx,
                                               "type": "bcn"
                                              })
            else:
                if re.search(player_names[0] + "|" + player_names[1], tweet_text):
                    nodes["nodes"][player_idx]["count"] += 1

                    if document["user"]["verified"]:
                        account = {"id": str(document["user"]["screen_name"]), 
                                   "type": "account"
                                  }

                        if account not in nodes["nodes"]:
                            nodes["nodes"].append(account)

                        links["links"].append({"source": nodes["nodes"].index(account), 
                                               "target": player_idx,
                                               "type": "bcn"
                                              })

            player_idx += 1                  
    
    client.close()

    with open('./assets/elclasico2017.json', 'w') as f:
        json = {"graph": {}, "multigraph": False, "directed": False}
        json = dict(json.items() + nodes.items() + links.items())

        g = json_graph.node_link_graph(json, directed=False)
        parts = community.best_partition(g)

        json['multigraph'] = True

        for key in parts:
            found = False

            i = 0
            while not found:
                if json['nodes'][i]['id'] == key:
                    json['nodes'][i]['community'] = parts[key]
                    found = True

                i += 1

            found = True

        f.write(str(json).replace("'", '"').replace("False", "false").replace("True", "true")) # Hago esto porque sino los strings aparecen con una u delante
