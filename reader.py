from htmldom.htmldom import HtmlDom

import re
from datetime import datetime, date, timedelta
#from village import ItemInventory

import db

reg_bid=re.compile(r'[^\d]*(\d*)')
reg_res=re.compile(r'([^ ]*) [^ ]* (\d*)')
reg_bld=re.compile(r'([^ ]*) &lt;span class=&quot;level&quot;&gt;[^ ]* (\d*)&lt;.*')
reg_queue=re.compile(r'([^\t]*)\t*[^ ]* (\d*)')

reg_ajax_token=re.compile(r"window\.ajaxToken = '(\w{32})';")

reg_report_type=re.compile(r'class="iReport iReport(\d*)"')

reg_hero_inventory=re.compile(
r'''<script type="text/javascript">
	window\.addEvent\('domready', function\(\)
	\{
		Travian\.Game\.Hero\.Inventory = new Travian\.Game\.Hero\.Inventory\(
		(\{ .*
	    \})\);
</script>''', re.DOTALL)

reg_hero_inventory=re.compile(
r'''Travian\.Game\.Hero\.Inventory = new Travian\.Game\.Hero\.Inventory\(.*?isInVillage: (\w*),.*?isDead: (\w*),.*?isRegenerating: (\w*),.*?heroState:.*?experience: (\w*),.*?culturePoints: (?P<culturePoints>\w*).*?a: (?P<a>\w*),.*?c: '(?P<c>\w*)',.*?gender: '(\w*)',.*?data:.*?\[(?P<items>.*)\],.*?text:''', re.DOTALL)
reg_hero_items=re.compile('\{.*?\}', re.DOTALL)
reg_item=re.compile(r"{.*?id:\t(?P<id>\w*),.*?typeId:\t(?P<typeId>\w*),.*?name:\t'(?P<name>.*?)',.*?placeId:\t(?P<placeId>\w*),.*?place:\t'(?P<place>\w*)',.*?slot:\t'(?P<slot>\w*)',.*?amount:\t(?P<amount>\w*),.*?\}".replace(r'\t', '\t'), re.DOTALL)
#.*?typeId:\t(?P<typeId>\w*),.*?name:\t'(?P<name>\w*)',placeId:\t(?P<placeId>\w*),.*?place:\t'(?P<place>\w*)',.*?slot:\t'(\w*)',.*?amount:\t(\w*),
#,placeId:\t(?P<placeId>\w*)

reg_village_id=re.compile(
r'\d+'
)

hero_status = {
        'heroStatus102': 'trapped',
        'heroStatus101': 'dead',
        'heroStatus100': 'home',
        'heroStatus3': 'moving',
        'heroStatus4': 'moving',
        'heroStatus5': 'moving',
        'heroStatus9': 'moving',
        'heroStatus40': 'moving',
        'heroStatus50': 'moving',
        'heroStatus101Regenerate': 'regenerate',
        'heroStatus103': 'defending'
    }

report_types = {
        0: 'spy',
        1: 'attack_green',
        2: 'attack_yellow',
        3: 'attack_red',
        4: 'defend_green',
        5: 'defend_yellow',
        6: 'defend_red',
        7: 'defend_gray',
        8: 'support_sent',
        11: 'resources_wood',
        12: 'resources_clay',
        13: 'resources_iron',
        14: 'resources_grain',
        15: 'spy_attack_green',
        16: 'spy_attack_yellow',
        17: 'spy_attack_red',
        18: 'spy_defend_green',
        19: 'spy_defend_yellow',
        20: 'animals_captured',
        21: 'adventure'
    }

def html_entities_decode(s):
    return s.replace('&auml;', 'ä').replace('&szlig;', 'ß')

def clean_useless_entities(s):
    return s.replace("&#x202d;", "").replace("&#x202c;", "").replace("\u200e", "").replace("&#37;", "").replace("&#45;", "").strip()

def read_resources(doc):
    """ At any page """

    resrList = doc.find("ul#stockBar")

    resources = []
    
    for resrElm in resrList.children():
        if resrElm.attr('id').startswith("stockBarResource"):
            resources.append(int(resrElm.find("div.middle span.value").text()))

    return resources

