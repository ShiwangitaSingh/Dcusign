##  Prerequisites (DocuSign Sandbox)

# 1. Create a **free developer account**: [https://developers.docusign.com/](https://developers.docusign.com/)
# 2. In **Settings → Apps and Keys**, create an **Integration Key** (client ID). You do **not** need it for this token-based quick demo, but you’ll need it for a production-ready OAuth flow later.
# 3. In **Apps and Keys**, click **Generate JWT/Access Token** or **Add User** → **Generate** a **User Access Token** (Sandbox). Copy the token value (starts with `eyJ...`).
# 4. Go to **Settings → Integrations → API and Keys** and note your **Account ID** (GUID looking string).

# > For this demo, you only need: **ACCESS\_TOKEN** (user token) and **ACCOUNT\_ID** (sandbox). You’ll paste both into `.env`.


# > **Note**: Access tokens expire after \~8 hours. If you get 401/permission errors, generate a fresh token from the DocuSign Sandbox UI and restart the app.

# Open: `http://localhost:5000`

### app.py

import os
import base64
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, SignHere, Tabs, Recipients, RecipientViewRequest

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCOUNT_ID = os.getenv("ACCOUNT_ID")
DS_BASE_PATH = os.getenv("DS_BASE_PATH", "https://demo.docusign.net/restapi")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
SIGNED_FOLDER = os.path.join(os.path.dirname(__file__), 'signed docs')

ALLOWED_EXTENSIONS = {"pdf"}

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "change-me")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SIGNED_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_api_client():
    if not ACCESS_TOKEN:
        raise RuntimeError("ACCESS_TOKEN is missing. Put it in your .env.")
    api_client = ApiClient()
    api_client.host = DS_BASE_PATH
    api_client.set_default_header("Authorization", f"Bearer {ACCESS_TOKEN}")
    return api_client


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/send", methods=["POST"])
def send_for_signing():
    # 1) Get form data
    recipient_name = request.form.get("recipient_name")
    recipient_email = request.form.get("recipient_email")
    x = request.form.get("x", type=int, default=100)
    y = request.form.get("y", type=int, default=150)
    page = request.form.get("page", type=int, default=1)

    file = request.files.get("file")
    if not file or file.filename == "":
        flash("Please choose a PDF file.")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Only PDF files are allowed.")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # 2) Read file and prepare DocuSign Document
    with open(filepath, "rb") as f:
        doc_b64 = base64.b64encode(f.read()).decode("ascii")

    document = Document(
        document_base64=doc_b64,
        name=filename,
        file_extension="pdf",
        document_id="1",
    )

    # 3) Signer + signature tab (with client_user_id for embedded signing)
    signer = Signer(
        email=recipient_email,
        name=recipient_name,
        recipient_id="1",
        routing_order="1",
        client_user_id="1000"  # REQUIRED for embedded signing
    )

    sign_here = SignHere(
        document_id="1",
        page_number=str(page),
        x_position=str(x),
        y_position=str(y)
    )
    signer.tabs = Tabs(sign_here_tabs=[sign_here])

    recipients = Recipients(signers=[signer])

    envelope_definition = EnvelopeDefinition(
        email_subject="Please sign this document",
        documents=[document],
        recipients=recipients,
        status="sent",  # "sent" to send immediately
    )

    # 4) Send envelope
    api_client = get_api_client()
    envelopes_api = EnvelopesApi(api_client)
    results = envelopes_api.create_envelope(
        account_id=ACCOUNT_ID,
        envelope_definition=envelope_definition
    )
    envelope_id = results.envelope_id
    session["last_envelope_id"] = envelope_id  # Store in session

    flash(f"Envelope ID: {envelope_id}")
    print(f"Envelope ID: {envelope_id}")

    # 5) Create recipient view (embedded signing link)
    return_url = url_for("done", _external=True)
    view_request = RecipientViewRequest(
        authentication_method="none",
        email=recipient_email,
        user_name=recipient_name,
        client_user_id="1000",  # MUST match signer.client_user_id
        return_url=return_url,
    )

    recipient_view = envelopes_api.create_recipient_view(
        account_id=ACCOUNT_ID,
        envelope_id=envelope_id,
        recipient_view_request=view_request
    )

    return redirect(recipient_view.url)



@app.route("/done")
def done():
    # After signing, DocuSign redirects back here (return_url)
    envelope_id = session.get("last_envelope_id")
    return render_template("done.html", envelope_id=envelope_id)


@app.route("/download", methods=["POST"])  # optional: supply envelope_id form field
def download():
    envelope_id = request.form.get("envelope_id")
    if not envelope_id:
        flash("Provide the Envelope ID to download the completed document.")
        return redirect(url_for("index"))

    api_client = get_api_client()
    envelopes_api = EnvelopesApi(api_client)

    # document_id = 'combined' returns a single PDF of all docs with signature cert
    pdf_bytes = envelopes_api.get_document(account_id=ACCOUNT_ID, envelope_id=envelope_id, document_id="combined")

    out_path = os.path.join(SIGNED_FOLDER, f"signed_{envelope_id}.pdf")
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)

    return send_file(out_path, as_attachment=True, download_name=f"signed_{envelope_id}.pdf")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    host = os.getenv("HOST", "127.0.0.1")
    app.run(host=host, port=port, debug=True)




