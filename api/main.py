import os
import requests
import base64
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
ROBLOSECURITY = os.getenv("ROBLOSECURITY")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

template_path = os.path.join(BASE_DIR, "assets", "status.svg.template")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


PUBLIC_DIR = os.path.join(BASE_DIR, "public")
if os.path.exists(PUBLIC_DIR):
    app.mount("/public", StaticFiles(directory=PUBLIC_DIR), name="public")

@app.get("/public/{file_path:path}")
async def serve_public(file_path: str):
    file_location = os.path.join(BASE_DIR, "public", file_path)
    if os.path.exists(file_location) and os.path.isfile(file_location):
        return FileResponse(file_location)
    return {"error": "File not found"}

@app.get("/debug/files")
async def debug_files():
    import os
    items = []
    try:
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                path = os.path.join(root, file)
                items.append(path)
    except Exception as e:
        items.append(f"Error: {e}")
    return {"BASE_DIR": BASE_DIR, "files": items}

@app.get("/")
async def read_index():
    # Try multiple possible paths
    possible_paths = [
        os.path.join(BASE_DIR, "public", "index.html"),
        "/var/task/api/public/index.html",
        os.path.join("/var/task/api", "public", "index.html"),
    ]
    
    for index_path in possible_paths:
        print(f"DEBUG: Trying {index_path}")
        if os.path.exists(index_path):
            print(f"DEBUG: Found at {index_path}")
            with open(index_path, "r") as f:
                return HTMLResponse(content=f.read())
    
    print(f"DEBUG: File not found in any path")
    return HTMLResponse(content="<h1>Frontend not available</h1>")

@app.get("/redirect/@{username}")
def redirect_username(username):
    userID = get_id_from_username(username)
    if userID <= 0:
        return RedirectResponse(url=f"https://www.roblox.com/search/users?keyword={username}")
    return redirect_userid(userID)

@app.get("/redirect/{userID}")
def redirect_userid(userID):
    if userID <= 0:
        return RedirectResponse(url="https://www.roblox.com/search/users")
    
    return RedirectResponse(url=f"https://www.roblox.com/users/{userID}/profile")

@app.get("/user/@{username}")
def get_status_from_name(username: str):
    id = get_id_from_username(username)
    return get_status_from_id(id)


@app.get("/user/{userID}")
def get_status_from_id(userID: int):

    if userID <= 0:
        return "User does not exist"
    
    status_data = get_status_data(userID)
    if not status_data:
        return "User data not found"
    
    displayname, username = get_names(userID)
    pfp_url = get_profile_picture_url(userID)
    pfp_data = get_profile_picture_data(pfp_url)
    game_id = status_data['universeId']
    game_name = get_game_name(game_id)
        
    status = status_data['userPresenceType']

    return generate_badge(displayname, username, pfp_data, game_name, status)
    

def get_names(userID):
    url = f"https://users.roblox.com/v1/users/{userID}"
    response = requests.get(url)
    data = response.json()
    if data['name']:
        username = data['name']
        displayname = data['displayName']
    return displayname, username


def get_profile_picture_url(userID):
    url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userID}&size=100x100&format=Png"
    response = requests.get(url)
    data = response.json()
    try:
        if data['data']:
            return data['data'][0]['imageUrl']
    except Exception as e:
        print(f"Failed to get profile picture URL: {e}")
        return "None"

def get_profile_picture_data(pfp_url):
    response = requests.get(pfp_url)
    uri = "data:image/png;base64," + base64.b64encode(response.content).decode("utf-8")
    return uri


def get_game_name(universeID):
    if not universeID:
        print("No universeID (game) recieved")
        return ""
    url = f"https://games.roblox.com/v1/games?universeIds={universeID}&fields=name"
    response = requests.get(url)
    data = response.json()
    try:
        if data['data']:
            return data['data'][0]['name']
    except Exception as e:
        print(f"Failed to get game name: {e}")
        return ""
    return ""


def get_status_data(userID: int):
    url = "https://presence.roblox.com/v1/presence/users"
    cookies = {".ROBLOSECURITY": ROBLOSECURITY}
    payload = { "userIds": [userID] }
    response = requests.post(url, json=payload, cookies=cookies) # type: ignore
    data = response.json()
    if data['userPresences']:
        return data['userPresences'][0]
    return None


def get_id_from_username(username):
    url = "https://users.roblox.com/v1/usernames/users"
    payload = {
        "usernames": [username], 
        "excludeBannedUsers": True
    }
    response = requests.post(url, json=payload)
    data = response.json()
    if data['data']:
        id = data['data'][0]['id']
        
        return id
    
    return -1


def generate_badge(displayname, username, pfp_uri, game, status):

    status_map = {
        3: "creating",
        2: "playing",
        1: "website",
        0: "offline"
    }
    
    status_class = status_map.get(status, "offline")

    with open(template_path, "r") as f:
        template = f.read()

    output = template.replace("{{displayname}}", displayname)\
        .replace("{{username}}", username)\
        .replace("{{pfp}}", pfp_uri)\
        .replace("{{game}}", game)\
        .replace("{{status}}", status_class)\
        .replace("{{status_class}}", status_class)

    return Response(
        content=output, 
        media_type="image/svg+xml",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )