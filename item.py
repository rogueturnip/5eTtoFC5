# vim: set tabstop=8 softtabstop=0 expandtab shiftwidth=4 smarttab : #
import xml.etree.cElementTree as ET
import re
import utils
import json
import os
from slugify import slugify
from shutil import copyfile

def parseItem(m, compendium, args):
    if '_copy' in m:
        if args.verbose:
            print("COPY: " + m['name'] + " from " + m['_copy']['name'] + " in " + m['_copy']['source'])
        xtrsrc = "./data/items.json"
        try:
            with open(xtrsrc) as f:
                d = json.load(f)
                f.close()
            mcpy = m
            for mn in d['item']:
                itemfound = False
                if mn['name'] == mcpy['_copy']['name']:
                    m = mn
                    m['name'] = mcpy['name']
                    m['source'] = mcpy['source']
                    if "otherSources" in mcpy:
                        m["otherSources"] = mcpy["otherSources"]
                    m['page'] = mcpy['page']
                    if '_mod' in mcpy['_copy']:
                        m = utils.modifyItem(m,mcpy['_copy']['_mod'])
                    itemfound = True
                    break
            if not itemfound:
                print("Could not find ",mcpy['_copy']['name'])
        except IOError as e:
            if args.verbose:
                print ("Could not load additional source ({}): {}".format(e.errno, e.strerror))
            return

    itm = ET.SubElement(compendium, 'item')
    name = ET.SubElement(itm, 'name')
    name.text = m['name']

    if args.nohtml:
        heading = ET.SubElement(itm, 'detail')
    else:
        heading = ET.SubElement(itm, 'heading')
    headings = []

    typ = ET.SubElement(itm, 'type')
    if 'type' in m:
        typ.text = m['type']
        if m['type'] == "AIR":
            typ.text = 'G'
        if m['type'] == "AT":
            typ.text = 'G'
        if m['type'] == "FD":
            typ.text = 'G'
        if m['type'] == "GS":
            typ.text = 'G'
        if m['type'] == "INS":
            typ.text = 'G'
        if m['type'] == "MNT":
            typ.text = 'G'
        if m['type'] == "MR":
            typ.text = 'W'
        if m['type'] == "OTH":
            typ.text = 'G'
        if m['type'] == "SCF":
            if 'rod' in m['name'].lower():
                typ.text = 'RD'
            elif 'wand' in m['name'].lower():
                typ.text = 'WD'
            elif 'staff' in m['name'].lower():
                typ.text = 'ST'
            typ.text = 'G'
        if m['type'] == "SHP":
            typ.text = 'G'
        if m['type'] == "T":
            typ.text = 'G'
        if m['type'] == "TAH":
            typ.text = 'G'
        if m['type'] == "TG":
            typ.text = 'G'
        if m['type'] == "VEH":
            typ.text = 'G'
        if m['type'] == 'GV':
            typ.text = 'G'
            headings.append("Generic Variant")

    if 'wondrous' in m and m['wondrous']:
        magic = ET.SubElement(itm, 'magic')
        magic.text = "1"
        headings.append("Wondrous item (tattoo)" if 'tattoo' in m and m['tattoo'] else "Wondrous item")
        if 'type' not in m:
            typ.text = 'W'

    if 'tier' in m: headings.append(m['tier']) 

    if 'curse' in m and m['curse']: headings.append("Cursed item")

    weight = ET.SubElement(itm, 'weight')
    if 'weight' in m: weight.text = str(m['weight'])

    if 'rarity' in m and m['rarity'] != 'None' and m['rarity'] != 'Unknown' and not args.nohtml:
        rarity = ET.SubElement(itm, 'rarity')
        rarity.text = str(m['rarity']).title()
        if m['rarity'] != 'None' and m['rarity'] != 'Unknown': headings.append(str(m['rarity']).title())


    if 'value' in m:
        value = ET.SubElement(itm, 'value')
        if args.nohtml:
            value.text = str(m['value']/100)
        elif m['value'] >= 100:
            value.text = "{:g} gp".format(m['value']/100)
        elif m['value'] >= 10:
            value.text = "{:g} sp".format(m['value']/10)
        else:
            value.text = "{:g} cp".format(m['value'])

    if 'staff' in m and m['staff']:
        headings.append('Staff')
        if 'type' not in m or m['type'] == 'SCF':
            typ.text = 'ST'

    if 'wand' in m and m['wand']:
        headings.append('Wand')
        if 'type' not in m or m['type'] == 'SCF':
            typ.text = 'WD'

    if 'weapon' in m and m['weapon'] and 'weaponCategory' in m:
        headings.append(m['weaponCategory'] + " Weapon")
        if m['weaponCategory'] == 'martial':
            if 'property' in m:
                m['property'].append('M')
            else:
                m['property'] = ['M']

    prop = ET.SubElement(itm, 'property')
    if 'property' in m: 
        if 'AF' in m['property']:
            headings.append("Ammunication (futuristic)")
            m['property'] = list(filter(lambda x: (x != 'AF'), m['property']))
            if 'A' not in m['property']: 
                m['property'].append('A')
        if 'RLD' in m['property']:
            headings.append("Reload")
            m['property'] = list(filter(lambda x: (x != 'RLD'), m['property']))
            if 'LD' not in m['property']: m['property'].append('LD')
        if 'BF' in m['property']:
            headings.append("Burst Fire")
            m['property'] = list(filter(lambda x: (x != 'BF'), m['property']))
            if 'R' not in m['property']: m['property'].append('R')
        prop.text = ",".join(m['property'])

    if 'type' in m:
        if m['type'] == 'LA':
            headings.append("Light Armor")
        elif m['type'] == 'MA':
            headings.append("Medium Armor")
        elif m['type'] == 'HA':
            headings.append("Heavy Armor")
        elif m['type'] == 'S':
            headings.append("Shield")
        elif m['type'] == 'SCF':
            headings.append("Spellcasting Focus")
        elif m['type'] == 'R':
            headings.append('Ranged Weapon')
        elif m['type'] == 'M':
            headings.append('Melee Weapon')
        elif m['type'] == 'A':
            headings.append('Ammunition')
        elif m['type'] == 'G':
            headings.append('Adventuring Gear')
        elif m['type'] == 'T':
            headings.append('Tools')
        elif m['type'] == 'AT':
            headings.append('Artisan Tools')
        elif m['type'] == 'GS':
            headings.append('Gaming Set')
        elif m['type'] == 'TG':
            headings.append('Trade Good')
        elif m['type'] == 'INS':
            headings.append('Instrument')
        elif m['type'] == 'MNT':
            headings.append('Mount')
        elif m['type'] == 'VEH':
            headings.append('Vehicle (land)')
        elif m['type'] == 'AIR':
            headings.append('Vehicle (air)')
        elif m['type'] == 'SHP':
            headings.append('Vehicle (water)')
        elif m['type'] == 'TAH':
            headings.append('Tack and Harness')
        elif m['type'] == 'FD':
            headings.append('Food and Drink')
        elif m['type'] == 'MR':
            headings.append('Magic Rune')
        elif m['type'] == 'OTH':
            headings.append('Other')
    if not args.nohtml:
        attunement = ET.SubElement(itm, 'attunement')
        if 'reqAttune' in m:
            if m['reqAttune'] == True:
                attunement.text = "Requires Attunement"
            else:
                attunement.text = "Requires Attunement " + m['reqAttune']
            headings.append("({})".format(attunement.text))

    if 'dmg1' in m:
        dmg1 = ET.SubElement(itm, 'dmg1')
        dmg1.text = utils.remove5eShit(m['dmg1'])


    if 'dmg2' in m:
        dmg2 = ET.SubElement(itm, 'dmg2')
        dmg2.text = utils.remove5eShit(m['dmg2'])

    if 'dmgType' in m:
        dmgType = ET.SubElement(itm, 'dmgType')
        if m['dmgType'] == 'O':
            dmgType.text = 'FC'
        elif m['dmgType'] == 'I':
            dmgType.text = 'PS'
        else:
            dmgType.text = m['dmgType']

    if 'range' in m:
        rng = ET.SubElement(itm, 'range')
        rng.text = m['range']


    if 'ac' in m:
        ac = ET.SubElement(itm, 'ac')
        ac.text = str(m['ac'])

    if 'bonus' in m:
        if 'type' in m and m['type'] in ['LA','MA','HA','S']:
            bonus = ET.SubElement(itm, 'modifier', {"category":"bonus"})
            bonus.text = "ac {}".format(m['bonus'])
        elif 'type' in m and m['type'] in ['M','R','A']:
            bonus = ET.SubElement(itm, 'modifier', {"category":"bonus"})
            bonus.text = "weapon attack {}".format(m['bonus'])
            bonus = ET.SubElement(itm, 'modifier', {"category":"bonus"})
            bonus.text = "weapon damage {}".format(m['bonus'])
        elif 'staff' in m and m['staff']:
            bonus = ET.SubElement(itm, 'modifier', {"category":"bonus"})
            bonus.text = "weapon attack {}".format(m['bonus'])
            bonus = ET.SubElement(itm, 'modifier', {"category":"bonus"})
            bonus.text = "weapon damage {}".format(m['bonus'])
        else:
            print(m)

    if 'poison' in m and m['poison']:
        headings.append('Poison')
        if 'type' not in m:
            typ.text = 'G'


    if 'entries' not in m:
        m['entries'] = []
        if 'tattoo' in m and m['tattoo']:
            m['entries'].append("Produced by a special needle, this magic tattoo features designs that emphasize one color{}.".format(
                " ({})".format(m['color']) if 'color' in m else ''))
            m['entries'].append( {
                "type": "entries",
                "name": "Tattoo Attunement",
                "entries": [ "To attune to this item, you hold the needle to your skin where you want the tattoo to appear, pressing the needle there throughout the attunement process. When the attunement is complete, the needle turns into the ink that becomes the tattoo, which appears on the skin.","If your attunement to the tattoo ends, the tattoo vanishes, and the needle reappears in your space." ] } )
    if 'resist' in m:
        if 'type' in m:
            if m['type'] == "LA" or m['type'] == "MA" or m['type'] == "HA":
                m['entries'].append("You have resistance to {} damage while you wear this armor.".format(m['resist']))
            elif m['type'] == "RG":
                m['entries'].append("You have resistance to {} damage while wearing this ring.".format(m['resist']))
            elif m['type'] == "P":
                m['entries'].append("When you drink this potion, you gain resistance to {} damage for 1 hour.".format(m['resist']))
        elif 'tattoo' in m and m['tattoo']:
            m['entries'].append( {
                "type": "entries",
                "name": "Damage Resistance",
                "entries": [
                    "While the tattoo is on your skin, you have resistance to {} damage".format(m['resist'])
                    ] } )
            m['entries'].append( {
                "type": "entries",
                "name": "Damage Absorption",
                "entries": ["When you take {} damage, you can use your reaction to gain immunity against that instance of the damage, and you regain a number of hit points equal to half the damage you would have taken. Once this reaction is used, it can't be used again until the next dawn.".format(m['resist'])] } )

    if 'stealth' in m and m['stealth']:
        stealth = ET.SubElement(itm, 'stealth')
        stealth.text = "1"
        m['entries'].append("The wearer has disadvantage on Stealth (Dexterity) checks.")

    if 'strength' in m:
        strength = ET.SubElement(itm, 'strength')
        strength.text = str(m['strength'] or '')
        if m['type'] == "HA":
            m['entries'].append("If the wearer has a Strength score lower than {}, their speed is reduced by 10 feet.".format(m['strength']))

    heading.text = ", ".join(headings)
    
