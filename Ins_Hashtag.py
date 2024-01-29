# File Name: Ins_Hashtag.py
# C1_Group3
# Name: Xinyi Yang, Yuetian Sun, Yi Guo, Man Luo, Yining Lu
# Andrew ID: xinyiy2, yuetians, yiguo, manluo, yininglu
# import from : (None)
# imported by: driver.py

"""
This file is used to go over pages of predefined or user-defined hashtags on Instagram,
gathering relevant infos such as num_of_likes, post_time, creator_link, hashtags from 
individual posts, then compiling all gathered info for meta analysis. The result will be 
a dataframe saved to local directory with industry/keyword prepended in name. Visualizations
include trimmed, tabulated dataframe view, Wordcloud of popular hashtags, by-hashtag visuals,
and creator ranking scatterplot (num_followers vs num_likes). 
"""

# Sample commands used to install relevant packages
#!pip install selenium
#!pip install webdriver_manager
#!pip install wordcloud
#!pip install difflib
#!pip install tabulate

import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from datetime import datetime

from collections import Counter
from itertools import chain
from random import shuffle
from random import sample
from random import randint

from webdriver_manager.chrome import ChromeDriverManager
from wordcloud import WordCloud, STOPWORDS
from difflib import SequenceMatcher
from tabulate import tabulate


### Fixed Variables (tags to use for scraping)
industry_names = ['food', 'baking', 'animals', 'beauty', 'design', 'nature', 'sports']
food_tags = ['#food', '#foodie', '#culinaryarts', '#michelinstar', '#gourmet', '#streetfood', '#chefstable', '#yummy', '#chefsofinstagram', '#delicious',
            '#finedining', '#homecooking', '#recipe', '#foodphotography', '#simplerecipes', '#foodporn', '#foodstagram', '#foodoftheday', '#foodblogger', '#comfortfood']

bakery_tags = ['#patisserie', '#pastry', "#ganache", "#chocolate", "#pâtisserie", "#gourmandise", '#donuts', '#sweet', '#pastrychef', '#bakinglove',
              '#dessert', '#baking', '#fallbaking', '#puffpastry', '#cake', '#pastryart', '#bakestagram', '#cream', '#madeleines', '#dessertporn']
animal_tags = ['#wildlife', '#wildlifephotography', '#wildanimals', '#netgeo', '#cuteanimals', '#animalsofinstagram', '#cutepetclub', '#animalplanet', '#zoo', '#zoophotography', 
               '#pet', '#petsofinstagram', '#kitty', '#dogs', '#puppy', '#petstagram', '#petlover', '#kittycat', '#catsofinstagram', '#dogsofinstagram']
beaut_tags = ['#fashion', '#fashionstyle', '#ootd', '#streetstyle', '#outfit', '#outfitinspiration', '#clothing', '#makeup', '#makeuptutorial', '#makeupartist', 
             '#stylish', '#styleblogger', '#fashionnova', '#fitness', '#fitnessbody', '#beautytips', '#classy', '#celebrity', '#model', '#casual']
design_tags = ['#DIY','#handmade','#design','#decoration','#crafts','#diyprojects','#diyideas','#handcraft','#artwork','#finearts']
landscape_tags = ['#naturephotography','#landscape','#naturelovers','#travelphotography','#landscapelovers','#landscapecaptures','#naturecaptures','#naturephoto','#naturegram','#nature_perfection']
sport_tags = ['#extremesports','#extremesportsphotography','#sports','#sportsphotography','#sportsnews','#sportsbikelife','#sportsperformance','#sportslife','#sportsday','#sportsphoto']
all_tags = [food_tags, bakery_tags, animal_tags, beaut_tags, design_tags, landscape_tags, sport_tags]

# logs into our Instagram account to start webscraping driver
def login():
    #THIS PRETTY MUCH TELLS THE WEB BROWSER WHICH WEBSITE TO GO TO
    driver.get('https://www.instagram.com/')
    print("Hopped on Instagram!")
    print("Waiting to login")
    #login
    time.sleep(3.5)

    username=driver.find_element(By.CSS_SELECTOR, "input[name='username']")
    password=driver.find_element(By.CSS_SELECTOR,"input[name='password']")

    username.clear()
    password.clear()

    
    #username.send_keys("DFP_F22C3_InstaHit_2")
    #username.send_keys("DFP_F22C3_InstaHit") # account bkup 1
    username.send_keys("dfp_instahit_demo") # account bkup 2

    password.send_keys("DFP_95888_C3")
    login = driver.find_element(By.CSS_SELECTOR,"button[type='submit']").click()
    print("Login info sent, logging in...")
    
    #save your login info?
    time.sleep(10)
    try:
        print("Closing unncessary prompt windows #1")
        notnow = driver.find_element(By.XPATH,"//button[contains(text(), 'Not Now')]").click()
    except:
        pass
    #turn on notif
    time.sleep(1)
    try:
        print("Closing unncessary prompt windows #2")
        notnow2 = driver.find_element(By.XPATH,"//button[contains(text(), 'Not Now')]").click()
    except:
        pass


# driver function that utilizes the navigation and scrape functions.

