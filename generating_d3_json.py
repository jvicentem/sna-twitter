# -*- coding: utf-8 -*-
from pymongo import MongoClient
import re
import networkx as nx
from networkx.readwrite import json_graph
import community
from tweets_getter import KeyStore

REAL_MADRID_PLAYERS = {
    'keylor,navas': 'navaskeylor',
    'ramos': 'sergioramos',
    'nacho': 'nachofi1990',
    'carvajal': 'danicarvajal92',
    'marcelo': 'marcelom12',
    'casemiro': 'casemiro',
    'kroos': 'tonikroos',
    'modric': 'lm19official', 
    'bale': 'garethbale11',
    'cristiano,ronaldo': 'cristiano',
    'karim,benzema': 'benzema',
    'kova': 'mateokova16',
    'asensio': 'marcoasensio10',
    'james': 'jamesdrodriguez',
    'casilla': 'kikocasilla13',
    'pepe': 'officialpepe',
    'varane': 'raphaelvarane',    
    'danil': '2daniluiz', 
    'morata': 'alvaromorata',
    'coentrao': 'fabio_coentrao',
    'vazquez': 'lucasvazquez91',
    'isco': 'isco_alarcon',
    'zinedine,zidane': 'zidane'
}

BARCELONA_PLAYERS = {
    'stegen': 'mterstegen1',
    'piqu[e|é]': '3gerardpique',
    'umtiti': 'umtitisam',
    'alba': 'jordialba',
    'roberto': 'sergiroberto10',
    'rakitic': 'ivanrakitic',
    'busquets': 'busquets',
    'iniesta': 'andresiniesta8',
    'alc[a|á]cer': 'paco93alcacer',
    'su[a|á]rez': 'luissuarez9',
    'leo,messi': 'messi',
    'gomes': 'aftgomes',
    'arda,turan': 'ardaturan',
    'neymar': 'neymarjr',
    'mascherano': 'mascherano',
    'mathieu': 'iamathieujeremy',
    'rafinha': 'rafinha',
    'enrique': 'luisenrique21'
}

def _players_dict_to_list(players_dict, player_type):
    twitter = KeyStore('./twitter_credentials.txt')

    players_list = []



    for player in players_dict:

        players_list.append({'id': players_dict[player], 
                             'count': 0, 
                             'type': player_type,
                             'graph': 0,
                             'img': str(twitter.api.users.search(q = players_dict[player])[0]['profile_image_url_https'])
                            })

    return players_list

def _analyse_real_madrid_players(real_madrid_players_dict, nodes, links, player_idx, document):
    tweet_text = document['text'].lower()

    for player in real_madrid_players_dict:
        player_names = player.split(',')

        if len(player_names) == 1:
            if player_names[0] != 'modric':
                if re.search(player_names[0], tweet_text):
                    nodes[player_idx]['count'] += 1

                    if document['user']['verified']:
                        account = {'id': str(document['user']['screen_name']), 
                                   'type': 'account'
                                  }

                        if account not in nodes:
                            nodes.append(account)

                        links.append({'source': nodes.index(account), 
                                      'target': player_idx,
                                      'type': 'rm'
                                     })
            else:
                if re.search(player_names[0] + '|' + real_madrid_players_dict[player], tweet_text):
                    nodes[player_idx]['count'] += 1     

                    if document['user']['verified']:
                        account = {'id': str(document['user']['screen_name']), 
                                   'type': 'account'
                                  }

                        if account not in nodes:
                            nodes.append(account)

                        links.append({'source': nodes.index(account), 
                                      'target': player_idx,
                                      'type': 'rm'
                                     })
        else:
            if re.search(player_names[0] + '|' + player_names[1], tweet_text):
                nodes[player_idx]['count'] += 1

                if document['user']['verified']:
                    account = {'id': str(document['user']['screen_name']), 
                               'type': 'account'
                              }

                    if account not in nodes:
                        nodes.append(account)

                    links.append({'source': nodes.index(account), 
                                  'target': player_idx,
                                  'type': 'rm'
                                 })

        player_idx += 1

    return player_idx

def _analyse_barcelona_players(barcelona_players_dict, nodes, links, player_idx, document):
    tweet_text = document['text'].lower()

    for player in barcelona_players_dict:
        player_names = player.split(',')

        if len(player_names) == 1:
            if re.search(player_names[0], tweet_text):
                nodes[player_idx]['count'] += 1

                if document['user']['verified']:
                    account = {'id': str(document['user']['screen_name']), 
                               'type': 'account'
                              }

                    if account not in nodes:
                        nodes.append(account)

                    links.append({'source': nodes.index(account), 
                                  'target': player_idx,
                                  'type': 'bcn'
                                 })
        else:
            if re.search(player_names[0] + '|' + player_names[1], tweet_text):
                nodes[player_idx]['count'] += 1

                if document['user']['verified']:
                    account = {'id': str(document['user']['screen_name']), 
                               'type': 'account'
                              }

                    if account not in nodes:
                        nodes.append(account)

                    links.append({'source': nodes.index(account), 
                                  'target': player_idx,
                                  'type': 'bcn'
                                 })

        player_idx += 1 

    return player_idx


def _analyse_all_players(real_madrid_players_dict, barcelona_players_dict, nodes, links, player_idx, document):
    player_idx = _analyse_real_madrid_players(real_madrid_players_dict, nodes, links, player_idx, document)
    _analyse_barcelona_players(barcelona_players_dict, nodes, links, player_idx, document)


def _write_d3_json_format(file_path, nodes, links):
    with open(file_path, 'w') as f:
        json = {'graph': {}, 'multigraph': False, 'directed': False}
        json['nodes'] = nodes
        json['links'] = links

        # Finding partitions
        g = json_graph.node_link_graph(json, directed=False)
        parts = community.best_partition(g)

        json['multigraph'] = True

        # Adding partition info into each node object
        for key in parts:
            found = False

            i = 0
            while not found:
                if json['nodes'][i]['id'] == key:
                    json['nodes'][i]['community'] = parts[key]
                    found = True
                i += 1

            found = True

        f.write(str(json).replace("'", '"')
                .replace('False', 'false')
                .replace('True', 'true')) # I need to do these, otherwise strings will have an annoying 'u' at the beggining  

if __name__ == '__main__':
    client = MongoClient('localhost', 27017)
    db = client.tweetsAGRS

    nodes = []
    links = []

    nodes = (_players_dict_to_list(REAL_MADRID_PLAYERS, 'player-rm') 
             +
             _players_dict_to_list(BARCELONA_PLAYERS, 'player-bcn'))

    for document in db.RMABCN.find({}):
        player_idx = 0

        # nodes and links lists will be modified
        _analyse_all_players(REAL_MADRID_PLAYERS, BARCELONA_PLAYERS, nodes, links, player_idx, document)

    client.close()

    _write_d3_json_format('./assets/elclasico2017.json', nodes, links)


