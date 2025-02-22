from flask import Flask, request, jsonify
import openai
from datetime import datetime
from chat_history import ChatHistory
from openai import OpenAI
import requests
import json
import os
app = Flask(__name__)
chat_history = ChatHistory()

PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WHATSAPP_API_URL = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def send_text_message(phone_number, message):
    """Function to send a simple text message, used for texts having formating or codes"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload_data = {
        "recipient_type": "individual",
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload_data)
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
    response_data = response.json()
    return response_data['messages'][0]['id']

def get_role_details():
    return """
    Name: React Developer
    Location: Vadodara
    Salary: 4 LPA
    Experience: 0-2 years
    Tools: Cursor/Windsurf
    Relocation: Yes
    Startup experience: Not required but preferred
    
    """

def generate_llm_response(conversation_history, role_details):
    messages = [
        {"role": "system", "content":"""You are a professional HR negotiation agent for a technology company hiring React developers. Your role is to have a structured conversation with candidates to assess their fit for the position. Ask questions one at a time about location, experience, tools, relocation, startup experience, and salary expectations. If a candidate's response is vague, incomplete, or needs clarification, ask follow-up questions to get specific details. Here are the key areas to cover:

1. Location - Get their current city and willingness to relocate if needed
2. React experience - Years of experience, specific projects, and portfolio links
3. Development tools - Experience with modern coding tools like Cursor/Windsurf
4. Office location - Ability to work from Vadodara office
5. Startup experience - Previous experience working in startup environments
6. Salary expectations - Comfort with 4 LPA starting salary, current salary details

Tone : Professional, Friendly, Conversational
Keep messages concise and focused on gathering information. Avoid lengthy appreciation of previous responses when moving to the next topic. Get straight to the point with clear, direct questions.

Be professional but conversational and friendly. Ask one question at a time and wait for the response before moving to the next topic. For any unclear responses, ask relevant follow-up questions to get complete information. Keep track of what has been discussed and what still needs to be covered.

IMPORTANT: Your response must be a JSON string with two fields:
1. "message": Your response message to the candidate
2. "isConversationGoing": true if the conversation should continue, false if all topics are covered and the candidate has confirmed completion

When all topics are covered, ask if they want to confirm and complete the conversation. Set isConversationGoing to false only after they confirm completion.

The conversation should be in English.
Here are the details of the role:
{role_details}
"""}
    ] + conversation_history
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    
    try:
        response_json = json.loads(response.choices[0].message.content)
        message = response_json.get("message", "")
        is_conversation_going = response_json.get("isConversationGoing", True)
        print(f"Message: {message}")
        print(f"Conversation continuing: {is_conversation_going}")
        return message, is_conversation_going
    except json.JSONDecodeError:
        # Fallback in case response is not valid JSON
        print("Warning: Response was not valid JSON")
        return response.choices[0].message.content, True

def generate_llm_response_after_negotiation(conversation_history, role_details):
    messages = [
        {"role": "system", "content":"""
         You are a professional HR negotiation agent for a technology company hiring React developers. Analyze the conversation history and role details to evaluate the candidate's fit. Provide a structured assessment in the following format:

         - Alignment: Number of requirements candidate meets (x/6)
         - Overall Fit: Rate as Excellent/Good/Moderate/Poor based on qualifications
         - Interest Level: Score 1-10 on candidate's enthusiasm to join (based on langugage and the time gap between the conversation)
         - Communication: Score 1-10 on clarity and professionalism
         - Interpersonal: Score 1-10 on rapport and engagement
         

         Key requirements to evaluate:
         1. Location/relocation flexibility
         2. React experience level
         3. Development tools familiarity  
         4. Office location acceptance
         5. Startup experience
         6. Salary expectations
         
         Here are the details of the role:
         {role_details}
         """}]+conversation_history

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content



@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if token == VERIFY_TOKEN:
            return str(challenge)
        return "Invalid verification token", 403

    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Skip status updates
            if 'statuses' in data['entry'][0]['changes'][0]['value']:
                return jsonify(status="success"), 200
            
            value = data['entry'][0]['changes'][0]['value']
            if 'messages' not in value:
                return jsonify(status="success"), 200
            
            # Extract message details
            message = value['messages'][0]
            phone_number = message['from']
            text = message.get('text', {}).get('body', '')
            
            # Store user message
            chat_history.add_message(phone_number, text, 'user')
            
            # Get conversation history and generate response
            conversation = chat_history.get_history(phone_number)
            llm_response, is_conversation_going = generate_llm_response(conversation, get_role_details())
            
            # Store bot response
            chat_history.add_message(phone_number, llm_response, 'assistant')
            send_text_message(phone_number, llm_response)
            print(f"\n is_conversation_going: {is_conversation_going}")
            if not is_conversation_going:
                llm_response_after_negotiation = generate_llm_response_after_negotiation(conversation, get_role_details())
                send_text_message(phone_number, llm_response_after_negotiation)
           
            
            return jsonify(status="success"), 200
            
        except Exception as e:
            print(f"Error: {e}")
            return jsonify(status="error"), 500



if __name__ == '__main__':
    app.run(port=4000, debug=True) 