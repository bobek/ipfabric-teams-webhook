import hmac

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request, status, BackgroundTasks
from fastapi.responses import RedirectResponse, Response
from models import Event

from config import settings
from teams import send_card

app = FastAPI()


@app.get("/", response_class=RedirectResponse)
async def redirect_root():
    return "/docs"


@app.get("/healthcheck", response_model=str)
async def root():
    return "Ok"


@app.post('/ipfabric')
async def webhook(data: Event, request: Request, bg_tasks: BackgroundTasks, x_ipf_signature: str = Header(None)):
    input_hmac = hmac.new(
        key=settings.ipf_secret.encode(),
        msg=await request.body(),
        digestmod="sha256"
    )
    if not hmac.compare_digest(input_hmac.hexdigest(), x_ipf_signature):
        raise HTTPException(status_code=400, detail="X-IPF-Signature does not match.")
    print(data.__dict__)
    bg_tasks.add_task(send_card, data)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
