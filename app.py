import os
import json
import openai
import streamlit as st
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail





openai.api_key = st.secrets.OpenAIAPI.openai_api_key
SENDGRID_API_KEY = st.secrets.SendGrid.sendgrid_api_key

functions = [
    {
        "name": "generate_email",
        "description": "Generate an email from a given context",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                },
                "subject": {
                    "type": "string"
                },
                "body": {
                    "type": "string"
                }
            },
            "required": ["to", "subject", "body"]
        },
    }
]
 
def generate_email(content):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "user", "content": content}
        ],
        functions=functions,
        function_call={"name": "generate_email"}
    )
    return json.loads(response["choices"][0]["message"]["function_call"]["arguments"])


def send_email(to, subject, body):
    sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
    mail = Mail(from_email="test@example.com", to_emails=to, subject=subject, plain_text_content=body)
    response = sg.send(mail)
    return response


st.title("Mail Generator")
st.write("自然言語でメールを生成して送信するアプリです")
 
with st.form("generate_email"):
    text = st.text_area("メールの概要を記述してください")
    submitted = st.form_submit_button("生成")
if submitted:
    try:
        with st.spinner("生成中..."):
            response_json = generate_email(text)
        for key, value in response_json.items():
            st.session_state[key] = value
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")


if "body" in st.session_state:
    with st.form("send_email"):
        st.write("以下の内容でメールを送信します")
        to_text = st.text_input("To", key="to")
        subject_text = st.text_input("Subject", key="subject")
        body_text = st.text_area("Content", key="body", height=320)
        sent = st.form_submit_button("送信")
    if sent:
        try:
            with st.spinner("送信中..."):
                res = send_email(to_text, subject_text, body_text)
            st.success("送信しました")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
