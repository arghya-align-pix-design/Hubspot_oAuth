# slack.py


import datetime
import json
import secrets
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
import base64
import hashlib

import requests
from integrations.integration_item import IntegrationItem

from fastapi import Request

from redis_client import add_key_value_redis, get_value_redis, delete_key_redis

# Client data and other dummy data
CLIENT_ID =  "XXX"
CLIENT_SECRET =  "XXX"
REDIRECT_URI = "http://localhost:6299/integrations/hubspot/oauth2callback"
scope = "crm.objects.companies.read crm.objects.companies.write crm.objects.contacts.read crm.objects.contacts.write"
authorization_url = f"https://app.hubspot.com/oauth/authorize?client_id={CLIENT_ID}&scope={scope}&redirect_uri=http%3A%2F%2Flocalhost%3A6299%2Fintegrations%2Fhubspot%2Foauth2callback"


# FUNCTION 1
async def authorize_hubspot(user_id, org_id):
    # TODO
    state_data = {
        "state": secrets.token_urlsafe(32),
        "user_id": user_id,
        "org_id": org_id,
    }
    encoded_state = base64.urlsafe_b64encode(
        json.dumps(state_data).encode("utf-8")
    ).decode("utf-8")

    auth_url = f"{authorization_url}&state={encoded_state}"

    await add_key_value_redis(
        f"hubspot_state:{org_id}:{user_id}", json.dumps(state_data), expire=600
    )
    # add_key_value_redis(f"hubspot_verifier:{org_id}:{user_id}", expire=600),

    return {"url": auth_url}


# FUNCTION 2
async def oauth2callback_hubspot(request: Request):
    #TODO
    print("=== TEST CODE RUNNING ===")

    # If any error happens, this handler throws error exception
    if request.query_params.get("error"):
        raise HTTPException(
            status_code=400, detail=request.query_params.get("error_description")
        )

    # Getting the access code from the parameters
    code = request.query_params.get("code")
    encoded_state = request.query_params.get("state")
    state_data = json.loads(base64.urlsafe_b64decode(encoded_state).decode("utf-8"))

    original_state = state_data.get("state")
    user_id = state_data.get("user_id")
    org_id = state_data.get("org_id")

    saved_state = await get_value_redis(f"hubspot_state:{org_id}:{user_id}")

    if not saved_state:
        raise HTTPException(status_code=400, detail="State is empty.")

    if original_state != json.loads(saved_state).get("state"):
       raise HTTPException(status_code=400, detail="State does not match.")

    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                "https://api.hubapi.com/oauth/v1/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "redirect_uri": REDIRECT_URI,
                    "code": code,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            ),
            delete_key_redis(f"hubspot_state:{org_id}:{user_id}"),
        )

    await add_key_value_redis(
        f"hubspot_credentials:{org_id}:{user_id}",
        json.dumps(response.json()),
        expire=600,
    )

    close_window_script = """
        <html>
            <head>
                <script>
                    // Redirect to your main app with a success flag
                    window.location.href = "http://localhost:3000/?auth=success";
                </script>
            </head>
            <body>
                <p>Redirecting back to the application...</p>
            </body>
        </html>
    """
    return HTMLResponse(content=close_window_script)


# FUNCTION3
async def get_hubspot_credentials(user_id, org_id):
    #TODO
    credentials = await get_value_redis(f"hubspot_credentials:{org_id}:{user_id}")
    if not credentials:
        raise HTTPException(status_code=400, detail="No credentials found.")
    credentials = json.loads(credentials)
    await delete_key_redis(f"hubspot_credentials:{org_id}:{user_id}")

    return credentials


# FUNCTION4
async def create_integration_item_metadata_object(response_json):
    # TODO
    props = response_json.get("properties", {})
    # Build the name (use email if no name)
    name = f"{props.get('firstname', '')} {props.get('lastname', '')}".strip()
    
    if not name or name == "":
        name = props.get("email", "Unnamed Contact")

    integration_item_metadata = IntegrationItem(
        id=response_json.get("id"),
        name=name,
        type="contact",
        creation_time=response_json.get("createdAt"),
        last_modified_time=response_json.get("updatedAt"),
        parent_id=None,
        parent_path_or_name=f"Company: {props.get('company', 'N/A')} | Email: {props.get('email', 'N/A')} | Phone: {props.get('phone', 'N/A')}",
    )

    return integration_item_metadata
    


# FUNCTION5
async def get_items_hubspot(credentials)-> list[IntegrationItem]:
    # TODO
    credentials = json.loads(credentials)
    access_token = credentials.get("access_token")
    print(access_token)
    
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token found")


    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch contacts")

    contacts = response.json().get("results", [])
    list_of_items = []

    for contact in contacts:
        item = await create_integration_item_metadata_object(contact)
        list_of_items.append(item)

    print(list_of_items)
    return list_of_items
