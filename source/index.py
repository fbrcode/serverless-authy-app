import os
from authy.api import AuthyApiClient

def lambda_handler(event, context):
    api_key = os.getenv('TWILIO_AUTHY_API_KEY')
    #print(api_key)
    authy_api = AuthyApiClient(api_key)
    p_email = event.get('email')
    p_phone = event.get('phone')
    p_ccode = event.get('ccode')
    user = authy_api.users.create(email=p_email,phone=p_phone,country_code=p_ccode)
    if user.ok():
        user_id = user.id
        print(user_id)
        return {"message":"User created successfully.","user":{"id":user_id},"success":"true"}
    else:
        return user.errors()

if __name__ == '__main__':
    import pprint
    import sys

    response = lambda_handler({'email': sys.argv[1],'phone': sys.argv[2],'ccode': sys.argv[3]}, None)
    pprint.pprint(response)
