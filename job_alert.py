name: Twice-Daily Remote Customer Care Job Alert

on:
  schedule:
    - cron: '0 10,22 * * *'  # runs twice a day: 10:00 UTC and 22:00 UTC
  workflow_dispatch:         # allows manual runs anytime

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests beautifulsoup4 pandas lxml yagmail

      - name: Run job alert script
        run: python job_alert.py
        env:
          GMAIL_USER: ${{ vars.GMAIL_USER }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
