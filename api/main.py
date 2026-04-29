import os
import requests
import base64
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
ROBLOSECURITY = os.getenv("ROBLOSECURITY")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

template_path = os.path.join(BASE_DIR, "assets", "status.svg.template")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

html_path = os.path.join(BASE_DIR, "..", "public", "index.html")
css_path = os.path.join(BASE_DIR, "..", "public", "style.css")
js_path = os.path.join(BASE_DIR, "..", "public", "script.js")

# Embedded frontend files
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roblox GitHub Profile Badge</title>
    <link rel="stylesheet" href="/public/style.css">
</head>
<body>
    <div class="wrapper">
        <header>
            <h1>Roblox GitHub Badge</h1>
            <p class="subtitle">Dynamic status updates for your README.md</p>
        </header>

        <main>
            <section class="generator-card">
                <form id="badge-form">
                    <div class="input-group">
                        <label for="user">Your Roblox @Username or ID</label>
                        <input type="text" id="user" placeholder="e.g. @frxctured0, 920740863, @roblox" required>
                    </div>

                    <div class="checkbox-group">
                        <label class="switch">
                            <input type="checkbox" id="centered">
                            <span class="slider"></span>
                            Centered Alignment
                        </label>
                        <label class="switch">
                            <input type="checkbox" id="redirect" checked>
                            <span class="slider"></span>
                            Link to Profile
                        </label>
                    </div>

                    <button id="generate-preview" type="submit" class="btn-primary">Generate Preview</button>
                </form>

                <hr>

                <div class="output-section">
                    <label>Preview</label>
                    <div id="preview-container">
                        <div class="placeholder-badge">Your badge will appear here</div>
                    </div>

                    <label for="github-output">Markdown Code</label>
                    <div class="textarea-wrapper">
                        <textarea id="github-output" readonly placeholder="![Roblox Status](...)"></textarea>
                        <button id="copy-btn" class="btn-copy">Copy</button>
                    </div>

                    <label>For active game</label>
                    <div>
                        <div>Follow <a href="https://www.roblox.com/users/10883920674/profile" target="_blank">@github_profile</a> on roblox and set your <a href="https://www.roblox.com/my/account#!/privacy/VisibilityAndPrivateServers/Visibility" target="_blank">"Show current experience"</a> to at least "Friends & people I follow"</div>
                    </div>
                </div>
            </section>

            <section class="features">
                <div class="feature-item">
                    <h3>Live Status</h3>
                    <p>Shows if you are Online, Offline, or In-Game in real-time.</p>
                </div>
                <div class="feature-item">
                    <h3>Game Detection</h3>
                    <p>Optionally displays the specific experience you're currently playing.</p>
                </div>
                <div class="feature-item">
                    <h3>Simple to Use</h3>
                    <p>Just copy and paste the generated text into your REAME.md</p>
                </div>
            </section>
        </main>

        <footer>
            <p>Developed by <strong>frxctured</strong> &bull; <a href="mailto:frxctured@frxctured.com">Contact</a></p>
        </footer>
        <script src="/public/script.js"></script>
    </div>
</body>
</html>"""

CSS_CONTENT = """:root {
    --bg-color: #0d1117;
    --card-bg: #161b22;
    --accent: #2f81f7;
    --text-main: #c9d1d9;
    --text-dim: #8b949e;
    --border: #30363d;
    --radius: 8px;
}

body {
    background-color: var(--bg-color);
    color: var(--text-main);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    margin: 0;
    line-height: 1.6;
}

.wrapper {
    max-width: 800px;
    margin: 0 auto;
    padding: 40px 20px;
}

header {
    text-align: center;
    margin-bottom: 40px;
}

header h1 {
    font-size: 2.5rem;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}

.subtitle {
    color: var(--text-dim);
    font-size: 1.1rem;
}

/* Generator Card */
.generator-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 30px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.2);
}

.input-group {
    display: flex;
    flex-direction: column;
    margin-bottom: 20px;
}

.input-group label {
    font-weight: 600;
    margin-bottom: 8px;
    font-size: 0.9rem;
}

input[type="text"] {
    background: var(--bg-color);
    border: 1px solid var(--border);
    color: white;
    padding: 12px;
    border-radius: var(--radius);
    font-size: 1rem;
    transition: border-color 0.2s;
}

input[type="text"]:focus {
    outline: none;
    border-color: var(--accent);
}

.checkbox-group {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    margin-bottom: 25px;
}

/* Custom Switches */
.switch {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    font-size: 0.9rem;
}

.btn-primary {
    background-color: #238636;
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: var(--radius);
    font-weight: 600;
    width: 100%;
    cursor: pointer;
    transition: filter 0.2s;
}

.btn-primary:hover {
    filter: brightness(1.1);
}

hr {
    border: 0;
    border-top: 1px solid var(--border);
    margin: 30px 0;
}

/* Output Section */
.output-section label {
    display: block;
    font-size: 0.8rem;
    color: var(--text-dim);
    text-transform: uppercase;
    margin-bottom: 10px;
}

