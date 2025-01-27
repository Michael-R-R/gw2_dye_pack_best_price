import sys
import re
import requests
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    isInTable = False
    isInTBody = False

    # dye pack title flags
    isInTR1 = False
    isInTR1TH1 = False
    isInTR1A2 = False

    # dye name and id flags
    isInDyeTR = False
    isInDyeTRTD2 = False
    isInDyeTRTD3 = False

    tbodyTRCounter = 0
    tr1ACounter = 0
    dyeTRTDCounter = 0
    dyeTRTDSpanCounter = 0

    dyePackName = ""
    dyeColorId = ""
    dyeName = ""
    dyeItemId = ""
    results = {}

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            if attrs[0][1] == "promo sortable table":
                self.isInTable = True

        if self.isInTable and tag == "tbody":
            self.isInTBody = True

        # handle the pack title logic
        if self.isInTBody:
            if tag == "tr":
                self.tbodyTRCounter += 1
                
                if self.tbodyTRCounter == 1:
                    self.isInTR1 = True
                elif self.tbodyTRCounter >= 3:
                    self.isInDyeTR = True
        
        if self.isInTR1:
            if tag == "th":
                self.isInTR1TH1 = True

        if self.isInTR1TH1:
            if tag == "a":
                self.tr1ACounter += 1

                if self.tr1ACounter == 2:
                    self.isInTR1A2 = True

        # handle dye name and id logic
        if self.isInDyeTR:
            if tag == "tr":
                id = attrs[0][1]
                id = re.search(r"[0-9]+", id).group(0)
                self.dyeColorId = id

            if tag == "td":
                self.dyeTRTDCounter += 1

                if self.dyeTRTDCounter == 2:
                    self.isInDyeTRTD2 = True
                elif self.dyeTRTDCounter == 3:
                    self.isInDyeTRTD3 = True

            if tag == "span":
                self.dyeTRTDSpanCounter += 1

                if self.dyeTRTDSpanCounter == 1:
                    self.dyeItemId = attrs[2][1]
    
    def handle_endtag(self, tag):
        if tag == "tbody":
            self.resetValues()

        if self.isInTBody:
            if self.isInTR1TH1 and tag == "th":
                if self.dyePackName != "":
                    if self.results.get(self.dyePackName) is None:
                        self.results[self.dyePackName] = []
                        self.isInTR1 = False
                        self.isInTR1TH1 = False
                        self.isInTR1A2 = False

            if tag == "tr":
                if self.dyeTRTDCounter >= 3:
                    self.isInDyeTR = False
                    self.isInDyeTRTD2 = False
                    self.isInDyeTRTD3 = False
                    self.dyeTRTDCounter = 0
                    self.dyeTRTDSpanCounter = 0
                    self.results[self.dyePackName].append((self.dyeColorId, self.dyeItemId, self.dyeName))
    
    def handle_data(self, data):
        if self.isInTR1TH1 and self.tr1ACounter == 0:
            if data != "":
                if self.dyePackName == "":
                    self.dyePackName = data.rstrip()

        # dye pack title name
        if self.isInTR1A2:
            self.dyePackName = data
            self.results[self.dyePackName] = []
            self.isInTR1 = False
            self.isInTR1TH1 = False
            self.isInTR1A2 = False

        # dye name and id
        if self.isInDyeTRTD2:
            self.dyeName = data
            self.isInDyeTRTD2 = False

    def resetValues(self):
        self.isInTable = False
        self.isInTBody = False
        self.isInTR1 = False
        self.isInTR1TH1 = False
        self.isInTR1A2 = False
        self.isInDyeTR = False
        self.isInDyeTRTD2 = False
        self.isInDyeTRTD3 = False
        self.tbodyTRCounter = 0
        self.tr1ACounter = 0
        self.dyeTRTDCounter = 0
        self.dyeTRTDSpanCounter = 0
        self.dyePackName = ""
        self.dyeColorId = ""
        self.dyeName = ""
        self.dyeItemId = ""

def getContentRequests(url):
    response = requests.get(url)
    return response.text

