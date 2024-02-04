# HealthHack
## MEDIC

Hello and Welcome to our Github Repository for MEDIC, a chatbot which aims to be able to offer personalised, tailored responses to patients 
who wish to equire on medical situations such as treatment plans, medicinal requirements, operations risks and benefits and more! Our aim is to aid doctors in informing patients of medical reports and scenarios which may be extremely technical in a manner by which they can grasp the relevant information more clearly. We aim for the process to be smooth for patients and to attain a wide user-base such that no matter who is in need, they will be able to get their questions answered effectively and efficiently.

## Main files

```script.js```
- sendMessage delivers the response generated from the medicine-chat Large Language Model (LLM) to the user
- sendText, sendAudio, sendImage: frontend to receive user inputs for the different input types - Text, Audio and Image inputs respectively
- textResponse: part of the sendMessage function that visualises the generated response from the LLM on the user's screen 
- addMessageToChatBox: displays the chat bubbles on the screen - based on the given parameters; represents the image as one sent by the user/ sent by the bot


```app.py```
- main page ("/") : Page accessed by user. Currently only accessible on one user per device; aims to enable a system by which more users can logon to access personalised chat information. When 1st accessed, new chat will be created by default for user to type in. Further updates to chats including sending of messages, addition of chats, renaming and deletion if chats are reflected on this page.

- retrieving chat info ("/get-chats"): Chat information including names for the user are retrieved from the database and reflected in the sidebar.

- renaming chats ("/rename-chat/<int:chat_session_id>"): When user hovers over an active chat, can click on the edit icon and rename the chat. New name is then routed from frontend to this route, and updates the relevant ChatTitle in the ChatSessions database - with the new title also being reflected in the sidebar.

- loading chats ("/load-chat"): When user selects a specific chat on the sidebar, chatID is retrieved and relevant messages of that specific chat are retreived from the Messages table in the database to be displayed on the frontend.

- sending messages ("/send_message") : When user types in the message in the message bar of the chat and sends it; message text is logged into the chat and used by the medicine-chat Large Language Model (LLM) to generate an appropriate response. Model's response is then also logged into the relevant table in the database and information of the model's response is sent to the frontend to be visualised to the user. Future aims include to enable Audio and Visual input from the user to be interpreted by models and warrant an appropriate response. 

- streaming videos ("/stream_video/<int:message_id>"): Based off of the generated text of the LLM, user can select an option on the frontend to create a video, for which the head_gen_model function is called onto the respective text and the reference audio and image in the references folder are used as a template for the creation of the video. The response is then returned to the frontend for the user to view.


```chat_app.db```

Tables:

- ChatSessions :
	ChatSessionID (int): ID of chat session
	ChatTitle (str): Name of the particular chat; can be renamed
	UserID (int): ID of user accessing the chat
	LastMessageTimestamp (datetime): Time at which the message was sent (UTC)
- Messages :
	MessageID (int): ID of message 
	ChatSessionID (int): Foreign key - linked with ChatSessions for ChatSessionID (Chat) in which message was sent
	MessageText (str): Constituent Text of the message
	Timestamp (datetime): Time at which message was sent (UTC)
	SentByUser (int): Integer to indicate if message was sent by user (if yes - 1. if sent by bot - 0)
- Users :
	UserID (int): ID of user
	Username (str): Name of user with particular ID
	CreatedAt (datetime): Timestamp of when user created his account/profile


```database.py```

- init_db(): Initializes the database with tables and a default user.
- reset_db():Resets the database (clears it) by removing all tables and re-initializing.
- start_new_chat(user_id): Starts a new chat session for a given user.
- load_chat(chat_session_id): Load a chat session by its ID.
- load_chats_for_sidebar():Loads all chat sessions to display in the sidebar.
- log_message(chat_session_id, message_text, sent_by_user): Adds a new message to the database.
	chat_session_id (int): The ID of the chat session.
	message_text (str): The text content of the message.
	sent_by_user (bool): True if the message is sent by the user, False if sent by the bot.





