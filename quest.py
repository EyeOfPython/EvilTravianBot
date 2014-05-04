
import action
import reader

def skip_tutorial(travian):
    action.action_tutorial(travian, "skip")

def do_tutorial(travian):
    action.action_tutorial(travian, "next", "Tutorial_01")
    action.action_tutorial(travian, "questWindowClosed")
    action.action_tutorial(travian, "tipsOff")
    action.action_tutorial(travian, None, "Tutorial_02")
    action.action_tutorial(travian, "next", "Tutorial_02")
    action.action_tutorial(travian, None, "Tutorial_03")
    action.action_build_up(travian, 1)
    action.action_tutorial(travian, None, "Tutorial_03")
    action.action_tutorial(travian, "next", "Tutorial_03")
    action.action_tutorial(travian, None, "Tutorial_04")
    action.action_build_up(travian, 1)
    action.action_tutorial(travian, None, "Tutorial_04")
    action.action_tutorial(travian, "next", "Tutorial_04")
    action.action_tutorial(travian, None, "Tutorial_04")
    action.action_build_up(travian, 2)
    action.action_tutorial(travian, None, "Tutorial_04")
    action.action_tutorial(travian, "next", "Tutorial_05")
    action.action_tutorial(travian, None, "Tutorial_05")

    travian.ajax_cmd("heroSetAttributes", {"resource":2, "attackBehaviour":"hide"})
    action.action_tutorial(travian, "next", "Tutorial_06")
    
    action.action_tutorial(travian, None, "Tutorial_07")
    travian.request_GET("/dorf2.php")
    action.action_tutorial(travian, None, "Tutorial_07")
    action.action_tutorial(travian, "next", "Tutorial_07")
    action.action_tutorial(travian, None, "Tutorial_08")
    action.action_build_new(travian, 19, 10)
    action.action_tutorial(travian, "next", "Tutorial_08")
    action.action_tutorial(travian, None, "Tutorial_09")
    action.action_build_new(travian, 39, 16)
    action.action_tutorial(travian, None, "Tutorial_09")
    action.action_tutorial(travian, "next", "Tutorial_09")
    action.action_tutorial(travian, None, "Tutorial_10")
    travian.ajax_cmd("premiumFeature", {"featureKey":"finishNow", "context":""})
    action.action_tutorial(travian, "next", "Tutorial_10")
    action.action_tutorial(travian, None, "Tutorial_11")
    action.action_adventure(travian)
    action.action_tutorial(travian, "next", "Tutorial_11")
    action.action_tutorial(travian, None, "Tutorial_12")

    travian.request_GET("/berichte.php")
    first_report = reader.read_reports(travian.current_page)[0]
    travian.request_GET(first_report['link'])

    action.action_tutorial(travian, "next", "Tutorial_12")
    travian.request_hero()
    action.action_apply_item(travian, travian.hero.inventory[len(travian.hero.inventory)-1], 1)
    action.action_tutorial(travian, None, "Tutorial_13")
    action.action_tutorial(travian, "next", "Tutorial_13")
    travian.ajax_cmd("overlay", {})
    action.action_tutorial(travian, "next", "Tutorial_14")
    action.action_tutorial(travian, "next", "Tutorial_15")