def gather_info(curr_hashtag):
    navigate_to(curr_hashtag)
    df = scrape()
    df['under'] = curr_hashtag
    df = df[["#Likes"] + ["under"] + df.columns[1:-1].tolist()]
    return df

# navigate the driver to the explore page of a specified hashtag on Instagram
def navigate_to(curr_hashtag):
    print(f"searching {curr_hashtag}...")
    time.sleep(1)
    
    # instagram update (left search bar hides search field, Oct 12 update) fix:
    open_search_bar = driver.find_elements(By.XPATH, "//*[name()='svg' and @aria-label='Search']")
    if open_search_bar:
        open_search_bar[0].click()

    #searchbox
    searchbox=driver.find_element(By.CSS_SELECTOR, "input[placeholder='Search']")
    
    time.sleep(0.5)
    #remove previously entered/leftover words
    searchbox.send_keys(Keys.COMMAND + "a")
    searchbox.send_keys(Keys.BACK_SPACE)

    #enters the to-be-searched hashtag
    searchbox.send_keys(curr_hashtag)
    time.sleep(4)

    #select the top fetched result and press it (navigate to it)
    searchbox.send_keys(Keys.ENTER)
    time.sleep(1)
    searchbox.send_keys(Keys.ENTER)
    
    time.sleep(5) # wait for page loading
    
    # click outside of search to reset mouse location to avoid wrong focus location
    el=driver.find_element(By.XPATH, "//button[contains(string(), 'Follow')]")

    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(el, -50, 50)
    action.click()

# clicks the next button on a post to its next img if next img exists
def next_page(driver, img_links, curr_imgs):
    try:
        driver.find_element(By.XPATH,"//button[@aria-label='Next']").click()
        time.sleep(0.5)
        #prev_post = driver.find_element(By.CSS_SELECTOR,"button[class=' _aahh']").click()
        return True

    except: #end of post reached
        img_links.append(curr_imgs)
        print("end of post reached!")
        return False 

# checks if the current window of a post is video (i.e., not static img)
def check_video(driver):
    time.sleep(0.5)
    if driver.find_elements(By.XPATH, "//*[name()='svg' and @aria-label='Audo is muted.']"): #video, skip
        print("found video, skipping")
        return True
    return False
    
# scrape all necessary info from the current window and return in df
def scrape(post_start=0, post_end=9):
    time.sleep(2)
    all_posts = driver.find_elements(By.CLASS_NAME, '_aagu')
    time.sleep(0.5)

    # open each post from search result
    likes = []
    i_post_times = []
    num_comments = []
    img_links = []
    creator_list = []
    all_hashtags = []
    post_mentioned_accounts_url = []
    mentioned_accounts_url = []
    post_links = [l.get_attribute('href') for l in driver.find_elements(By.XPATH, "//*[name()='a' and @role='link']")[post_start:post_end]]


    for i,post in enumerate(all_posts[post_start:post_end]):
        # open the ith post
        post.click()
        time.sleep(0.5)
        
        # mark start of post
        is_first = True
        
        # check for page loading
        wait = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,'//span[@class="_aap6 _aap7 _aap8"]/a')))
        
        curr_imgs = []
        while(True):
            next_post = False
            next_pic = False
            
            #################### scrape each image's relevant info ####################
            # print("===================================")
            
            for _ in range(4): #check twice since sometimes 1st time loading not complete
                if check_video(driver): #check if curr is a video
                    if not next_page(driver, img_links, curr_imgs): # go to next page if possible
                        next_post = True #end of post reached
                        break 
                    else:
                        next_pic = True
                else:
                    # print("=== re-verifying if it is video ===")
                    pass
            
            if next_post:
                break
            
            if next_pic:
                continue
                
            if is_first:

                # 1st page takes first, all else takes 2nd instance of _acaz
                try: 
                    driver.find_elements(By.CLASS_NAME, '_acaz')[0].find_elements(By.TAG_NAME, 'img')
                    curr_imgs.append(driver.find_elements(By.CLASS_NAME, '_acaz')[0].find_element(By.TAG_NAME, 'img').get_attribute("src"))
                    is_first = False

                # 
                except: 
                    # has only 1 pic, get current thumbnail pic
                    img_links.append([driver.find_elements(By.CLASS_NAME, '_aagv')[i+post_start].find_element(By.TAG_NAME, 'img').get_attribute("src")]) 
                    #print("single image post!")
                    break


            else: #not 1st image in post, grab middle link
                if driver.find_elements(By.CLASS_NAME, '_acaz'):
                    curr_imgs.append(driver.find_elements(By.CLASS_NAME, '_acaz')[1].find_element(By.TAG_NAME, 'img').get_attribute("src"))
            
            if not next_page(driver, img_links, curr_imgs):
                break
        
        #################### other metadata aside from image ####################
        # get creator info
        creator = driver.find_element(By.XPATH,'//span[@class="_aap6 _aap7 _aap8"]/a').get_attribute('href')
        creator_list.append(creator)

        # num of likes/views & time since post
        if driver.find_elements(By.XPATH, "//div[@class='_aacl _aaco _aacw _aacx _aada _aade']"):
                post_Like = driver.find_element(By.XPATH, "//div[@class='_aacl _aaco _aacw _aacx _aada _aade']")
                likes.append(post_Like.text.replace(',',''))

        else:
            likes.append('')

        # post time
        i_post_times.append(driver.find_element(By.XPATH, "//time[@class='_aaqe']").text)

        # hashtags 
        if driver.find_elements(By.XPATH, "//*[name()='span' and @class='_aacl _aaco _aacu _aacx _aad7 _aade']"):
            hashtag_txt = driver.find_element(By.XPATH, "//*[name()='span' and @class='_aacl _aaco _aacu _aacx _aad7 _aade']").text
            tmp_hashtags = re.findall("#\S+", hashtag_txt)
            all_hashtags.append(tmp_hashtags)
        
        else: #add empty if not found
            all_hashtags.append([])
            mentioned_accounts.append([])
            
        #Returning all the links for the accounts which has been mentioned in the post as well as the comments
        wait = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//span[@class="_aap6 _aap7 _aap8"]/a')))
        mentioned_account = driver.find_elements(By.XPATH, "//span[@class='_aacl _aaco _aacu _aacx _aad7 _aade']/a")
        for account in mentioned_account:
            single_account_url = account.get_attribute('href')
            if single_account_url.startswith('https://www.instagram.com/explore/') == False:
                post_mentioned_accounts_url.append(single_account_url)
        mentioned_accounts_url.append(post_mentioned_accounts_url)

        ############### close current page ###############

        driver.find_element(By.XPATH, "//*[name()='svg' and @aria-label='Close']").click()
    
    img_df = pd.DataFrame(np.array(list(zip(creator_list, likes, i_post_times, post_links, img_links)), dtype = "object"),
                   columns=['Creator_link', '#Likes', 'Post_time', 'Post_link', 'Img_links'])
    img_df["hashtag"] = all_hashtags
    img_df["Access_time"] = datetime.now().strftime("%m/%d/%y %H:%M:%S")[:-1] + str(randint(1,9))
    try:
        img_df["Creator_name"]=creator_info(creator_list)['Creator_Name']
        img_df["Creator_Followers"]= creator_info(creator_list)['#Followers']
    except:
        img_df["Creator_name"]= np.nan
        img_df["Creator_Followers"]= np.nan
    img_df["mentioned_accounts_url"]= mentioned_accounts_url
    img_df = img_df[['#Likes','Post_time','Access_time','Post_link', 'Img_links', \
                     'hashtag', 'Creator_name','Creator_Followers','Creator_link','mentioned_accounts_url']]
    
    return img_df

