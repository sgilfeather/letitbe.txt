import requests
import re
import string
import random
import json
import time

from bs4 import BeautifulSoup


# scrape_lyric_text()
# purpose:    converts soup "div" tag with div tags of  lyrics into plaintext
#             block of lyrics lines separated by "\n"
# parameters: bs4 "div" tag object containing lyrics 
# returns:    plaintext lyric string

def get_lyric_text(root_soup):	
    #replace all breaks with \n in order to break up lines
    for br in root_soup.find_all("br"):
        br.replace_with("\n")

    final_lyrics = root_soup.text
    #remove any verse labels, which are placed inside square brackets
    final_lyrics = re.sub("\[.*\]", "", final_lyrics)

    #remove remaining non-lyric text at end of page content
    if final_lyrics.endswith("EmbedShare URLCopyEmbedCopy"):
        final_lyrics = final_lyrics[:-len("EmbedShare URLCopyEmbedCopy")]
    return final_lyrics


# get_page_songs()
# purpose:    finds all songs from page of artist song search. returns text
# 	          block of concatenated lyrics from all songs
# parameters: dict "content" containing list, "songs" with dict entries for
#             song information
# returns:    plaintext string block of all lyrics

def get_page_songs(song_set):
    all_page_text = ""
    curr_title = "_" #placeholder to offset first title
    songlyric_list = []

    for song in song_set:
        t = song["title"].lower().strip()

        # skip songs where beatles aren't the main artist, and skips
        # remastered and multi-take duplicates of the same song
        if song["primary_artist"]["id"] == 586 and not t.startswith(curr_title):
            print(song["title"])
            song_page = requests.get(song["url"])
            song_soup = BeautifulSoup(song_page.content, "html.parser")
            lyric_soup = song_soup.find(id="lyrics-root")
			
            #song has lyrics; otherwise, doesn't have "lyric-root" div
            if type(lyric_soup) != type(None):
                #get plaintext of lyrics, and add to list of song lyrics 
                songlyric_list.append(get_lyric_text(lyric_soup))
            
            # stripped title of song, without version in parentheses
            curr_title = song["title"].lower().strip()
            paren = song["title"].find("(")
            if paren != -1:
                curr_title = song["title"][:paren].lower().strip()
    
    all_page_text = '\n'.join(songlyric_list)
    return all_page_text

#######################################

# main
start_time = time.time()

client_token = "KgllR-0qdOfJ4KHTD_s_nHMRhbCiSnzmbWCeA5J1C5QJtvBVuao9z" \
               "i2aCOUGKGwU"
songs_url = "https://api.genius.com/artists/586/songs?per_page=50&page={}"
auth_header = ("Bearer ", client_token)

response = requests.get(songs_url.format("1"), 
           headers = { "Authorization":''.join(auth_header) })
song_set = response.json()["response"]["songs"]

count = 1
while len(song_set) != 0:
    if count != 1:
        response = requests.get(songs_url.format(str(count)), 
                   headers = { "Authorization":''.join(auth_header) })
        song_set = response.json()["response"]["songs"]
    page_text = get_page_songs(song_set)
	
    #create new file for scraped lyrics with name corresponding to song page
    new_filename = "./lyric_files/" + str(count) + "_page.txt"
    with open(new_filename, 'w') as f:
        f.write(page_text)
    count = count + 1

print("Process finished --- {} seconds ---".format(time.time() - start_time))
