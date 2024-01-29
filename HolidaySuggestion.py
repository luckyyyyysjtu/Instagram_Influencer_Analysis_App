# File Name: HolidaysSuggestion.py
# C1_Group3
# Name: Xinyi Yang, Yuetian Sun, Yi Guo, Man Luo, Yining Lu
# Andrew ID: xinyiy2, yuetians, yiguo, manluo, yininglu
# imported by: driver.py

"""
This file is used to get the coming holidays. It has two options. The first is to get holidays
classifited into different categories. It requests an input from user and output related holidays
in the following 7 days. The second is to get holidays related to our specified instagram fields.
It requests an input from user and output related holidays in the following 3 days. For both
options, press q to quit.
"""


import pandas as pd
import datetime
from tabulate import tabulate


class HolidaySuggestion:
    def __init__(self, path="Holidays_202210_202309.xlsx"):
        self.df = pd.read_excel(path).astype('str')
        self.selected_df = None
        self.answer_category = {'1': "Animal",
                                '2': "Appreciation",
                                '3': "Arts & Entertainment",
                                '4': "Cause",
                                '5': "Cultural",
                                '6': "Federal",
                                '7': "Food & Beverage",
                                '8': "Fun",
                                '9': "Health",
                                '10': "Relationship",
                                '11': "Religious",
                                '12': "Special Interest"}

    def modify_datetime(self, dtime):
        my_time = datetime.datetime.strptime(dtime, '%b %d%A')
        if int(my_time.strftime('%m')) >= int(datetime.datetime.now().strftime('%m')):
            my_time = my_time.replace(year=2022)
        else:
            my_time = my_time.replace(year=2023)
        return my_time.strftime('%Y-%m-%d %a')

    def preprocessing(self):
        self.df['Date'] = self.df['Date'].apply(self.modify_datetime)
        now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.df['Days Coming'] = self.df['Date'].apply(lambda x: (
            datetime.datetime.strptime(x, '%Y-%m-%d %a') - now).days)
        self.df.loc[self.df['Category'] ==
                    'AppreciationHealth', 'Category'] = 'Appreciation'
        self.df.loc[self.df['Category'] ==
                    'AnimalHealth', 'Category'] = 'Animal'
        self.df.loc[self.df['Category'] ==
                    'FederalFood & Beverage', 'Category'] = 'Food & Beverage'
        self.df.loc[self.df['Category'] ==
                    'CulturalSpecial Interest', 'Category'] = 'Special Interest'

    def get_category_holiday_df(self, answer, days_coming=7):
        self.selected_df = self.df[(self.df['Category'] == self.answer_category[answer]) & (
            self.df['Days Coming'] <= days_coming) & (self.df['Days Coming'] >= 0)]

    def get_field_related_holiday_df(self, answer, days_coming=3):
        # Animals
        # Category: Animals
        if answer == '1':
            self.selected_df = self.df[(self.df['Category'] == "Animal")
                                       & (self.df['Days Coming'] <= days_coming) & (self.df['Days Coming'] >= 0)]
        # Beauty
        # Tags: Fashion
        elif answer == '2':
            self.selected_df = self.df[(self.df['Tags'].str.contains('Conservation'))
                                       & (self.df['Days Coming'] <= days_coming) & (self.df['Days Coming'] >= 0)]
        # DIY & Design
        # Category: Arts & Entertainment
        elif answer == '3':
            self.selected_df = self.df[(self.df['Category'] == "Arts & Entertainment")
                                       & (self.df['Days Coming'] <= days_coming) & (self.df['Days Coming'] >= 0)]
        # Extreme Sports & Outdoor activities
        # Tags: Lifestyle, Hobby, Fun, Sports, Health
        elif answer == '4':
            self.selected_df = self.df[(self.df['Tags'].str.contains("Lifestyle|Hobby|Fun,|Sports|Health"))
                                       & (self.df['Days Coming'] <= days_coming) & (self.df['Days Coming'] >= 0)]
        # Food & Cooking
        # Tags: Beverage, Breakfast, Cooking, Drinking, Fast Food, Fruit, Liquor, Vegetable, Healthy Food
        elif answer == '5':
            self.selected_df = self.df[(self.df['Tags'].str.contains("Beverage|Breakfast|Cooking|Drinking|Fast Food|Fruit|Liquor|Vegetable|Healthy Food"))
                                       & (self.df['Days Coming'] <= days_coming) & (self.df['Days Coming'] >= 0)]
        # Nature & landscapes
        # Tags: Wildlife, Conservation, Environment, Environmental
        elif answer == '6':
            self.selected_df = self.df[(self.df['Tags'].str.contains("Wildlife|Conservation|Environment"))
                                       & (self.df['Days Coming'] <= days_coming) & (self.df['Days Coming'] >= 0)]
        # Sweets & Bakery
        # Tags: Baking, Beverage, Chocolate, Dessert, Sweet Food, Ice Cream, Candy
        elif answer == '7':
            self.selected_df = self.df[(self.df['Tags'].str.contains("Baking|Beverage|Chocolate|Dessert|Sweet Food|Ice Cream|Candy"))
                                       & (self.df['Days Coming'] <= days_coming) & (self.df['Days Coming'] >= 0)]

    def print_selected_df(self):
        print(tabulate(self.selected_df, headers='keys',
              tablefmt='psql', showindex=False))