def read_storage_capacity(doc):
    """ At any page """
    
    capacity_warehouse = int(doc.find("span#stockBarWarehouse").text())
    capacity_granary   = int(doc.find("span#stockBarGranary").text())
    
    return [ capacity_warehouse ] * 3 + [ capacity_granary ] # Match it to a resource list

def read_production(doc):
    """ Requires dorf1.php """

    prodList = doc.find("table#production tbody tr td.num")

    production = []
    for prodElm in prodList:
        production.append(int(prodElm.text().replace("&#x202d;", "").replace("&#x202c;", "").replace("\u200e", "").strip()))

    return production

def read_production_boost(doc):
    """ At any page """
    
    resrList = doc.find("ul#stockBar")

    resources = []
    
    for resrElm in resrList.children():
        if resrElm.attr('id').startswith("stockBarResource"):
            resources.append(1.25 if resrElm.find("div.middle img.productionBoost").html() else 1)
    
    return resources

def read_build_queue(doc):
    """ Requires dorf1.php or dorf2.php """

    queue = doc.find("div.buildingList div.boxes-contents ul li")
    build_queue = []
    for bldElm in queue:
        m = reg_queue.match(bldElm.find("div.name").text())
        try:
            timer = (datetime.strptime(bldElm.find("div.buildDuration span").text(), "%H:%M:%S") - datetime(1900, 1, 1)) # - timedelta(hours=1))
        except:
            continue
        
        build_queue.append({ 'building': db.get_gid_by_name(m.group(1)), 'level': int(m.group(2)), 'timer':timer })

    return build_queue

def read_server_time(doc):
    """ At any page """

    timestr = doc.find("div#servertime span#tp1").text()
    if not timestr:
        return datetime.today()
    
    server_time = datetime.strptime(timestr, "%H:%M:%S") - datetime(1900, 1, 1)
    client_time = date.today()
    server_time = datetime(client_time.year, client_time.month, client_time.day) + server_time

    return server_time

def read_resource_fields(doc):
    """ Requires dorf1.php """
    resmap = doc.find("map#rx")

    buildings = []
    for field in resmap.children():
        if field.attr('href') == "dorf2.php": break
        bid = reg_bid.match(field.attr('href')).group(1)
        m = reg_res.match(field.attr('alt'))
        
        buildings.append((int(bid), db.get_gid_by_name(m.group(1)), int(m.group(2))))

    return buildings

def read_buildings(doc):
    """ Requires dorf2.php """
    bldmap = doc.find("map#clickareas")

    buildings = []

    for building in bldmap.children():
        bid = reg_bid.match(building.attr('href')).group(1)

        if building.attr('alt').find(' ') == -1: # building could be empty
            buildings.append((int(bid), 0, 0))
            continue
            
        m = reg_bld.match(building.attr('alt'))

        buildings.append((int(bid), db.get_gid_by_name(html_entities_decode(m.group(1))), int(m.group(2))))
        
    return buildings

def read_adventure_number(doc):
    """ At any page """
    bubble = doc.find("div#sidebarBoxHero div.speechBubbleContainer div.speechBubbleContent").text()

    if not bubble:
        return 0

    return int(bubble)

def read_adventures(doc):
    """ Requires hero_adventure.php """

    adventures = doc.find("form#adventureListForm tr")
    
    advs = []
    
    for adventure in adventures:
        link = "/" + adventure.find("td.goTo a").attr("href").replace('&amp;', '&')
        timer = datetime.strptime(adventure.find("td.moveTime span").text().strip(), "%H:%M:%S") - datetime(1900, 1, 1)
        diff = int(adventure.find("td.difficulty img").attr("class")[-1])
        advs.append({ 'link': link, 'timer': timer, 'difficulty': diff })
        
    return advs

