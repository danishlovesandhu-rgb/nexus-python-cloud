# NEXUS-X Python Cloud Runner

A minimal single-user Python script runner with a terminal-style web interface.

## Important security limitation

This is a personal-use starter, **not a secure sandbox**. The script runs as a subprocess under the web service's operating-system account. A Python script can still access files and network resources available to that account. The timeout and file-size checks are operational limits, not a security boundary.

- Run only scripts you wrote and trust.
- Do not share the URL or access key.
- Do not use this for public users, unknown uploads, malware, or sensitive workloads.
- For a real multi-user service, use isolated containers/VMs, non-root execution, network isolation, CPU/RAM/PID limits, per-user authorization, and a job queue.

## Deploy free (Android + GitHub + Render)

1. Install Termux from F-Droid or its official GitHub release.
2. In Termux:
   ```sh
   pkg update -y
   pkg install -y git
   ```
3. Create a GitHub repository named `nexus-python-cloud`.
4. Upload these project files to that repository. You can use GitHub's mobile website, or clone/push from Termux:
   ```sh
   git clone https://github.com/YOUR_USERNAME/nexus-python-cloud.git
   cd nexus-python-cloud
   ```
   Copy the downloaded project files into this folder, then:
   ```sh
   git add .
   git commit -m "Create NEXUS-X Python cloud runner"
   git push
   ```
5. Sign in to Render and choose **New + → Blueprint**. Connect the GitHub repository. Render reads `render.yaml`.
6. Wait for deployment. In the Render service's Environment page, find the generated `APP_KEY`. Keep it private.
7. Open the Render service URL on Android. Enter the `APP_KEY`, choose a `.py` file, and press **RUN SCRIPT**.

## Free-hosting limits

Free services can sleep when idle, have limited CPU/RAM and may change their free-tier terms. The first request after sleeping can be slow. This is not an always-on production server.

## Local syntax check in Termux

```sh
pkg install -y python
python -m py_compile app.py
```

To run locally for testing:
```sh
pip install -r requirements.txt
export APP_KEY='make-a-long-random-secret'
uvicorn app:app --host 127.0.0.1 --port 8000
```
Open `http://127.0.0.1:8000` on the same phone.
