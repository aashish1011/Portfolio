# Portfolio

## Persistent admin uploads on Vercel

The admin dashboard stores its editable content and resume image in Vercel Blob. Before deploying:

1. Open the project in Vercel and go to **Storage**.
2. Create a **Blob** store with **Public** access and connect it to this project.
3. Redeploy the project so `BLOB_STORE_ID` and the Vercel Blob credentials are available to the Flask function.
4. Set a stable `SECRET_KEY` in the Vercel environment variables so admin sessions survive function restarts.

For local development without Blob credentials, edits are saved to `content.json` and resume uploads to `static/uploads/`.