# check if the user entered keyword is valid
def validate_keyword(keyword):
    if keyword is None:
        return False

    if not keyword:
        print("Keyword cannot be empty")
        return False
    
    if len(keyword.split()) != 1:
        print("Please enter a single word")
        return False

    return True

########################################################################
## Driver functions for scraping

# search by a pre-specified industry using user's choice
def industry_search(choice):
    indx = int(choice)
    if indx not in list(range(1, 8)):
        raise ValueError("something is wrong about the industry index conversion!")

    industry = all_tags[indx-1]

    curr_hashtag = industry[0]
    all_df = gather_info(curr_hashtag)

    for tag in industry[1:]:
        new_df = gather_info(tag)
        all_df = pd.concat([all_df, new_df])


    all_df.reset_index(inplace = True, drop = True)
    all_df.to_csv(f"{industry_names[indx-1]}.csv", index = False)
    return all_df   

# search using a user specified keyword    
def user_specified_search(keyword):
    curr_hashtag = '#' + keyword
    all_df = gather_info(curr_hashtag)
    all_hashtags = all_df.hashtag.tolist()

    cnt2tags = grp_hashtag_by_freq(all_hashtags)
    clean_dict(cnt2tags, curr_hashtag)

    reduced_tags_ranked = reduce_tags(cnt2tags, max_len = 2, general = False)
    reduced_tags_gen = reduce_tags(cnt2tags, max_len = 2, general = True)
    reduced_tags = list(set(reduced_tags_ranked) | set(reduced_tags_gen))

    print(f"Reduced set of hashtags for expansion: {reduced_tags}")

    for tag in reduced_tags:
        new_df = gather_info(tag)
        all_df = pd.concat([all_df, new_df])


    all_df.reset_index(inplace = True, drop = True)
    all_df.to_csv(f"{keyword}.csv", index = False)
    return all_df
    
########################################################################
## Visualization/ analysis functions

# draw wordcloud for a compiled df's gathered hashtags
# df should be obtained from a search func above or previously downloaded (in option c and d)
def hashtag_WC(all_related_hashtags):
    key_words = all_related_hashtags

    # clr template
    avail_clrs = ["paleturquoise", "plum", "lightgreen", "salmon", "cornflowerblue", "navajowhite"]
    clr = np.random.choice(avail_clrs, 1, replace = False)[0]

    title = "Used hashtags under related posts"

    # wrdcld generation
    wrds_4_cld = " ".join(key_words)
    wordcloud = WordCloud(width = 1000, height = 800, random_state=1999, 
                          background_color= clr, colormap='Set1', max_words = 120,
                          collocations=True, stopwords = STOPWORDS).generate(wrds_4_cld)


    # plot WordCloud                       
    fig = plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad = 0)
    #plt.title(f"{label}-label keywords")
    fig.suptitle(title, fontsize=20, fontname='Comic Sans MS')
    plt.show()

