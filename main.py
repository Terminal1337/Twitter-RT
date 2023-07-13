import httpx
import string
import hashlib
import os
import ctypes
import time
import threading
from colorama import Fore,init
import tls_client
import json
from loaders.proxy_loader import *
from loaders.loadJson import readjson
init(convert=True)


class Twtitter():
    def __init__(self) -> None:
        self.succes  = 0
        self.retweets = 0
        self.likes = 0
        self.replies = 0
        self.replies_list = open('replies.txt',encoding='utf8').read().split('\n')
        self.errors = 0 
        self.config = readjson("config.json")
        self.lock = threading.Lock()
        self.do_retweet = self.config["tokens"]["retweet"]
        self.do_like = self.config["tokens"]["like"]
        self.do_reply = self.config["tokens"]["reply"]
        self.mToken = self.config["main"]["auth_token"]
        self.repliers = open('input/repliers.txt',encoding='utf-8').read().split('\n')
        self.mct0 = False
        if not self.config["main"]["ct0"] == "":
            self.mct0 = self.config["main"]["ct0"]
        self.use_image = self.config["main"]["image"]
        self.video = self.config["main"]["video"]
        self.tweet = open(self.config['main']['tweet_file'],encoding='utf-8').read()
        self.cooldown = self.config['main']['cooldown']
        self.tokens = open('input/tokens.txt',encoding='utf-8').read().split("\n")
        threading.Thread(target=self.consoleUpdater).start()
        self.threads = int(input("Threads : "))
   
    def tweet_and_return_id(self):
        proxy = getProxy()
        client = httpx.Client(proxies=proxy)
        cookies = {
            'auth_token': self.mToken
        }
        headers =  {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'origin': 'https://twitter.com',
            'referer': 'https://twitter.com/settings/profile',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'en'
        }
        if not self.mct0:
            ct0_response = client.post('https://twitter.com/i/api/1.1/account/update_profile.json', cookies=cookies, headers=headers)
            self.mct0 = ct0_response.cookies['ct0']
        cookies['ct0'] = self.mct0
        headers['x-csrf-token'] = self.mct0
        headers["content-type"] = "application/json"
        payload ={"variables":{"tweet_text":self.tweet,"dark_request":False,"media":{"media_entities":[],"possibly_sensitive":False},"semantic_annotation_ids":[]},"features":{"tweetypie_unmention_optimization_enabled":True,"responsive_web_edit_tweet_api_enabled":True,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":True,"view_counts_everywhere_api_enabled":True,"longform_notetweets_consumption_enabled":True,"tweet_awards_web_tipping_enabled":False,"longform_notetweets_rich_text_read_enabled":True,"longform_notetweets_inline_media_enabled":False,"responsive_web_graphql_exclude_directive_enabled":True,"verified_phone_label_enabled":True,"freedom_of_speech_not_reach_fetch_enabled":True,"standardized_nudges_misinfo":True,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":False,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":False,"responsive_web_graphql_timeline_navigation_enabled":True,"responsive_web_enhance_cards_enabled":False},"queryId":"XJbwBegmIRLwZzLTQxNDXA"}
        if self.use_image:
            bytes = str(os.stat('img.jpg').st_size)
            params = {
            "command": "INIT",
            "total_bytes": bytes,
            "media_type": "image/jpeg"
        }
            upload_url = "https://upload.twitter.com/i/media/upload.json"
            headers_img = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'de-DE,de;q=0.9',
            'cache-control': 'no-cache',
            # 'content-length': '0',
            'origin': 'https://twitter.com',
            'pragma': 'no-cache',
            'referer': 'https://twitter.com/',
            'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5024.121 Safari/537.36",
        }
            response = client.post(upload_url, params=params, headers=headers_img, cookies={
            'auth_token': self.mToken
        })
            
            media_id = response.json()["media_id"]
            with open('img.jpg', 'rb') as file:
                hash_md5 = hashlib.md5()
                for chunk in iter(lambda: file.read(4096), b""):
                    hash_md5.update(chunk)
                    md5 = hash_md5.hexdigest()
                    files = [('media', (self.use_image, open(self.use_image, 'rb'), 'image/jpeg'))]
                boundary = '----WebKitFormBoundary' \
                + ''.join(random.sample(string.ascii_letters + string.digits, 16))
                headers["content-type"] = f"multipart/form-data; boundary={boundary}"
                params = {
            "command": "APPEND",
            "media_id": media_id,
            "segment_index": 0
        }
            # del headers["content-length"]
            response = client.post(upload_url, params=params, headers=headers_img, cookies={'auth_token': self.mToken},files=files)
            if response.status_code != 204:
                print(f"Failed to set profile picture {response.status_code} {response.text} at APPEND")
                return False
            params = {
                "command": "FINALIZE",
                "media_id": media_id,
                "original_md5": md5
            }
            del headers["content-type"]
            response = client.post(upload_url, params=params, headers=headers_img, cookies={
                'auth_token': self.mToken
        })
            
            if response.status_code != 201:
                return False
            payload ={"variables":{"tweet_text":self.tweet,"dark_request":False,"media":{"media_entities":[{"media_id": media_id,"tagged_users": []}],"possibly_sensitive":False},"semantic_annotation_ids":[]},"features":{"tweetypie_unmention_optimization_enabled":True,"responsive_web_edit_tweet_api_enabled":True,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":True,"view_counts_everywhere_api_enabled":True,"longform_notetweets_consumption_enabled":True,"tweet_awards_web_tipping_enabled":False,"longform_notetweets_rich_text_read_enabled":True,"longform_notetweets_inline_media_enabled":False,"responsive_web_graphql_exclude_directive_enabled":True,"verified_phone_label_enabled":True,"freedom_of_speech_not_reach_fetch_enabled":True,"standardized_nudges_misinfo":True,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":False,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":False,"responsive_web_graphql_timeline_navigation_enabled":True,"responsive_web_enhance_cards_enabled":False},"queryId":"XJbwBegmIRLwZzLTQxNDXA"}

        resp = client.post('https://twitter.com/i/api/graphql/GUFG748vuvmewdXbB5uPKg/CreateTweet',json=payload, cookies=cookies, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            self.tweet_id = data['data']['create_tweet']['tweet_results']['result']['rest_id']
            with self.lock:
                print(f"{Fore.RED}INFO : {Fore.RESET}[{Fore.CYAN}TWEETID{Fore.RESET}] - {Fore.LIGHTBLACK_EX}{self.tweet_id}{Fore.RESET}")
            threading.Thread(target=self.HandlerLikeRetweet).start()

    def HandlerLikeRetweet(self):
        for i in range(len(self.tokens)):
                    try:
                        threading.Thread(target=self.likeme,args=(self.tokens[i],)).start()
                        if threading.active_count() >= self.threads:
                            while True:
                                if threading.active_count() < self.threads:
                                    break
                    except Exception as e:
                        print(e)
                        self.errors += 1
                        pass
    def HandlerReply(self):
        for i in range(len(self.repliers)):
                if threading.active_count() >= self.threads:
                    while True:
                        if threading.active_count() < self.threads:
                            break 
                threading.Thread(target=self.reply,args=(self.repliers[i],)).start()

    def likeme(self,token):
        try:
            proxy = getProxy()
            mct0 = ''
            client = httpx.Client(proxies=proxy)
     
            cookies = {
            'auth_token': token
        }
            headers =  {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'origin': 'https://twitter.com',
            'referer': 'https://twitter.com/settings/profile',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'en'
        }
        
            ct0_response = client.post('https://twitter.com/i/api/1.1/account/update_profile.json', cookies=cookies, headers=headers)
            mct0 = ct0_response.cookies['ct0']
            cookies['ct0'] = mct0
            headers['x-csrf-token'] = mct0
            headers["content-type"] = "application/json"
            if self.do_retweet:    
                threading.Thread(target=self.retweetme,args=(client,cookies,headers,proxy)).start()
            if self.do_like:
                resp = client.post('https://twitter.com/i/api/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet',json={"variables":{"tweet_id":self.tweet_id},"queryId":"lI07N6Otwv1PhnEgXILM7A"},headers=headers,cookies=cookies)
                if "Done" in resp.text:
                    self.likes += 1
                    
            return
        except Exception as e:
            print(e)
            self.errors += 1
            return
    def retweetme(self,client : httpx.Client ,cookies,headers,proxy):
        try:
          
      
            resp = client.post('https://twitter.com/i/api/graphql/ojPdsZsimiJrUGLR1sjUtA/CreateRetweet',json={"variables":{"tweet_id":self.tweet_id,"dark_request":False},"queryId":"ojPdsZsimiJrUGLR1sjUtA"},cookies=cookies,headers=headers)
            if resp.status_code == 200:
                self.retweets+=1
                
        except:
            self.errors += 1
            return
    def consoleUpdater(self):
        while True:
            ctypes.windll.kernel32.SetConsoleTitleW(f"Twitter Bot | Retweets : {self.retweets} | Likes : {self.likes} | Replies : {self.replies} | Errors : {self.errors} ")
    def reply(self,token):
        try:

            proxy = getProxy()
            mct0 = ''
            client = tls_client.Session(client_identifier='chrome112',random_tls_extension_order=True)
            cookies = {
            'auth_token': token
        }
            headers =  {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'origin': 'https://twitter.com',
            'referer': 'https://twitter.com/settings/profile',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'en'
        }
        
            ct0_response = client.post('https://twitter.com/i/api/1.1/account/update_profile.json', cookies=cookies, headers=headers,proxy=proxy)
            mct0 = ct0_response.cookies['ct0']
            cookies['ct0'] = mct0
            headers['x-csrf-token'] = mct0
            headers["content-type"] = "application/json"
            replyc = random.choice(self.replies_list)
            resp = client.post("https://twitter.com/i/api/graphql/C2dcvh7H69JALtomErxWlA/CheckTweetForNudge",headers=headers,cookies=cookies,json={"variables":{"tweet_text":replyc,"tweet_type":"Reply","in_reply_to_tweet_id":self.tweet_id,"conversation_id":self.tweet_id,"enable_nudge_testing_keyword":False},"features":{"standardized_nudges_toxicity":False},"queryId":"C2dcvh7H69JALtomErxWlA"},proxy=proxy)
        #reply
            resp = client.post('https://twitter.com/i/api/graphql/GUFG748vuvmewdXbB5uPKg/CreateTweet',headers=headers,cookies=cookies,json={"variables":{"tweet_text":replyc,"reply":{"in_reply_to_tweet_id":self.tweet_id,"exclude_reply_user_ids":[]},"dark_request":False,"media":{"media_entities":[],"possibly_sensitive":False},"semantic_annotation_ids":[]},"features":{"tweetypie_unmention_optimization_enabled":True,"responsive_web_edit_tweet_api_enabled":True,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":True,"view_counts_everywhere_api_enabled":True,"longform_notetweets_consumption_enabled":True,"tweet_awards_web_tipping_enabled":False,"longform_notetweets_rich_text_read_enabled":True,"longform_notetweets_inline_media_enabled":False,"responsive_web_graphql_exclude_directive_enabled":True,"verified_phone_label_enabled":True,"freedom_of_speech_not_reach_fetch_enabled":False,"standardized_nudges_misinfo":True,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":False,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":False,"responsive_web_graphql_timeline_navigation_enabled":True,"responsive_web_enhance_cards_enabled":False},"queryId":"GUFG748vuvmewdXbB5uPKg"},proxy=proxy)
            if resp.status_code == 200:
                with self.lock:
                    print(f"{Fore.RED}INFO : {Fore.RESET}[{Fore.CYAN}REPLIED{Fore.RESET}] - {Fore.LIGHTBLACK_EX}{token}{Fore.RESET}")
            self.replies+=1
            ctypes.windll.kernel32.SetConsoleTitleW(f"Twitter Bot | Succes : {self.succes} | Errors : {self.errors} | Tweet : {self.tweet_id} | Replies : {self.replies} | Dev: @ratelimits")
            return
        except:
            self.errors += 1
            ctypes.windll.kernel32.SetConsoleTitleW(f"Twitter Bot | Succes : {self.succes} | Errors : {self.errors} | Tweet : {self.tweet_id} | Replies : {self.replies} | Dev: @ratelimits")
            return

if __name__ == "__main__":
    twitter = Twtitter()
    twitter.tweet_and_return_id()