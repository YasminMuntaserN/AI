import requests
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("ZEYTOON_TOKEN").strip()

BASE_URL = os.getenv("BASE_URL").strip() 

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "User-Agent": "curl/7.55.1",
    "Accept": "application/json"
}

def get_team_names():

    url = f"{BASE_URL}/teams"

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f" خطأ في جلب الفرق: {resp.status_code} {resp.text[:200]}")
        return []
    
    try:
        data = resp.json()
    
    except Exception:
        print(" لم أستطع تحويل الرد إلى JSON")
        return []

    teams = data.get("data", [])

    teams_names=[]
    
    for team in teams:
        teams_names.append(team.get("name"))
    
    return teams_names

def get_team_agents_ids(team_name):

    url = f"{BASE_URL}/teams"

    resp = requests.get(url, headers=headers, params={"expand": "agents"})

    if resp.status_code != 200:
        print(f" خطأ في جلب الفرق: {resp.status_code} {resp.text}")
        return []

    try:
        data = resp.json()
    except Exception:
        print(" لم أستطع تحويل الرد إلى JSON")
        return []

    teams = data.get("data", [])
    for team in teams:

        if team.get("name") == team_name:
            
            team_agents = team.get("agents", [])

            team_agents_ids=[]
            
            for ag in team_agents:
                team_agents_ids.append(ag["id"])

            return team_agents_ids

    print(f" الفريق '{team_name}' غير موجود.")
    return []

def get_all_inbox_ids():

    url = f"{BASE_URL}/inboxes"

    resp = requests.get(url, headers=headers)

    if resp.status_code != 200:
        print(f" خطأ في جلب الفرق: {resp.status_code} {resp.text}")
        return []

    try:
        data = resp.json()
    
    except Exception:
        print(" لم أستطع تحويل الرد إلى JSON")
        return []

    inbox_ids = []
    for box in data.get("data", []):
        inbox_ids.append(box["id"])

    return inbox_ids

def get_open_unassigned_conversations_ids(inbox_id):

    url = f"{BASE_URL}/conversations"
    
    params = {
        "status": "opened",
        "inbox_ids[]": inbox_id
    }
    resp = requests.get(url, headers=headers, params=params)
    
    if resp.status_code != 200:
        print(f" خطأ في جلب المحادثات من الصندوق {inbox_id}: {resp.status_code} {resp.text[:200]}")
        return []

    try:
        payload = resp.json()
        data = payload.get("data", [])
    except Exception:
        print(" لم أستطع تحويل رد المحادثات إلى JSON")
        return []

    
    opened_unassigned_ids = []
    for conv in data:
        if not conv.get("assign_to"):
            opened_unassigned_ids.append(str(conv.get("id")))
   
    return opened_unassigned_ids

def get_open_agent_id_conversations_ids(inbox_id, agent_id):

    url = f"{BASE_URL}/conversations"
    params = {
        "inbox_ids[]": inbox_id
    }
    resp = requests.get(url, headers=headers, params=params)
    
    if resp.status_code != 200:
        print(f" خطأ في جلب المحادثات من الصندوق {inbox_id}: {resp.status_code} {resp.text[:200]}")
        return []

    try:
        payload = resp.json()
        data = payload.get("data", [])
    except Exception:
        print(" لم أستطع تحويل رد المحادثات إلى JSON")
        return []

    
    open_agent_id_conversations_ids = []
    for conv in data:
        if not conv.get("assign_to"):
            continue
        assigned_to_id=conv.get("assign_to")["id"].strip()
        if  assigned_to_id==str(agent_id).strip():
            open_agent_id_conversations_ids.append(str(conv.get("id")))
   
    return open_agent_id_conversations_ids

def get_conversation_text(conversation_id, last_msgs_count=8):
    url = f"{BASE_URL}/conversations/{conversation_id}/messages"
    resp = requests.get(url, headers=headers)
    
    if resp.status_code != 200:
        print(f" خطأ في جلب الرسائل للمحادثة {conversation_id}: {resp.status_code} {resp.text}")
        return "",""
    
    try:
        messages = resp.json().get("data", [])
    except Exception:
        print(" لم أستطع تحويل رد الرسائل إلى JSON")
        return "",""

    if not messages:
        return "",""

    if messages[0]['user']['type'].lower().strip()=="agent":
        return "",""
    
    conversation=""
    messages_conversation=messages[1:last_msgs_count]
    
    for msg_conv in reversed(messages_conversation):
        m = msg_conv.get("content")
        if m: 
            conversation += m + "\n"

    msg=messages[0].get("content") 
    return conversation, msg

