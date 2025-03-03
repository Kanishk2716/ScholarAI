import streamlit as st
import uuid
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Firebase credentials path from .env
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")

if FIREBASE_CREDENTIALS_PATH is None:
    st.error("Firebase credentials not found. Please set the environment variable in the .env file.")
else:
    # Initialize Firebase only once
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)

db = firestore.client()


def generate_room_id():
    return str(uuid.uuid4())[:8]

def join_room(room_id, username):
    room_ref = db.collection("study_rooms").document(room_id)
    room = room_ref.get()
    if room.exists:
        room_ref.update({"participants": firestore.ArrayUnion([username])})
        return True
    return False

def create_room(username, room_name):
    room_id = generate_room_id()
    db.collection("study_rooms").document(room_id).set({
        "name": room_name if room_name else f"{username}'s Room",
        "created_by": username,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "document": "",
        "messages": [],
        "resources": [],
        "participants": [username]
    })
    return room_id

def send_message(room_id, username, message):
    if message.strip():
        room_ref = db.collection("study_rooms").document(room_id)
        room_ref.update({"messages": firestore.ArrayUnion([{  
            "user": username, "message": message, "timestamp": datetime.now().strftime("%H:%M:%S")
        }])})

def save_document(room_id, document_content):
    db.collection("study_rooms").document(room_id).set({"document": document_content}, merge=True)

def add_resource(room_id, username, title, link):
    if title.strip() and link.strip():
        db.collection("study_rooms").document(room_id).update({"resources": firestore.ArrayUnion([{  
            "title": title, "link": link, "added_by": username, "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])})

def firebase_collaborative_study():
    st.title("Collaborative Study Room")
    
    if 'room_id' not in st.session_state:
        st.session_state.room_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    if st.session_state.room_id is None:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Join Existing Room")
            join_room_id = st.text_input("Room ID", key="join_room_id")
            join_username = st.text_input("Your Name (for joining)", key="join_username")
            if st.button("Join Room"):
                if join_room_id and join_username and join_room(join_room_id, join_username):
                    st.session_state.room_id = join_room_id
                    st.session_state.username = join_username
                    send_message(join_room_id, "System", f"{join_username} joined the room")
                    st.rerun()
                else:
                    st.error("Room not found")

        with col2:
            st.subheader("Create New Room")
            create_username = st.text_input("Your Name (for creating)", key="create_username")
            room_name = st.text_input("Room Name (optional)", key="room_name")
            if st.button("Create Room"):
                if create_username:
                    new_room_id = create_room(create_username, room_name)
                    st.session_state.room_id = new_room_id
                    st.session_state.username = create_username
                    st.success(f"Room created! Your Room ID is: {new_room_id}")
                    st.rerun()

    else:
        room_ref = db.collection("study_rooms").document(st.session_state.room_id)
        current_room = room_ref.get().to_dict()
        
        st.subheader(f"Room: {current_room['name']}")
        st.write(f"Room ID: {st.session_state.room_id}")
        st.write(f"Participants: {', '.join(current_room['participants'])}")
        
        if st.button("Leave Room"):
            room_ref.update({"participants": firestore.ArrayRemove([st.session_state.username])})
            send_message(st.session_state.room_id, "System", f"{st.session_state.username} left the room")
            st.session_state.room_id = None
            st.session_state.username = None
            st.rerun()
        
        doc_tab, chat_tab, resources_tab = st.tabs(["Shared Document", "Discussion", "Shared Resources"])
        
        with doc_tab:
            st.subheader("Collaborative Document")
            new_doc_content = st.text_area("Edit collaboratively", current_room.get("document", ""), height=300)
            if st.button("Save Document"):
                save_document(st.session_state.room_id, new_doc_content)
                send_message(st.session_state.room_id, "System", f"{st.session_state.username} updated the document")
                st.success("Document saved")

        with chat_tab:
            st.subheader("Group Discussion")
            messages = current_room.get("messages", [])
            for msg in reversed(messages):  # Show latest messages first
                st.write(f"[{msg['timestamp']}] **{msg['user']}**: {msg['message']}")
            message = st.text_input("Type your message")
            if st.button("Send") and message.strip():
                send_message(st.session_state.room_id, st.session_state.username, message)
                st.rerun()

        with resources_tab:
            st.subheader("Shared Resources")
            resources = current_room.get("resources", [])
            for resource in resources:
                st.write(f"📌 **{resource['title']}** (Added by {resource['added_by']})")
                st.write(f"🔗 [Open]({resource['link']})")
            resource_title = st.text_input("Resource Title")
            resource_link = st.text_input("Resource Link")
            if st.button("Share Resource") and resource_title.strip() and resource_link.strip():
                add_resource(st.session_state.room_id, st.session_state.username, resource_title, resource_link)
                send_message(st.session_state.room_id, "System", f"{st.session_state.username} shared a resource: {resource_title}")
                st.rerun()
