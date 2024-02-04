import pandas as pd
from flask import Flask, Response, request, jsonify, session, render_template
from uuid import uuid4
from database import *
import sys
from llm_script import medicine_llm
from head_gen_script import main as head_gen_engine
import torch
import os
import gc
import torch

app = Flask(__name__)
app.secret_key = "MEDiC"


@app.route("/")
def index():
    print("Welcome to MEDiC")
    init_db()
    chat_session_id = start_new_chat(1)
    session["chat-session-id"] = chat_session_id
    return render_template("index.html")


def model_function(input_text):
    output_chat = medicine_llm(input_text)
    return output_chat


base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of app.py
reference_path = os.path.join(base_dir, "references")
ref_audio = os.path.join(reference_path, "audio/converted.wav")
ref_img = os.path.join(reference_path, "images/doctor.jpg")


def head_gen_model(
    input_text,
    ref_audio=ref_audio,
    ref_img=ref_img,
    save_dir="./results",
    lang="ENGLISH",
    translate=False,
):
    output_string = head_gen_engine(
        input_text, ref_audio, ref_img, save_dir, lang, translate
    )
    # clears memory once done with head generation
    gc.collect()
    torch.cuda.empty_cache()
    return output_string


@app.route("/send_message", methods=["POST"])
def send_message():
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        json_data = request.json
        message = json_data.get("message", "")
        chat_id = session["chat-session-id"]
        # Generate a unique identifier for the message

        # Logs the user's message
        log_message(chat_id, message, True)

        # Process the message through the model function and get the response
        response = model_function(message)

        # Logs the bot's response
        message_id = log_message(chat_id, response, False)
    elif content_type == "audio/wav":
        # TODO: Handle audio
        return
    elif content_type == "image/jpeg":
        # TODO: Handle image
        return
    else:
        return "Content-Type not supported!", 400

    return jsonify(response=response, id=chat_id, message_id=message_id)


@app.route("/get-chats", methods=["GET"])
def get_all_chats():
    # TODO: Fetch all chats using given userID
    ##for now retrieving all chats
    chats = load_chats_for_sidebar()
    if chats != None:
        chat_response = list(
            map(
                lambda chat: {
                    "chatSessionId": chat[0],
                    "chatTitle": chat[1],
                    "lastMessageTimestamp": chat[2],
                },
                chats,
            )
        )
    else:
        chat_response = None
    return jsonify(chat_response)


@app.route("/rename-chat/<int:chat_session_id>", methods=["POST"])
def rename_chat(chat_session_id):
    new_title = request.json.get("newTitle")
    # Call function to update chat title in the database
    update_chat_title(chat_session_id, new_title)
    return jsonify({"success": True})


@app.route("/load-chat", methods=["GET"])
def load_chat_from_sidebar():
    chat_session_id = request.headers.get("id")
    chat_log = load_chat(chat_session_id)
    chat_response = list(
        map(
            lambda log: {"message_id": log[0], "message": log[1], "by_user": log[2]},
            chat_log,
        )
    )
    session["chat-session-id"] = chat_session_id
    return jsonify(chat_response)


def generate_video(video_path):
    with open(video_path, "rb") as video_file:
        while True:
            chunk = video_file.read(1024 * 1024)  # Read 1MB chunks
            if not chunk:
                break
            yield chunk


@app.route("/stream_video/<int:message_id>")
def stream_video(message_id):
    video_path = head_gen_model(load_message(message_id)[0][0])
    # clearing memory
    return Response(generate_video(video_path), mimetype="video/mp4")


@app.route("/reset-sidebar", methods=["DELETE"])
def reset_sidebar():
    clear_user_history(user_id=1, excluded_chat_id=session["chat-session-id"])
    return jsonify("resert")


if __name__ == "__main__":
    app.run(debug=True)
