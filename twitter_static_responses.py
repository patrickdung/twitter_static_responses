# -*- coding: utf-8 -*-

# SPDX-License-Identifier: AGPL-3.0-only
#
# Copyright (c) 2022 Patrick Dung

from __future__ import unicode_literals
from pelican import signals, contents
import os, urllib.request, datetime, sys

import json
from collections import OrderedDict

from urllib.parse import urlparse

# from pelican.readers import BaseReader

# from flask import jsonify

"""
  This plugin
"""

def article_url(content):
  return SITEURL+'/'+content.url
  ##return PROD_SITEURL+'/'+content.url

# TWITTER_STATS_OVERWRITE_INITIAL_CACHE
def initialize_module(pelican):
  global TWITTER_DISPLAY_STATIC_RESPONSES, TWITTER_BEARER_TOKEN, TWITTER_STATS_CACHE_FILENAME, TWITTER_STATS_UPDATE_INITIAL_CACHE, SITEURL, TWITTER_USERNAME

  for parameter in [ 'TWITTER_DISPLAY_STATIC_RESPONSES', 'TWITTER_BEARER_TOKEN', 'TWITTER_STATS_CACHE_FILENAME', 'TWITTER_STATS_UPDATE_INITIAL_CACHE', 'SITEURL', 'TWITTER_USERNAME' ]:
    if not parameter in pelican.settings.keys():
      print ("twitter_stats" + parameter + "not defined in settings")
    else:
      globals()[parameter] = pelican.settings.get(parameter)
      print (parameter, pelican.settings.get(parameter))

  # if TWITTER_STATS_OVERWRITE_INITIAL_CACHE:
  #  overwrite_initial_cache ()

  # if TWITTER_STATS_UPDATE_INITIAL_CACHE:
  #  update_initial_cache ()

"""
def overwrite_initial_cache ():
    try:
    except:
        raise

def update_initial_cache ():
    try:
    except:
        raise
"""

class Stats(object):
  def __init__(self):
    self.liked = []
    self.reposted = []

def setup_twitter_stats(generator, metadata):
  metadata['twitter_stats'] = Stats()

def fetch_twitter_stats(generator, content):
  target_url = article_url(content)

  if (content.metadata.get("tweet_id") not in {None, ""}):
      # metadata['tweet_id'] = self.process_metadata('tweet_id', tweet_id)
      tweet_id = content.metadata.get('tweet_id')
      # print (tweet_id)

      incoming_json_liking_users = {}
      incoming_json_retweeted_users = {} 

      api_result_liking_users=(fetch_tweet_liking_users (tweet_id))
      # print (api_result_liking_users)
      if api_result_liking_users:
        incoming_json_liking_users = json.loads(api_result_liking_users)

      api_result_retweeted_users=(fetch_tweet_retweeted_users (tweet_id))
      # print (api_result_retweeted_users)
      if api_result_retweeted_users:
        incoming_json_retweeted_users = json.loads(api_result_retweeted_users)

      merged_json={}
      #if (incoming_json_liking_users["data"] not in []) : 
      if "data" in incoming_json_liking_users and incoming_json_liking_users["data"]:
      ##if "data" in incoming_json_liking_users and incoming_json_liking_users['data'] not in {None, ""}:
        print ("DEBUG0")
        #merged_json={'data': incoming_json_liking_users['data']}
        merged_json = incoming_json_liking_users
        print ("DEBUG2", merged_json)

      if "data" in incoming_json_retweeted_users and incoming_json_retweeted_users["data"]:
      #if (incoming_json_retweeted_users["data"] not in []) :
      #if incoming_json_retweeted_users['data'] not in {None, ""}:
      #  merged_json={'data': merged_json['data'] + incoming_json_retweeted_users['data']}
        #merged_json={'data': merged_json['data'].append(incoming_json_retweeted_users['data'])}
        #merged_json={'data': incoming_json_liking_users['data']+incoming_json_retweeted_users['data']}
       resulting_list = list(merged_json['data'])
       resulting_list.extend(x for x in incoming_json_retweeted_users['data'] if x not in resulting_list)
       merged_json = {'data': resulting_list}
      print ("M----")
      print (merged_json)
 
      if TWITTER_STATS_UPDATE_INITIAL_CACHE and "data" in merged_json:
        try:
          file = open(TWITTER_STATS_CACHE_FILENAME, "r")
          cached_json = json.load(file)
          file.close()

          if cached_json is None:
            cached_json = {}

          print ("pre-merge-----------")
          print (cached_json)
          ##cached_json.update(merged_json)
          # for list, py 3.9+
          #cached_json = {'data': cached_json['data'] | merged_json['data']}
          resulting_list = list(cached_json['data'])
          resulting_list.extend(x for x in merged_json['data'] if x not in resulting_list)
          cached_json = {'data': resulting_list}

          print ("post-merge----------------")
          print (cached_json)
          file = open(TWITTER_STATS_CACHE_FILENAME, "w+")
          json.dump(cached_json, file)
          file.close()
        except:
          raise
      else:
        cached_json=merged_json

      #current_Item_Count = 0
      #for x in api_result:
      if "data" not in cached_json:
        return
      print ("DEBUG1", cached_json['data'])
      for item in cached_json['data']:
      ##print (j['children'])
        #print (item.get('tweet_id'))
        if ( item.get("tweet_id", "") == content.metadata.get('tweet_id') ):
        #if (current_Item_Count >= TWITTER_STATS_MAX_ITEMS) : break
        #if (current_Item_Count >= 100) : break
          tweet = {
            "tweet_id": tweet_id,
            "by-id": item.get("by-id", ""),
            "property": item.get("property", ""),
            "by-name": item.get("by-name", ""),
            "ref_url": item.get("ref_url", ""),
          }

          # print (tweet["tweet_id"], tweet["property"], tweet["by-id"], tweet["by-name"])
          if tweet["property"] == 'like-of':
            tweet["reaction"] = 'liked'
            tweet["icon"] = '❤️'
            content.twitter_stats.liked.append(tweet)
          elif tweet["property"] == 'repost-of':
            tweet["reaction"] = 'reposted'
            tweet["icon"] = '🔄'
            content.twitter_stats.reposted.append(tweet)
          elif tweet["property"] == 'mention-of':
            tweet["reaction"] = 'mentioned'
            tweet["icon"] = '💬'
            content.twitter_stats.mentioned.append(tweet)
          else:
            print(f'Unrecognized reaction type: {tweet["property"]}')
            tweet["reaction"] = 'unclassified'
            tweet["icon"] = '❔'
            content.twitter_stats.unclassified.append(tweet)