# find the longest overlap of two strings
def get_common_words(string1, string2):
    string1 = string1.lower()
    string2 = string2.lower()
    
    if string1 == string2:
        return '' #skip duplicates
    
    match = SequenceMatcher(None, string1, string2).find_longest_match()
    if match.size < 3:
        return ''
    return string1[match.a:match.a + match.size]

# uses the 1st, middle and last hashtag in a lists to condense hashtag lists
# the condensed results are just max len overlaps for the selected hashtag w.r.t. all other hashtags
def condense_post_hashtag(l_hashtag):
    if not l_hashtag:
        return
    
    condensed_hashtags = []
    n = len(l_hashtag)
    mid = (n-1) // 2
    
    for s in l_hashtag:
        overlap_strt = get_common_words(l_hashtag[0][1:], s[1:])
        overlap_mid  = get_common_words(l_hashtag[mid][1:], s[1:])
        overlap_end  = get_common_words(l_hashtag[-1][1:], s[1:])
    
        condensed_hashtags.extend([overlap_strt, overlap_mid, overlap_end])
    return condensed_hashtags

# similar to above function but randomly samples 3 hashtags instead of using top, middle and bottom hashtags
# can provide more diverse results if run multiple times but usually less well than the above
def r_condense_post_hashtag(l_hashtag):
    if not l_hashtag:
        return
    
    condensed_hashtags = []
    n = len(l_hashtag)

    if n < 3:
        print("sample < 3 records, defaulting to nonrandom anchors.")
        return condense_post_hashtag(l_hashtag)
    
    inds = sample(range(n), 3)
    for s in l_hashtag:
        overlap_strt = get_common_words(l_hashtag[inds[0]][1:], s[1:])
        overlap_mid  = get_common_words(l_hashtag[inds[1]][1:], s[1:])
        overlap_end  = get_common_words(l_hashtag[inds[2]][1:], s[1:])
    
        condensed_hashtags.extend([overlap_strt, overlap_mid, overlap_end])
    return condensed_hashtags

# condense hashtags in a list of [lists containng hashtags]
def get_hashtag_overlaps_2D(L_hashtags, random = False):
    tag_overlaps = []
    ### if randomly select anchors ### 
    if random:
        for l_hashtag in L_hashtags:
            tag_overlaps.extend(r_condense_post_hashtag(l_hashtag))
        return Counter(tag_overlaps)

    ### Fixed anchors (start, mid, end) ###
    for l_hashtag in L_hashtags:
        tag_overlaps.extend(condense_post_hashtag(l_hashtag))
    return Counter(tag_overlaps)

# condense hashtags in a list
def get_hashtag_overlaps_1D(L_hashtags, random = False):
    ### if randomly select anchors ### 
    if random:
        return Counter(r_condense_post_hashtag(L_hashtags))

    ### Fixed anchors (start, mid, end) ###
    return Counter(condense_post_hashtag(L_hashtags))

# groups all hashtags by freq of its occurence in the list
def grp_hashtag_by_freq(all_hashtags):
    hashtag_collection = []
    hashtags_count = {}
    
    for tags in all_hashtags:
        for tag in tags:
            hashtag_collection.append(tag) #append tags
    
    # count tags (dict: tag:freq)
    for i in hashtag_collection:
        if i in hashtags_count.keys():
            hashtags_count[i] +=1
        else:
            hashtags_count[i] = 1
    
    # reverse dict mapping freq:tag
    flipped = {}
    for key, value in hashtags_count.items():
        if value not in flipped.keys():
            flipped[value] = [key]
        else:
            flipped[value].append(key)
    for i in sorted(flipped.keys(),reverse = True):
        if i > 1:
            print(str(i), 'counts:', flipped[i])
            
    return flipped

# removes the used hashtag from the gathered hashtag results to avoid duplicates
def clean_dict(cnt2tags, curr_hashtag):
    for k in sorted(cnt2tags.keys(),reverse = True):
        if curr_hashtag in cnt2tags[k]:
            #print(f"found match at count = {k}")
            cnt2tags[k].remove(curr_hashtag)
            if not cnt2tags[k]: #if becomes empty
                del cnt2tags[k]
    return

# reduces the number of hashtags from all hashtags in all relevants posts
# narrow: return top freq results
# general: get reduced from each count (get distinct overlaps first, then take unique from each overlap)
def reduce_tags(cnt2tags, max_len = 10, general = False):
    if general:
        results = reduce_tags_general(cnt2tags, max_len)
    else:
        results = reduce_tags_narrow(cnt2tags, max_len)
    
    if max_len is not None:
        #if len(set(results)) < max_len:
        #    print(f"found only {len(set(results))} distinct hashtags")
        return results[:max_len]
    return results
    

def reduce_tags_narrow(cnt2tags, max_len = 10):
    reduced = []
    for i in sorted(cnt2tags.keys(), reverse = True):
        reduced.extend(cnt2tags[i])
        if len(reduced) > max_len:
            break
    return reduced

