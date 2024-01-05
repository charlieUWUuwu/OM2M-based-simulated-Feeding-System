import mylibs.in_API as in_API
import mylibs.mn_API as mn_API

def setUp():
    # create mn_AE
    mn_API.create_AE("PEN_1", "pen")
    mn_API.create_AE("PEN_2", "pen")
    mn_API.create_AE("FEED_GATEWAY", "control")
    
    # create container in mn_AE
    mn_API.create_CNT("PEN_1", "DATA", "data")
    mn_API.create_CNT("PEN_2", "DATA", "data")
    mn_API.create_CNT("FEED_GATEWAY", "DATA", "control")
    
    # create in_AE
    in_API.create_AE("WEB_DATA", "web")
    in_API.create_AE("WEB_CONTROL", "control")
    
    # create container in in_AE
    in_API.create_CNT("WEB_DATA", "PEN_1", "data")
    in_API.create_CNT("WEB_DATA", "PEN_2", "data")
    in_API.create_CNT("WEB_CONTROL", "DATA", "control")
    
    # create subscription in the container of mn_AE
    mn_API.create_SUB("PEN_1", "DATA", "SUB_IN_WEB_DATA", "WEB_DATA")
    mn_API.create_SUB("PEN_2", "DATA", "SUB_IN_WEB_DATA", "WEB_DATA")
    
    # create subscription in the container of in_AE
    # 記得先將 in_app.py 運行起來(才有127.0.0.1:3000)
    in_API.create_SUB(False, "WEB_CONTROL", "DATA", "SUB_MN", "FEED_GATEWAY")
    in_API.create_SUB(True, "WEB_DATA", "PEN_1", "SUB_WEB_CONTROL", "WEB_CONTROL")
    in_API.create_SUB(True, "WEB_DATA", "PEN_2", "SUB_WEB_CONTROL", "WEB_CONTROL")
    
    return "setup complete"