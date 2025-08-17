### README.md 

```md
# DocuSign Flask Embedded Signing Demo

# URLs-

1. This is URL for access consent- https://account-d.docusign.com/oauth/auth?response_type=code&scope=signature%20impersonation&client_id=33cafb67-e100-4cdd-92bb-694c38487083&redirect_uri=http://127.0.0.1:5000

2. Creating envelope POST https://demo.docusign.net/restapi/v2.1/accounts/{accountId}/envelopes

3. Generate Signing URL (Embedded Signing) https://demo.docusign.net/restapi/v2.1/accounts/{accountId}/envelopes/{envelopeId}/views/recipient

4. Download Signed Document
API:
GET https://demo.docusign.net/restapi/v2.1/accounts/{accountId}/envelopes/{envelopeId}/documents/{documentId}


## Quick Start
1. Create a DocuSign **Developer/Sandbox** account.
2. Generate a **User Access Token** in Sandbox (valid ~8 hours) and note your **Account ID**.
3. Copy `.env.example` → `.env` and fill in `ACCESS_TOKEN` and `ACCOUNT_ID`.
4. `pip install -r requirements.txt`
5. `python app.py` and open `http://localhost:5000`.

## How it works
- `/send` creates an **Envelope** with your uploaded PDF and a `SignHere` tab at (x,y) on a given page.
- It then calls `create_recipient_view` to get an **embedded signing URL** and redirects you there.
- After signing, DocuSign redirects to `/done`.
- Use `/download` with the Envelope ID to download the signed PDF (combined doc).

## Notes
- The **access token** in `.env` expires in ~8 hours. Generate a new one in the Sandbox UI if needed.
- For production: implement OAuth (Authorization Code or JWT) and handle token refresh automatically.
- You can add more tabs (initials/date), multiple recipients, routing order, etc.
- To position the signature accurately, open your PDF, note pixel coordinates, or switch to **Anchor Tabs** (search by text anchors).

## Troubleshooting
- **401 Unauthorized**: Your token expired → generate a fresh token.
- **ACCOUNT_ID wrong**: Verify in DocuSign settings (Sandbox account).
- **Redirect loop**: Ensure `return_url` points to `/done` and your app is reachable.
- **Tab position off**: Adjust `x`, `y`, and `page`. PDF coordinate origin is top-left (SDK maps to DocuSign units automatically).
```

---


## 7) Production Next Steps (to impress)

* Implement **OAuth (JWT or Auth Code)** and automatic token refresh.
* Use **Anchor Tabs** (e.g., place signature at text like `\*\*SIGN_HERE\*\*`).
* Support **multiple recipients** and **routing order**.
* Add **webhooks (Connect)** to auto-download completed documents.
* Store signed PDFs and **Certificate of Completion** to S3/Drive.
* Add a **status page** listing envelopes and statuses.

---