def reduce_tags_general(cnt2tags, max_len = 10):
    reduced = []
    for i in sorted(cnt2tags.keys(), reverse = True):
        ############## Early termination ##############
        if i < 2: #skip the 1 cnts
            break

        if len(reduced) > max_len: #have enough tags already
            break

        to_process = cnt2tags[i]
        
        if len(to_process) <= 2:
            reduced.extend(to_process[:2])
            continue

        if len(to_process) < 10: #only reduce if we have >10 tags in curr grp, otherwise sample 2
            reduced.extend(sample(to_process, 2))
            continue
        
        ################# Get current tags (of same cnt) overlaps ###############
        overlaps = get_hashtag_overlaps_1D(to_process, random = False)

        if len(overlaps) == 1: #if no overlap, keep all curr tags
            reduced.extend(to_process)
            continue

        overlap = [k for k in overlaps.keys() if len(k) > 3]
        overlap = sorted(overlap, key = lambda x: -len(x))

        #############################################################################
        # get first word containing the overlap pieces
        loop_cnt = 0
        kept_tags = []
        have_enough = False
        
        while len(set(kept_tags)) < 3 and loop_cnt < 3: #try to get diverse results
            for part in overlap: #part is a piece of overlap, not necc a whole word
                if have_enough:
                    break 
                    
                shuffle(overlap)
                for tag in to_process: # get more general results
                    if len(set(kept_tags)) > 5: # if we have enough results from this cnt already
                        have_enough = True
                        break
                        
                    if part in tag:
                        kept_tags.append(tag)
                        break #search next subword
            loop_cnt += 1
            reduced += list(set(kept_tags))

    return reduced


def sorted_scrape(df):
    postlikes = []
    position_list = []
    index_list = []
    likes_followers_d = df.groupby('#Likes')['Creator_Followers'].apply(list).to_dict()
    
    for i in likes_followers_d.keys():
        number_likes = i.split(' ')[0]
        if ',' in number_likes:
            postlikes.append(int(number_likes.replace(',','')))
        elif i == 'others':
            i = 0
        else:
            postlikes.append(int(number_likes))
    sorted_postlikes = sorted(postlikes,reverse = True)
    
    for i in sorted_postlikes:
        position = df.index[df['#Likes']== str(i) + ' likes']
        position_list.append(list(position))
        
    for i in position_list:
        for y in i:  
            index_list.append(y)
            
    sorted_df = df.loc[index_list]
    return sorted_df


def creator_info(creator_list):
    followers = []
    following = []
    posts = []
    creator_name = []

    for creator in creator_list:
        driver.get(creator)
        header = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.TAG_NAME, "header")))
        Post = header.find_element(By.XPATH,"//div[contains(text(),' posts')]").text.replace('posts','').replace(',','').strip()
        Following = header.find_element(By.XPATH,"//div[contains(text(),' following')]").text.replace('following','').replace(',','').strip()
        Follower = header.find_element(By.XPATH,"//div[contains(text(),' followers')]").text.replace('followers','').replace(',','').strip()
        try:
            Name = driver.find_element(By.XPATH, "//h2[@class='_aacl _aacs _aact _aacx _aada']").text
        except:
            Name = driver.find_element(By.XPATH, "//h1[@class='_aacl _aacs _aact _aacx _aada']").text
        posts.append(Post)
        followers.append(Follower)
        following.append(Following)
        creator_name.append(Name)

    creator_profiles = pd.DataFrame(np.array(list(zip(creator_name, followers, following, posts)), dtype = "object"),
                       columns=['Creator_Name','#Followers', '#Following', '#Posts'])
    return creator_profiles


def all_mentioned_url_under_hashtag(df):
    all_mentioned_urls = []
    for i in list(df['mentioned_accounts_url']):
        for y in i:
            all_mentioned_urls.append(y)
    return list(set(all_mentioned_urls))


# Mentioned Accounts Profiles - sorted based on number of followers
def mentioned_accounts_info(all_mentioned_urls):
    mentioned_profiles = {}
    creator_dictionary = {}
    ordered_followers = []
    sorted_creators = []

    for mentioned_creator in all_mentioned_urls:
        driver.get(mentioned_creator)
        try:
            header = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.TAG_NAME, "header")))
            Post = header.find_element(By.XPATH, "//div[contains(text(),' posts')]").text.replace('posts', '').replace(',',
                                                                                                                       '').strip()
            Following = header.find_element(By.XPATH, "//div[contains(text(),' following')]").text.replace('following',
                                                                                                           '').replace(',',
                                                                                                                       '').strip()
            Follower = header.find_element(By.XPATH, "//div[contains(text(),' followers')]").text.replace('followers',
                                                                                                          '').replace(',',
                                                                                                                      '').strip()
            if Follower.endswith('M'):
                Follower = int(float(Follower.split('M')[0]) * 1000000)
            elif Follower.endswith('K'):
                Follower = int(float(Follower.split('K')[0]) * 1000)
            elif ',' in Follower:
                Follower = int(Follower.replace(',', ''))
            else:
                Follower = int(Follower)

            try:
                Name = driver.find_element(By.XPATH, "//h2[@class='_aacl _aacs _aact _aacx _aada']").text
            except:
                Name = driver.find_element(By.XPATH, "//h1[@class='_aacl _aacs _aact _aacx _aada']").text
            creator_dictionary[Follower] = [Name, Follower, Following, Post]
        except:
            print("Instagram is currently having difficulties. The page is not available.")

    for i in sorted(creator_dictionary.keys(), reverse=True):
        ordered_followers.append(i)

    for i in ordered_followers:
        sorted_creators.append(creator_dictionary[i])
    mentioned_profiles = pd.DataFrame(np.array(sorted_creators), dtype="object",
                                      columns=['Creator_Name', '#Followers', '#Following', '#Posts'])

    return mentioned_profiles


