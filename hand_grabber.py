from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from hand_grabber import *
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import re


def convert(string):
    list1 = []
    list1[:0] = string
    return list1


def list_to_string(s):
    str1 = ""
    for ele in s:
        str1 += ele
    return str1


def hand_strength(t):
    # s = strength
    s = 0
    if t == "HIGH CARD":
        s = 1
    elif t == "PAIR":
        s = 2
    return t


def format_action(s):
    if s.find("Call") != -1:
        action_type = "calls"
    elif s.find("Bet") != -1 and s.find("Entry Bet") == -1:
        action_type = "bets"
    elif s.find("Raise") != -1:
        action_type = "raises"
    elif s.find("Fold") != -1:
        action_type = "folds"
    elif s.find("Muck") != -1:
        action_type = "doesn't show hand"
    elif s.find("Check") != -1:
        action_type = "checks"
    else:
        # print("s returned")
        return s

    if s[0] == "w":
        index1 = 8
    else:
        index1 = 11
    player_temp_id = s[:index1]

    # get and format bet from string
    count = 0
    # print(s)
    if action_type != "folds" and action_type != "doesn't show hand" and action_type != "checks":
        while s[-(count+1)] != " ":
            count+= 1
        bet = s[-count:]
        while bet[0] == " " or re.match("[a-z]", bet[0]) is not None:
            bet = bet[1:]
        bet = " $" + ("%.2f" % float(bet))
    else:
        bet = ""
    # remove bet from string
    while s[-1] == " " or re.match("[0-9]", s[-1]) is not None or re.match(
            "\.", s[-1]) is not None:
        s = s[:-1]
    s = player_temp_id + ": " + action_type + bet
    return s

