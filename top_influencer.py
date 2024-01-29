# import from : Emoji.py
# imported by: driver.py

"""
This file is used to get and analyze top influencers’ profile data in the 
user's chosen category. After the category is chosen, it gets the top 50 influencers 
in the category from https://hypeauditor.com/top-instagram/. 
Then it uses Selenium to crawl 50 influencers’ profile data from their Instagram 
page to get their image link, post number, following number, follower number, 
introduction text, menu text, joined date and country. The file outputs statistical 
descriptions and visualization of above data to give user insights about how to 
become a top influencer.

"""

from bs4 import BeautifulSoup
import pandas as pd
import re
import requests
from tabulate import tabulate
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import warnings
from pyecharts.charts import Map, Tab
from pyecharts import options as opts
import Emoji
import random
import emoji
from webdriver_manager.chrome import ChromeDriverManager

warnings.filterwarnings("ignore")
pd.set_option('display.float_format', lambda x: '%.2f' % x)


class TopInfluencer:
    def __init__(self):
        self.category_url = {"All Categories": "/top-instagram/",
                             "Accessories & Jewellery": "/top-instagram-accessories-jewellery/",
                             "Adult content": "/top-instagram-adult-content/",
                             "Alcohol": "/top-instagram-alcohol/",
                             "Animals": "/top-instagram-animals/",
                             "Architecture & Urban Design": "/top-instagram-architecture-urban-design/",
                             "Art/Artists": "/top-instagram-art-artists/",
                             "Beauty": "/top-instagram-beauty/",
                             "Business & Careers": "/top-instagram-business-careers/",
                             "Cars & Motorbikes": "/top-instagram-cars-motorbikes/",
                             "Cinema & Actors/actresses": "/top-instagram-cinema-actors-actresses/",
                             "Clothing & Outfits": "/top-instagram-clothing-outfits/",
                             "Comics & sketches": "/top-instagram-comics-sketches/",
                             "Computers & Gadgets": "/top-instagram-computers-gadgets/",
                             "Crypto": "/top-instagram-crypto/",
                             "DIY & Design": "/top-instagram-diy-design/",
                             "Education": "/top-instagram-education/",
                             "Extreme Sports & Outdoor activity": "/top-instagram-extreme-sports-outdoor-activity/",
                             "Family": "/top-instagram-family/",
                             "Fashion": "/top-instagram-fashion/",
                             "Finance & Economics": "/top-instagram-finance-economics/",
                             "Fitness & Gym": "/top-instagram-fitness-gym/",
                             "Food & Cooking": "/top-instagram-food-cooking/",
                             "Gaming": "/top-instagram-gaming/",
                             "Health & Medicine": "/top-instagram-health-medicine/",
                             "Humor & Fun & Happiness": "/top-instagram-humor-fun-happiness/",
                             "Kids & Toys": "/top-instagram-kids-toys/",
                             "Lifestyle": "/top-instagram-lifestyle/",
                             "Literature & Journalism": "/top-instagram-literature-journalism/",
                             "Luxury": "/top-instagram-luxury/",
                             "Machinery & Technologies": "/top-instagram-machinery-technologies/",
                             "Management & Marketing": "/top-instagram-management-marketing/",
                             "Mobile related": "/top-instagram-mobile-related/",
                             "Modeling": "/top-instagram-modeling/",
                             "Music": "/top-instagram-music/",
                             "NFT": "/top-instagram-nft/",
                             "Nature & landscapes": "/top-instagram-nature-landscapes/",
                             "Photography": "/top-instagram-photography/",
                             "Racing Sports": "/top-instagram-racing-sports/",
                             "Science": "/top-instagram-science/",
                             "Shopping & Retail": "/top-instagram-shopping-retail/",
                             "Shows": "/top-instagram-shows/",
                             "Sports with a ball": "/top-instagram-sports-with-a-ball/",
                             "Sweets & Bakery": "/top-instagram-sweets-bakery/",
                             "Tobacco & Smoking": "/top-instagram-tobacco-smoking/",
                             "Trainers & Coaches": "/top-instagram-trainers-coaches/",
                             "Travel": "/top-instagram-travel/",
                             "Water sports": "/top-instagram-water-sports/",
                             "Winter sports": "/top-instagram-winter-sports/"}
        self.answer_category = {'1': "Animals",
                                '2': "Beauty",
                                '3': "DIY & Design",
                                '4': "Extreme Sports & Outdoor activity",
                                '5': "Food & Cooking",
                                '6': "Nature & landscapes",
                                '7': "Sweets & Bakery"}
        self.df = None
        self.user_info = None
        # define the Selenium webdriver settings
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

    def get_influencer_df(self, answer):
        response = requests.get(
            'https://hypeauditor.com' + self.category_url[self.answer_category[answer]])
        res = BeautifulSoup(response.text, "html.parser")

        # get influencer current rank in specific field -> curr_rank
        # get influencer rank change between this month and last month -> diff_rank
        rank_content = res.findAll('div', attrs={'class': "row-cell rank"})
        curr_rank = []
        diff_rank = []
        for record in rank_content:
            num = re.findall(">([0-9]+)<", str(record))
            curr_rank.append(int(num[0]))
            diff = re.findall("--([a-z]+)\"", str(record))
            if diff == []:
                diff_rank.append(0)
            elif diff[0] == 'good':
                diff_rank.append(int(num[1]))
            else:  # diff[0] == 'bad'
                diff_rank.append(-int(num[1]))

        # get influencer name -> name
        name_content = res.findAll(
            'div', attrs={'class': "contributor__name-content"})
        name = []
        for record in name_content:
            word = re.findall(">(.*)<", str(record))  # greedy
            name.append(word[0])

        # get influencer title -> title
        title_content = res.findAll(
            'div', attrs={'class': "contributor-wrap contributor__content"})
        title = []
        for record in title_content:
            title_start = re.findall("contributor__title.*", str(record))
            if title_start == []:
                title.append('')
            else:
                word = re.findall(">(.*)<!-- --><!-- -->",
                                  title_start[0])  # greedy
                title.append(word[0])

        # get influencer category -> category
        category_content = res.findAll(
            'div', attrs={'class': "row-cell category"})
        category = []
        for record in category_content:
            word = re.findall(">([a-zA-Z &;/]+?)<", str(record))
            for i in range(len(word)):
                word[i] = word[i].replace('&amp;', '&')
            category.append(word)

        # get influencer followers number -> followers
        followers_content = res.findAll(
            'div', attrs={'class': "row-cell subscribers"})
        followers = []
        for record in followers_content:
            word = re.findall(">(.*)<", str(record))
            followers.append(word[0])

        # get influencer audience top country -> country
        country_content = res.findAll(
            'div', attrs={'class': "row-cell audience"})
        country = []
        for record in country_content:
            word = re.findall(">(.*)<", str(record))
            if word == []:
                country.append('')
            else:
                country.append(word[0])

        # get influencer authentic engagement -> auth_eng
        # The metric shows the average number of organic likes and comments per post,
        # i.e. likes and comments that come from real people, without using grey hat methods.
        auth_eng_content = res.findAll(
            'div', attrs={'class': "row-cell authentic"})
        auth_eng = []
        for record in auth_eng_content:
            word = re.findall(">(.*)<", str(record))
            auth_eng.append(word[0])

        # get influencer average engagement -> avg_eng
        avg_eng_content = res.findAll(
            'div', attrs={'class': "row-cell engagement"})
        avg_eng = []
        for record in avg_eng_content:
            word = re.findall(">(.*)<", str(record))
            avg_eng.append(word[0])

        self.df = pd.DataFrame({'rank': curr_rank,
                                'rank_change': diff_rank,
                                'name': name,
                                'title': title,
                                'category': category,
                                'followers': followers,
                                'max_followers_from': country,
                                'auth_eng': auth_eng,
                                'avg_eng': avg_eng})

    def print_df(self, data, showind):
        print(tabulate(data, headers='keys', tablefmt='psql', floatfmt=".2f",showindex=showind))

    # log in to Instagram
    def log_in(self):
        # open instagram
        url = 'https://www.instagram.com/'
        self.driver.get(url)

        # enter user info
        # backup account if it is blocked
        # ig_phone = "dfp_group_instahit"
        # ig_pass = "instahitgroup"
        ig_phone = "instahitgroup"
        ig_pass = "DFPGroup"

        # login in
        myElem = WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@name='username']")))
        myElem.send_keys(ig_phone)
        self.driver.find_element(By.NAME, "password").send_keys(ig_pass)
        self.driver.find_element(By.XPATH, "//div[text()='Log In']").click()
        time.sleep(10)
        self.driver.find_element(
            By.XPATH, "//button[text()='Save Info']").click()
        time.sleep(15)

    # get Instagram top influencers' profile data
    def get_user_info(self):
        info_list = []

        for user in self.df.name:
            # open page
            url = 'https://www.instagram.com/{}/'.format(user)
            self.driver.get(url)

            # get header block
            header = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.TAG_NAME, "header")))

            # get image, post num, following num, follower num, introduction text of influencer
            Image = header.find_element(
                By.CLASS_NAME, "_aa8j").get_attribute('src')
            Post = header.find_element(
                By.XPATH, "//div[contains(text(),' posts')]").text.replace('posts', '').replace(',', '').strip()
            Following = header.find_element(
                By.XPATH, "//div[contains(text(),' following')]").text.replace('following', '').replace(',', '').strip()
            Follower = header.find_element(
                By.XPATH, "//div[contains(text(),' followers')]").text.replace('followers', '').replace(',', '').strip()
            Intro = self.driver.find_element(
                By.CLASS_NAME, "_aa_c").text.strip()

            time.sleep(15)

            # get menu defined by influencer
            Menu = ';'.join([i.text for i in self.driver.find_elements(
                By.CLASS_NAME, "_ab0c")]).strip()

            # get influencer reg date and country
            try:
                self.driver.find_element(
                    By.XPATH, "//div[@class='_abm0']").click()
                self.driver.find_element(
                    By.XPATH, "//button[text()='About this account']").click()
                time.sleep(5)
                DateJoined = self.driver.find_element(
                    By.XPATH, "//div[@data-testid='ata_date_joined_row']").text.replace('Date joined\n', '')
                Country = self.driver.find_element(
                    By.XPATH, "//div[@data-testid='ata_country_row']").text.replace('Account based in\n', '')
            except:
                DateJoined = ''
                Country = ''

            info_list.append((user, Image, Post, Following,
                             Follower, Intro, Menu, DateJoined, Country))
            self.user_info = pd.DataFrame(info_list)
            self.user_info.columns = ['Influencer_ID', 'Image', 'Post_Number', 'Following_Number',
                                      'Follower_Number', 'Introduction', 'Menu', 'Date_Joined', 'Country']
        self.driver.close()

    # draw boxplot and return outlier data
    def find_outlier(self, columnName):
        p = (self.user_info[[columnName]]).boxplot(return_type='dict')
        x = p['fliers'][0].get_xdata()
        y = p['fliers'][0].get_ydata()
        return x, y

    # label minimum and maximum value of outliers
    def plot_outlier(self):
        plt.figure(figsize=(12, 8),constrained_layout=True)
        lst = ['Post_Number', 'Following_Number',
               'Follower_Number(Thousand)', 'Joined_Month']
        # print("Box Plot of Influencers' Numerical Features:")
        plt.suptitle("Box Plot of Influencers' Numerical Features")
        for i in range(4):
            plt.subplot(2, 2, i+1)
            x, y = self.find_outlier(lst[i])
            # deal with no outlier situation
            try:
                plt.annotate(max(y), xy=(x[np.argmax(y)], max(
                    y)), xytext=(x[np.argmax(y)] + 0.05, max(y)))
                plt.annotate(min(y), xy=(x[np.argmin(y)], min(
                    y)), xytext=(x[np.argmin(y)] + 0.05, min(y)))
            except:
                pass
        plt.show()
        
    # scatter plot of influencers' follower number and other three numerical features
    # add the outliers' account name to the scatter plot
    def plot_scatter(self):
        plt.style.use('_mpl-gallery')
        sns.set_style({'font.sans-serif': ['simhei', 'Arial']})
        c1 = 'Follower_Number(Thousand)'
        lst = ['Post_Number', 'Following_Number', 'Joined_Month']
        # print("Scatter Plot of Relationship between Other Numerical Features and Follower Number:")
        for c2 in lst:
            y1 = self.find_outlier(c2)[1]
            y2 = self.find_outlier(c1)[1]
            plt.clf()
            plt.figure(figsize=(8,6),constrained_layout=True)
            plt.scatter(self.user_info[c2], self.user_info[c1], s= self.user_info[c1]/100,c=self.user_info[c2], cmap='Wistia')
            for a in y1:
                for b in y2:
                    for row in range(self.user_info.shape[0]):
                        if self.user_info.iloc[row][c2] == a:
                            plt.text(
                                x=a, y=self.user_info.iloc[row][c1], fontsize=10, s=self.user_info.iloc[row].Influencer_ID)
                        elif self.user_info.iloc[row][c1] == b:
                            plt.text(
                                x=self.user_info.iloc[row][c2], y=b, fontsize=10, s=self.user_info.iloc[row].Influencer_ID)
            plt.title("Scatter Plot of Relationship between " + c2.replace("_", " ") + " and Follower Number")
            plt.xlabel(c2.replace("_", " "))
            plt.ylabel(c1.replace("_", " "))
            plt.show()
        
    def influencer_clustering(self):
        Xi = self.user_info[['Influencer_ID', 'Post_Number', 'Following_Number',
                             'Follower_Number(Thousand)', 'Joined_Month']].dropna()
        X = np.array(self.user_info[['Post_Number', 'Following_Number',
                     'Follower_Number(Thousand)', 'Joined_Month']].dropna())

        scale = MinMaxScaler().fit(X)
        X1 = scale.transform(X)
        colors = ['red', 'pink', 'orange', 'gray', 'blue', 'green']

        # create a KMeans object and set cluster number=3
        cluster = KMeans(n_clusters=3)
        cluster = cluster.fit(X1)
        # get predicted labels
        y_pred = cluster.labels_

        # show influencer name by clustered type
        print("\nClustering influencers into 3 types according to their post number, following number, follower number and joined date.")
        for i in range(3):
            print("Type %d Influencer:" % (i+1))
            for j in range(Xi[y_pred == i].iloc[:, 0].shape[0]):
                print(Xi[y_pred == i].iloc[:, 0].iloc[j], end=' ')
                if (j + 1) % 4 == 0 and j > 0: 
                    print("\n")
            print(end="\n\n")
        print("-----------------------------------------------------------------------------------------") 
        print()

       # print median statistics of numerical attributes for influencer with different types
        Xi['Type'] = y_pred+1
        d = Xi.groupby('Type').median()
        d1 = pd.DataFrame(d.values.T, index=d.columns, columns=d.index)
        d1.loc['Count'] = Xi.groupby('Type').count()['Influencer_ID']
        print("Median of Influencers of Different Types")
        self.print_df(d1, True)
        print()
        print("-----------------------------------------------------------------------------------------") 


        # create two-way plots for all numerical attributes by predicted type
        K = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
        lst = ['Post Number', 'Following Number',
               'Follower Number(Thousand)', 'Joined Months']
        typ = ['Type 1', 'Type 2', 'Type 3']
        count = 1
        # print("\nTwo-way Plots for All Numeric Attributes by Clustered Type")
        plt.figure(figsize=(20, 8),constrained_layout=True)
        plt.suptitle("Two-way Plots for All Numeric Attributes by Clustered Type")
        for k1, k2 in K:
            plt.subplot(2, 3, count)
            for j in range(3):
                plt.scatter(X[y_pred == j, k1], X[y_pred == j, k2],
                            marker="o", s=8, color=colors[j], label=typ[j])
                plt.xlabel(lst[k1])
                plt.ylabel(lst[k2])
                plt.legend(loc='upper right')
            count += 1
        plt.show()

    def country_map(self):
        Xc = self.user_info.dropna(subset=['Country'])
        Xc = Xc[Xc.Country != 'Not shared']
        Xc = Xc[Xc.Country != '']
        Influencer_Num = Map().add(series_name="Influencer Number", data_pair=[list(z) for z in zip(Xc.groupby('Country').count()['Influencer_ID'].index, Xc.groupby('Country').count()['Influencer_ID'])], maptype='world')\
            .set_global_opts(visualmap_opts=opts.VisualMapOpts(max_=max(Xc.groupby('Country').count()['Influencer_ID'])))\
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False, color="blue"))
        Post_Num = Map().add(series_name="Post Number", data_pair=[list(z) for z in zip(Xc.groupby('Country').median()['Post_Number'].index, Xc.groupby('Country').median()['Post_Number'])], maptype='world')\
            .set_global_opts(visualmap_opts=opts.VisualMapOpts(max_=max(Xc.groupby('Country').median()['Post_Number'])))\
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False, color="blue"))
        Following_Number = Map().add(series_name="Following Number", data_pair=[list(z) for z in zip(Xc.groupby('Country').median()['Following_Number'].index, Xc.groupby('Country').median()['Following_Number'])], maptype='world')\
            .set_global_opts(visualmap_opts=opts.VisualMapOpts(max_=max(Xc.groupby('Country').median()['Following_Number'])))\
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False, color="blue"))
        Follower_Number = Map().add(series_name="Follower Number", data_pair=[list(z) for z in zip(Xc.groupby('Country').median()['Follower_Number(Thousand)'].index, Xc.groupby('Country').median()['Follower_Number(Thousand)'])], maptype='world')\
            .set_global_opts(visualmap_opts=opts.VisualMapOpts(max_=max(Xc.groupby('Country').median()['Follower_Number(Thousand)'])))\
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False, color="blue"))
        Joined_Month = Map().add(series_name="Joined Months", data_pair=[list(z) for z in zip(Xc.groupby('Country').median()['Joined_Month'].index, Xc.groupby('Country').median()['Joined_Month'])], maptype='world')\
            .set_global_opts(visualmap_opts=opts.VisualMapOpts(max_=max(Xc.groupby('Country').median()['Joined_Month'])))\
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False, color="blue"))

        tab = Tab(page_title="World Map of Top Influencers' Profile Data")
        tab.add(Influencer_Num, "Influencer Number")
        tab.add(Post_Num, "Post Number")
        tab.add(Following_Number, "Following Number")
        tab.add(Follower_Number, "Follower Number")
        tab.add(Joined_Month, "Joined Months")
        tab.render('influencer_country_map.html')

    def numerical_analysis(self):
        # change Follower Number from str type to int
        # show # of thousand user
        self.user_info['Follower_Number(Thousand)'] = [int(float(i[:-1]))*1000 if i[-1] == "M"
                                                       else (int(float(i[:-1])) if i[-1] == "K"
                                                             else int(i[:-1])/1000)
                                                       for i in self.user_info.Follower_Number]
        self.user_info['Post_Number'] = pd.to_numeric(
            self.user_info['Post_Number'])
        self.user_info['Following_Number'] = pd.to_numeric(
            self.user_info['Following_Number'])

        self.user_info['Country'] = ["China" if i ==
                                     "Hong Kong" else i for i in self.user_info.Country]

        # deal with date data -> Date_Joined
        # calculate the how long the influencer has been joining instagram -> Joined_Month
        self.user_info['Date_Joined'] = [
            i if i != "" else None for i in self.user_info['Date_Joined']]
        self.user_info['Date_Joined'] = pd.to_datetime(
            self.user_info['Date_Joined'], format='%B %Y')
        self.user_info['Joined_Month'] = (
            2022-self.user_info['Date_Joined'].dt.year)*12 + (9-(self.user_info['Date_Joined'].dt.month))

        # print statistics of Post_Number,Following_Number,Follower_Number,Joined_Month
        print()
        print("Numerical Analysis of Top 50 Instagram Influencers:")
        self.print_df(self.user_info.describe()[1:], True)
        print()
        print("-----------------------------------------------------------------------------------------") 


        # plot outlier influencers' numerical features in four dimensions
        self.plot_outlier()

        # plot scatter plot to show relationship between numerical attributes and follower numbers
        # outlier influencer names are exhibited near the point for user's reference
        self.plot_scatter()

        # cluster influencers into 3 types according to their 4 numerical features
        # so that users can see how influencers belong to different tiers
        # and set up a goal for the type they would like to grow into
        self.influencer_clustering()

        # get median statistics heatmap of influencers by their country and render a html
        # 1. influencer number
        # 2. post number median
        # 3. following number median
        # 4. follower number median
        # 5. joined months median
        self.country_map()

    def random_draw(self, number, rang):
        ind = set()
        while True:
            ind.add(random.randint(0, rang))
            if len(ind) == number:
                break
        return ind

    def text_analysis(self):
        # print random 5 introductions
        number = 5
        rang = len(self.user_info)-1
        print()
        print(str(number)+" Examples of Influencers' Self-Introduction:")
        ind = self.random_draw(number, rang)
        for (i, j) in enumerate(ind):
            print(str(i+1)+". "+self.user_info.Influencer_ID[j])
            print(self.user_info['Introduction'][j]+"\n")
        print("-----------------------------------------------------------------------------------------") 
        

        # print random 5 Menu
        print()
        print(str(number)+" Examples of Influencers' Self-Defined Menu:")
        self.user_info['Menu'][self.user_info['Menu'].isna()]=''
        menu = [i for i in self.user_info['Menu'] if i != '']
        name = [self.user_info['Influencer_ID'][j] for j in range(
            len(self.user_info)) if self.user_info['Menu'][j] != '']
        rang = len(menu)-1
        ind = self.random_draw(number, rang)
        for (i, j) in enumerate(ind):
            print(str(i+1)+". "+name[j])
            print(str(menu[j])+"\n")
        print("-----------------------------------------------------------------------------------------") 


        # remove emoji from introduction
        intros = [i for i in self.user_info.Introduction]
        for i, intro in enumerate(self.user_info.Introduction):
            es = emoji.distinct_emoji_list(intro)
            for e in es:
                intros[i] = intros[i].replace(e, '')
        # split lines
        introduction = [i.split("\n") for i in intros]
        # remove punctuations and cut lines into short phrases
        remove_chars = list(
            '[·’!"\#$%&\'()＃！（）*+,-./:;<=>?\@，：?￥★、…．＞【】［］《》？“”‘’\[\\]^_`{|}~]+')
        remove_chars.append("\\\\")
        remove_chars.append("//")
        phrases = [u for k in [j.strip().split(' ') for i in introduction for j in i]
                   for u in k if u not in remove_chars and u != '']

        # define link pattern : .com(none @) or with / and.
        link_pat = r'(^[^@]*\.com)|(\.(.*)/([0-9a-zA-Z]))|(([0-9a-zA-Z])/(.*)\.)'
        # define contact info pattern: contain @ (whether email or instagram account)
        at_pat = r'@'
        link_lst = [k for k in phrases if re.search(link_pat, k) != None]

        # print random 5 links
        print()
        print(str(number)+" Examples of Influencers' External Link Shown:")
        rang = len(link_lst)-1
        ind = self.random_draw(number, rang)

        for (i, j) in enumerate(ind):
            print(str(i+1)+". " + link_lst[j])
        print()
        print("-----------------------------------------------------------------------------------------") 


        # show a table of introduction text related statistics
        # line_cnt: average number of lines in influencers' introduction
        line_cnt = np.mean([len(l) for l in introduction])
        # phrase_cnt_line: average number of phrases per line
        phrase_cnt_line = len(phrases)/sum([len(i) for i in introduction])
        # phrase_cnt_intro: average number of phrases in one introduction
        phrase_cnt_intro = len(phrases)/len(introduction)
        # link_pct: percentage of influencers that attach links in introduction
        link_count = 0
        for i in introduction:
            flag = "N"
            for j in i:
                if re.search(link_pat, j) != None:
                    flag = 'Y'
            if flag == "Y":
                link_count += 1
        link_pct = link_count/len(introduction)*100
        # at_pct: percentage of influencers that attach contact info in introduction
        at_count = 0
        for i in introduction:
            flag = "N"
            for j in i:
                if re.search(at_pat, j) != None:
                    flag = 'Y'
            if flag == "Y":
                at_count += 1
        at_pct = at_count/len(introduction)*100
        df_intro = pd.DataFrame([line_cnt, phrase_cnt_line, phrase_cnt_intro, link_pct, at_pct],
                                index=['# Average Lines', '# Average Phrases / Line', '# Average Phrases / Intro',
                                       '% With Links', '% With Contact Info'], columns=['Statistics'])
        print()
        print("Statistical Truth of Influencers' Introduction:")
        self.print_df(df_intro, True)
        print()
        print("-----------------------------------------------------------------------------------------") 


        # draw word cloud of emoji and size them according to used frequency
        # in influencers' introduction and menu
        emoji_cloud = Emoji.EmojiCloud()
        #print("Emoji used most in Influencers' Introduction: ")
        emoji_cloud.generate(self.user_info.Introduction, "Introduction")
        #print("Emoji used most in Influencers' Self-defined Menu: ")
        emoji_cloud.generate(self.user_info.Menu, "Menu")


if __name__ == "__main__":
    top_influencer = TopInfluencer()

    
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
        #top_influencer.user_info.to_csv('user_info_demo.csv',index=False)

        
    print("Top 50 Instagram Influencers Profile from " +
          top_influencer.answer_category[answer] + " Category:")
    top_influencer.print_df(top_influencer.user_info[['Influencer_ID', 'Post_Number', 'Following_Number',
                                                     'Follower_Number', 'Date_Joined', 'Country']], False)
    
    top_influencer.numerical_analysis()
    top_influencer.text_analysis()
    