#create a scatterplot to show the relationship between number of likes and number of followers
#for candidate posts under a single hashtag
def scatterplot_posts_suggestion(df):
    postlikes = []
    likes_followers_d = df.groupby('#Likes')['Creator_Followers'].apply(list).to_dict()

    #find number of likes for posts
    for i in likes_followers_d.keys():
        number_likes = i.split(' ')[0]
        if ',' in number_likes:
            postlikes.append(int(number_likes.replace(',','')))
        elif i == 'others':
            i = 0
        else:
            postlikes.append(int(number_likes))

    #small to big post likes
    stb_position_list = []
    stb_index_list = []
    stb_num_likes = []
    stb_num_followers = []
    for i in sorted(postlikes):
        position = df.index[df['#Likes']== str(i) + ' likes']
        stb_position_list.append(list(position))
    for i in stb_position_list:
        for y in i:
            stb_index_list.append(y)


    stb_sorted_df = df.loc[stb_index_list]
    data_postlikes_followers = stb_sorted_df.loc[:,['#Likes','Creator_Followers']]
    for i in data_postlikes_followers.loc[:,'#Likes']:
        stb_num_likes.append(int(i.split(' ')[0]))
    for i in data_postlikes_followers.loc[:,'Creator_Followers']:
        i = str(i)
        if 'K' in i:
            stb_num_followers.append(int(float(i.split('K')[0])*1000))
        elif 'M' in i:
            stb_num_followers.append(int(float(i.split('M')[0])*1000000))
        elif ','in i:
            stb_num_followers.append(int(i.split(',')[0])*1000+int(i.split(',')[1]))
        elif i == 'nan':
            stb_num_followers.append(0)
        else:
            stb_num_followers.append(int(i))

    #Scatterplot of post like vs total follower for candidate posts under one hashtag
    plt.style.use('_mpl-gallery')
    annotations = []
    creator_name_list = stb_sorted_df.loc[:,['Creator_name']].values.tolist()

    for i in creator_name_list:
        for y in i:
            annotations.append(y)

    fig, ax = plt.subplots(figsize=(8, 6),constrained_layout=True)
    ax.scatter(stb_num_followers, stb_num_likes, s= stb_num_likes,c=stb_num_followers, cmap='Wistia')
    ax.set_xlabel('Number of followers')
    ax.set_ylabel('Number of likes')
    ax.set_title('Number of Likes VS Number of Followers')
    for i, label in enumerate(annotations):
        plt.text(stb_num_followers[i], stb_num_likes[i],label)
    plt.show()

# in saved .csv the list are treated as '[a,b,c]' which needs proper conversion back to list
# converts such columns (e.g., links, hashtag, mentioned names) bk to list for proper data format
def castToList(df):
    df["Img_links"] = df['Img_links'].apply(lambda x: re.sub("[\[\]']", "", x).split(', '))
    df["hashtag"] = df['hashtag'].apply(lambda x: re.sub("[\[\]']", "", x).split(', '))
    df['mentioned_accounts_url'] = df['mentioned_accounts_url'].apply(lambda x: re.sub("[\[\]']", "", x).split(', '))
    return

# calculates number of hours passed from a timedelta object
def getHour(diff):
    return diff.days * 24 + diff.seconds // 3600
    
# parses the date columns in our data to calculate num of hours passed of ea post's post time upto now
def parseNgetHour(t, curr):
    diff = datetime.now() - datetime.strptime(curr, '%x %X') 

    if 'MINUTE' in t: # like '18 MINUTES AGO'
        return getHour(diff)

    if 'HOUR' in t: # like '11 HOURS AGO', requires diff of curr too
        return int(t.split()[0]) + getHour(diff) 

    if 'DAY' in t: # like '1 DAY AGO', requires diff of curr too
        return int(t.split()[0]) * 24 + getHour(diff)

    if ',' in t: # more than 7 days ago, like 'MAY 30, 2019'
        diff = (datetime.now() - datetime.strptime(t, '%B %d, %Y'))
        return getHour(diff)
    
    # like 'MAY 19'
    t = t + ', ' + str(datetime.now().year)
    diff = (datetime.now() - datetime.strptime(t, '%B %d, %Y'))
    return getHour(diff)
    
    
