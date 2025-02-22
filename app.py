import json
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, request, jsonify
from openai import OpenAI

from chat_history import ChatHistory

app = Flask(__name__)
chat_history = ChatHistory()

load_dotenv()

PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WHATSAPP_API_URL = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
VERIFY_TOKEN = "my_custom_token_123"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

model = "gpt-4o-mini"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
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
    Job Title: React Developer - 1
    Location: Vadodara, Gujarat, India
    Salary Range: 4 LPA - 6 LPA
    Skills required: ReactJs
    Experience: 0-2 years
    """

def generate_llm_response(conversation_history, role_details):
    #print(f"Generating LLM response for conversation history: {conversation_history}")
    messages = [
        {"role": "system",
          "content": """You are a professional Recruiter for a technology company. Your job is to have a short but structured conversation with candidates to collect more information about their fit for the job role. Ask questions one at a time about location, professional years of experience, their willingness to relocate and salary expectations in terms of Cost to Company (CTC) annually."""
        },
        {"role": "user", 
        "content": f"""
         As a highly efficient and busy recruiter, you must keep track of the conversation history, ensure you're covering all key points, speak fast and not repeat yourself. When all topics are covered, ask if they want to complete the conversation. Set isConversationGoing to false only after they confirm completion.

         INSTRUCTIONS:
         Here are the key areas to cover:

            0. Name confirmation - Get their full name.
            1. Location - Get their current city and willingness to relocate to the city mentioned in the job description. If they are willing to relocate, move on to next question. If they are in the same city as the job location, ask if they are willing to travel to the office location 5 days a week.
            2. React experience - Years of experience, specific projects, and portfolio links. If they give non-zero years of experience, ask for any specific projects and live project links or portfolio links projects they have worked on. Ask for portfolio links / live project links only if they have worked on React projects.
            3. Startup experience - Previous experience working in startup environments.
            4. Salary expectations - Current salary details (CTC annually) and expected salary (CTC annually). If their expected salary is not in the range of 4 -6 LPA, ask them to see if they will consider a salary within the range?
            5. Previous work experience - Ask them their professional work history. Ask them the size of the companies they've worked at and reasons for leaving the last job they mentioned.        

        TONE : 
        Professional, Friendly, Terse but conversational and in English. 
        Keep messages concise. DO NOT CONFIRM WHAT THEY JUST SAID. IT SHOULD BE LIKE " okay, got it. ...."
        If a candidate's response is vague, incomplete, or needs clarification, ask follow-up questions to get specific details. 
         
        Ask one question at a time and wait for the response before moving to the next topic. 
        For any unclear responses or incomplete responses, ask relevant follow-up questions to get complete information. 
        Keep track of what has been discussed and what still needs to be covered.

        OUTPUT FORMAT: Your response must be a JSON string with two fields:
        {{
            "message": "Your response message to the candidate",
            "isConversationGoing": true if the conversation should continue, false if all topics are covered and the candidate has confirmed completion
        }}

        IMPORTANT:
        You may be having conversations with multiple candidates at the same time. So, make sure to use the conversation history for each candidate to generate the response.

        WHEN TO STOP THE CONVERSATION:
        - If all the 4 points are covered, set isConversationGoing to false, politely thank them for their time and say you will get back to them with next steps.
        - If the candidate says they are not interested in the role, reply back with a message to that effect and set isConversationGoing to false.
        - If the conversation has been going on for more than 40 messages, set isConversationGoing to false.
        - If the candidate is not responding to your messages for more than 10 minutes, set isConversationGoing to false.

        JOB DESCRIPTION FOR REFERENCE
        {role_details}

        THE CONVERSATION HISTORY UPTILL NOW:
        {conversation_history}

        Based on the most recent message from the user, respond back to the user with appropriate message in the given format"""}
    ]
    
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages
    )

    print(f"Response: {response.choices[0].message.content}")
    try:
        response_json = json.loads(response.choices[0].message.content.strip("```json\n"))
        message = response_json.get("message", "")
        is_conversation_going = response_json.get("isConversationGoing", True)
        #print(f"Message: {message}")
        #print(f"Conversation continuing: {is_conversation_going}")
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
        model=model,
        messages=messages
    )

    print(f"Response: {response.choices[0].message.content}")
    return response.choices[0].message.content

def generate_summarize_conversation(chat_history, role_details):
    messages = [
        {"role": "system",
          "content": f"""
        You are an HR analytics system. Analyze the conversation history and provide scores based on the following criteria:
       
        - React experience scoring:
          None = 0, within 0-2 years = 8, within 3 years = 5, outside range = 0
        
        - Location scoring:
          Same city as mentioned in job description = 10, 
          Different city/state from what is mentioned in the job description but willing to relocate = 5,
          Not willing to relocate or no answer = 0
          
        - Salary expectations scoring:
          N/A = 0, within 4-6 LPA = 8, within 3-7 LPA = 5, outside range = 0
          
        - React project details:
          Specific examples with details = 8, Vague answers = 5, No details = 0
          
        - Name confirmation:
          The answer to the question on name confirmation should be used. This will be in the "message" field of the JSON object after the name confirmation question
        Return scores in JSON format with these exact keys:
        {{
            "name": "<name>",
            "location": "<score>",
            "React experience": "<score>",
            "Salary expectations": "<score>",
            "Previous work experience": "<score>",
            "total": "<sum of all scores>"
        }}

        JOB DESCRIPTION FOR REFERENCE:
        {role_details}

        CONVERSATION HISTORY:
        {chat_history}

        """}] 

    response = openai_client.chat.completions.create(
        model=model,
        messages=messages
    )
    response_json = json.loads(response.choices[0].message.content.strip("```json\n"))
    print(f"Summary Response: {response_json}")
    return response_json

added_candidates = []
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
            
            print(f"\n\ndata: {data}\n\n")

            # Extract message details
            message = value['messages'][0]
            phone_number = message['from']
            text = message.get('text', {}).get('body', '')
            print(f"{phone_number} : {text}")
            # Store user message
            chat_history.add_message(phone_number, text, 'user')
            # Get conversation history and generate response
            conversation = chat_history.get_history(phone_number)
            llm_response, is_conversation_going = generate_llm_response(conversation, get_role_details())

            # Store bot response
            chat_history.add_message(phone_number, llm_response, 'assistant')

            print(f"llm_response: {llm_response}")
            send_text_message(phone_number, llm_response)
            
            print(f"\n is_conversation_going: {is_conversation_going}")
            chat_history.save_history()
            
            if not is_conversation_going:
                print(f"Conversation completed for {phone_number}. Generating summary for chat history: {chat_history.get_history(phone_number)}")
                
                summarize_conversation = generate_summarize_conversation(chat_history.get_history(phone_number), get_role_details())
                # Write summary to a file with phone number and timestamp
                if phone_number not in added_candidates:
                    try:
                        with open('src/report.json', 'r+') as f:
                            try:
                                existing_data = json.load(f)
                            except json.JSONDecodeError:
                                existing_data = []
                        
                        existing_data.append(summarize_conversation)
                        f.seek(0)
                        json.dump(existing_data, f, indent=2)
                        f.truncate()
                        added_candidates.append(phone_number)
                    except Exception as e:
                        print(f"Error appending to report.json: {e}")

            return jsonify(status="success"), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify(status="error"), 500


if __name__ == '__main__':
    app.run(port=9009, debug=True) 