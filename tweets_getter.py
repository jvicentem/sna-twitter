# -*- coding: utf-8 -*-
from twitter import *
import time
import logging
from datetime import datetime
from pymongo import MongoClient
import random
import signal
import sys

class KeyStore:
    def __init__(self, keyfile):
        self.keys = [line.rstrip('\n') for line in open(keyfile)]
        self.idx = random.randint(0, (len(self.keys)-1))
        self._when_idx_changed()

    def size(self):
        return len(self.keys)

    def change_credentials(self):
        self.idx = (self.idx + 1) % len(self.keys)
        self._when_idx_changed()

    def _when_idx_changed(self):
        key = self.keys[self.idx].split()
        #consumer_key, consumer_secret_key, access_token, acess_token_secret
        auth = OAuth(key[2], key[3], key[0], key[1])
        self.api = Twitter(auth=auth)
        self.stream = TwitterStream(auth = auth, secure = True)


def save_tweet(tweet, db, tweets_saved):
    if 'id' in tweet:
        if db.RMAATM.find({'id': tweet['id']}).count() == 0: 
            tweet['_id'] = tweet['id']
            db.RMAATM.insert_one(tweet) 
            tweets_saved += 1

    return tweets_saved

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    key_store = KeyStore('./twitter_credentials.txt')
    
    tries = 0
    seconds_to_sleep = 1

    tweets_saved = 0
    tweets_saved_aux = 0
    show_info_every_x_tweets = 100

    signal.signal(signal.SIGINT, signal.default_int_handler)

    while True:
        try:
            logging.info('Event started')
            client = MongoClient('localhost', 27017)
            db = client.tweetsAGRS 
            query_stream_string = '#ElClasico, #RMABCN, #RMBCN, #RealMadridBarcelona, #HalaMadrid, #ForçaBarça'
            
            while True:
                twitter_stream = key_store.stream.statuses.filter(track = query_stream_string)
                key_store.change_credentials()

                for tweet in twitter_stream:
                    tweets_saved = save_tweet(tweet, db, tweets_saved)

                    if tweets_saved - tweets_saved_aux == show_info_every_x_tweets:
                        logging.info('%i tweets saved' % db.RMAATM.find({}).count())
                        tweets_saved_aux = tweets_saved

        except KeyboardInterrupt:
            logging.info('Exiting program safely...')
            client.close()
            sys.exit(0)      

        except BaseException as e:
            logging.error(e)
            seconds_to_sleep = random.randint(1, 5)
            logging.error('Error, retrying in %i seconds' % seconds_to_sleep)
            time.sleep(seconds_to_sleep)
            key_store.change_credentials()