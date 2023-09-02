import sqlite3
import json
import os

debug_connection = sqlite3.connect("Civ5DebugDatabase.db")
cur = debug_connection.cursor()

local_conn = sqlite3.connect("Localization-Full.db")
tran = local_conn.cursor()

language_list = ["en","zh","fr","de","it","jp","kr","pl","ru","es"]

def translate(language,key):
    if key == None:
        return 
    language_table = "Language_en_US"
    match language:
        case "en":
            language_table = "Language_en_US"
        case "zh":
            language_table = "Language_ZH_HANT_HK"
        case "fr":
            language_table = "Language_FR_FR"
        case "de":
            language_table = "Language_DE_DE"
        case "it":
            language_table = "Language_IT_IT"
        case "jp":
            language_table = "Language_JA_JP"
        case "kr":
            language_table = "Language_KO_KR"
        case "pl":
            language_table = "Language_PL_PL"
        case "ru":
            language_table = "Language_RU_RU"
        case "es":
            language_table = "Language_ES_ES"
    tran.execute("SELECT Text FROM " + language_table + " WHERE Tag=?",(key,))
    translation = tran.fetchall()
    if translation == []:
        return []
    return strip_tags_from_text(translation[0][0])

def strip_tags_from_text(key):
    tags = ["[ICON_INFLUENCE]","[ICON_GOLDEN_AGE]","[ICON_TROPHY_BRONZE]","[ICON_TROPHY_SILVER]","[ICON_TROPHY_GOLD]","[ICON_INTERNATIONAL_TRADE]","[ICON_OCCUPIED]","[ICON_HAPPINESS_4]","[ICON_CITIZEN]","[ICON_HAPPINESS_1]","[ICON_CAPITAL]","[ICON_TOURISM]","[NEWLINE]","[TAB]","[ICON_STRENGTH]","[COLOR_POSITIVE_TEXT]","[ENDCOLOR]","[ICON_GREAT_PEOPLE]"]
    for tag in tags:
        key = key.replace(tag,"").replace("  "," ")
    res_strings = cur.execute("SELECT IconString FROM Resources").fetchall()
    for res_string in res_strings:
        key = key.replace(res_string[0],"").replace("  "," ")
    yields = cur.execute("SELECT IconString FROM Yields").fetchall()
    for yiel in yields:
        key = key.replace(yiel[0],"").replace("  "," ")
    key.replace("  "," ")
    return key


