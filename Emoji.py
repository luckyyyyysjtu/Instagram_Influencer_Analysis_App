# File Name: Emoji.py
# C1_Group3
# Name: Xinyi Yang, Yuetian Sun, Yi Guo, Man Luo, Yining Lu
# Andrew ID: xinyiy2, yuetians, yiguo, manluo, yininglu
# imported by: top_influencer.py

"""
This file is used to get  the emojis in a string list and visualize the frequency using word cloud. It defines a class EmojiCloud. After calling generate function, it will get emojis out of string list and elimiate skin tone difference between emojis. Then it will calculate the frequency and plot the wordcloud.
"""

from collections import Counter
import emoji
import matplotlib.pyplot as plt
from wordcloud import WordCloud


class EmojiCloud:
    def __init__(self, font_path='NotoEmoji-VariableFont_wght.ttf'):
        self.font_path = font_path
        self.word_cloud = self.initialize_wordcloud()
        self.emoji_probability = None
        self.emoji_list_decoded = []
        self.emoji_dict = dict()
        self.emoji_dict_decoded = dict()

    def initialize_wordcloud(self):
        return WordCloud(font_path=self.font_path,
                         width=2000,
                         height=1000,
                         background_color='white',
                         random_state=42,
                         collocations=False)

    def get_emoji(self, text):
        for i, word in enumerate(text):
            es = emoji.distinct_emoji_list(word)
            for e in es:
                self.emoji_list_decoded.append(emoji.demojize(e))

    def eliminate_skin_tone(self):
        self.emoji_dict_decoded = Counter(self.emoji_list_decoded)
        for key in list(self.emoji_dict_decoded.keys()):
            if 'skin_tone' in key:
                new_key = '_'.join(key.split('_')[:-3]) + ':'
                self.emoji_dict_decoded[new_key] = self.emoji_dict_decoded.get(
                    new_key, 0) + self.emoji_dict_decoded.pop(key)
        for key in self.emoji_dict_decoded.keys():
            self.emoji_dict[emoji.emojize(key)] = self.emoji_dict_decoded[key]

    # input a list of strings containing emojis
    def generate(self, text, titlestr):
        self.get_emoji(text)
        self.eliminate_skin_tone()
        total_count = sum(self.emoji_dict.values())
        self.emoji_probability = {
            emoji: count/total_count for emoji, count in self.emoji_dict.items()}
        wc = self.word_cloud.generate_from_frequencies(self.emoji_dict)
        plt.figure(figsize=(12, 8))
        plt.title(f"Word Cloud of Emoji used most in {titlestr}")
        plt.imshow(wc)
        plt.axis("off")
        plt.show()