# displays the content density plot, showcasing avg no of pics per post under ea relevant hashtag    
def cnt_visual(df):
    print("#############################################################################")
    print("Showing hashtag content density by avg num of pics under a post for ea. hashtag")
    sizeOfHashtag = df.groupby(["under"]).size() #how many posts searched in ea hashtag
    tmp_df = df.explode('Img_links').reset_index(drop=True) 
    sizeOfPost = tmp_df.groupby(["under"]).size() #how many pic under each post per hashtag
    data = sizeOfPost.divide(sizeOfHashtag, fill_value=0) #avg num of pics per post under ea hashtag
    plt.figure(figsize=(8, 6), constrained_layout=True)
    my_cmap = plt.cm.get_cmap('GnBu')
    data_color = [x / max(data) for x in data]
    colors = my_cmap(data_color)
    plt.bar(data.index, data.values, color = colors)
    plt.xticks(rotation=90)
    plt.xlabel("Hashtag")
    plt.ylabel("Number of pictures per post")
    plt.title("Avg. Number of pictures per post under each hashtag")
    plt.show()

# displays the content quality plot, showcasing avg no of likes per post under ea relevant hashtag        
def likes_visual(df):
    print("#############################################################################")
    print("Showing hashtag quality by avg num of likes under a post for ea. hashtag")
    # extract likes, sub invalid with 0 to avoid calculation error
    tmp_df = df[["under"]].copy()
    df["#Likes"].replace('', np.nan, inplace = True)
    all_likes = ' '.join(df["#Likes"].fillna('others').tolist())
    all_likes = all_likes.replace("others", "0 likes").split(" likes")
    all_likes = [int(l) for l in all_likes if l.strip()]
    assert len(all_likes) == len(df)    
    
    tmp_df["likes"] = all_likes
    data = tmp_df.groupby(["under"]).agg('mean').likes

    plt.figure(figsize=(8, 6),constrained_layout=True)
    my_cmap = plt.cm.get_cmap('GnBu')
    data_color = [x / max(data) for x in data]
    colors = my_cmap(data_color)
    plt.bar(data.index, data.values, color = colors)
    plt.xticks(rotation=90)
    plt.xlabel("Hashtag")
    plt.ylabel("Number of likes per post")
    plt.title("Avg. Number of likes per post under each hashtag")
    plt.show()
    
    print("#############################################################################")
    print("Showing hashtag activeness by avg likes gained per hour for ea. hashtag")
    active_visual(df, data)

# displays the content activeness plot, showcasing avg no of likes gained per hour for a post under ea relevant hashtag
def active_visual(df, avg_likes):
    tmp_df = df[["under"]].copy()
    tmp_df["Hours_Ago"] = df.apply(lambda x: parseNgetHour(x["Post_time"], x["Access_time"]), axis=1)
    avg_hours = tmp_df.groupby(["under"]).agg("mean").Hours_Ago
    data = avg_likes.divide(avg_hours, fill_value=0) #avg num of pics per post under ea hashtag
    
    plt.figure(figsize=(8, 6),constrained_layout=True)
    my_cmap = plt.cm.get_cmap('GnBu')
    data_color = [x / max(data) for x in data]
    colors = my_cmap(data_color)
    plt.bar(data.index, data.values, color = colors)
    plt.xticks(rotation=90)
    plt.xlabel("Hashtag")
    plt.ylabel("Number of likes per hour")
    plt.title("Avg. Number of likes gained per hour under each hashtag")
    plt.show()

