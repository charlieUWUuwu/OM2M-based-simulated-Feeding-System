import requests

OM2M_URL = "http://127.0.0.1:8282/~"
CSE_ID = "/mn-cse/"
CSE_NAME = "mn-name"
LOGIN="admin"
PSWD="admin"
OM2M_BASE = OM2M_URL+CSE_ID
auth_headers = {"X-M2M-ORIGIN":LOGIN+":"+PSWD}
common_headers = {"Accept": "application/json"}

# ---------------------------------------------------------
import configparser, json
config = configparser.ConfigParser()
with open('config.json', 'r') as f:
    config = json.load(f)

mn_IP = config["mn_cse"]["ip"]
in_IP = config["in_cse"]["ip"]
mn_PORT = config["mn_cse"]["port"] # 3300
FEED_GATEWAY_ROUTE = config["mn_cse"]["route"]["FEED_GATEWAY"] 
# ---------------------------------------------------------

def create_AE(name, category):
    global mn_IP, mn_PORT
    header_ae = {"Content-Type":"application/xml;ty=2"}
    name_ae = name
    body_ae = f"""
        <m2m:ae xmlns:m2m="http://www.onem2m.org/xml/protocols" rn="{name_ae}" >
            <api>app-sensor</api>
            <lbl>Category/{category} Location/{name_ae}</lbl>
            <poa>http://{mn_IP}:{mn_PORT}/{name_ae}</poa>
            <rr>true</rr>
        </m2m:ae>
    """.format(name_ae, category, mn_IP, mn_PORT)
    response = requests.delete(OM2M_BASE+CSE_NAME+"/"+name_ae, headers={**auth_headers, **common_headers})
    print(response)
    response = requests.post(OM2M_BASE, data=body_ae, headers={**auth_headers, **common_headers, **header_ae})
    print(response)
    

def create_CNT(name_ae, name_cnt, category):
    header_cnt = {"Content-Type":"application/xml;ty=3"}
    body_cnt = f"""
        <m2m:cnt xmlns:m2m="http://www.onem2m.org/xml/protocols" rn="{name_cnt}">
            <lbl>Category/{category} Location/{name_ae}</lbl>
        </m2m:cnt>
    """
    response = requests.post(OM2M_BASE+CSE_NAME+"/"+name_ae, data=body_cnt, headers={**auth_headers, **common_headers, **header_cnt})
    print(response)
    return response


def create_SUB(name_ae, name_cnt, name_sub, nu_name):
    header_sub = {"Content-Type":"application/xml;ty=23"}
    body_cnt = f"""
        <m2m:sub xmlns:m2m="http://www.onem2m.org/xml/protocols" rn="{name_sub}">
            <nu>http://{in_IP}:8080/~/in-cse/in-name/{nu_name}</nu>
            <nct>2</nct>
        </m2m:sub>
    """
    response = requests.post(OM2M_BASE+CSE_NAME+"/"+name_ae+"/"+name_cnt, data=body_cnt, headers={**auth_headers, **common_headers, **header_sub})
    print(response)
    return response


def create_CIN_data(name_ae, penId, name_cnt, water_value, food_value):
    header_cin = {"Content-Type":"application/xml;ty=4"}
    body_cin = f"""
        <m2m:cin xmlns:m2m="http://www.onem2m.org/xml/protocols">
            <cnf>sensor data</cnf>
            <con>
              &lt;obj&gt;
                &lt;str name=&quot;penId&quot; val=&quot;{penId}&quot;/&gt;
                &lt;int name=&quot;water&quot; val=&quot;{water_value}&quot;/&gt;
                &lt;int name=&quot;food&quot; val=&quot;{food_value}&quot;/&gt;
              &lt;/obj&gt;
            </con>
        </m2m:cin>
        """ 
    response = requests.post(OM2M_BASE+CSE_NAME+"/"+name_ae+"/"+name_cnt, data=body_cin, headers={**auth_headers, **common_headers, **header_cin})
    return response


def create_CIN_action(name_ae, penId, name_cnt, action):
    header_cin = {"Content-Type":"application/xml;ty=4"}
    body_cin = f"""
        <m2m:cin xmlns:m2m="http://www.onem2m.org/xml/protocols">
            <cnf>action data</cnf>
            <con>
              &lt;obj&gt;
                &lt;str name=&quot;penId&quot; val=&quot;{penId}&quot;/&gt;
                &lt;str name=&quot;action&quot; val=&quot;{action}&quot;/&gt;
              &lt;/obj&gt;
            </con>
        </m2m:cin>
        """ 
    response = requests.post(OM2M_BASE+CSE_NAME+"/"+name_ae+"/"+name_cnt, data=body_cin, headers={**auth_headers, **common_headers, **header_cin})
    return response