def assign_conversation_agent(conversation_id, agent_id):

    url = f"{BASE_URL}/conversations/{conversation_id}"

    payload = {"assign_to": agent_id}

    resp = requests.put(url, headers=headers, json=payload)

    if resp.status_code != 200:
        print(f" فشل الإسناد: المحادثة {conversation_id} → الوكيل {agent_id}")

STATE_FILE = "rr_state.json"

def assign_conversation_team_round_robin(team_name, conversation_id):

    team_members = get_team_agents_ids(team_name)
    
    if not team_members:
        print(f" لا يوجد وكلاء في الفريق: {team_name}")
        return None

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {}

    last_index = state.get(team_name, -1)

    next_index = (last_index + 1) % len(team_members)

    agent_id = team_members[next_index]

    state[team_name] = next_index

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f ,ensure_ascii=False)

    return assign_conversation_agent(conversation_id, agent_id)

def get_team_agents_info(team_name):
 
    url = f"{BASE_URL}/teams"

    resp = requests.get(url, headers=headers, params={"expand": "agents"})

    if resp.status_code != 200:
        print(f" خطأ في جلب الفرق: {resp.status_code} {resp.text}")
        return []

    try:
        data = resp.json()
    except Exception:
        print(" لم أستطع تحويل الرد إلى JSON")
        return []

    teams = data.get("data", [])
    
    for team in teams:

        if team.get("name") == team_name:
            
            team_agents=team.get("agents", [])

            team_agents_info=[]
        
            for ag in team_agents:
                info = f"id={ag["id"]}, Name= {ag["first_name"]}  {ag["last_name"]} \n"
                team_agents_info.append(info)

            return team_agents_info

    print(f" الفريق '{team_name}' غير موجود.")
    return []

def set_conversation_status(conversation_id, status):
    try:

        url_statuses = f"{BASE_URL}/conversation_statuses"
        params = {
            "inbox_ids[]": [conversation_id] 
        }
        resp_statuses = requests.get(url_statuses, headers=headers, params=params)
        
        if resp_statuses.status_code != 200:
            print(f"فشل جلب الحالات: {resp_statuses.status_code}, {resp_statuses.text}")
            return False

        data = resp_statuses.json()

        statuses = data.get("data", [])

        status_id = None
        for st in statuses:
            if st.get("name") == status:
                status_id = st.get("id")
                break

        if not status_id:
            print(f" لم أجد حالة باسم {status}")
            return False

        url_conv = f"{BASE_URL}/conversations/{conversation_id}"

        payload = {"conversation_status_id": status_id}

        resp_update = requests.put(url_conv, headers=headers, json=payload)

        if resp_update.status_code != 200:
            print(f"  فشل تحديث حالة المحادثة {conversation_id}")
            return False
        
        return True

    except Exception as e:
        print(f"خطأ أثناء تحديث الحالة: {e}")
        return False

def send_conversation_msg(conversation_id, msg, status="بانتظار الرد"):
    try:

        url = f"{BASE_URL}/conversations/{conversation_id}/messages"

        payload = {}

        payload["content"] = msg

        resp = requests.post(url, headers=headers, json=payload)

        if resp.status_code != 200:
            print(f" فشل إرسال الرسالة للمحادثة {conversation_id}: {resp.status_code} ")
            return False

        set_conversation_status(conversation_id, status)
        return True
    
    except Exception:
        print(f" فشل إرسال الرسالة للمحادثة {conversation_id} ")
        return False
    
def get_article_detail(article_id): 

    url = f"{BASE_URL}/articles/{article_id}"

    resp = requests.get(url, headers=headers)
    
    if resp.status_code != 200:
        print(f" خطأ في جلب تفاصيل المقال {article_id}: {resp.status_code}")
        return None
    
    try:
        payload = resp.json()
    except Exception:
        print(" لم أستطع تحويل الرد إلى JSON")
        return None

    data = payload.get("data", {})

    blocks = data.get("blocks", []) 

    full_text=""
    
    for b in blocks:
        html=b.get("content", "")
        text=re.sub('<.*?>', '', html)
        full_text=full_text+text + "\n"

    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "content": full_text
    }

def get_all_articles(articles_json_file):

    url = f"{BASE_URL}/articles"

    resp = requests.get(url, headers=headers)
    
    if resp.status_code != 200:
        print(f" خطأ في جلب قائمة المقالات: {resp.status_code}")
        return []
    try:
        payload = resp.json()
    except Exception:
        print(" لم أستطع تحويل الرد إلى JSON")
        return []

    articles = payload.get("data", [])
    results = []

    for art in articles:
        art_id = art.get("id")
        detail = get_article_detail(art_id)   
        if detail:
            results.append({
                "id": art_id,
                "title": detail["title"],
                "content": detail["content"]
            })

    try:
        with open(articles_json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False)
    except Exception as e:
        print(f" خطأ أثناء حفظ المقالات: {e}")
    