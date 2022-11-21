from webbrowser import get
from fastapi_offline import FastAPIOffline
from fastapi import Security, FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, PlainTextResponse 
from fastapi.security.api_key import APIKeyHeader, APIKey
from pydantic import BaseModel, Field
import time
import secrets
import string
import uuid



expiry = 80 # Expiry time in ms.

smiley_datastore = {}

flag = "FLAG_PLACEHOLDER"

# Instantiating an empty dict to store our API keys and the time (in ms) that they were created.
API_KEYS = {}
API_KEY_NAME = "access_key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

description = """
LulzCorp is the first company to offer HaaS (Happiness as a Service). 
The concept is simple. Query our custom, proprietary API and you'll receive a smile. The HTTP response is sure to cure any sadness.

### *Warning!*
The intern that wrote our core API said that one of the methods is vulnerable to something. I vaguely remember them saying it was vulnerable "Remote something something". Anyways, we never documented the issue before they left for Microsoft. We really need to start documenting this stuff in Jira. As a precaution, we added a layer of protection. Every call to our API now requires an *API key*. Anyone can create an API key. Trick is, the key is only valid for ~80 milliseconds. This should keep most script kiddies from abusing our API. 

#### Update 10/6/2022:
LulzCorp is pleased to announce that we've received over 25 million in Series A funding. We'll be using this additional capital to fund our R&D into new smiley faces. 

#### Update 11/9/2022:
All is lost. The end is neigh. We've had to lay off over 90 percent of our engineering staff. Now it's just our janitor and a part-time intern. We should have just sold to Elon Musk when we had the chance. 

## API Endpoints
### Create API Keys `/create_key` 

You'll need a valid key to contact any of the protected endpoints. Format of API keys are a 64 character alphanumeric string. Keep in mind any generated keys are only valid for about 80 milliseconds. 

Keys must be provided as a HTTP header: `access_key: 2DYP486XQORSLQZQ1RZ49RTRH4OIKSG74HC2QCAQP1Q6OUWMC9WEQYH39U2RC07D`

###  Default Smile `/smile`

This is the default API endpoint. Simply provide a valid API key and you'll receive joy. 

### Temporarily Store Custom Smileys `/custom/upload`

LulzCorp allows advanced users to store their own custom smileys in memory to be retrieved later. To upload a custom smiley, send an HTTP POST with a valid API key.

This API allows you to create custom smiley faces using math in Python. If it's possible in Python, it's possible here!

**Example:**

`curl http://ip/custom/upload -H "access_key: 2DYP486XQORSLQZQ1RZ49RTRH4OIKSG74HC2QCAQP1Q6OUWMC9WEQYH39U2RC07D" -H "Content-Type: application/json" -d '{"text": "smiley = \':D\' * 8"}`

Note the local variable `smiley`. Assign the output of your logic to `smiley`. The contents of smiley will be sent back to the requestor. 

If your custom smiley was stored successfully you'll be provided the ID of the smiley so you can fetch it later.

**Example ID:**

`97a41f6f-a6d8-4d6c-9a51-d9ab1f84df8d`

### Fetch Custom Smileys `/custom/fetch/{smile_id}`
Provide the ID you received while uploading your custom smile and a valid API key. 


"""

tags_metadata = [
    {
        "name": "Open",
        "description": "Operations that **do not** require an API key.",
    },
    {
        "name": "Protected",
        "description": "Operations that require a valid API key.",
    },
    {
        "name": "Default",
        "description": "Redirect `/` to `/docs`",
    },
]

app = FastAPIOffline(
    openapi_tags=tags_metadata,
    title="LulzCorpAPI",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "DC610: castleOak",
        "url": "https://twitter.com/Castle__Oak",
        "email": "pmg-burn@protonmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)


async def get_api_key(
    api_key_header: str = Security(api_key_header),
) -> None:

    if api_key_header not in API_KEYS:
        raise HTTPException(
            status_code=403, detail="FORBIDDEN - Key does not exist."
        )
    
    if round(time.time() * 1000 - API_KEYS[api_key_header] > expiry):
        raise HTTPException(
            status_code=403, detail="FORBIDDEN - Key exists but has expired."
        )

class Smiley(BaseModel):
    text: str 


@app.get("/", tags=["Default"])
async def index() -> None:
    return RedirectResponse("/docs")

@app.get("/smile", dependencies=[Depends(get_api_key)], tags=["Protected"])
async def smile() -> dict:
    return PlainTextResponse(":-D")

@app.get("/user-flag", dependencies=[Depends(get_api_key)], tags=["Protected"])
async def user_level_flag() -> dict:
    return PlainTextResponse(flag)

@app.post("/custom/upload", dependencies=[Depends(get_api_key)], tags=["Protected"])
async def upload_custom_smile(smiley_post: Smiley):
    smiley_id = str(uuid.uuid4())
    smiley_datastore[smiley_id] = smiley_post.text
    return PlainTextResponse(smiley_id) 

@app.get("/custom/fetch/{smile_id}", dependencies=[Depends(get_api_key)], tags=["Protected"])
async def fetch_custom_smile(smile_id: str):
    try: 
        contents = smiley_datastore[smile_id]
        local_vars = {}
        exec(str(contents), None, local_vars)
        return PlainTextResponse(str(local_vars["smiley"]))
    except Exception as e:
        raise HTTPException(500, f"Internal Server Error - Problem with Smiley Payload: {e}")

@app.get("/create_key", tags=["Open"])
async def create_key() -> str:
    key = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(64))
    # Store a kv pair containing the key and creation time. 
    API_KEYS[key] = round(time.time() * 1000)
    return PlainTextResponse(key)

####################################