def startInsScrape():
    global driver 
    driver = webdriver.Chrome(ChromeDriverManager().install())
    login()

    query = '''Please selection from an option below: \n
        a: General Industry-based search \n
        b: Custom keyword search \n
        c: demo industry search (Food & Cooking) \n
        d: demo keyword search (culinary arts) \n'''
    print(query)
    choice = input("Enter your choice (a, b, c or d): " or 'a').lower()

    while choice not in ['a', 'b', 'c', 'd']:
        print("Please enter a valid input!")
        choice = input("Enter your choice (a, b, c or d): " or 'a').lower()

    ################################################################################    
    print("\n########################################")
    if choice == 'a':
        query = '''Please selection from an option below: \n
        1. Food & Cooking (Fine dining, homecooking, Food blog) \n
        2. Bakery (Dessert, Patisserie) \n
        3. Animals (Wildlife, Pets) \n
        4. Beauty (Fashion, Clothing, Cosmetics, Fitness) \n
        5. DIY & Design (Life style/home design) \n
        6. Nature & landscape (photography) \n
        7. Sports (sportslife)'''
        print(query)

        choice = input("Enter your choice (1 through 7): " or '1').lower()

        while choice not in ['1', '2', '3', '4', '5', '6', '7']:
            print("Please enter a valid input!")
            choice = input("Enter your choice (1 through 7): " or '1').lower()
            
        all_df = industry_search(choice)
        print(tabulate(all_df.iloc[:, [0, 1, 2, 3, 4, 6, 7, 8]], headers='keys', tablefmt='psql', showindex=False))

        #############################  Visualization  #############################
        all_related_hashtags = list(chain.from_iterable(all_df.hashtag.tolist()))
        all_related_hashtags = list(map(lambda x: x[1:], all_related_hashtags))
        print("Breakdown of popular hashtags from posts within the selected industry: ")
        try:
            hashtag_WC(all_related_hashtags)
        except:
            print("Wordcloud plot failed to load!")

        
        print("Hashtag related insights: ")
        try:
            cnt_visual(all_df)
        except:
            pass

        try:
            likes_visual(all_df)
        except:
            pass

        print("Most popular posts: ")
        top_candidate_posts = sorted_scrape(all_df).head(10)
        print(tabulate(top_candidate_posts, headers='keys', tablefmt='psql', showindex=False))

        print("Popular accounts for mentioning: ")
        mentioned_df = mentioned_accounts_info(all_mentioned_url_under_hashtag(top_candidate_posts)).head(10)
        print(tabulate(mentioned_df, headers='keys', tablefmt='psql', showindex=False))


    ################################################################################
    if choice == 'b':

        keyword = input("Enter a hashtag/keyword w/o space (e.g., foodart): ").lower()
        while not validate_keyword(keyword):
            keyword = input("Enter a hashtag/keyword w/o space (e.g., foodart): ").lower()

        # custom search
        all_df = user_specified_search(keyword)
        print(tabulate(all_df.iloc[:,[0,1,2,3,4,6,7,8]], headers='keys', tablefmt='psql', showindex=False))

        #############################  Visualization  #############################
        all_related_hashtags = list(chain.from_iterable(all_df.hashtag.tolist()))
        all_related_hashtags = list(map(lambda x: x[1:], all_related_hashtags))
        print("Breakdown of popular hashtags from related posts of the keyword entered: ")
        try:
            hashtag_WC(all_related_hashtags)
        except:
            print("Wordcloud plot failed to load!")

        
        print("Hashtag related insights: ")
        try:
            cnt_visual(all_df)
        except:
            pass

        try:
            likes_visual(all_df)
        except:
            pass

        print("Most popular posts: ")
        top_candidate_posts = sorted_scrape(all_df).head(10)
        print(tabulate(top_candidate_posts.iloc[:,[0,1,2,3,4,6,7,8]], headers='keys', tablefmt='psql', showindex=False))

        print("Relationship between Post Likes and Number of Followers for candidate posts: ")
        scatterplot_posts_suggestion(top_candidate_posts)

        print("Popular accounts for mentioning: ")
        mentioned_df = mentioned_accounts_info(all_mentioned_url_under_hashtag(top_candidate_posts)).head(10)
        print(tabulate(mentioned_df, headers='keys', tablefmt='psql', showindex=False))


    ################################################################################    
    if choice == 'c':
        
        query = 'Runnning results on a previously scraped industry data: Food & Dining'
        print(query)
        
        all_df = pd.read_csv("food.csv")
        assert(all_df.shape[0] == 180)
        print(f'Food & Dining data read sucessfully!')
        castToList(all_df)
        
        #############################  Visualization  #############################
        all_related_hashtags = list(chain.from_iterable(all_df.hashtag.tolist()))
        all_related_hashtags = list(map(lambda x: x[1:], all_related_hashtags))
        print("Breakdown of popular hashtags from posts within the selected industry: ")
        try:
            hashtag_WC(all_related_hashtags)
        except:
            print("Wordcloud plot failed to load!")

        
        print("Hashtag related insights: ")
        try:
            cnt_visual(all_df)
        except:
            pass

        try:
            likes_visual(all_df)
        except:
            pass

        print("Most popular posts: ")
        top_candidate_posts = sorted_scrape(all_df).head(10)
        print(tabulate(top_candidate_posts.iloc[:,[0,1,2,3,4,6,7,8]], headers='keys', tablefmt='psql', showindex=False))

        print("Popular accounts for mentioning: ")
        mentioned_df = pd.read_csv('food_category_mentioned_accounts.csv')
        print(tabulate(mentioned_df, headers='keys', tablefmt='psql', showindex=False))
        
        
    ################################################################################    
    if choice == 'd':
        
        query = 'Runnning results on a previously scraped custom input data: keyword = culinaryarts'
        print(query)
        
        all_df = pd.read_csv("culinaryarts.csv", encoding = 'Latin1')
        assert(all_df.shape[0] == 135)
        print(f'<Culinary Arts> data read sucessfully!')
        castToList(all_df)

        #############################  Visualization  #############################
        all_related_hashtags = list(chain.from_iterable(all_df.hashtag.tolist()))
        all_related_hashtags = list(map(lambda x: x[1:], all_related_hashtags))
        print("Breakdown of popular hashtags from related posts of the keyword entered: ")
        try:
            hashtag_WC(all_related_hashtags)
        except:
            print("Wordcloud plot failed to load!")

        
        print("Hashtag related insights: ")
        try:
            cnt_visual(all_df)
        except:
            pass

        try:
            likes_visual(all_df)
        except:
            pass
        

        print("Most popular posts: ")
        top_candidate_posts = sorted_scrape(all_df.iloc[28:,:]).head(10)
        print(tabulate(top_candidate_posts.iloc[:,[0,1,2,3,4,6,7,8]], headers='keys', tablefmt='psql', showindex=False))

        print("Relationship between Post Likes and Number of Followers for top candidate posts: ")
        scatterplot_posts_suggestion(top_candidate_posts)

        print("Popular accounts for mentioning: ")
        mentioned_df = pd.read_csv('mentioned_accounts_culinaryarts.csv')
        print(tabulate(mentioned_df, headers='keys', tablefmt='psql', showindex=False))

        driver.close()

    return all_df

########################################################################
## utilizes user input to drive action
if __name__ == "__main__":
    ins_df = startInsScrape()