#Planned Endpoints
#1. Technologies | True
def get_technologies(language):
    print("TECHNOLOGIES")
    tech_list = []
    tech_id = 1
    cur.execute("SELECT Type,Description,Civilopedia,Cost,Era,Quote FROM Technologies")
    techs = cur.fetchall()
    for tech in techs:
        print(translate(language,tech[1]))
        tech_template = {}
        tech_template["id"] = tech_id
        tech_template["name"] = translate(language,tech[1])
        tech_template["icon"] = "https://eyefyre.github.io/civvapi/images/tech_icons/" + translate("en",tech[1]).replace(" ","_").lower() + ".png"
        cur.execute("SELECT Description FROM Eras where Type=?",(tech[4],))
        n = cur.fetchall()
        tech_template["era"] = translate(language,n[0][0])
        tech_template["cost"] = tech[3]
        tech_template["civilopedia_entry"] = translate(language,tech[2])
        tech_template["quote"] = translate(language,tech[5]).replace("[NEWLINE]","").replace("[TAB]","")#.replace("\"","")
        cur.execute("SELECT * FROM Technology_PrereqTechs WHERE TechType =?", (tech[0],))
        prereqs = cur.fetchall()
        tech_prereqs = []
        for prereq in prereqs:
            cur.execute("SELECT Description FROM Technologies WHERE Type =?", (prereq[1],))
            n = cur.fetchall()
            tech_prereqs.append({"name":translate(language,n[0][0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/tech/"+ translate("en",n[0][0]).replace(" ","_").lower() + ".json"})
        tech_template["tech_prereqs"] = tech_prereqs

        cur.execute("SELECT * FROM Technology_PrereqTechs WHERE PrereqTech =?", (tech[0],))
        unlocks = cur.fetchall()
        tech_unlocks = []
        for unlock in unlocks:
            cur.execute("SELECT Description FROM Technologies WHERE Type =?", (unlock[0],))
            n = cur.fetchall()
            tech_unlocks.append({"name":translate(language,n[0][0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/tech/"+ translate("en",n[0][0]).replace(" ","_").lower() + ".json"})
        tech_template["tech_unlocks"] = tech_unlocks

        cur.execute("SELECT Description FROM Units WHERE PrereqTech=?",(tech[0],))
        units = cur.fetchall()
        unit_unlocks = []
        for unit in units:
            unit_unlocks.append({"name":translate(language,unit[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/units/"+ translate("en",unit[0]).replace(" ","_").lower() + ".json"})
        tech_template["unit_unlocks"] = unit_unlocks

        cur.execute("SELECT Description FROM Buildings WHERE PrereqTech=?", (tech[0],))
        buildings = cur.fetchall()
        building_unlocks = []
        for building in buildings:
            building_unlocks.append({"name":translate(language,building[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/buildings/"+ translate("en",building[0]).replace(" ","_").lower() + ".json"})
        tech_template["building_unlocks"] = building_unlocks

        tech_id += 1
        if not os.path.exists("v1/"+ language + "/tech"):
            os.makedirs("v1/"+ language + "/tech")
        with open("v1/" + language + "/tech/" + translate("en",tech[1]).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(tech_template, outfile,indent=4)
        tech_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/tech/"+ translate("en",tech[1]).replace(" ","_").lower() + ".json"
        tech_list.append(tech_template)

    if not os.path.exists("v1/"+ language + "/tech"):
        os.makedirs("v1/"+ language + "/tech")
    with open("v1/" + language + "/tech/technologies.json", 'w') as outfile:
        json.dump(tech_list, outfile,indent=4)
#2. Units | True
def get_units(language):
    print("UNITS")
    unit_list = []
    unit_id = 1
    cur.execute("SELECT Type,Description,Civilopedia,Strategy,Help,Combat,RangedCombat,Cost,FaithCost,Moves,Range,PrereqTech FROM Units WHERE Special != ? OR Special IS ?",("SPECIALUNIT_PEOPLE",None))#Special IS ?",(None,))
    units = cur.fetchall()
    for unit in units:
        print(translate(language,unit[1]))
        unit_template = {}
        unit_template["id"] = unit_id
        unit_template["name"] = translate(language,unit[1])
        unit_template["icon"] = "https://eyefyre.github.io/civvapi/images/unit_icons/" + translate("en",unit[1]).replace(" ","_").lower() + ".png"
        unit_template["game_info"] = translate(language,unit[4])
        unit_template["historical_info"] = translate(language,unit[2])
        unit_template["strategy"] = translate(language,unit[3])
        unit_template["movement"] = unit[9]
        unit_template["cost"] = {"production":unit[7],"faith":unit[8]}

        unit_template["prereq_tech"] = None
        if unit[11] != None:
            unit_tech = cur.execute("SELECT Description FROM Technologies WHERE Type=?",(unit[11],)).fetchone()
            unit_template["prereq_tech"] = {"name":translate(language,unit_tech[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/tech/"+ translate("en",unit_tech[0]).replace(" ","_").lower() + ".json"}


        free_promotions = []
        promos = cur.execute("SELECT PromotionType FROM Unit_FreePromotions WHERE UnitType=?",(unit[0],)).fetchall()
        for promo in promos:
            promo_info = cur.execute("SELECT Description,PediaType FROM UnitPromotions WHERE Type=?",(promo[0],)).fetchone()
            addon = ""
            match promo_info[1]:
                case "PEDIA_HEAL":
                    addon = "_H"
                case "PEDIA_AIR":
                    addon = "_A"
                case "PEDIA_ATTRIBUTES":
                    addon = "_AT"
                case "PEDIA_MELEE":
                    addon = "_M"
                case "PEDIA_NAVAL":
                    addon = "_N"
                case "PEDIA_RANGED":
                    addon = "_R"
                case "PEDIA_SCOUTING":
                    addon = "_S"
                case "PEDIA_SHARED":
                    addon = "_SH"
            free_promotions.append({"name":translate(language,promo_info[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/promotions/" + (translate("en",promo_info[0]) + addon).replace(" ","_").replace("/","_").lower() + ".json"})
        unit_template["free_promotions"] = free_promotions


        unit_id += 1
        if not os.path.exists("v1/"+ language + "/units"):
            os.makedirs("v1/"+ language + "/units")
        with open("v1/" + language + "/units/" + translate("en",unit[1]).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(unit_template, outfile,indent=4)
        unit_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/units/"+ translate("en",unit[1]).replace(" ","_").lower() + ".json"
        unit_list.append(unit_template)

    if not os.path.exists("v1/"+ language + "/units"):
        os.makedirs("v1/"+ language + "/units")
    with open("v1/" + language + "/units/units.json", 'w') as outfile:
        json.dump(unit_list, outfile,indent=4)
#3. Promotions | True
def get_promotions(language):
    print("PROMOTIONS")
    promotion_list = []
    promotion_id = 1
    cur.execute("SELECT Type,Description,Help,PromotionPrereq,PromotionPrereqOr1,PromotionPrereqOr2,PromotionPrereqOr3,PromotionPrereqOr4,PromotionPrereqOr5,PromotionPrereqOr6,PromotionPrereqOr7,PromotionPrereqOr8,PromotionPrereqOr9,PediaType FROM UnitPromotions WHERE PediaType IS NOT NULL")
    promotions = cur.fetchall()
    for promotion in promotions:
        print(translate(language,promotion[1]))
        promotion_template={}
        promotion_template["id"] = promotion_id
        promotion_template["name"] = translate(language,promotion[1])
        promotion_template["game_info"] = translate(language,promotion[2])
        prereqs = []
        promotion_template["prereq_promotions"] = prereqs
        promotion_template["icon"] = "https://eyefyre.github.io/civvapi/images/promotion_icons/" + translate("en",promotion[1]).replace(" ","_").replace("/","_").lower() + ".png"
        for prereqPromo in [promotion[3],promotion[4],promotion[5],promotion[6],promotion[7],promotion[8],promotion[9],promotion[10],promotion[11],promotion[12]]:
            if prereqPromo != None:
                prereq = cur.execute("SELECT Description from UnitPromotions WHERE Type=?",(prereqPromo,)).fetchone()
                prereqs.append({"name":translate(language,prereq[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/promotions/" + translate("en",prereq[0]).replace(" ","_").replace("/","_").lower() + ".json"})
        promotion_template["prereq_promotions"] = prereqs
        promotion_id += 1

        addon = ""
        match promotion[13]:
            case "PEDIA_HEAL":
                addon = "_H"
            case "PEDIA_AIR":
                addon = "_A"
            case "PEDIA_ATTRIBUTES":
                addon = "_AT"
            case "PEDIA_MELEE":
                addon = "_M"
            case "PEDIA_NAVAL":
                addon = "_N"
            case "PEDIA_RANGED":
                addon = "_R"
            case "PEDIA_SCOUTING":
                addon = "_S"
            case "PEDIA_SHARED":
                addon = "_SH"
        promotion_template["icon"] = "https://eyefyre.github.io/civvapi/images/promotion_icons/" + (translate("en",promotion[1]) + addon).replace(" ","_").replace("/","_").lower() + ".png"
        if not os.path.exists("v1/"+ language + "/promotions"):
            os.makedirs("v1/"+ language + "/promotions")
        with open("v1/" + language + "/promotions/" + (translate("en",promotion[1]) + addon).replace(" ","_").replace("/","_").lower() + ".json", 'w') as outfile:
            json.dump(promotion_template, outfile,indent=4)
        promotion_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/promotions/"+ (translate("en",promotion[1]) + addon).replace(" ","_").lower() + ".json"
        promotion_list.append(promotion_template)

    if not os.path.exists("v1/"+ language):
        os.makedirs("v1/"+ language)
    with open("v1/" + language + "/promotions/promotions.json", 'w') as outfile:
        json.dump(promotion_list, outfile,indent=4)
#4. Buildings | True
def get_buildings(language):
    print("BUILDINGS")
    building_list = []
    building_id = 1
    exclude_list = ("BUILDING_CIRCUS_MAXIMUS","BUILDING_NATIONAL_TREASURY","BUILDING_GRAND_TEMPLE","BUILDING_HERMITAGE","BUILDING_HEROIC_EPIC","BUILDING_IRONWORKS","BUILDING_NATIONAL_COLLEGE","BUILDING_NATIONAL_EPIC","BUILDING_INTELLIGENCE_AGENCY","BUILDING_TOURIST_CENTER","BUILDING_OXFORD_UNIVERSITY","BUILDING_PALACE")
    buildings = cur.execute(f"SELECT Type,Description,Civilopedia,Strategy,Help,Cost,FaithCost,GoldMaintenance,prereqTech,Happiness FROM Buildings WHERE WonderSplashImage IS NULL AND TYPE NOT IN {format(exclude_list)}").fetchall()
    for building in buildings:
        print(translate(language,building[1]))
        building_template = {}
        building_template["id"] = building_id
        building_template["name"] = translate(language,building[1])
        building_template["game_info"] = translate(language,building[4])
        building_template["strategy"] = translate(language,building[3])
        building_template["historical_info"] = translate(language,building[2])
        building_template["cost"]={"production":building[5],"faith":building[6]}
        building_template["gold_maintenance"] = building[7]
        building_template["icon"] = "https://eyefyre.github.io/civvapi/images/building_icons/" + translate("en",building[1]).replace(" ","_").lower() + ".png"

        building_template["prereq_tech"] = None
        prereq_tech = cur.execute("SELECT Description FROM Technologies WHERE Type=?",(building[8],)).fetchone()
        if prereq_tech != None:
            building_template["prereq_tech"] = {"name":translate(language,prereq_tech[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/tech/"+ translate("en",prereq_tech[0]).replace(" ","_").lower() + ".json"}


        ryields = cur.execute("SELECT * FROM Building_YieldChanges WHERE BuildingType=?",(building[0],)).fetchall()
        yield_template = {"gold":0,"production":0,"science":0,"culture":0,"food":0,"faith":0,"happiness":0}
        for ryield in ryields:
            match ryield[1]:
                case "YIELD_FOOD":
                    yield_template["food"] = ryield[2]
                case "YIELD_PRODUCTION":
                    yield_template["production"] = ryield[2]
                case "YIELD_GOLD":
                    yield_template["gold"] = ryield[2]
                case "YIELD_SCIENCE":
                    yield_template["science"] = ryield[2]
                case "YIELD_CULTURE":
                    yield_template["culture"] = ryield[2]
                case "YIELD_FAITH":
                    yield_template["faith"] = ryield[2]
        yield_template["happiness"] = building[9]
        building_template["yields"] = yield_template


        if not os.path.exists("v1/"+ language + "/buildings"):
            os.makedirs("v1/"+ language + "/buildings")
        with open("v1/" + language + "/buildings/" + translate("en",building[1]).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(building_template, outfile,indent=4)
        building_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/buildings/"+ translate("en",building[1]).replace(" ","_").lower() + ".json"
        building_list.append(building_template)

    if not os.path.exists("v1/"+ language + "/buildings"):
        os.makedirs("v1/"+ language + "/buildings")
    with open("v1/" + language + "/buildings/buildings.json", 'w') as outfile:
        json.dump(building_list, outfile,indent=4)
#5. Wonders | True 
def get_wonders(language):
    print("WONDERS")
    wonder_list = []
    wonder_id = 1
    cur.execute("SELECT Type,Description,Civilopedia,Cost,Strategy,Help,Quote,PrereqTech,UnmoddedHappiness FROM Buildings WHERE WonderSplashImage IS NOT NULL")
    wonders = sorted(cur.fetchall())
    for wonder in wonders:
        print(translate(language,wonder[1]))
        wonder_template = {}
        wonder_template["id"] = wonder_id
        wonder_template["name"] = translate(language,wonder[1])
        wonder_template["production_cost"] = wonder[3]
        wonder_template["game_info"] = translate(language,wonder[5])
        wonder_template["strategy"] = translate(language,wonder[4])
        wonder_template["historical_info"] = translate(language,wonder[2])
        wonder_template["icon"] = "https://eyefyre.github.io/civvapi/images/wonder_icons/" + translate("en",wonder[1]).replace(" ","_").lower() + ".png"
        wonder_template["background_image"] = "https://eyefyre.github.io/civvapi/images/wonder_backgrounds/" + translate("en",wonder[1]).replace(" ","_").lower() + ".png"
        wonder_template["quote"] = translate(language,wonder[6])

        cur.execute("SELECT Description FROM Technologies WHERE Type=?", (wonder[7],))
        prereq_tech = cur.fetchone()
        wonder_template["tech_prereq"] = None
        if prereq_tech != None:
            wonder_template["tech_prereq"] = {"name":translate("en",prereq_tech[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/tech/"+ translate("en",prereq_tech[0]).replace(" ","_").lower() + ".json"}
        
        yield_template = {"gold":0,"production":0,"science":0,"culture":0,"food":0,"faith":0,"happiness":0}
        if wonder[8] != 0:
            yield_template["happiness"] = wonder[8]
        yields_changes = cur.execute("SELECT * from Building_YieldChanges WHERE BuildingType=?",(wonder[0],)).fetchall()
        for yields in yields_changes:
            match yields[1]:
                case "YIELD_FOOD":
                    yield_template["food"] = yields[2]
                case "YIELD_PRODUCTION":
                    yield_template["production"] = yields[2]
                case "YIELD_GOLD":
                    yield_template["gold"] = yields[2]
                case "YIELD_SCIENCE":
                    yield_template["science"] = yields[2]
                case "YIELD_CULTURE":
                    yield_template["culture"] = yields[2]
                case "YIELD_FAITH":
                    yield_template["faith"] = yields[2]
        wonder_template["yields"] = yield_template
        wonder_id += 1


        if not os.path.exists("v1/"+ language + "/wonders"):
            os.makedirs("v1/"+ language + "/wonders")
        with open("v1/" + language + "/wonders/" + translate("en",wonder[1]).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(wonder_template, outfile,indent=4)
        wonder_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/wonders/"+ translate("en",wonder[1]).replace(" ","_").lower() + ".json"
        wonder_list.append(wonder_template)

    cur.execute("SELECT Type,Description,Civilopedia,Cost,Strategy,Help,Quote,PrereqTech FROM Buildings WHERE Type=? OR Type=?OR Type=? OR Type=? OR Type=? OR Type=? OR Type=? OR Type=? OR Type=? OR Type=? OR Type=? OR Type=?", ("BUILDING_CIRCUS_MAXIMUS","BUILDING_NATIONAL_TREASURY","BUILDING_GRAND_TEMPLE","BUILDING_HERMITAGE","BUILDING_HEROIC_EPIC","BUILDING_IRONWORKS","BUILDING_NATIONAL_COLLEGE","BUILDING_NATIONAL_EPIC","BUILDING_INTELLIGENCE_AGENCY","BUILDING_TOURIST_CENTER","BUILDING_OXFORD_UNIVERSITY","BUILDING_PALACE"))
    nationals = sorted(cur.fetchall())
    for national in nationals:
        print(translate(language,national[1]))
        national_template = {}
        national_template["id"] = wonder_id
        national_template["name"] = translate(language,national[1])
        national_template["production_cost"] = national[3]
        national_template["game_info"] = translate(language,national[5])
        national_template["strategy"] = translate(language,national[4])
        national_template["historical_info"] = translate(language,national[2])
        national_template["icon"] = "https://eyefyre.github.io/civvapi/images/wonder_icons/" + translate("en",national[1]).replace(" ","_").lower() + ".png"
        national_template["background_image"] = None
        national_template["quote"] = None

        cur.execute("SELECT Description FROM Technologies WHERE Type=?", (national[7],))
        prereq_tech = cur.fetchone()
        national_template["tech_prereq"] = None
        if prereq_tech != None:
            national_template["tech_prereq"] = {"name":translate("en",prereq_tech[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/tech/"+ translate("en",prereq_tech[0]).replace(" ","_").lower() + ".json"}
        wonder_id += 1


        if not os.path.exists("v1/"+ language + "/wonders"):
            os.makedirs("v1/"+ language + "/wonders")
        with open("v1/" + language + "/wonders/" + translate("en",national[1]).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(national_template, outfile,indent=4)
        wonder_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/wonders/"+ translate("en",wonder[1]).replace(" ","_").lower() + ".json"
        wonder_list.append(national_template)
        
    cur.execute("SELECT Type,Description,Civilopedia,Strategy,Help,Cost,TechPrereq from Projects WHERE Type=? OR Type=?",("PROJECT_MANHATTAN_PROJECT","PROJECT_APOLLO_PROGRAM"))
    projects = cur.fetchall()
    for project in projects:
        project_template = {}
        project_template["id"] = wonder_id
        project_template["name"] = translate(language,project[1])
        project_template["production_cost"] = project[5]
        project_template["game_info"] = translate(language,project[4])
        project_template["strategy"] = translate(language,project[3])
        project_template["historical_info"] = translate(language,project[2])
        project_template["icon"] = "https://eyefyre.github.io/civvapi/images/wonder_icons/" + translate("en",project[1]).replace(" ","_").lower() + ".png"
        project_template["background_image"] = None
        project_template["quote"] = None
        cur.execute("SELECT Description FROM Technologies WHERE Type=?", (project[6],))
        prereq_tech = cur.fetchone()
        project_template["tech_prereq"] = {"name":translate("en",prereq_tech[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/tech/"+ translate("en",prereq_tech[0]).replace(" ","_").lower() + ".json"}
        wonder_id += 1

        if not os.path.exists("v1/"+ language + "/wonders"):
            os.makedirs("v1/"+ language + "/wonders")
        with open("v1/" + language + "/wonders/" + translate("en",project[1]).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(project_template, outfile,indent=4)
        wonder_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/wonders/"+ translate("en",wonder[1]).replace(" ","_").lower() + ".json"
        wonder_list.append(project_template)

    if not os.path.exists("v1/"+ language + "/wonders"):
        os.makedirs("v1/"+ language + "/wonders")
    with open("v1/" + language + "/wonders/wonders.json", 'w') as outfile:
        json.dump(wonder_list, outfile,indent=4)
    
#6. Social Policies | True
def get_policies(language):
    print("SOCIAL POLICIES")
    policy_list = []
    policy_id = 1
    cur.execute("SELECT Type,Description,Civilopedia,Help,PolicyBranchType,Level FROM Policies WHERE PolicyBranchType !=?",("null",))
    policies = sorted(cur.fetchall())
    for policy in policies:
        print(translate(language,policy[1]))
        policy_template = {}
        policy_template["id"] = policy_id
        policy_template["name"] = translate(language,policy[1])
        policy_template["game_info"] = translate(language,policy[3])
        if policy[5] != 0:
            policy_template["game_info"] = translate(language,policy[3]).replace(translate(language,policy[1]),"")
        policy_template["historical_info"] = translate(language,policy[2])
        policy_template["icon"] = "https://eyefyre.github.io/civvapi/images/policy_icons/" + translate("en",policy[1]).replace(" ","_").lower() + ".png"

        prereq_policy_list = []
        prereq_policies = cur.execute("SELECT * FROM Policy_PrereqPolicies WHERE PolicyType=?",(policy[0],)).fetchall()
        for prereq_policy in prereq_policies:
            pol = cur.execute("SELECT Description FROM Policies WHERE Type=?",(prereq_policy[1],)).fetchone()
            prereq_policy_list.append({"name":translate(language,pol[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/policies/"+ translate("en",pol[0]).replace(" ","_").lower() + ".json"})
        policy_template["required_policies"] = prereq_policy_list
        policy_template["tenet_level"] = policy[5]
        
        branch = cur.execute("SELECT Type,Description,Help,EraPrereq FROM PolicyBranchTypes WHERE Type=?",(policy[4],)).fetchone()
        era = cur.execute("SELECT Description FROM Eras WHERE Type=?",(branch[3],)).fetchone()
        branch_template = {"name":translate(language,branch[1]),"game_info":translate(language,branch[2]),"prereq_era":None,"historical_info":None}
        if era != None:
            branch_template["prereq_era"] = translate(language,era[0])
        if policy[4] != "POLICY_BRANCH_FREEDOM" and policy[4] != "POLICY_BRANCH_AUTOCRACY" and policy[4] != "POLICY_BRANCH_ORDER":
            policy_branch = cur.execute("SELECT Civilopedia FROM Policies WHERE Type=? ",(branch[0].replace("BRANCH_",""),)).fetchone()
            branch_template["historical_info"] = translate(language,policy_branch[0])
        policy_template["branch"] = branch_template

        addon = ""
        if policy[1] == "TXT_KEY_POLICY_UNIVERSAL_HEALTHCARE":
            match policy[4]:
                case "POLICY_BRANCH_FREEDOM":
                    addon = "_F"
                case "POLICY_BRANCH_AUTOCRACY":
                    addon = "_A"
                case "POLICY_BRANCH_ORDER":
                    addon = "_O"
        policy_template["icon"] = ("https://eyefyre.github.io/civvapi/images/policy_icons/" + translate("en",policy[1]) + addon).replace(" ","_").lower() + ".png"
        if not os.path.exists("v1/"+ language + "/policies"):
            os.makedirs("v1/"+ language + "/policies")
        with open(("v1/" + language + "/policies/" + translate("en",policy[1]) + addon).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(policy_template, outfile,indent=4)
        policy_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/policies/"+ translate("en",policy[1]).replace(" ","_").lower() + ".json"
        policy_list.append(policy_template)

        policy_id += 1

    if not os.path.exists("v1/"+ language):
        os.makedirs("v1/"+ language)
    with open("v1/" + language + "/policies/policies.json", 'w') as outfile:
        json.dump(policy_list, outfile,indent=4)

#7. Specialists and Great people | True
def get_specialists_and_great_people(language):
    print("SPECIALISTS")
    specgreat_list = []
    specgreat_id = 1
    cur.execute("SELECT Type,Description,Civilopedia,Strategy,Help FROM Units WHERE Special=?",("SPECIALUNIT_PEOPLE",))
    great_people = cur.fetchall()
    for great_person in great_people:
        print(translate(language,great_person[1]))
        great_person_template = {}
        great_person_template["id"] = specgreat_id
        great_person_template["name"] = translate(language,great_person[1])
        great_person_template["game_info"] = translate(language,great_person[4])
        great_person_template["strategy"] = translate(language,great_person[3])
        great_person_template["historical_info"] = translate(language,great_person[2])
        great_person_template["icon"] = "https://eyefyre.github.io/civvapi/images/specialist_icons/" + translate("en",great_person[1]).replace(" ","_").lower() + ".png"

        if not os.path.exists("v1/"+ language + "/specialists"):
            os.makedirs("v1/"+ language + "/specialists")
        with open("v1/" + language + "/specialists/" + translate("en",great_person[1]).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(great_person_template, outfile,indent=4)
        great_person_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/specialists/"+ translate("en",great_person[1]).replace(" ","_").lower() + ".json"
        specgreat_list.append(great_person_template)

        specgreat_id += 1

    cur.execute("SELECT Type,Description,Strategy FROM Specialists")
    great_people = cur.fetchall()
    for great_person in great_people:
        great_person_template = {}
        great_person_template["id"] = specgreat_id
        great_person_template["name"] = translate(language,great_person[1]).split("|")[0]
        great_person_template["game_info"] = None
        great_person_template["strategy"] = translate(language,great_person[2])
        great_person_template["historical_info"] = None
        great_person_template["icon"] = "https://eyefyre.github.io/civvapi/images/specialist_icons/" + translate("en",great_person[1]).split("|")[0].replace(" ","_").lower() + ".png"

        if not os.path.exists("v1/"+ language + "/specialists"):
            os.makedirs("v1/"+ language + "/specialists")
        with open("v1/" + language + "/specialists/" + translate("en",great_person[1]).split("|")[0].replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(great_person_template, outfile,indent=4)
        great_person_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/specialists/"+ translate("en",great_person[1]).replace(" ","_").lower() + ".json"
        specgreat_list.append(great_person_template)

        specgreat_id += 1

    if not os.path.exists("v1/"+ language):
        os.makedirs("v1/"+ language)
    with open("v1/" + language + "/specialists/specialists.json", 'w') as outfile:
        json.dump(specgreat_list, outfile,indent=4)
#8. Civlizations & Leaders | True
def get_civilizations(language):
    print("CIVILIZATIONS")
    civilizations_list = []
    civilizations_id = 1
    cur.execute("SELECT Type,Description,ShortDescription,CivilopediaTag,Adjective,DawnOfManQuote FROM Civilizations WHERE Playable=?",(1,))
    civilizations = cur.fetchall()
    for civilization in civilizations:
        print(translate(language,civilization[2]))
        civilization_template = {}
        civilization_template["id"] = civilizations_id
        civilization_template["name"] = translate(language,civilization[2])
        civilization_template["icon"] = "https://eyefyre.github.io/civvapi/images/civ_icons/" + translate("en",civilization[2]).replace(" ","_").lower() + ".png"
        civilization_template["dawn_of_man"] = translate(language,civilization[5])



        unique_buildings = []
        buildings = cur.execute("SELECT BuildingType from Civilization_BuildingClassOverrides WHERE CivilizationType=?",(civilization[0],)).fetchall()
        for building in buildings:
            building_name = cur.execute("SELECT Description FROM Buildings WHERE Type=?",(building[0],)).fetchone()
            unique_buildings.append({"name":translate(language,building_name[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/buildings/"+ translate("en",building_name[0]).replace(" ","_").lower() + ".json"})
        civilization_template["unique_buildings"] = unique_buildings

        unique_units = []
        units = cur.execute("SELECT UnitType from Civilization_UnitClassOverrides WHERE CivilizationType=?",(civilization[0],)).fetchall()
        for unit in units:
            unit_name = cur.execute("SELECT Description FROM Units WHERE Type=?",(unit[0],)).fetchone()
            unique_units.append({"name":translate(language,unit_name[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/units/"+ translate("en",unit_name[0]).replace(" ","_").lower() + ".json"})
        civilization_template["unique_units"] = unique_units

        city_names = []
        cities = cur.execute("SELECT CityName FROM Civilization_CityNames WHERE CivilizationType=?",(civilization[0],)).fetchall()
        for city in cities:
            city_names.append(translate(language,city[0]))
        civilization_template["city_names"] = city_names

        
        spy_names = []
        spies = cur.execute("SELECT SpyName FROM Civilization_SpyNames WHERE CivilizationType=?",(civilization[0],)).fetchall() 
        for spy in spies:
            spy_names.append(translate(language,spy[0]))
        civilization_template["spy_names"] = spy_names

        historical_info = []
        info_flag = False
        info_id = 1
        while not info_flag:
            info_template = {"heading":None,"text":None}
            info_template["heading"] = translate(language,civilization[3] + "_HEADING_" + str(info_id))
            info_template["text"] = translate(language,civilization[3] + "_TEXT_" + str(info_id))
            info_id += 1
            if translate(language,civilization[3] + "_HEADING_" + str((info_id))) == []:
                info_flag = True
            historical_info.append(info_template)
        civilization_template["historical_info"] = historical_info


        leader_ID = cur.execute("SELECT LeaderheadType FROM Civilization_Leaders WHERE CivilizationType=?",(civilization[0],)).fetchone()[0]
        leader = cur.execute("SELECT * FROM Leaders WHERE Type=?",(leader_ID,)).fetchone()
        leader_template = {}
        leader_template["name"] = translate(language,leader[4] + "_NAME")
        leader_template["subtitle"] = translate(language,leader[4] + "_SUBTITLE")
        leader_template["lived"] = translate(language,leader[4] + "_LIVED")
        leader_template["icon"] = "https://eyefyre.github.io/civvapi/images/leader_icons/" + translate("en",leader[4] + "_NAME").replace(" ","_").lower() + ".png"

        trait_id = cur.execute("SELECT TraitType FROM Leader_Traits WHERE LeaderType=?",(leader[1],)).fetchone()[0]
        trait = cur.execute("SELECT Description,ShortDescription FROM Traits WHERE Type=?",(trait_id,)).fetchone()
        leader_template["trait"] = {"name":translate(language,trait[1]),"effect":translate(language,trait[0])}

        titles = []
        info_flag = False
        info_id = 1
        while not info_flag:
            titles.append(translate(language,leader[4] + "_TITLES_" + str(info_id)))
            info_id += 1
            if translate(language,leader[4] + "_TITLES_" + str((info_id))) == []:
                info_flag = True
            historical_info.append(info_template)
        leader_template["titles"] = titles

        historical_info = []
        info_flag = False
        info_id = 1
        while not info_flag:
            info_template = {"heading":None,"text":None}
            info_template["heading"] = translate(language,leader[4] + "_HEADING_" + str(info_id))
            info_template["text"] = translate(language,leader[4] + "_TEXT_" + str(info_id))
            info_id += 1
            if translate(language,leader[4] + "_HEADING_" + str((info_id))) == []:
                info_flag = True
            historical_info.append(info_template)
        leader_template["historical_info"] = historical_info


        civilization_template["leader"] = leader_template
        civilizations_id += 1

        if not os.path.exists("v1/"+ language + "/civilizations"):
            os.makedirs("v1/"+ language + "/civilizations")
        with open("v1/" + language + "/civilizations/" + translate("en",civilization[2]).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(civilization_template, outfile,indent=4)
        civilization_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/civilizations/"+ translate("en",civilization[2]).replace(" ","_").lower() + ".json"
        civilizations_list.append(civilization_template)

    if not os.path.exists("v1/"+ language):
        os.makedirs("v1/"+ language)
    with open("v1/" + language + "/civilizations/civilizations.json", 'w') as outfile:
        json.dump(civilizations_list, outfile,indent=4)

#10. City States | True
def get_city_states(language):
    print("CITY STATES")
    city_state_list = []
    state_id = 1
    cur.execute("SELECT Type,Description,Civilopedia,Adjective,MinorCivTrait FROM MinorCivilizations")
    states = cur.fetchall()
    for state in states:
        print(translate(language,state[1]))
        state_template = {}
        state_template["id"] = state_id
        state_template["name"] = translate(language,state[1])
        state_template["historical_info"] = translate(language,state[2])
        #state_template["citizen_adjective"] = translate(language,state[3])
        state_template["category"] = translate(language,"TXT_KEY_" + state[4])
        state_id += 1

        if not os.path.exists("v1/"+ language + "/citystates"):
            os.makedirs("v1/"+ language + "/citystates")
        with open("v1/" + language + "/citystates/" + translate("en",state[1]).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(state_template, outfile,indent=4)
        state_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/citystates/"+ translate("en",state[1]).replace(" ","_").lower() + ".json"
        city_state_list.append(state_template)

    if not os.path.exists("v1/"+ language):
        os.makedirs("v1/"+ language)
    with open("v1/" + language + "/citystates/citystates.json", 'w') as outfile:
        json.dump(city_state_list, outfile,indent=4)
    
#11. Terrain | True
def get_terrains(language):
    print("TERRAINS")
    terrain_list = []
    terrain_id = 1
    cur.execute("SELECT Type,Description,Civilopedia,Movement,Defense,Impassable FROM Terrains")
    terrains = cur.fetchall()
    for terrain in terrains:
        print(translate(language,terrain[1]))
        terrain_template={}
        terrain_template["id"] = terrain_id
        terrain_template["name"] = translate(language,terrain[1])
        terrain_template["historical_info"] = translate(language,terrain[2])
        terrain_template["icon"] = "https://eyefyre.github.io/civvapi/images/terrain_icons/" + translate("en",terrain[1]).replace(" ","_").lower() + ".png"
        terrain_template["movement_cost"] = terrain[3]
        if terrain[5] == 1:
            terrain_template["movement_cost"] = -1
        terrain_template["combat_modifier"] = terrain[4]

        ryields = cur.execute("SELECT * FROM Terrain_Yields WHERE TerrainType=?",(terrain[0],)).fetchall()
        yield_template = {"gold":0,"production":0,"science":0,"culture":0,"food":0,"faith":0,"happiness":0}
        for ryield in ryields:
            match ryield[1]:
                case "YIELD_FOOD":
                    yield_template["food"] = ryield[2]
                case "YIELD_PRODUCTION":
                    yield_template["production"] = ryield[2]
        terrain_template["yields"] = yield_template

        terrain_template["features"] = None
        terrain_template["resources"] = None

        terrain_features = cur.execute("SELECT * FROM Feature_TerrainBooleans WHERE TerrainType=?",(terrain[0],)).fetchall()
        terrain_f = []
        for feature in terrain_features:
            fature = cur.execute("SELECT Description FROM Features WHERE Type=?",(feature[0],)).fetchone()
            terrain_f.append({"name":translate(language,fature[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/features/"+ translate("en",fature[0]).replace(" ","_").lower() + ".json"})
        terrain_template["features"] = terrain_f

        terrain_resources = cur.execute("SELECT * FROM Resource_TerrainBooleans WHERE TerrainType=?",(terrain[0],)).fetchall()
        terrain_r = []
        for resource in terrain_resources:
            rsource = cur.execute("SELECT Description FROM Resources WHERE Type=?",(resource[0],)).fetchone()
            terrain_r.append({"name":translate(language,rsource[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/resources/"+ translate("en",rsource[0]).replace(" ","_").lower() + ".json"})
        terrain_template["resources"] = terrain_r
        
        terrain_id += 1

        if not os.path.exists("v1/"+ language + "/terrains"):
            os.makedirs("v1/"+ language + "/terrains")
        with open("v1/" + language + "/terrains/" + translate("en",terrain[1]).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(terrain_template, outfile,indent=4)
        terrain_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/terrains/"+ translate("en",terrain[1]).replace(" ","_").lower() + ".json"
        terrain_list.append(terrain_template)

    if not os.path.exists("v1/"+ language):
        os.makedirs("v1/"+ language)
    with open("v1/" + language + "/terrains/terrains.json", 'w') as outfile:
        json.dump(terrain_list, outfile,indent=4)
#12. Features | True  | Add FakeFeatures (Lake & River)
def get_features(language):
    print("FEATURES")
    feature_list = []
    feature_id = 1
    cur.execute("SELECT Type,Description,Civilopedia,Help,Defense,Movement,Impassable,InBorderHappiness FROM Features")
    features = cur.fetchall()
    for feature in features:
        print(translate(language,feature[1]))
        feature_template={}
        feature_template["id"] = feature_id
        feature_template["name"] = translate(language,feature[1])
        feature_template["historical_info"] = translate(language,feature[2])
        feature_template["icon"] = "https://eyefyre.github.io/civvapi/images/feature_icons/" + translate("en",feature[1]).replace(" ","_").lower() + ".png"
        feature_template["movement_cost"] = feature[5]
        if feature[6] == 1:
            feature_template["movement_cost"] = -1
        feature_template["combat_modifier"] = feature[4]

        ryields = cur.execute("SELECT * FROM Feature_YieldChanges WHERE FeatureType=?",(feature[0],)).fetchall()
        yield_template = {"gold":0,"production":0,"science":0,"culture":0,"food":0,"faith":0,"happiness":0}
        if feature[7] != 0:
            yield_template["happiness"] = feature[7]
        for ryield in ryields:
            match ryield[1]:
                case "YIELD_FOOD":
                    yield_template["food"] = ryield[2]
                case "YIELD_PRODUCTION":
                    yield_template["production"] = ryield[2]
                case "YIELD_GOLD":
                    yield_template["gold"] = ryield[2]
                case "YIELD_SCIENCE":
                    yield_template["science"] = ryield[2]
                case "YIELD_CULTURE":
                    yield_template["culture"] = ryield[2]
                case "YIELD_FAITH":
                    yield_template["faith"] = ryield[2]
        feature_template["yields"] = yield_template

        feature_resources = cur.execute("SELECT * FROM Resource_FeatureBooleans WHERE FeatureType=?",(feature[0],)).fetchall()
        feature_r = []
        for resource in feature_resources:
            rsource = cur.execute("SELECT Description FROM Resources WHERE Type=?",(resource[0],)).fetchone()
            feature_r.append({"name":translate(language,rsource[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/resources/"+ translate("en",rsource[0]).replace(" ","_").lower() + ".json"})
        feature_template["resources"] = feature_r
        
        feature_id += 1

        if not os.path.exists("v1/"+ language + "/features"):
            os.makedirs("v1/"+ language + "/features")
        with open("v1/" + language + "/features/" + translate("en",feature[1]).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(feature_template, outfile,indent=4)
        feature_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/features/"+ translate("en",feature[1]).replace(" ","_").lower() + ".json"
        feature_list.append(feature_template)

    if not os.path.exists("v1/"+ language):
        os.makedirs("v1/"+ language)
    with open("v1/" + language + "/features/features.json", 'w') as outfile:
        json.dump(feature_list, outfile,indent=4)
#13. Resources | True
def get_resources(language):
    print("RESOURCES")
    resource_list = []
    resource_id = 1
    cur.execute("SELECT Type,Description,Civilopedia,Help,TechReveal FROM Resources")
    resources = cur.fetchall()
    for resource in resources:
        print(translate(language,resource[1]))
        resource_template={}
        resource_template["id"] = resource_id
        resource_template["name"] = translate(language,resource[1])
        resource_template["game_info"] = translate(language,resource[3])
        resource_template["historical_info"] = translate(language,resource[2])
        resource_template["icon"] = "https://eyefyre.github.io/civvapi/images/resource_icons/" + translate("en",resource[1]).replace(" ","_").lower() + ".png"
        resource_template["prereq_tech"] = None
        prereq_tech = cur.execute("SELECT Description FROM Technologies WHERE Type=?",(resource[4],)).fetchone()
        if prereq_tech != None:
            resource_template["prereq_tech"] = {"name":translate(language,prereq_tech[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/tech/"+ translate("en",prereq_tech[0]).replace(" ","_").lower() + ".json"}

        ryields = cur.execute("SELECT * FROM Resource_YieldChanges WHERE ResourceType=?",(resource[0],)).fetchall()
        yield_template = {"gold":0,"production":0,"science":0,"culture":0,"food":0,"faith":0,"happiness":0}
        for ryield in ryields:
            match ryield[1]:
                case "YIELD_GOLD":
                    yield_template["gold"] = ryield[2]
                case "YIELD_FOOD":
                    yield_template["food"] = ryield[2]
                case "YIELD_PRODUCTION":
                    yield_template["production"] = ryield[2]
        resource_template["yields"] = yield_template
            
        improvements = cur.execute("SELECT * FROM Improvement_ResourceTypes WHERE ResourceType=?",(resource[0],)).fetchall()
        improved_by = []
        for improvement in improvements:
            improve = cur.execute("SELECT Description FROM Improvements WHERE Type=?",(improvement[0],)).fetchone()
            improved_by.append({"name":translate(language,improve[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/improvements/"+ translate("en",improve[0]).replace(" ","_").lower() + ".json"})
        resource_template["improved_by"] = improved_by

        terrain_feature_list = []
        features = cur.execute("SELECT * FROM Resource_FeatureBooleans WHERE ResourceType=?",(resource[0],)).fetchall()
        for feature in features:
            res_feat = cur.execute("SELECT Description FROM Features WHERE Type=?",(feature[1],)).fetchone()
            terrain_feature_list.append({"name":translate(language,res_feat[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/features/" + translate("en",res_feat[0]).replace(" ","_").lower() + ".json"})
        
        terrains = cur.execute("SELECT * FROM Resource_TerrainBooleans WHERE ResourceType=?",(resource[0],)).fetchall()
        for terrain in terrains:
            res_terr = cur.execute("SELECT Description FROM Terrains WHERE Type=?",(terrain[1],)).fetchone()
            terrain_feature_list.append({"name":translate(language,res_terr[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/terrains/" + translate("en",res_terr[0]).replace(" ","_").lower() + ".json"})
        
        resource_template["terrains_found_on"] = terrain_feature_list
        
        resource_id += 1

        if not os.path.exists("v1/"+ language + "/resources"):
            os.makedirs("v1/"+ language + "/resources")
        with open("v1/" + language + "/resources/" + translate("en",resource[1]).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(resource_template, outfile,indent=4)
        resource_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/resources/"+ translate("en",resource[1]).replace(" ","_").lower() + ".json"
        resource_list.append(resource_template)

    if not os.path.exists("v1/"+ language):
        os.makedirs("v1/"+ language)
    with open("v1/" + language + "/resources/resources.json", 'w') as outfile:
        json.dump(resource_list, outfile,indent=4)
#14. Improvements True | Add Roads + RailRoads
def get_improvements(language):
    print("IMPROVEMENTS")
    improvement_list = []
    improvement_id = 1
    cur.execute("SELECT Type,Description,Civilopedia,CivilizationType FROM Improvements")
    improvements = cur.fetchall()
    for improvement in improvements:
        print(translate(language,improvement[1]))
        improvement_template = {}
        improvement_template["id"] = improvement_id
        improvement_template["name"] = translate(language,improvement[1])
        improvement_template["game_info"] = translate(language,improvement[2])
        improvement_template["icon"] = "https://eyefyre.github.io/civvapi/images/improvement_icons/" + translate("en",improvement[1]).replace(" ","_").lower() + ".png"
        improvement_template["nearby_mountain_bonus"] = {"food":None}
        bonus_template = {"food":None}
        mount_bonus = cur.execute("SELECT * FROM Improvement_AdjacentMountainYieldChanges WHERE ImprovementType=?",(improvement[0],)).fetchall()
        for bonus in mount_bonus:
            match bonus[1]:
                case "YIELD_FOOD":
                    bonus_template["food"] = bonus[2]
        improvement_template["nearby_mountain_bonus"] = bonus_template

        valid_build_list = []
        valid_terrains = cur.execute("SELECT * FROM Improvement_ValidTerrains WHERE ImprovementType=?",(improvement[0],)).fetchall()
        for valid_terrain in valid_terrains:
            terrain_name = cur.execute("SELECT Description FROM Terrains WHERE Type=?",(valid_terrain[1],)).fetchone()
            valid_build_list.append({"name":translate(language,terrain_name[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/terrains/"+ translate("en",terrain_name[0]).replace(" ","_").lower() + ".json"})
        valid_features = cur.execute("SELECT * FROM Improvement_ValidFeatures WHERE ImprovementType=?",(improvement[0],)).fetchall()
        for valid_feature in valid_features:
            feature_name = cur.execute("SELECT Description FROM Features WHERE Type=?",(valid_feature[1],)).fetchone()
            valid_build_list.append({"name":translate(language,feature_name[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/features/"+ translate("en",feature_name[0]).replace(" ","_").lower() + ".json"})
        improvement_template["can_be_built_on"] = valid_build_list


        improved_resource_list = []
        improved_resources = cur.execute("SELECT ImprovementType,ResourceType FROM Improvement_ResourceTypes WHERE ImprovementType=?",(improvement[0],)).fetchall()
        for resource in improved_resources:
            resource_name = cur.execute("SELECT Description FROM Resources WHERE Type=?",(resource[1],)).fetchone()
            improved_resource_list.append({"name":translate(language,resource_name[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/resources/"+ translate("en",resource_name[0]).replace(" ","_").lower() + ".json"})
        improvement_template["improves_resources"] = improved_resource_list


        improvement_template["prereq_tech"] = None
        build_name = improvement[0].replace("IMPROVEMENT","BUILD").replace("ARCHAEOLOGICAL","ARCHAEOLOGY")
        prereq_tech = cur.execute("SELECT PrereqTech from Builds WHERE Type=? AND PrereqTech!=?",(build_name,"null",)).fetchall()
        for tech in prereq_tech:
            tec = cur.execute("SELECT Description from Technologies WHERE Type=?",(tech[0],)).fetchone()
            improvement_template["prereq_tech"] = {"name":translate(language,tec[0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/tech/"+ translate("en",tec[0]).replace(" ","_").lower() + ".json"}


        req_civs = cur.execute("SELECT ShortDescription FROM Civilizations WHERE Type=?",(improvement[3],)).fetchall()
        improvement_template["required_civ"] = None
        if req_civs != []:
            improvement_template["required_civ"] = {"name":translate("en",req_civs[0][0]),"url":"https://eyefyre.github.io/civvapi/v1/" + language + "/civilizations/"+ translate("en",req_civs[0][0]).replace(" ","_").lower() + ".json"}
        
        ryields = cur.execute("SELECT * FROM Improvement_Yields WHERE ImprovementType=?",(improvement[0],)).fetchall()
        yield_template = {"gold":0,"production":0,"science":0,"culture":0,"food":0,"faith":0,"happiness":0}
        for ryield in ryields:
            match ryield[1]:
                case "YIELD_FOOD":
                    yield_template["food"] = ryield[2]
                case "YIELD_PRODUCTION":
                    yield_template["production"] = ryield[2]
                case "YIELD_GOLD":
                    yield_template["gold"] = ryield[2]
                case "YIELD_SCIENCE":
                    yield_template["science"] = ryield[2]
                case "YIELD_CULTURE":
                    yield_template["culture"] = ryield[2]
                case "YIELD_FAITH":
                    yield_template["faith"] = ryield[2]
        improvement_template["yields"] = yield_template
        improvement_id += 1

        if not os.path.exists("v1/"+ language + "/improvements"):
            os.makedirs("v1/"+ language + "/improvements")
        with open("v1/" + language + "/improvements/" + translate("en",improvement[1]).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(improvement_template, outfile,indent=4)
        improvement_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/improvements/"+ translate("en",improvement[1]).replace(" ","_").lower() + ".json"
        improvement_list.append(improvement_template)

    if not os.path.exists("v1/"+ language):
        os.makedirs("v1/"+ language)
    with open("v1/" + language + "/improvements/improvements.json", 'w') as outfile:
        json.dump(improvement_list, outfile,indent=4)
#15. Religions | True
def get_religions(language):
    print("RELIGIONS")
    religion_list = []
    religion_id = 1
    cur.execute("SELECT Description,Civilopedia FROM Religions WHERE ID!=?",(0,))
    religions = cur.fetchall()
    for religion in religions:
        print(translate(language,religion[0]))
        religion_template={}
        religion_template["id"] = religion_id
        religion_template["name"] = translate(language,religion[0])
        religion_template["summary"] = translate(language,religion[1])
        religion_id += 1

        if not os.path.exists("v1/"+ language + "/religions"):
            os.makedirs("v1/"+ language + "/religions")
        with open("v1/" + language + "/religions/" + translate("en",religion[0]).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(religion_template, outfile,indent=4)
        religion_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/religions/"+ translate("en",religion[1]).replace(" ","_").lower() + ".json"
        religion_list.append(religion_template)

    if not os.path.exists("v1/"+ language):
        os.makedirs("v1/"+ language)
    with open("v1/" + language + "/religions/religions.json", 'w') as outfile:
        json.dump(religion_list, outfile,indent=4)
#16. Beliefs | True
def get_beliefs(language):
    print("BELIEFS")
    belief_list = []
    belief_id = 1
    cur.execute("SELECT Type,Description,ShortDescription,Pantheon,Founder,Follower,Enhancer,Reformation FROM Beliefs")
    beliefs = cur.fetchall()
    for belief in beliefs:
        print(translate(language,belief[2]))
        belief_template={}
        belief_template["id"] = belief_id
        belief_template["name"] = translate(language,belief[2])
        belief_template["summary"] = translate(language,belief[1])
        belief_template["belief_category"] = None
        if belief[3] == 1:
            belief_template["belief_category"] = translate(language,"TXT_KEY_CONCEPT_RELIGION_PANTHEON_BELIEFS_TOPIC")
        if belief[4] == 1:
            belief_template["belief_category"] = translate(language,"TXT_KEY_CONCEPT_RELIGION_FOUNDER_TOPIC")
        if belief[5] == 1:
            belief_template["belief_category"] = translate(language,"TXT_KEY_CONCEPT_RELIGION_FOLLOWER_TOPIC")
        if belief[6] == 1:
            belief_template["belief_category"] = translate(language,"TXT_KEY_CONCEPT_RELIGION_ENHANCER_TOPIC")
        if belief[7] == 1:
            belief_template["belief_category"] = translate(language,"TXT_KEY_PEDIA_BELIEFS_CATEGORY_6")
        belief_id += 1

        if not os.path.exists("v1/"+ language + "/beliefs"):
            os.makedirs("v1/"+ language + "/beliefs")
        with open("v1/" + language + "/beliefs/" + translate("en",belief[2]).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(belief_template, outfile,indent=4)
        belief_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/beliefs/"+ translate("en",belief[2]).replace(" ","_").lower() + ".json"
        belief_list.append(belief_template)

    if not os.path.exists("v1/"+ language):
        os.makedirs("v1/"+ language)
    with open("v1/" + language + "/beliefs/beliefs.json", 'w') as outfile:
        json.dump(belief_list, outfile,indent=4)
#17. World Congress | true
def get_resolutions(language):
    resolution_list = []
    resolution_id = 1
    resolutions = cur.execute("SELECT Type,Description,Help FROM Resolutions").fetchall()
    for resolution in resolutions:
        print(translate(language,resolution[1]))
        resolution_template = {}
        resolution_template["resolution_id"] = resolution_id
        resolution_template["name"] = translate(language,resolution[1])
        resolution_template["summary"] = translate(language,resolution[2])
        resolution_template["project_prizes"] = None
        if resolution[0] == "RESOLUTION_WORLD_FAIR":
            prize_template = {"gold":translate(language,"TXT_KEY_LEAGUE_PROJECT_REWARD_WORLD_FAIR_3_HELP"),"silver":translate(language,"TXT_KEY_LEAGUE_PROJECT_REWARD_WORLD_FAIR_2_HELP"),"bronze":translate(language,"TXT_KEY_LEAGUE_PROJECT_REWARD_WORLD_FAIR_1_HELP")}
            resolution_template["project_prizes"] = prize_template
            resolution_template["summary"] = translate(language,resolution[2]).replace(":","").replace("{TXT_KEY_LEAGUE_PROJECT_REWARD_WORLD_FAIR_3_HELP}","").replace("{TXT_KEY_LEAGUE_PROJECT_REWARD_WORLD_FAIR_2_HELP}","").replace("{TXT_KEY_LEAGUE_PROJECT_REWARD_WORLD_FAIR_1_HELP}","")
        if resolution[0] == "RESOLUTION_WORLD_GAMES":
            prize_template = {"gold":translate(language,"TXT_KEY_LEAGUE_PROJECT_REWARD_WORLD_GAMES_3_HELP"),"silver":translate(language,"TXT_KEY_LEAGUE_PROJECT_REWARD_WORLD_GAMES_2_HELP"),"bronze":translate(language,"TXT_KEY_LEAGUE_PROJECT_REWARD_WORLD_GAMES_1_HELP")}
            resolution_template["project_prizes"] = prize_template
            resolution_template["summary"] = translate(language,resolution[2]).replace(":","").replace("{TXT_KEY_LEAGUE_PROJECT_REWARD_WORLD_GAMES_3_HELP}","").replace("{TXT_KEY_LEAGUE_PROJECT_REWARD_WORLD_GAMES_2_HELP}","").replace("{TXT_KEY_LEAGUE_PROJECT_REWARD_WORLD_GAMES_1_HELP}","").replace("  "," ")
        if resolution[0] == "RESOLUTION_INTERNATIONAL_SPACE_STATION":
            prize_template = {"gold":translate(language,"TXT_KEY_LEAGUE_PROJECT_REWARD_ISS_3_HELP").replace("({TXT_KEY_BUILDING_INTERNATIONAL_SPACE_STATION_HELP})","") + translate(language,"TXT_KEY_BUILDING_INTERNATIONAL_SPACE_STATION_HELP"),"silver":translate(language,"TXT_KEY_LEAGUE_PROJECT_REWARD_ISS_2_HELP"),"bronze":translate(language,"TXT_KEY_LEAGUE_PROJECT_REWARD_ISS_1_HELP")}
            resolution_template["project_prizes"] = prize_template
            resolution_template["summary"] = translate(language,resolution[2]).replace(":","").replace("{TXT_KEY_LEAGUE_PROJECT_REWARD_ISS_3_HELP}","").replace("{TXT_KEY_LEAGUE_PROJECT_REWARD_ISS_2_HELP}","").replace("{TXT_KEY_LEAGUE_PROJECT_REWARD_ISS_1_HELP}","").replace("  "," ")


        resolution_id += 1
        if not os.path.exists("v1/"+ language + "/resolutions"):
            os.makedirs("v1/"+ language + "/resolutions")
        with open("v1/" + language + "/resolutions/" + translate("en",resolution[1]).replace(" ","_").lower() + ".json", 'w') as outfile:
            json.dump(resolution_template, outfile,indent=4)
        resolution_template["url"] = "https://eyefyre.github.io/civvapi/v1/" + language + "/resolutions/"+ translate("en",resolution[1]).replace(" ","_").lower() + ".json"
        resolution_list.append(resolution_template)

    if not os.path.exists("v1/"+ language):
        os.makedirs("v1/"+ language)
    with open("v1/" + language + "/resolutions/resolutions.json", 'w') as outfile:
        json.dump(resolution_list, outfile,indent=4)


for language in language_list:
    print(language)
    get_technologies(language)
    get_units(language)
    get_promotions(language)
    get_buildings(language)
    get_wonders(language)
    get_policies(language)
    get_specialists_and_great_people(language)
    get_civilizations(language)
    get_city_states(language)
    get_terrains(language)
    get_features(language)
    get_resources(language)
    get_improvements(language)
    get_religions(language)
    get_beliefs(language)
    get_resolutions(language)

