SHANKAR TRADING DASHBOARD V31.1 — RESPONSIVE DEPLOYMENT

Supported screens
- Android/iPhone mobile
- Tablets
- Laptop and desktop

Responsive behaviour
- Mobile: single-column cards and full-width controls
- Tablet: two-column cards where space allows
- Desktop: wide terminal layout
- Option chain: horizontally swipe/scroll on smaller screens
- Charts, metrics, calendar, pivot cards and MTF panels resize automatically

Run locally
1. Open this folder in VS Code.
2. Install packages: pip install -r requirements.txt
3. Add your credentials to .streamlit/secrets.toml using secrets.example.toml.
4. Run: streamlit run app.py

Important
- Never upload .streamlit/secrets.toml to GitHub.
- The access token may expire and need replacement.
- This dashboard is for the Indian market. Commodity and crypto UI is not shown.
