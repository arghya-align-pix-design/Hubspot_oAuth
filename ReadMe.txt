***HubSpot App Setup Instructions***
1) Create a HubSpot Developer Account

-> Go to the HubSpot Developer Dashboard.

-> Sign in and create a developer account if you don’t have one.

2) Create a New App

-> Under the Auth tab:

  -> Note the Client ID, Client Secret, and App ID.

  -> In Redirect URL, enter:

    ->->  "http://localhost:6299/integrations/hubspot/oauth2callback"  <-<-
  
  -> Under Scopes, select the permissions required:

     -> crm.objects.contacts.read

     -> crm.objects.contacts.write

       (and any other scopes you wish to test)

-> Save your app configuration.

3) Create a Test Account

->From the developer dashboard, create a test account.

-> This allows you to create sample data (contacts, companies, etc.) without using a production account.

4) Populate Sample Data

-> In your test account, create dummy contacts to validate fetching contacts via API.

5) Use the API Endpoints

-> The OAuth flow uses official HubSpot endpoints:

-> Authorization URL:

   ->->  "https://app.hubspot.com/oauth/authorize"  <-<-
-> Token Exchange URL:

   ->->  "https://api.hubapi.com/oauth/v1/token"  <-<-

#For additional details, see HubSpot’s documentation:
   HubSpot OAuth 2.0 Overview

# FRONTEND IMPLEMENTATION NOTE

 For testing and demonstration purposes, I implemented a standalone 
 React frontend that interacts with the backend APIs I developed 
 (located at localhost:6299).

 Although the assignment includes a frontend/src/integrations/hubspot.js 
 file stub, I opted to create my own fully functional React component to:

 Provide clear UI feedback (e.g., success dialogs, error messages)
 Display the contacts in a table format
 Enable direct testing of the OAuth flow end to end

 The custom frontend is coupled to the backend endpoints created in this 
 project. If you prefer, you can integrate the logic into the provided 
 frontend folder, or run my React frontend separately alongside the backend.

#BACKEND SETUP

 The FastAPI backend is configured to run on port 6299 (instead of the 
 default 8000) because port 8000 was occupied by my local PostgreSQL 
 database.

 Redis is running in WSL (Windows Subsystem for Linux) on port 6379. 
 The backend connects to Redis via 127.0.0.1:6379.

 If you prefer, you can adjust the ports in the FastAPI uvicorn launch 
 command or in environment variables as needed.

#LOCAL DEVELOPMENT NOTES

 Backend runs on http://localhost:6299

 Frontend runs on http://localhost:3000

 Redis is available at 127.0.0.1:6379 (running inside WSL)

 If you want to change the ports, update:

    Backend uvicorn command (for FastAPI)

    Any axios URLs in the frontend


