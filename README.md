# Jenkins Automation Hub

A hands-on CI/CD project that automates testing, Docker image creation, and deployment of a FastAPI application using **Jenkins, GitHub Webhooks, Docker, and ngrok**.

The application displays a greeting in the browser. When code is pushed to the GitHub `main` branch, GitHub sends a webhook to Jenkins. Jenkins checks out the latest source, prepares a Python environment, runs automated tests, builds a Docker image, and replaces the previous application container with the updated version.

> **Final verified result:** Jenkins build **#11** was triggered by a GitHub push, the automated test passed, the Docker image built successfully, the application container was redeployed, and the browser displayed **“Hello from Hermione!!”** at `http://localhost:8082`.

---

## Table of contents

1. [Project overview](#1-project-overview)
2. [Architecture and CI/CD flow](#2-architecture-and-cicd-flow)
3. [Technology stack](#3-technology-stack)
4. [Repository structure](#4-repository-structure)
5. [Prerequisites](#5-prerequisites)
6. [Clone the repository](#6-clone-the-repository)
7. [Run the application locally](#7-run-the-application-locally)
8. [Run automated tests](#8-run-automated-tests)
9. [Build and run with Docker manually](#9-build-and-run-with-docker-manually)
10. [Configure Jenkins](#10-configure-jenkins)
11. [Configure GitHub Webhooks with ngrok](#11-configure-github-webhooks-with-ngrok)
12. [Understand the Jenkins pipeline](#12-understand-the-jenkins-pipeline)
13. [End-to-end execution](#13-end-to-end-execution)
14. [Failures encountered and their solutions](#14-failures-encountered-and-their-solutions)
15. [Verification and useful commands](#15-verification-and-useful-commands)
16. [Cleanup](#16-cleanup)
17. [Security considerations](#17-security-considerations)
18. [Limitations and possible improvements](#18-limitations-and-possible-improvements)

---

## 1. Project overview

### Objective

To implement a practical Continuous Integration and Continuous Deployment (CI/CD) workflow for a small FastAPI application.

The project demonstrates how a source-code change can automatically travel through the following steps:

- A developer updates application code.
- The developer commits and pushes the change to GitHub.
- GitHub sends a push event to Jenkins through a webhook.
- Jenkins checks out the latest repository version.
- Jenkins creates a Python virtual environment and installs dependencies.
- Jenkins executes automated tests using `pytest`.
- If tests pass, Jenkins checks Docker connectivity and builds a Docker image.
- Jenkins removes only the previous application container belonging to this project.
- Jenkins starts a new container using the updated image.
- The updated application becomes available in the browser.

### Application behavior

The initial application greeting was:

```text
Hello from Dobby!!
```

The application was later changed to:

```text
Hello from Hermione!!
```

The test was deliberately left expecting the old greeting to demonstrate that a failed test prevents deployment. After correcting the test expectation, the next GitHub push triggered a successful pipeline and deployed the updated greeting.

### Project links

- **GitHub repository:** https://github.com/bytemonkk/Jenkins-Automation-Hub
- **Jenkins job:** `FastAPI-CI-CD`
- **Jenkins dashboard:** http://localhost:8080
- **Application:** http://localhost:8082

---

## 2. Architecture and CI/CD flow

```text
       Developer
           |
           | 1. Commit and push
           v
     GitHub Repository
           |
           | 2. Push webhook event
           v
      ngrok HTTPS Tunnel
           |
           | 3. Forwards request to localhost:8080
           v
       Jenkins Server
           |
           | 4. Checkout source from main
           v
      Verify Project Files
           |
           v
    Setup Python Environment
           |
           v
       Install Dependencies
           |
           v
      Run pytest Tests
           |
           | Tests must pass
           v
    Check Docker Connectivity
           |
           v
      Build Docker Image
           |
           v
      Docker Deployment
           |
           | Remove previous project container
           | Start updated project container
           v
       Docker Container
       Host: 8082
       Container: 8000
           |
           v
     FastAPI Application
           |
           v
  http://localhost:8082
```

### Important pipeline behavior

The test stage acts as a **quality gate**. If a test fails, later stages are skipped. This prevents an unverified application version from being built and deployed.

The deployment stage replaces the existing container named `jenkins-automation-hub-app`. It does not intentionally stop or remove unrelated containers.

---

## 3. Technology stack

| Technology | Purpose |
|---|---|
| Python | Application programming language |
| FastAPI | Web application framework |
| Uvicorn | ASGI server used to run FastAPI |
| pytest | Automated testing |
| FastAPI TestClient | HTTP testing of the application |
| Git and GitHub | Version control and source repository |
| Jenkins | CI/CD pipeline automation |
| Jenkinsfile | Pipeline-as-code configuration |
| Docker | Application containerization |
| Docker Desktop | Local Docker engine on Windows |
| ngrok | HTTPS tunnel to expose local Jenkins webhook endpoint |
| PowerShell | Local Windows command-line environment |

### Environment used during implementation

The verified implementation used:

- Windows with PowerShell
- Jenkins `2.580.2`, running as a Windows service
- Docker Desktop `4.97.0`
- Docker Engine `29.9.2`
- Git `2.49.0`
- Python `3.14.4` in the Jenkins Windows environment
- Python `3.12-slim` as the Docker image base
- ngrok `3.39.11-msix-stable`

Versions may differ on another machine. Use compatible, currently supported versions when recreating the project.

---

## 4. Repository structure

```text
Jenkins-Automation-Hub/
│
├── app.py               # FastAPI application
├── test_app.py          # Automated application test
├── requirements.txt     # Python dependencies
├── Dockerfile           # Instructions to build the application image
├── Jenkinsfile          # Jenkins declarative pipeline
├── .dockerignore        # Files excluded from Docker build context
├── .gitignore           # Files excluded from Git
└── README.md            # Project documentation
```

A local `.venv/` directory may be created during development. It should not be committed to Git.

### `app.py`

```python
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
```

### `test_app.py`

```python
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_homepage():
    response = client.get("/")

    assert response.status_code == 200
    assert "Hello from Hermione!!" in response.text
```

The test checks two things:

1. The homepage returns HTTP status code `200`.
2. The response contains the expected greeting.

If the application greeting changes, update the expected text in the test as well.

### `requirements.txt`

```text
fastapi
uvicorn[standard]
httpx
pytest
```

- `fastapi`: Web framework.
- `uvicorn[standard]`: ASGI server.
- `httpx`: HTTP client dependency used by the test client in this setup.
- `pytest`: Test runner.

### `Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Explanation:

- `FROM`: Uses a lightweight Python base image.
- `WORKDIR`: Sets `/app` as the working directory inside the image.
- `COPY requirements.txt .`: Copies dependency definitions.
- `RUN pip install`: Installs application dependencies.
- `COPY app.py .`: Copies the FastAPI application.
- `EXPOSE 8000`: Documents the port used by the application inside the container.
- `CMD`: Starts Uvicorn and makes the application listen on all container interfaces.

### `.dockerignore`

The file excludes development and Git files from the Docker build context. The project configuration used exclusions such as:

```text
.venv/
venv/
__pycache__/
.pytest_cache/
.git/
.gitignore
```

### `.gitignore`

The Git ignore file excludes local environment files and generated Python files. For example:

```gitignore
venv/
.venv/
__pycache__/
*.py[cod]
.env
```

---

## 5. Prerequisites

Install or configure the following before starting:

1. **Git** – to clone, commit, and push the repository.
2. **Python** – to run the application and tests locally.
3. **Docker Desktop** – with the Docker engine running and Linux containers enabled.
4. **Jenkins** – installed and accessible from the browser.
5. **Jenkins Git integration** – the Git plugin must be available for Pipeline from SCM checkout.
6. **Jenkins GitHub integration** – the GitHub plugin must be installed for the GitHub webhook trigger used here.
7. **ngrok** – required only when GitHub needs to reach Jenkins running on your local machine.
8. A GitHub repository containing this project.

The exact Jenkins plugin installation and configuration screens can vary by Jenkins release. Ensure the Git and GitHub integration plugins are installed before configuring the job.

### Check installations

Run these in PowerShell:

```powershell
git --version
python --version
docker --version
docker compose version
ngrok version
```

Check Docker connectivity:

```powershell
docker version
```

The command should show both Docker Client and Server information. If the server section is missing, start Docker Desktop and wait for the engine to become ready.

---

## 6. Clone the repository

Open PowerShell and execute:

```powershell
git clone https://github.com/bytemonkk/Jenkins-Automation-Hub.git
```

Move into the project directory:

```powershell
cd Jenkins-Automation-Hub
```

Open it in VS Code:

```powershell
code .
```

The original development directory used during implementation was:

```text
E:\Jenkins-Automation-Hub
```

Your local directory can be different.

---

## 7. Run the application locally

From the project root, create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation because of the execution policy, you can avoid activation and invoke the environment's Python executable directly. Alternatively, for the current PowerShell session only, an administrator-approved execution policy adjustment may be needed.

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the application:

```powershell
python -m uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

The page should display:

```text
Hello from Hermione!!
```

Stop the development server with `Ctrl+C`.

---

## 8. Run automated tests

Make sure dependencies are installed, then run:

```powershell
python -m pytest -v
```

Expected successful result:

```text
test_app.py::test_homepage PASSED

1 passed
```

A passing test means the homepage returned status `200` and contained the expected greeting.

The pipeline also runs this test. A failed test stops the pipeline before the Docker build and deployment stages.

---

## 9. Build and run with Docker manually

Make sure Docker Desktop is running.

### Build the image

Run this from the project root:

```powershell
docker build -t jenkins-automation-hub:latest .
```

### Run the container

```powershell
docker run -d --restart unless-stopped --name jenkins-automation-hub-app -p 8082:8000 jenkins-automation-hub:latest
```

Port mapping:

- `8082`: Port on the Windows host.
- `8000`: Port inside the container where Uvicorn listens.

Open the application:

```text
http://localhost:8082
```

### Check the running container

```powershell
docker ps
```

### View application logs

```powershell
docker logs jenkins-automation-hub-app
```

### Stop and remove only this project's application container

```powershell
docker rm -f jenkins-automation-hub-app
```

This command targets the named application container only. Do not use broad cleanup commands such as `docker rm -f $(docker ps -aq)` or `docker system prune -a` on a machine hosting other projects.

---

## 10. Configure Jenkins

### 10.1 Start Jenkins

Open the Jenkins dashboard:

```text
http://localhost:8080
```

Sign in with your Jenkins account.

In the implementation environment, Jenkins was installed as a Windows service with service name `Jenkins`.

### 10.2 Create a Pipeline job

1. Select **New Item**.
2. Enter the job name:

   ```text
   FastAPI-CI-CD
   ```

3. Select **Pipeline**.
4. Select **OK**.

### 10.3 Configure Pipeline from SCM

In the job configuration, find the **Pipeline** section.

Set:

| Setting | Value |
|---|---|
| Definition | Pipeline script from SCM |
| SCM | Git |
| Repository URL | `https://github.com/bytemonkk/Jenkins-Automation-Hub.git` |
| Credentials | None for this public repository |
| Branch specifier | `*/main` |
| Script Path | `Jenkinsfile` |

Save the configuration.

**Why Pipeline from SCM?**

The pipeline definition is stored in the GitHub repository as a `Jenkinsfile`. Jenkins reads that file from source control. This keeps pipeline configuration version-controlled alongside the application.

### 10.4 Enable the GitHub webhook trigger

Open the job's **Configure** page.

Under **Build Triggers**, enable:

```text
GitHub hook trigger for GITScm polling
```

Save the job.

This tells Jenkins to respond to GitHub webhook notifications for the configured repository.

### 10.5 Important: Jenkins service and Docker access

In this implementation, Jenkins ran as a Windows service under the `LocalSystem` account.

Docker Desktop's executable was installed at:

```text
C:\Users\MANOJ KUMAR SUNKARA\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe
```

The Jenkins service did not inherit the interactive user's Docker-specific PATH. Therefore, the Jenkins pipeline used the **absolute path** to `docker.exe` rather than relying on the command being available as `docker`.

This path is specific to the machine used during implementation. If you recreate the project:

1. Find the actual location of `docker.exe` on your machine.
2. Confirm that the Jenkins service account can access the executable and communicate with the Docker engine.
3. Update the Docker executable path in the `Jenkinsfile` if it differs.
4. Restart the Jenkins service if you change service-level environment variables.

Do not blindly copy the example path onto another computer.

---

## 11. Configure GitHub Webhooks with ngrok

### Why ngrok was needed

Jenkins was running locally at:

```text
http://localhost:8080
```

GitHub's servers cannot directly send webhook requests to a localhost address on your computer. ngrok creates a publicly reachable HTTPS endpoint and forwards incoming requests to the local Jenkins server.

### 11.1 Start ngrok

Install ngrok and authenticate it according to the current ngrok instructions.

Open a separate terminal and run:

```powershell
ngrok http 8080
```

Keep this terminal open while webhook testing is required.

ngrok displays a forwarding address similar to:

```text
https://example-name.ngrok-free.dev
```

The actual address is generated by ngrok and may change when the tunnel is restarted.

During this implementation, the forwarding address was:

```text
https://clutter-matching-jump.ngrok-free.dev
```

It forwarded traffic to:

```text
http://localhost:8080
```

### 11.2 Add the webhook in GitHub

1. Open the GitHub repository:

   `https://github.com/bytemonkk/Jenkins-Automation-Hub`

2. Select **Settings**.
3. Open **Webhooks**.
4. Select **Add webhook**.

Use the following configuration:

| Field | Value |
|---|---|
| Payload URL | `https://YOUR-NGROK-URL/github-webhook/` |
| Content type | `application/json` |
| Secret | Configure a secret for a secured setup; the learning setup used a blank secret |
| Events | Just the push event |
| Active | Enabled |

Replace `YOUR-NGROK-URL` with the currently active ngrok HTTPS hostname.

For the original tunnel, the configured payload URL was:

```text
https://clutter-matching-jump.ngrok-free.dev/github-webhook/
```

The trailing `/` is included.

Save the webhook.

### 11.3 Test the webhook

GitHub sends a ping event after webhook creation. In this implementation, the ping delivery returned:

```text
HTTP 200
```

Then a real Git push was performed. Jenkins build #9 showed:

```text
Started by GitHub push by bytemonkk
```

This confirmed that an actual push event reached Jenkins and triggered the job.

### 11.4 Keep the tunnel available

The ngrok terminal must remain running for GitHub to reach the local Jenkins server through that tunnel.

If ngrok is stopped:

- GitHub cannot reach the old forwarding endpoint.
- Webhook deliveries may fail.
- Restarting ngrok may generate a different URL.
- If the URL changes, update the GitHub webhook Payload URL.

---

## 12. Understand the Jenkins pipeline

The pipeline is defined in the root-level `Jenkinsfile`.

The configured job uses **Pipeline from SCM**, so Jenkins checks out the repository and reads this file.

### Pipeline stages

| Stage | Responsibility |
|---|---|
| Declarative: Checkout SCM | Jenkins checks out the configured GitHub branch |
| Verify | Confirms the project workspace and files |
| Setup Environment | Creates `.venv` and installs `requirements.txt` |
| Test | Runs `pytest` |
| Build | Confirms the application test stage completed and checks Python |
| Docker Connectivity | Runs Docker CLI using its absolute executable path |
| Docker Build | Builds `jenkins-automation-hub:latest` |
| Docker Deploy | Removes the previous named application container and starts the updated one |

### Important Docker commands used by the pipeline

Docker connectivity:

```powershell
"C:\Users\MANOJ KUMAR SUNKARA\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe" version
```

Build image:

```powershell
"C:\Users\MANOJ KUMAR SUNKARA\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe" build -t jenkins-automation-hub:latest .
```

Remove the previous application container:

```powershell
"C:\Users\MANOJ KUMAR SUNKARA\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe" rm -f jenkins-automation-hub-app
```

Start the updated container:

```powershell
"C:\Users\MANOJ KUMAR SUNKARA\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe" run -d --restart unless-stopped --name jenkins-automation-hub-app -p 8082:8000 jenkins-automation-hub:latest
```

The pipeline handles the case where the old container does not yet exist, so the first deployment can proceed.

### Why the test stage must run before Docker deployment

The order is intentional:

```text
Test -> Docker Build -> Docker Deploy
```

If a test fails, Jenkins skips the later stages. This prevents a version that failed its automated test from replacing the currently running application.

### Deployment behavior and downtime

This project uses a simple replacement strategy:

1. Remove the existing `jenkins-automation-hub-app` container.
2. Start a new container from the newly built image.

There may be a brief period when the application is unavailable between these operations. This is a learning-project deployment strategy, not a zero-downtime rolling or blue-green deployment.

---

## 13. End-to-end execution

After Jenkins, Docker Desktop, and the webhook are configured, use this workflow for each code change.

### Step 1: Make a code change

For example, edit `app.py` and update the greeting.

If the expected application behavior changes, update `test_app.py` to match.

### Step 2: Run tests locally

```powershell
python -m pytest -v
```

### Step 3: Review Git changes

```powershell
git status
```

### Step 4: Stage the changes

```powershell
git add app.py test_app.py
```

Stage only the files that you intend to commit. For a documentation-only change, for example:

```powershell
git add README.md
```

### Step 5: Commit

Example:

```powershell
git commit -m "feat: update application greeting"
```

### Step 6: Push to GitHub

```powershell
git push origin main
```

### Step 7: Check Jenkins

Open:

```text
http://localhost:8080
```

Select the `FastAPI-CI-CD` job and open the latest build.

Check the Console Output. A webhook-triggered build should contain a line similar to:

```text
Started by GitHub push by <github-username>
```

### Step 8: Confirm deployment

When Jenkins reports:

```text
Finished: SUCCESS
```

open:

```text
http://localhost:8082
```

Confirm that the browser displays the latest greeting.

---

## 14. Failures encountered and their solutions

The failures below are part of the actual implementation process. They are documented because they explain important CI/CD troubleshooting concepts.

### Failure 1: Jenkins could not find Docker in PATH

**What happened**

The initial Docker connectivity stage attempted to locate Docker using:

```text
where docker
```

The Jenkins build failed because the Windows Jenkins service could not find Docker through its PATH.

**Why it happened**

Jenkins was running as a Windows service under `LocalSystem`. Its environment was different from the interactive Windows user's environment, where Docker Desktop's executable was available.

**Solution**

The pipeline was changed to call Docker using its absolute executable path:

```text
C:\Users\MANOJ KUMAR SUNKARA\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe
```

The next build successfully displayed Docker Client and Server details.

**Lesson**

A command that works in an interactive terminal may fail inside a CI service because the service can run under a different account and environment.

---

### Failure 2: First attempt to deploy a repeatable container

**What needed improvement**

The first deployment command started a container with a fixed name. Re-running it would fail if a container with that name was already present.

**Solution**

The deployment stage was changed to remove the previous project container before starting the new one:

```powershell
docker rm -f jenkins-automation-hub-app
```

The pipeline handles the no-existing-container case, then runs the replacement container:

```powershell
docker run -d --restart unless-stopped --name jenkins-automation-hub-app -p 8082:8000 jenkins-automation-hub:latest
```

**Lesson**

A deployment process should account for the state left by previous deployments. This implementation makes repeated deployments possible without accumulating containers with the same name.

---

### Failure 3: GitHub webhook could not directly reach localhost

**What happened**

Jenkins was running locally, but GitHub needed a reachable endpoint to send push notifications.

**Why it happened**

`localhost` refers to the machine on which a request is made. GitHub's servers cannot use your computer's `localhost` address to reach your Jenkins instance.

**Solution**

ngrok exposed a temporary HTTPS endpoint and forwarded requests to local port `8080`.

The GitHub webhook used:

```text
https://YOUR-NGROK-URL/github-webhook/
```

The GitHub ping returned HTTP 200, and a subsequent push triggered Jenkins build #9.

**Lesson**

A webhook requires a network-reachable endpoint. A tunnel can help during local development, but it is not a substitute for secure production ingress.

---

### Failure 4: Build #10 failed because the test expected the old greeting

**What happened**

The application was changed from:

```text
Hello from Dobby!!
```

to:

```text
Hello from Hermione!!
```

However, `test_app.py` still expected the old Dobby greeting.

The GitHub push triggered Jenkins build #10. The test failed because the actual application response contained Hermione while the test expected Dobby.

The later stages, including Docker Build and Docker Deploy, were skipped.

**Solution**

The expected greeting in `test_app.py` was updated:

```python
assert "Hello from Hermione!!" in response.text
```

The change was committed and pushed.

**Why this failure was useful**

It demonstrated the CI quality gate in practice. Jenkins did not deploy the application after the test failed. The previously deployed container remained running because the deployment stage was never reached.

**Lesson**

Automated tests must represent the intended application behavior. A failing test should stop an unsafe or unverified deployment.

---

### Successful recovery: Build #11

After the test expectation was corrected, the next GitHub push triggered Jenkins build #11.

The console output confirmed:

```text
Started by GitHub push by bytemonkk
```

The test result was:

```text
test_app.py::test_homepage PASSED
1 passed
```

The Docker image was built and tagged:

```text
Successfully built c1daa7d97c7d
Successfully tagged jenkins-automation-hub:latest
```

The previous application container was removed and a new one was started. Jenkins finished with:

```text
Finished: SUCCESS
```

The browser was then verified at `http://localhost:8082`, displaying:

```text
Hello from Hermione!!
```

This confirmed the complete GitHub-to-Jenkins-to-Docker deployment flow.

---

## 15. Verification and useful commands

Run these commands in PowerShell when troubleshooting.

### Git status and history

```powershell
git status
git log --oneline -5
```

### Python version

```powershell
python --version
```

### Run tests

```powershell
python -m pytest -v
```

### Docker version and engine connectivity

```powershell
docker version
```

### List running containers

```powershell
docker ps
```

### List all containers

```powershell
docker ps -a
```

### List local images

```powershell
docker images
```

### Inspect application logs

```powershell
docker logs jenkins-automation-hub-app
```

### Follow application logs

```powershell
docker logs -f jenkins-automation-hub-app
```

Press `Ctrl+C` to stop following logs. This does not stop the container.

### Check the application

Open:

```text
http://localhost:8082
```

### Jenkins

Open:

```text
http://localhost:8080
```

Inspect the latest `FastAPI-CI-CD` build's Console Output for the exact stage where a failure occurred.

---

## 16. Cleanup

Use these commands only when you intentionally want to remove this project's application resources.

### Remove the application container

```powershell
docker rm -f jenkins-automation-hub-app
```

### Remove this project's image

```powershell
docker rmi jenkins-automation-hub:latest
```

The image removal may fail if a container still uses the image. Remove the project container first.

### Stop ngrok

Return to the terminal running ngrok and press:

```text
Ctrl+C
```

### Stop the local FastAPI development server

If one is running, press:

```text
Ctrl+C
```

**Do not remove or stop unrelated Docker containers.** The implementation environment also contained containers for other work. The Jenkins deployment was designed to target only `jenkins-automation-hub-app`.

---

## 17. Security considerations

This is a local learning project, not a production-hardened deployment.

- ngrok creates a publicly reachable endpoint while the tunnel is active. Anyone who can reach the endpoint may be able to send requests to the exposed Jenkins service.
- Keep the tunnel running only when needed.
- Use a strong Jenkins administrator password and appropriate user permissions.
- Configure a webhook secret and validate webhook requests in a secured deployment. The learning setup documented here used a blank secret.
- Do not commit passwords, access tokens, private keys, `.env` files, or other secrets to Git.
- Avoid exposing Jenkins or Docker management interfaces publicly without appropriate security controls.
- Use secure ingress, TLS, authentication, authorization, and network restrictions for a production environment.
- The Docker CLI path and ngrok hostname in this README are machine/session-specific examples, not universal values.

---

## 18. Limitations and possible improvements

The project achieves an automated CI/CD flow, but it can be extended further.

1. **Zero-downtime deployment:** Replace the remove-then-run strategy with blue-green or rolling deployment.
2. **BuildKit:** Configure Docker Buildx/BuildKit instead of the legacy builder.
3. **Dependency pinning:** Pin Python dependency versions for more reproducible builds.
4. **Test coverage:** Add tests for error handling and additional API routes.
5. **Container health checks:** Add a Docker health check and verify readiness before considering deployment successful.
6. **Rollback:** Retain a previous known-good image and automate rollback if the new container fails its health check.
7. **Secrets management:** Store credentials in Jenkins Credentials and use a webhook secret.
8. **Production hosting:** Deploy to a dedicated server or cloud environment with secure ingress rather than relying on a developer's local machine and ngrok.
9. **Observability:** Add application logs, metrics, and monitoring.

---

## Key concepts demonstrated

| Concept | What this project demonstrates |
|---|---|
| Continuous Integration | Automatically checking changes pushed to GitHub |
| Continuous Delivery/Deployment | Building and deploying the application through Jenkins |
| Pipeline as Code | Defining CI/CD stages in a `Jenkinsfile` |
| Webhook | Notifying Jenkins when a GitHub push occurs |
| Automated Testing | Preventing deployment when a test fails |
| Docker Image | Packaging the FastAPI application and dependencies |
| Docker Container | Running the packaged application in isolation |
| Port Mapping | Exposing container port `8000` through host port `8082` |
| Troubleshooting | Resolving service PATH, webhook reachability, and test failures |

## Final result

<pre>
GitHub Push
    |
    v
GitHub Webhook
    |
    v
Jenkins Pipeline
    |
    +--> Checkout
    +--> Verify
    +--> Setup Python Environment
    +--> Install Dependencies
    +--> Run Tests
    +--> Check Docker
    +--> Build Image
    +--> Deploy Container
    |
    v
FastAPI Application
    |
    v
http://localhost:8082
</pre>

**Project status: Successfully implemented and verified with Jenkins build #11.**
