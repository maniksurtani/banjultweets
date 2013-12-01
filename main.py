#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.appengine.api import memcache

### Config parameters

twitter_user = 'RCKILDUFF'
consumer_key = 'CXk87McBrZ1ITptGgaTFVw'
consumer_secret = 'UitLoFkNWDZ1gd2FOYBBwK4IkHA6GGESHNWBQsjYGk'
access_token_key = '20942256-kfCGtx1TEyjROt3luc67Wb0CxZqluDK8NFk5O29rI'
access_token_secret = 'rfJGawdovs9EqpmFUxK7p8D6eM4h5VD6f1tLJYrYcyJF3'
num_tweets = 200

class GeotaggedTweet():
  def __init__(self, tweet_id, text, created, lat, lon):
    self.tweet_id = tweet_id
    self.text = text.replace('"', "'") # Clean content
    self.created = created
    self.lat = lat
    self.lon = lon

  def get_url(self):
    return "http://twitter.com/%s/status/%s" % (twitter_user, self.tweet_id)

class MainHandler(webapp2.RequestHandler):

  def load_tweets(self):
    data = memcache.get('cached_tweets')
    if data is None:
      from TwitterAPI import TwitterAPI
      api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)
      r = api.request('statuses/user_timeline', {'screen_name': twitter_user, 'count': num_tweets})
      data = []
      for item in r.get_iterator():
        # Filter out tweets that don't have geo-tags
        if item['coordinates']:
          record = GeotaggedTweet(item['id'], item['text'], item['created_at'], item['coordinates']['coordinates'][1], item['coordinates']['coordinates'][0])
          data.append(record)

      memcache.add('cached_tweets', data, 120)

    return data

  def get(self):

      # count = 0
      # for p in points:
      #   init += '''
      #     point%s = new google.maps.Marker({
      #     position: new google.maps.LatLng(%s, %s), 
      #     title: "%s: %s",
      #     animation: google.maps.Animation.DROP,
      #     })
      #   point%s.setMap(map);
      #   google.maps.event.addListener(point%s, 'click', function(){window.open('%s', '_blank')});
      #   ''' % (count, p['coordinates'][1], p['coordinates'][0], p['date'], p['tweet'].replace('"', "'"), count, count, p['tweet_url'])
      #   count += 1

#<script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDR-_Q-RdUECMwbnZ7_2QftKwVef4m3O74&sensor=false">
          # </script>
      ### This should be pure JS
    html = '''
        <head>
        <style type="text/css">
          #map-canvas { height: 100% }
        </style>
        <script type="text/javascript">
          var infoWindow;
          var maniksHouse;
          var map;
          function initialize() {
            var mapOptions = {
              center: new google.maps.LatLng(51.540339,-0.094864),
              zoom: 13,
              mapTypeId: google.maps.MapTypeId.TERRAIN
            };
            map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);

            maniksHouse = new google.maps.Marker({
              position: new google.maps.LatLng(51.540339,-0.094864), 
              title: "Manik's House",
              animation: google.maps.Animation.DROP,
              icon: 'manik.png'
            });

            maniksHouse.setMap(map);
            google.maps.event.addListener(maniksHouse, 'click', function() {
              var contentString = "<b>Manik's House.</b><br>This is the location of Manik's house in London.";              
              infoWindow = new google.maps.InfoWindow({
                content: contentString
              });
              infoWindow.open(map, maniksHouse);
            });

'''     
    count = 0
    for tweet in self.load_tweets():
      html += '''
            point%s = new google.maps.Marker({
            position: new google.maps.LatLng(%s, %s), 
            title: "%s: %s",
            animation: google.maps.Animation.BOUNCE,
            icon: 'tweet.png'
            })
            point%s.setMap(map);
            google.maps.event.addListener(point%s, 'click', function(){window.open('%s', '_blank')});
    ''' % (count, tweet.lat, tweet.lon, tweet.created, tweet.text, count, count, tweet.get_url())
    count += 1


    ### TODO - add section for intended route.

    html += '''

          }

          function loadScript() {
            t = document.getElementById("tweets");
            var script = document.createElement('script');
            script.type = 'text/javascript';
            script.src = 'https://maps.googleapis.com/maps/api/js?v=3.exp&key=AIzaSyDR-_Q-RdUECMwbnZ7_2QftKwVef4m3O74&sensor=false&' +
              'callback=initialize';
            document.body.appendChild(script);
          }

          window.onload = loadScript;
  </script>
  </head><body><div id="map-canvas" />
</body>
    '''
    self.response.write(html)


app = webapp2.WSGIApplication([    
    ('/', MainHandler)    
], debug=True)
