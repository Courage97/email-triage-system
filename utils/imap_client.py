import pathfix  # noqa
# utils/imap_client.py
# IMAP email fetching — robust Windows-compatible connection

import imaplib
import email
import ssl
import socket
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime


def connect(host: str, port: int, username: str, password: str) -> imaplib.IMAP4_SSL:
    """
    Connect and authenticate to an IMAP server.
    Uses a permissive SSL context for maximum compatibility.
    """
    try:
        # Permissive SSL — works on most corporate/university mail servers
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode    = ssl.CERT_NONE

        mail = imaplib.IMAP4_SSL(host, port, ssl_context=context)
        mail.login(username, password)
        return mail

    except imaplib.IMAP4.error as e:
        err = str(e)
        if b'AUTHENTICATIONFAILED' in e.args[0] if e.args else False:
            raise ConnectionError(
                "Authentication failed. Check your email and password.\n\n"
                "**Gmail users:** Use an App Password, not your regular password. "
                "Go to: Google Account → Security → 2-Step Verification → App Passwords."
            )
        raise ConnectionError(f"IMAP login failed: {err}")

    except socket.timeout:
        raise ConnectionError(
            f"Connection timed out connecting to {host}:{port}.\n"
            "Check the host and port, and make sure IMAP is enabled in your email settings."
        )

    except OSError as e:
        raise ConnectionError(
            f"Could not reach {host}:{port}.\n\n"
            f"**Error:** {e}\n\n"
            "Common fixes:\n"
            "- Check your internet connection\n"
            "- Verify the IMAP host and port\n"
            "- For Gmail: enable IMAP in Settings → See all settings → Forwarding and POP/IMAP\n"
            "- For Outlook: enable IMAP in Settings → Mail → Sync email"
        )

    except Exception as e:
        raise ConnectionError(f"Unexpected error: {e}")


def fetch_unread(mail: imaplib.IMAP4_SSL, folder: str = "INBOX", limit: int = 20) -> list[dict]:
    """Fetch unread emails, newest first."""
    mail.select(folder, readonly=False)
    status, messages = mail.search(None, 'UNSEEN')
    if status != 'OK' or not messages[0]:
        return []
    uids = messages[0].split()[-limit:][::-1]
    return _fetch_batch(mail, uids)


def fetch_all_recent(mail: imaplib.IMAP4_SSL, folder: str = "INBOX", limit: int = 20) -> list[dict]:
    """Fetch recent emails regardless of read status."""
    mail.select(folder, readonly=True)
    status, messages = mail.search(None, 'ALL')
    if status != 'OK' or not messages[0]:
        return []
    uids = messages[0].split()[-limit:][::-1]
    return _fetch_batch(mail, uids)


def mark_as_read(mail: imaplib.IMAP4_SSL, uid: bytes, folder: str = "INBOX"):
    """Mark a single email as read."""
    try:
        mail.select(folder, readonly=False)
        mail.store(uid, '+FLAGS', '\\Seen')
    except Exception as e:
        print(f"[imap_client] mark_as_read failed: {e}")


def disconnect(mail: imaplib.IMAP4_SSL):
    """Safely close the IMAP connection."""
    try:
        mail.close()
        mail.logout()
    except Exception:
        pass


def test_connection(host: str, port: int, username: str, password: str) -> tuple[bool, str]:
    """Test credentials without fetching. Returns (success, message)."""
    try:
        mail = connect(host, port, username, password)
        disconnect(mail)
        return True, "Connected successfully"
    except ConnectionError as e:
        return False, str(e)


# ─── Private Helpers ──────────────────────────────────────────────────────────

def _fetch_batch(mail: imaplib.IMAP4_SSL, uids: list) -> list[dict]:
    results = []
    for uid in uids:
        try:
            parsed = _fetch_single(mail, uid)
            if parsed:
                results.append(parsed)
        except Exception:
            continue
    return results


def _fetch_single(mail: imaplib.IMAP4_SSL, uid: bytes) -> dict | None:
    status, data = mail.fetch(uid, '(RFC822)')
    if status != 'OK' or not data or data[0] is None:
        return None

    msg = email.message_from_bytes(data[0][1])

    subject  = _decode_header_value(msg.get('Subject', '(no subject)'))
    sender   = _decode_header_value(msg.get('From', ''))
    date_str = msg.get('Date', '')

    try:
        raw_date = parsedate_to_datetime(date_str)
        date     = raw_date.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        raw_date = datetime.now()
        date     = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return {
        'uid':      uid,
        'subject':  subject,
        'sender':   sender,
        'date':     date,
        'raw_date': raw_date,
        'body':     _extract_body(msg),
    }


def _decode_header_value(value: str) -> str:
    try:
        parts   = decode_header(value)
        decoded = []
        for part, encoding in parts:
            if isinstance(part, bytes):
                decoded.append(part.decode(encoding or 'utf-8', errors='replace'))
            else:
                decoded.append(str(part))
        return ' '.join(decoded).strip()
    except Exception:
        return str(value)


def _extract_body(msg) -> str:
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            ctype       = part.get_content_type()
            disposition = str(part.get('Content-Disposition', ''))
            if 'attachment' in disposition:
                continue
            if ctype == 'text/plain':
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    body    = part.get_payload(decode=True).decode(charset, errors='replace')
                    break
                except Exception:
                    continue
            if ctype == 'text/html' and not body:
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    body    = _strip_html(
                        part.get_payload(decode=True).decode(charset, errors='replace')
                    )
                except Exception:
                    continue
    else:
        try:
            charset = msg.get_content_charset() or 'utf-8'
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(charset, errors='replace')
                if msg.get_content_type() == 'text/html':
                    body = _strip_html(body)
        except Exception:
            body = ''

    return body.strip()[:2000]


def _strip_html(html: str) -> str:
    import re
    clean = re.sub(r'<[^>]+>', ' ', html)
    clean = re.sub(r'&nbsp;', ' ', clean)
    clean = re.sub(r'&amp;',  '&', clean)
    clean = re.sub(r'&lt;',   '<', clean)
    clean = re.sub(r'&gt;',   '>', clean)
    clean = re.sub(r'\s+',    ' ', clean)
    return clean.strip()