import logging
import imaplib
import email
import datetime
from email.header import decode_header
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.graph_repository import PostgreSQLGraphRepository
from app.services.credential_vault import CredentialVault

logger = logging.getLogger("app.services.email_service")

class EmailSyncService:
    """
    Email Integration Service syncing confirmation and reply messages
    from employer portals directly into the career knowledge graph.
    INVARIANT: Real IMAP inbox verification with AES-256 Fernet decrypted credentials from Vault.
    """
    @staticmethod
    async def sync_confirmation_emails(
        session: AsyncSession,
        user_id: str,
        imap_server: str = "imap.gmail.com",
        email_address: str = None,
        app_password: str = None,
        company_filter: str = None
    ) -> List[Dict[str, Any]]:
        logger.info(f"EmailSyncService: starting sync sequence for {email_address or 'Vault Stored IMAP Account'}")
        
        # Retrieve decrypted IMAP credentials from Vault if not explicitly passed
        if not email_address or not app_password:
            vault_creds = await CredentialVault.get_imap_credentials(session)
            if vault_creds:
                email_address = vault_creds.get("email_address")
                app_password = vault_creds.get("app_password")
                imap_server = vault_creds.get("imap_server", imap_server)
        
        graph_repo = PostgreSQLGraphRepository(session)
        sync_results = []
        
        # 1. Attempt real IMAP SSL Connection if credentials exist
        if email_address and app_password:
            try:
                logger.info(f"EmailSync: Connecting to SSL IMAP server '{imap_server}' for {email_address}...")
                mail = imaplib.IMAP4_SSL(imap_server)
                mail.login(email_address, app_password)
                mail.select("inbox")
                
                # Search for application receipts
                search_query = '(OR SUBJECT "application" SUBJECT "applying")'
                if company_filter:
                    search_query = f'(OR SUBJECT "{company_filter}" SUBJECT "application")'
                    
                status, messages = mail.search(None, search_query)
                if status == "OK":
                    mail_ids = messages[0].split()
                    for mail_id in mail_ids[-10:]:
                        status, data = mail.fetch(mail_id, "(RFC822)")
                        if status == "OK":
                            raw_email = data[0][1]
                            msg = email.message_from_bytes(raw_email)
                            
                            subject, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding or "utf-8", errors="ignore")
                            
                            sender = msg.get("From", "")
                            date = msg.get("Date", "")
                            
                            sync_results.append({
                                "subject": subject,
                                "sender": sender,
                                "date": date,
                                "source": "IMAP Live Sync Verified",
                                "verified": True
                            })
                mail.close()
                mail.logout()
            except Exception as imap_err:
                logger.warning(f"EmailSync: Live IMAP sync exception: {imap_err}")
                
        # 2. Return truthful verification status without manufactured fallback receipts
        if not sync_results:
            logger.info("EmailSync: No matching employer application confirmation email detected in inbox.")
            return []
                
        # Register logs & update status in Graph Repository
        if sync_results:
            nodes = await graph_repo.get_entities_by_type("APPLICATION")
            for node in nodes:
                props = dict(node.properties)
                if str(props.get("user_id")) != str(user_id):
                    continue
                comp = props.get("company", "")
                for res in sync_results:
                    if comp and (comp.lower() in res.get("subject", "").lower() or comp.lower() in res.get("company", "").lower()):
                        props["status"] = "SUBMITTED_VERIFIED"
                        if "EMAIL_CONFIRMED: Real IMAP sync verified employer receipt." not in props.get("logs", []):
                            props.setdefault("logs", []).append("EMAIL_CONFIRMED: Real IMAP sync verified employer receipt.")
                            props["email_confirmation"] = {
                                "subject": res["subject"],
                                "sender": res["sender"],
                                "date": res.get("date")
                            }
                        node.properties = props
                        session.add(node)
            await session.commit()
            
        return sync_results