#preview-container {
    background: var(--bg-color);
    border: 1px dashed var(--border);
    border-radius: var(--radius);
    min-height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
}

#preview-container a, #preview-container div {
    margin: 0;
    padding: 0;
    line-height: 0;
}

.textarea-wrapper {
    position: relative;
    margin-bottom: 20px;
}

textarea {
    width: 100%;
    height: 80px;
    background: #010409;
    color: #7ee787;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 12px;
    font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, monospace;
    resize: none;
    box-sizing: border-box;
}

.btn-copy {
    position: absolute;
    top: 8px;
    right: 8px;
    background: var(--border);
    color: var(--text-main);
    border: none;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.7rem;
    cursor: pointer;
}

/* Features Grid */
.features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-top: 40px;
}

.feature-item h3 {
    font-size: 1rem;
    margin-bottom: 5px;
}

.feature-item p {
    font-size: 0.85rem;
    color: var(--text-dim);
}

footer {
    text-align: center;
    margin-top: 60px;
    padding-top: 20px;
    border-top: 1px solid var(--border);
    color: var(--text-dim);
    font-size: 0.9rem;
}

a {
    color: var(--accent);
    text-decoration: none;
}"""

JS_CONTENT = """const BASE_URL = "https://roblox-github-profile-badge.vercel.app";

form = document.getElementById("badge-form");
user = document.getElementById("user");
generateBtn = document.getElementById("generate-preview");
previewCnt = document.getElementById("preview-container");
output = document.getElementById("github-output");
copybtn = document.getElementById("copy-btn")

centeredCB = document.getElementById("centered");
redirectCB = document.getElementById("redirect");

var centered = centeredCB.checked;
var redirect = redirectCB.checked;

centeredCB.addEventListener("change", function () {
    centered = centeredCB.checked;
});

redirectCB.addEventListener("change", function () {
    redirect = redirectCB.checked;
});

generateBtn.addEventListener("click", function (e) {
    e.preventDefault();

    const badge_url = generate_badge_url(user.value);
    const redirect_url = generate_redirect_url(user.value);

    previewCnt.innerHTML = "Loading...";

    const newImg = document.createElement("img");

    newImg.onload = function () {
        previewCnt.innerHTML = "";

        let finalElement;

        if (redirect) {
            const newAnchor = document.createElement("a");
            newAnchor.href = redirect_url;
            newAnchor.target = "_blank";
            newAnchor.append(newImg);
            finalElement = newAnchor;
        } else {
            finalElement = newImg;
        }

        if (centered) {
            const wrapper = document.createElement("div");
            wrapper.setAttribute("align", "center");
            wrapper.append(finalElement);
            previewCnt.style.justifyContent = "center";
            previewCnt.append(wrapper);
        } else {
            previewCnt.style.justifyContent = "flex-start";
            previewCnt.append(finalElement);
        }

        output.value = previewCnt.innerHTML;
    };

    newImg.onerror = function () {
        previewCnt.innerHTML = "Error: Could not load badge.";
    };

    newImg.src = badge_url;
});

copybtn.addEventListener("click", function () {
    output.select();
    output.setSelectionRange(0, 99999);

    navigator.clipboard.writeText(output.value);

    alert("Copied the text: " + output.value);
});


function generate_badge_url(id_or_name) {
    return BASE_URL + "/api/user/" + id_or_name
}

function generate_redirect_url(id_or_name) {
    return BASE_URL + "/api/redirect/" + id_or_name
}

function fetch_image(badge_url) {
    return fetch(badge_url).then(function (response) {
        if (!response.ok) throw new Error('Image not found');
        return response.blob();
    });
}"""

app = FastAPI()

if os.path.exists(PUBLIC_DIR):
    app.mount("/public", StaticFiles(directory=PUBLIC_DIR), name="public")

@app.get("/")
async def home():
    try:
        with open(html_path, "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content=HTML_CONTENT)

@app.get("/public/style.css")
async def serve_css():
    try:
        with open(css_path, "r") as f:
            return Response(content=f.read(), media_type="text/css")
    except FileNotFoundError:
        return Response(content=CSS_CONTENT, media_type="text/css")

@app.get("/public/script.js")
async def serve_js():
    try:
        with open(js_path, "r") as f:
            return Response(content=f.read(), media_type="application/javascript")
    except FileNotFoundError:
        return Response(content=JS_CONTENT, media_type="application/javascript")

@app.get("/api/redirect/@{username}")
def redirect_username(username):
    userID = get_id_from_username(username)
    if userID <= 0:
        return RedirectResponse(url=f"https://www.roblox.com/search/users?keyword={username}")
    return redirect_userid(userID)

@app.get("/api/redirect/{userID}")
def redirect_userid(userID):
    if userID <= 0:
        return RedirectResponse(url="https://www.roblox.com/search/users")
    
    return RedirectResponse(url=f"https://www.roblox.com/users/{userID}/profile")

@app.get("/api/user/@{username}")
def get_status_from_name(username: str):
    id = get_id_from_username(username)
    return get_status_from_id(id)


@app.get("/api/user/{userID}")
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