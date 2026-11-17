from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Jenkins Automation Hub")

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Jenkins Automation Hub</title>
        </head>
        <body>
            <h1>Hello from Hermione!!</h1>
            <p>My first Jenkins CI/CD application.</p>
        </body>
    </html>
    """
