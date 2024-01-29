# File Name: driver.py
# C1_Group3
# Name: Xinyi Yang, Yuetian Sun, Yi Guo, Man Luo, Yining Lu
# Andrew ID: xinyiy2, yuetians, yiguo, manluo, yininglu
# import from : Ins_Hashtag.py, top_influencer.py, HolidaySuggestion.py, twitter.py
# imported by: (None)

"""
This file is used to go over pages of predefined or user-defined hashtags on Instagram,
gathering relevant infos such as num_of_likes, post_time, creator_link, hashtags from 
individual posts, then compiling all gathered info for meta analysis. The result will be 
a dataframe saved to local directory with industry/keyword prepended in name. Visualizations
include trimmed, tabulated dataframe view, Wordcloud of popular hashtags, by-hashtag visuals,
and creator ranking scatterplot (num_followers vs num_likes). 
"""

import Ins_Hashtag as Ins   
import top_influencer as top
import HolidaySuggestion as hs
import twitter
import pandas as pd

if __name__ == "__main__":

    print("Welcome to InstaHit, where everyone has the potential to become an influencer!")
    print('''
      ###      #      #   #####   ######    #        #    #    ###   ######
       #      # #    #   #          #      # #       #    #     #      #
       #     #   #  #     ####      #     #####      ######     #      #
       #    #      #         #      #    #     #     #    #     #      #
     ####  #      #     #####       #   #       #    #    #   ####     #
        ''')
    ################  Instagram Scrape ##################
    print("########################################")
    print("Scraping Instagram posts under hashtags: ...")
    ins_df = Ins.startInsScrape()

    ################  Top Influencer ##################
    print("########################################")
    print("Scraping Top influencers info on Instagram: ...")
    top_influencer = top.TopInfluencer()

    
    print('''
    a) Use the Code from Demo File
    b) Request Most Current Data''')
    
    choice = input("Make the choice whether to use downloaded data: ")
    
    if choice =="a":
        top_influencer.driver.close()
        top_influencer.user_info=pd.read_csv('user_info_demo.csv')
        answer="1"
        
    if choice =="b":  
        print('''
        See the top 50 instagram influencer from these categories:
        1) Animals
        2) Beauty
        3) DIY & Design
        4) Extreme Sports & Outdoor Activity
        5) Food & Cooking
        6) Nature & landscapes
        7) Sweets & Bakery
        ''')
        answer = input("Which category are you interested in?   ")

    
    top_influencer.get_influencer_df(answer)
    print("Top 50 Instagram Influencers from " +
          top_influencer.answer_category[answer] + " Category:")
        
        
    print('''
    rank_change: rank change between this month and last month
    auth_eng: authentic engagement, showing the average number of likes and comments from real people per post
    ''')
    top_influencer.print_df(top_influencer.df[['rank', 'rank_change', 'name', 'title',
                                               'category', 'max_followers_from', 'auth_eng', 'avg_eng']], False)
    
    if choice =="b": 
        top_influencer.log_in()
        top_influencer.get_user_info()
        top_influencer.user_info.to_csv('user_info_demo.csv',index=False)

        
    print("Top 50 Instagram Influencers Profile from " +
          top_influencer.answer_category[answer] + " Category:")
    top_influencer.print_df(top_influencer.user_info[['Influencer_ID', 'Post_Number', 'Following_Number',
                                                     'Follower_Number', 'Date_Joined', 'Country']], False)
    
    top_influencer.numerical_analysis()
    top_influencer.text_analysis()


    ################  Holiday ##################
    print("########################################")
    print("Starting Holiday suggestions based on current date: ...")
    holiday_suggestion = hs.HolidaySuggestion()
    holiday_suggestion.preprocessing()
    
    answer = ''
    while answer != 'Q' and answer != 'q':
        print('''
        See the holidays in the following 7 days from these categories:
        1) Animal
        2) Appreciation
        3) Arts & Entertainment
        4) Cause
        5) Cultural
        6) Federal
        7) Food & Beverage
        8) Fun
        9) Health
        10) Relationship
        11) Religious
        12) Special Interest
        Q) Quit from this program
        ''')
        answer = input('Select the category you are interested in!\n').strip()
        if answer == 'Q' or answer == 'q':
            print('Quit successfully!')
            break
        elif answer not in [str(i) for i in range(1, 13)]:
            print('Your choice is not valid: ', answer)
            continue
        holiday_suggestion.get_category_holiday_df(answer)
        holiday_suggestion.print_selected_df()
        
    answer = ''
    while answer != 'Q' and answer != 'q':
        print('''
        See the possible related holidays in the following 3 days from these fields:
        1) Animals
        2) Beauty
        3) DIY & Design
        4) Extreme Sports & Outdoor Activity
        5) Food & Cooking
        6) Nature & landscapes
        7) Sweets & Bakery
        Q) Quit from this program
        ''')
        answer = input('Select the industry you are interested in!\n').strip()
        if answer == 'Q' or answer == 'q':
            print('Quit successfully!')
            break
        elif answer not in [str(i) for i in range(1, 8)]:
            print('Your choice is not valid: ', answer)
            continue
        holiday_suggestion.get_field_related_holiday_df(answer)
        holiday_suggestion.print_selected_df()

    ################  Twitter ##################
    print("########################################")
    print("Starting Twitter search using keyword: ...")
    keyword = input("Please enter a keyword to search on Twitter:  ")
    twitter.enterKeyWord(keyword)