dyePacks = [
    "Aurene_Dye_Kit",
    "Awakened_Dye_Kit",
    "Bloodstone_Dye_Kit",
    "Blue_Shift_Dye_Kit",
    "Celebratory_Dye_Pack",
    "Charr_Dye_Kit",
    "Consortium_Dye_Pack",
    "Crimson_Lion_Dye_Kit",
    "Darkest_Abyss_Dye_Kit",
    "Deathly_Dye_Kit",
    "Dedicated_Dye_Kit",
    "Delectable_Birthday_Dyes",
    "Dragon%27s_Watch_Dye_Pack",
    "Elonian_Beasts_Dye_Kit",
    "Elonian_Landscape_Dye_Kit",
    "Enemies_Dye_Pack",
    "Exuberant_Dye_Kit",
    "Fine_Black_Lion_Dye_Canister%E2%80%94Blue",
    "Fine_Black_Lion_Dye_Canister%E2%80%94Green",
    "Fine_Black_Lion_Dye_Canister%E2%80%94Red",
    "Fine_Black_Lion_Dye_Canister%E2%80%94Yellow",
    "Flame_Dye_Kit",
    "Frost_Dye_Kit",
    "Glint%27s_Winter_Dye_Kit",
    "Heroes_Dye_Pack",
    "Jade_Dye_Kit",
    "Jormag_Dye_Kit",
    "Jubilant_Dye_Pack",
    "Kralkatorrik_Dye_Kit",
    "Lion%27s_Arch_Commemorative_Dye_Kit",
    "Lion%27s_Arch_Rebuild_Dye_Kit",
    "Lion%27s_Arch_Survivors_Dye_Kit",
    "Mad_King_Dye_Kit",
    "Metallurgic_Dye_Kit",
    "Monstrous_Dye_Kit",
    "Mordremoth_Dye_Kit",
    "Norn_Dye_Kit",
    "Primordus_Dye_Kit",
    "Sacred_Dye_Kit",
    "Seven_Dragon_Dye_Pack",
    "Shadow_Dye_Kit",
    "Smooth_Berry_Dye_Kit",
    "Solar_and_Lunar_Dye_Kit",
    "Soo-Won_Dye_Kit",
    "Taimi%27s_Dye_Kit",
    "Toxic_Dye_Kit",
    "Triumphant_Dye_Kit",
    "Vibrant_Dye_Kit",
    "Victorious_Dye_Kit",
    "Winter_Chimes_Dye_Kit",
    "Wintersday_Dye_Kit",
    "Zhaitan_Dye_Kit",
    "Zephyrite_Color_Swatch:_Blue",
    "Zephyrite_Color_Swatch:_Green",
    "Zephyrite_Color_Swatch:_Red",
    "Zephyrite_Color_Swatch:_Yellow",
]

# ask for user input to select dye pack (56)
print("*** Dye Packs ***")
counter = 1
for pack in dyePacks:
    print(f"{counter}: {dyePacks[counter - 1]}")
    counter += 1

selectedPack = input("\nSelect a dye pack(#): ")
try:
    if int(selectedPack) < 1 or int(selectedPack) > 56:
        sys.exit(1)
except ValueError:
    sys.exit(1)
print("")

apiKey = "<ADD API KEY HERE>"

dyesPackText = getContentRequests(f"https://wiki.guildwars2.com/wiki/{dyePacks[int(selectedPack) - 1]}")
parser = MyHTMLParser()
parser.feed(dyesPackText)

accDyeText = getContentRequests(f"https://api.guildwars2.com/v2/account/dyes?access_token={apiKey}")
accDyes = []
accDyePattern = r"[0-9]+"
accDyes = re.findall(accDyePattern, accDyeText, re.MULTILINE)

# record only dyes not in account
for dyeID in accDyes:
    for pack in parser.results:
        for dye in parser.results[pack]:
            if dyeID == dye[0]:
                parser.results[pack].remove(dye)

# store the 3 highest costing dyes
topPrices = [(0, "", "") for _ in range(3)]
priceUrlTemplate = "https://api.guildwars2.com/v2/commerce/prices/"
for pack in parser.results:
    for dye in parser.results[pack]:
        dyeId = dye[1]
        priceUrl = f"{priceUrlTemplate}{dyeId}"
        priceText = getContentRequests(priceUrl)
        priceSearch = re.search(r"\"unit_price\": [0-9]+", priceText)
        if priceSearch is None:
            continue
        price = priceSearch.group(0)
        price = re.search(r"[0-9]+", price).group(0)
        price = int(price)
        
        if price > topPrices[0][0]:
            topPrices[0] = (price, pack, dye[2])
            topPrices.sort()

# print the highest costing dye with pack name
print("*** Highest Costing Dye ***")
for i, (price, pack, dye) in reversed(list(enumerate(topPrices))):
    print(f"{i + 1}. Pack Name: {pack}")
    print(f"   Dye Name: {dye}")
    print(f"   Price: {price}")