def fetch_tweet_liking_users (tweet_id):
    ''' https://api.twitter.com/2/tweets/<tweet_id>/liking_users '''

    tweet_query_url = 'https://api.twitter.com/2/tweets/' + tweet_id + '/liking_users'
    # print (tweet_query_url)
    try:
      req = urllib.request.Request(tweet_query_url, headers={'Authorization': 'Bearer ' + TWITTER_BEARER_TOKEN})
      response = urllib.request.urlopen(req)
      data = response.read().decode("utf-8")
      # print (str(data))
      j = json.loads(data)
    except:
      raise

    current_Item_Count = 0
    tweets = []

    if ("data" in j):
      for x in j['data']:
        #if ( x.get("tweet-id", "") == content.metadata.get('tweet_id') ):
        if (current_Item_Count >= 100) : break
      
        liked_tweet = {
          "tweet_id": tweet_id,
          "property": "like-of",
          "by-id": x.get("id", ""),
          "by-name": x.get("name", ""),
          "ref_url": "https://twitter.com/"+TWITTER_USERNAME+"/status/"+tweet_id+"/likes",
        }
        tweets.append(liked_tweet)
        current_Item_Count += 1

      ##return json.dumps(tweets)
      return json.dumps({'data': tweets})
    else:
      #return json.dumps({'data': []})
      return
     
def fetch_tweet_retweeted_users (tweet_id):
    ''' https://api.twitter.com/2/tweets/<tweet_id>/retweeted_by '''

    tweet_query_url = 'https://api.twitter.com/2/tweets/' + tweet_id + '/retweeted_by'
    # print (tweet_query_url)
    try:
      req = urllib.request.Request(tweet_query_url, headers={'Authorization': 'Bearer ' + TWITTER_BEARER_TOKEN})
      response = urllib.request.urlopen(req)
      data = response.read().decode("utf-8")
      # print (str(data))
      j = json.loads(data)
    except:
      raise

    current_Item_Count = 0
    tweets = []

    if ("data" in j):
      for x in j['data']:
        #if ( x.get("tweet-id", "") == content.metadata.get('tweet_id') ):
        if (current_Item_Count >= 100) : break
      
        retweeted_tweet = {
          "tweet_id": tweet_id,
          "property": "repost-of",
          "by-id": x.get("id", ""),
          "by-name": x.get("name", ""),
          "ref_url": "https://twitter.com/"+TWITTER_USERNAME+"/status/"+tweet_id+"/retweets",
        }
        tweets.append(retweeted_tweet)
        current_Item_Count += 1

      ##return json.dumps(tweets)
      return json.dumps({'data': tweets})
    else:
      #return json.dumps({'data': []})
      return
     
def register():
    signals.initialized.connect(initialize_module)
    signals.article_generator_context.connect(setup_twitter_stats)
    signals.article_generator_write_article.connect(fetch_twitter_stats)
