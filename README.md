# GitHub Webhook Setup Guide

This guide will walk you through setting up GitHub webhooks for your action-repo.

## Step 1: Create the Action Repository

1. Go to GitHub and create a new repository called `action-repo`
2. Initialize it with a README
3. Clone it locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/action-repo.git
   cd action-repo
   ```

## Step 2: Set Up Local Development (Using ngrok)

For local testing, you'll need to expose your localhost to the internet using ngrok:

1. **Download and install ngrok**
   - Visit: https://ngrok.com/download
   - Follow installation instructions for your OS

2. **Start your Flask application**
   ```bash
   # In your webhook-repo directory
   python run.py
   ```

3. **Start ngrok in a new terminal**
   ```bash
   ngrok http 5000
   ```

4. **Copy the ngrok URL**
   - Look for the "Forwarding" line, e.g., `https://abc123.ngrok.io`
   - Your webhook URL will be: `https://abc123.ngrok.io/webhook/receiver`

## Step 3: Configure GitHub Webhook

1. **Navigate to your action-repo on GitHub**
   - Go to: `https://github.com/YOUR_USERNAME/action-repo`

2. **Open Repository Settings**
   - Click on "Settings" tab
   - Click on "Webhooks" in the left sidebar
   - Click "Add webhook" button

3. **Configure the Webhook**

   Fill in the following details:

   - **Payload URL**: 
     - Local testing: `https://your-ngrok-url.ngrok.io/webhook/receiver`
     - Production: `https://your-server.com/webhook/receiver`
   
   - **Content type**: 
     - Select `application/json`
   
   - **Secret**: 
     - Leave blank for now (optional security feature)
   
   - **SSL verification**: 
     - Enable SSL verification (recommended)
   
   - **Which events would you like to trigger this webhook?**
     - Select "Let me select individual events"
     - Check these boxes:
       - ✅ **Pushes**
       - ✅ **Pull requests**
     - Uncheck everything else
   
   - **Active**: 
     - ✅ Make sure this is checked

4. **Save the Webhook**
   - Click "Add webhook" button
   - GitHub will send a test ping to verify the endpoint
   
5. **Start UI in a new terminal**
   ```bash
   streamlit run ui.py
   ```

## Step 4: Verify Webhook Setup

1. **Check Recent Deliveries**
   - In webhook settings, click on your webhook
   - Click "Recent Deliveries" tab
   - You should see a "ping" event with a green checkmark (✅)

2. **Test with a Push**
   ```bash
   # In your action-repo directory
   echo "Test" >> README.md
   git add README.md
   git commit -m "Test webhook"
   git push origin main
   ```

3. **Check the webhook receiver**
   - Look at your Flask terminal for incoming requests
   - Check your Streamlit UI at `http://localhost:8501`
   - You should see the push event appear

## Step 5: Test Pull Request and Merge

### Create a Pull Request

1. **Create a new branch**
   ```bash
   git checkout -b feature-test
   echo "Feature content" >> feature.txt
   git add feature.txt
   git commit -m "Add feature"
   git push origin feature-test
   ```

2. **Create PR on GitHub**
   - Go to your action-repo on GitHub
   - Click "Pull requests" tab
   - Click "New pull request"
   - Select `base: main` and `compare: feature-test`
   - Click "Create pull request"
   - Check your webhook receiver - you should see a PULL_REQUEST event

### Test Merge

1. **Merge the Pull Request**
   - On the PR page, click "Merge pull request"
   - Click "Confirm merge"
   - Check your webhook receiver - you should see a MERGE event


