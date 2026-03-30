import zaetoon_helpers as zaetoon

if __name__ == "__main__":
    teams = zaetoon.get_team_names()
    print("أسماء الفرق:", teams)

# if __name__ == "__main__":
#     team_name="الصيانة"
#     agents_ids = zaetoon.get_team_agents_ids(team_name)
#     print(agents_ids)

# if __name__ == "__main__":

#     inbox_ids=zaetoon.get_all_inbox_ids()

#     for inbox_id in inbox_ids:

#         open_convs_ids=zaetoon.get_open_unassigned_conversations_ids(inbox_id)
#         print("Inbox= ", inbox_id)
#         print("Open conversations= ",open_convs_ids)

# if __name__ == "__main__":  
#     conversation_id=756867
#     message = zaetoon.get_conversation_text(conversation_id)
#     print(message)

# if __name__ == "__main__":
#     team_name = "المالية"
#     agents_ids = zaetoon.get_team_agents_ids(team_name)
#     if len(agents_ids) > 0:
#         agent_id = agents_ids[0]
#         zaetoon.assign_conversation_agent(756867, agent_id)

# if __name__ == "__main__":
#     team_name="المالية"
#     conversation_id1 = 756501
#     conversation_id2 = 756494
#     zaetoon.assign_conversation_team_round_robin(team_name, conversation_id1)
#     zaetoon.assign_conversation_team_round_robin(team_name, conversation_id2)

# if __name__ == "__main__":
#     team_name = "المستخدمين"
#     agents_info = zaetoon.get_team_agents_info(team_name)
#     print(agents_info)

# if __name__ == "__main__":
#     zaetoon.set_conversation_status(756867,"بانتظار الرد")

# if __name__ == "__main__":
#     zaetoon.send_conversation_msg(757078, "مرحباً بك في خدمة العملاء هذه رسالة تجريبية ")

# if __name__ == "__main__":
#     articles_json_file="data/articles.json"
#     zaetoon.get_all_articles(articles_json_file)