def read_hero(doc, hero):
    """ Requires hero_inventory.php """
    from hero import ItemInventory
    status_class = doc.find("div.heroStatusMessage img").attr("class")
    status = hero_status.get(status_class, None)

    health = int(doc.find("div.powervalue span.value").text().replace("&#x202d;", "").replace("&#x202c;", "").replace("\u200e", "").replace("&#37;", "").strip())
    exp = int(doc.find("div.experience div.experience").text())

    skill_table = doc.find("table#attributesOfHero")
    hero.skill_points['power'] = int(skill_table.find("tr.power td.points").text())
    hero.skill_points['off_bonus'] = int(skill_table.find("tr.offBonus td.points").text())
    hero.skill_points['def_bonus'] = int(skill_table.find("tr.defBonus td.points").text())
    hero.skill_points['production'] = int(skill_table.find("tr.productionPoints td.points").text())

    for i, resr_radio in enumerate(doc.find("div#setResource div.resource input.radio")):
        if resr_radio.attr('checked') == 'checked':
            hero.production_slot = i
            break

    m = reg_hero_inventory.search(doc.find("html").html())
    hero.culture_points = int(m.group('culturePoints'))
    hero.item_a = m.group('a')
    hero.item_c = m.group('c')
    
    hero.inventory = []
    for item in reg_hero_items.findall(m.group('items')):
        m = reg_item.match(item)
        hero.inventory.append(ItemInventory(m))

    hero.status = status
    hero.health = health
    hero.exp = exp

def read_ajax_token(doc):
    """ At any page """

    return reg_ajax_token.search(doc.find("html").html()).group(1)

def read_reports(doc):
    """ Requires a page of berichte.php """

    report_list = doc.find("table.row_table_data tr")

    report_list = iter(report_list)
    next(report_list)

    reports = []
    
    for reportElm in report_list:
        typestr = reportElm.find("img.iReport").html()
        if not typestr:
            continue
        typ = int(reg_report_type.search(typestr).group(1))
        link = '/' + reportElm.find("a.adventure").attr("href").replace('&amp;', '&')

        reports.append({'type':typ, 'link':link})

    return reports

def read_inbox(doc):
    """ Requires a page of nachrichten.php """
     
    inbox_list = doc.find("table.inbox tr")
    
    inbox = None

    for messageElm in inbox_list:
        if inbox is None:
            inbox = []
            continue
        a = messageElm.find("td.subject a")
        href = '/' + a.attr("href").strip()
        subject = a.text().strip()
        sender = messageElm.find("td.send").text().strip()
        inbox.append({'sender':sender, 'subject':subject, 'href':href})
        
    return inbox

def read_villages(doc, only_active=False):
    """ At any page """
    
    village_list = doc.find("div#sidebarBoxVillagelist ul li a%s" % (".active" if only_active else ""))
    villages = []
    for village in village_list:
        href = village.attr("href")
        village_id = reg_village_id.search(href).group(0)
        name = village.find("div.name").text()
        coord_x = int(clean_useless_entities(village.find("span.coordinateX").text())[1:])
        coord_y = int(clean_useless_entities(village.find("span.coordinateY").text())[:-1])
        villages.append({'village_id':village_id, 'name': name, 'coord': (coord_x, coord_y)})
    return villages

def read_troop_movement_simple(doc):
    """Requires a page of dorf1.php"""
    movements = doc.find("table#movements tr")
    
    movs = []
    
    s = True
    for mov in movements:
        if s:
            s = False
            continue
        time = datetime.strptime(mov.find("div.dur_r span").text(), "%H:%M:%S") - datetime(1900, 1, 1)
        type1 = mov.find("td.typ img").attr("class")
        movs.append({'type':type1, 'timer': time})
        
    return movs

if __name__ == "__main__":
    from account import Account
    import log
    import hero
    log.logger.log_name = 'Gl4ss'
    acc = Account((3,'de'),'Gl4ss')
    acc.loadup()
    #doc = acc.request_GET('/dorf1.php')
    #print(read_production_boost(doc))
    
    doc = acc.request_GET('/hero_inventory.php')
    h = hero.Hero()
    read_hero(doc, h)
    print(h)
    print(h.get_production_bonus())