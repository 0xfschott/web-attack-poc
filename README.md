# web attack PoC creator (WAPC)

WAPC is a web application designed to aid in building and serving proof-of-concept (PoC) attacks for various web vulnerabilities during penetration tests. It provides an interface for configuring and serving custom HTML pages to demonstrate vulnerabilities related to Cross-Origin Resource Sharing (CORS), Cross-Site Request Forgery (CSRF), Clickjacking, etc. Custom templates can be added and easily changed. Prebuilt templates will be added in the future.

![image](https://github.com/0xfschott/web-attack-poc/assets/17066401/a422cf23-8cfe-4d66-9b07-0c131fd22766)

**Features:**
- Create and manage custom HTML templates for different attacks
- Serve templates dynamically with unique URLs
- Import pre-built templates for common vulnerabilities
- Session-based management to isolate user templates


## Installation Guide
Needs Python 3.7 or higher

```
git clone https://github.com/yourusername/web-attack-poc.git
cd web-attack-poc
python -m venv venv
source venv/bin/activate
pip install -r requiremnents
python app.py
```
Access the application: Open your web browser and navigate to http://127.0.0.1:5000.