#    if args.nohtml:
#        try:
#            itm.remove(heading)
#        except:
#            pass

    if 'items' in m:
        if 'scfType' in m:
            if m['scfType'] == "arcane":
                m['entries'].insert(0,"An arcane focus is a special item–an orb, a crystal, a rod, a specially constructed staff, a wand-like length of wood, or some similar item–designed to channel the power of arcane spells. A sorcerer, warlock, or wizard can use such an item as a spellcasting focus.")
            elif m['scfType'] == "druid":
                m['entries'].insert(0,"A druidic focus might be a sprig of mistletoe or holly, a wand or scepter made of yew or another special wood, a staff drawn whole out of a living tree, or a totem object incorporating feathers, fur, bones, and teeth from sacred animals. A druid can use such an object as a spellcasting focus.")
            elif m['scfType'] == "holy":
                m['entries'].insert(0,"A holy symbol is a representation of a god or pantheon. It might be an amulet depicting a symbol representing a deity, the same symbol carefully engraved or inlaid as an emblem on a shield, or a tiny box holding a fragment of a sacred relic. A cleric or paladin can use a holy symbol as a spellcasting focus. To use the symbol in this way, the caster must hold it in hand, wear it visibly, or bear it on a shield.")
        for i in m['items']:
            if args.nohtml:
                m['entries'].append(re.sub(r'^(.*?)(\|.*?)?$',r'\1',i))
            else:
                m['entries'].append(re.sub(r'^(.*?)(\|.*?)?$',r'<item>\1</item>',i))
    elif 'scfType' in m:
        if m['scfType'] == "arcane":
            m['entries'].insert(0,"An arcane focus is a special item designed to channel the power of arcane spells. A sorcerer, warlock, or wizard can use such an item as a spellcasting focus.")
        elif m['scfType'] == "druid":
            m['entries'].insert(0,"A druid can use this object as a spellcasting focus.")
        elif m['scfType'] == "holy":
            m['entries'].insert(0,"A holy symbol is a representation of a god or pantheon.")
            m['entries'].insert(1,"A cleric or paladin can use a holy symbol as a spellcasting focus. To use the symbol in this way, the caster must hold it in hand, wear it visibly, or bear it on a shield.")

    if 'lootTables' in m and not args.srd:
        if args.nohtml:
            m['entries'].append("Found On: {}".format(", ".join(m['lootTables'])))
        else:
            m['entries'].append("<i>Found On: {}</i> ".format(", ".join(m['lootTables'])))


    if 'source' in m and not args.srd:
        slug = slugify(m["name"])
        if args.addimgs and os.path.isdir("img") and not os.path.isfile(os.path.join(args.tempdir,"items", slug + ".png")) and not os.path.isfile(os.path.join(args.tempdir,"items",slug+".jpg")):
            if not os.path.isdir(os.path.join(args.tempdir,"items")):
                os.mkdir(os.path.join(args.tempdir,"items"))
            if 'image' in m:
                artworkpath = m['image']
            else:
                artworkpath = None
            itemname = m["original_name"] if "original_name" in m else m["name"]
            if artworkpath and os.path.isfile("./img/" + artworkpath):
                artworkpath = "./img/" + artworkpath
            elif os.path.isfile("./img/items/" + m["source"] + "/" + itemname + ".jpg"):
                artworkpath = "./img/items/" + m["source"] + "/" + itemname + ".jpg"
            elif os.path.isfile("./img/items/" + m["source"] + "/" + itemname + ".png"):
                artworkpath = "./img/items/" + m["source"] + "/" + itemname + ".png"
            elif os.path.isfile("./img/" + m["source"] + "/" + itemname + ".png"):
                artworkpath = "./img/" + m["source"] + "/" + itemname + ".png"
            elif os.path.isfile("./img/" + m["source"] + "/" + itemname + ".jpg"):
                artworkpath = "./img/" + m["source"] + "/" + itemname + ".jpg"
            elif os.path.isfile("./img/items/" + "/" + itemname + ".jpg"):
                artworkpath = "./img/items/" + "/" + itemname + ".jpg"
            elif os.path.isfile("./img/items/" + "/" + itemname + ".png"):
                artworkpath = "./img/items/" + "/" + itemname + ".png"
            elif os.path.isfile("./img/" + "/" + itemname + ".png"):
                artworkpath = "./img/" + "/" + itemname + ".png"
            elif os.path.isfile("./img/" + "/" + itemname + ".jpg"):
                artworkpath = "./img/" + "/" + itemname + ".jpg"
            if artworkpath is not None:
                ext = os.path.splitext(artworkpath)[1]
                copyfile(artworkpath, os.path.join(args.tempdir,"items",slug + ext))
                imagetag = ET.SubElement(itm, 'image')
                imagetag.text = slug + ext
        elif args.addimgs and os.path.isfile(os.path.join(args.tempdir,"items", slug + ".png")):
            imagetag = ET.SubElement(itm, 'image')
            imagetag.text = slug + ".png"
        elif args.addimgs and os.path.isfile(os.path.join(args.tempdir,"items", slug + ".jpg")):
            imagetag = ET.SubElement(itm, 'image')
            imagetag.text = slug + ".jpg"

        sourcetext = "{} p. {}".format(
            utils.getFriendlySource(m['source'],args), m['page']) if 'page' in m and m['page'] != 0 else utils.getFriendlySource(m['source'],args)

        if 'otherSources' in m and m["otherSources"] is not None:
            for s in m["otherSources"]:
                sourcetext += ", "
                sourcetext += "{} p. {}".format(
                    utils.getFriendlySource(s["source"],args), s["page"]) if 'page' in s and s["page"] != 0 else utils.getFriendlySource(s["source"],args)
        if 'entries' in m:
            if args.nohtml:
                m['entries'].append("Source: {}".format(sourcetext))
            else:
                m['entries'].append("<i>Source: {}</i>".format(sourcetext))
        else:
            if args.nohtml:
                m['entries'] = ["Source: {}".format(sourcetext)]
            else:
                m['entries'] = ["<i>Source: {}</i>".format(sourcetext)]
        if not args.nohtml:
            source = ET.SubElement(itm, 'source')
            source.text = sourcetext
    bodyText = ET.SubElement(itm, 'text')
    bodyText.text = ""

    if 'entries' in m:
        for e in m['entries']:
            if type(e) == dict and e['type'] == 'table':
                if 'caption' in e:
                    bodyText.text += "{}\n".format(e['caption'])
                if 'colLabels' in e:
                    bodyText.text += " | ".join([utils.remove5eShit(x)
                                        for x in e['colLabels']])+"\n"
                for row in e['rows']:
                    rowthing = []
                    for r in row:
                        if isinstance(r, dict) and 'roll' in r:
                            rowthing.append(
                                "{}-{}".format(
                                    r['roll']['min'],
                                    r['roll']['max']) if 'min' in r['roll'] else str(
                                    r['roll']['exact']))
                        else:
                            rowthing.append(utils.fixTags(str(r),m,args.nohtml))
                    bodyText.text += " | ".join(rowthing) + "\n"
            elif "entries" in e:
                subentries = []
                if 'name' in e:
                    if args.nohtml:
                        bodyText.text += "{}: ".format(e['name'])
                    else:
                        bodyText.text += "<b>{}:</b> ".format(e['name'])
                for sube in e["entries"]:
                    if type(sube) == str:
                        subentries.append(utils.fixTags(sube,m,args.nohtml))
                    elif type(sube) == dict and "text" in sube:
                        subentries.append(utils.fixTags(sube["text"],m,args.nohtml))
                    elif type(sube) == dict and sube['type'] == 'table':
                        if 'caption' in sube:
                            subentries.append("{}".format(sube['caption']))
                        if 'colLabels' in sube:
                            subentries.append(" | ".join([utils.remove5eShit(x)
                                                for x in sube['colLabels']]))
                        for row in sube['rows']:
                            rowthing = []
                            for r in row:
                                if isinstance(r, dict) and 'roll' in r:
                                    rowthing.append(
                                        "{}-{}".format(
                                            r['roll']['min'],
                                            r['roll']['max']) if 'min' in r['roll'] else str(
                                            r['roll']['exact']))
                                else:
                                    rowthing.append(utils.fixTags(str(r),m,args.nohtml))
                            subentries.append(" | ".join(rowthing))
                    elif type(sube) == dict and sube["type"] == "list" and "style" in sube and sube["style"] == "list-hang-notitle":
                        for item in sube["items"]:
                            if type(item) == dict and 'type' in item and item['type'] == 'item':
                                if args.nohtml:
                                    subentries.append("• {}: {}".format(item["name"],utils.fixTags(item["entry"],m,args.nohtml)))
                                else:
                                    subentries.append("• <i>{}:</i> {}".format(item["name"],utils.fixTags(item["entry"],m,args.nohtml)))
                            else:
                                subentries.append("• {}".format(utils.fixTags(item,m,args.nohtml)))
                    elif type(sube) == dict and sube["type"] == "list":
                        for item in sube["items"]:
                            if type(item) == dict and "entries" in item:
                                ssubentries = []                    
                                for sse in item["entries"]:
                                    if type(sse) == str:
                                        ssubentries.append(utils.fixTags(sse,m,args.nohtml))
                                    elif type(sse) == dict and "text" in sse:
                                        ssubentries.append(utils.fixTags(sse["text"],m,args.nohtml))
                                    subentries.append("\n".join(ssubentries))
                            elif type(item) == dict and 'type' in item and item['type'] == 'item':
                                if args.nohtml:
                                    subentries.append("• {}: {}".format(item["name"],utils.fixTags(item["entry"],m,args.nohtml)))
                                else:
                                    subentries.append("• <i>{}:</i> {}".format(item["name"],utils.fixTags(item["entry"],m,args.nohtml)))
                            elif type(item) == dict and item["type"] == "list" and "style" in item and item["style"] == "list-hang-notitle":
                                for subitem in item["items"]:
                                    if args.nohtml:
                                        subentries.append("• {}: {}".format(subitem["name"],utils.fixTags(subitem["entry"],m,args.nohtml)) + "\n")
                                    else:
                                        subentries.append("• <i>{}:</i> {}".format(subitem["name"],utils.fixTags(subitem["entry"],m,args.nohtml)) + "\n")
                            else:
                                subentries.append("• {}".format(utils.fixTags(item,m,args.nohtml)))
                bodyText.text += "\n".join(subentries) + "\n"
            else:
                if type(e) == dict and e["type"] == "list" and "style" in e and e["style"] == "list-hang-notitle":
                    for item in e["items"]:
                        if type(item) == dict:
                            if args.nohtml:
                                bodyText.text += "• {}: {}".format(item["name"],utils.fixTags(item["entry"],m,args.nohtml)) + "\n"
                            else:
                                bodyText.text += "• <i>{}:</i> {}".format(item["name"],utils.fixTags(item["entry"],m,args.nohtml)) + "\n"
                        else:
                            bodyText.text += "• {}".format(utils.fixTags(item,m,args.nohtml)) + "\n"
                elif type(e) == dict and e["type"] == "list":
                    for item in e["items"]:
                        if "entries" in item:
                            subentries = []                    
                            for sube in item["entries"]:
                                if type(sube) == str:
                                    subentries.append(utils.fixTags(sube,m,args.nohtml))
                                elif type(sube) == dict and "text" in sube:
                                    subentries.append(utils.fixTags(sube["text"],m,args.nohtml))
                                bodyText.text += "\n".join(subentries) + "\n"
                        else:
                            bodyText.text += "• {}".format(utils.fixTags(item,m,args.nohtml)) + "\n"
                else:
                    bodyText.text += utils.fixTags(e,m,args.nohtml) + "\n"

    bodyText.text = bodyText.text.rstrip()
    for match in re.finditer(r'([0-9])+[dD]([0-9])+([ ]?[-+][ ]?[0-9]+)?',bodyText.text):
        if not itm.find("./[roll='{}']".format(match.group(0))):
            roll = ET.SubElement(itm, 'roll')
            roll.text = "{}".format(match.group(0)).replace(' ','')
