# Portfolio

## Persistent admin uploads on Vercel

The admin dashboard stores its editable content and resume PDF in Vercel Blob. Before deploying:

1. Open the project in Vercel and go to **Storage**.
2. Create a **Blob** store with **Public** access and connect it to this project.
3. Redeploy the project so `BLOB_STORE_ID` and the Vercel Blob credentials (`BLOB_READ_WRITE_TOKEN` or `VERCEL_BLOB_READ_WRITE_TOKEN`) are available to the Flask function.
4. Set a stable `SECRET_KEY` in the Vercel environment variables so admin sessions survive function restarts.

For local development without Blob credentials, edits are saved to `content.json` and resume uploads to `static/uploads/`.

## Portfolio chatbot

The floating assistant on the portfolio, project, and resume pages uses the existing `chatbot.py` parser and Groq answer flow. Set `GROQ_API_KEY` in the Vercel project environment variables (and in a local `.env` file for development) before deploying. The assistant reads the current resume configured for `/resume`, including a resume uploaded to Vercel Blob. Upload a resume in the portfolio admin before using chat. The rest of the portfolio remains available if the key or resume is missing, while chat responds as temporarily unavailable.
