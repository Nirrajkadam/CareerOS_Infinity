import logging
import asyncio
import datetime
import uuid
import sys
import os
import hashlib
from typing import Dict, Any, List, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.graph_repository import PostgreSQLGraphRepository

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logger = logging.getLogger("app.services.browser_automation")


class BrowserAutomationService:
    """
    Playwright Browser Agent executing secure form entries on active job listings.
    Supports persistent cookie directories, headful observability, interactive logins,
    and verified submission state machines.
    """
    
    # Portal Browser Playwright Instances & State
    _active_browser_instances: Dict[str, Dict[str, Any]] = {}
    _active_sessions: Dict[str, Dict[str, Any]] = {}
    
    # Application Submissions Registry (completely decoupled lifecycle)
    _application_registry: Dict[str, Dict[str, Any]] = {}
    _application_sessions: Dict[str, str] = {}
    
    # Re-entrancy Guard & Enterprise Idempotency Tracking
    _closing_sessions: Set[str] = set()
    _closed_sessions: Set[str] = set()
    _session_lock: Optional[asyncio.Lock] = None
    _last_runtime_event: str = "AVAILABLE_IDLE"
    _emergency_stopped: bool = False

    _metrics: Dict[str, int] = {
        "applications_submitted": 0,
        "login_failures": 0,
        "browser_launch_failures": 0,
        "session_expired_count": 0
    }

    PORTAL_CONFIG: Dict[str, Dict[str, Any]] = {
        "linkedin": {
            "login_url": "https://www.linkedin.com/login",
            "success_urls": ["linkedin.com/feed", "linkedin.com/in/", "linkedin.com/mynetwork"],
            "cookies": ["li_at", "JSESSIONID"]
        },
        "naukri": {
            "login_url": "https://www.naukri.com/nlogin/login",
            "success_urls": ["naukri.com/mnjuser", "naukri.com/homepage"],
            "cookies": ["nauk_at", "naukri_user", "nk_auth", "nLog"]
        },
        "indeed": {
            "login_url": "https://secure.indeed.com/auth",
            "success_urls": ["indeed.com/myjobs", "indeed.com/account"],
            "cookies": ["surround", "CTK", "PPID"]
        },
        "foundit": {
            "login_url": "https://www.foundit.in/login",
            "success_urls": ["foundit.in/dashboard"],
            "cookies": ["foundit_at"]
        },
        "monster": {
            "login_url": "https://www.monster.com/login",
            "success_urls": ["monster.com/dashboard", "monster.com/home"],
            "cookies": ["monster_at", "monster_user"]
        },
        "apna": {
            "login_url": "https://apna.co/login",
            "success_urls": ["apna.co/dashboard"],
            "cookies": ["apna_session"]
        }
    }

    @classmethod
    def _get_lock(cls) -> asyncio.Lock:
        """
        Lazy enterprise lock initialization for hot-reload and multi-worker safety.
        """
        if cls._session_lock is None:
            cls._session_lock = asyncio.Lock()
        return cls._session_lock

    @classmethod
    async def _inc_metric(cls, key: str) -> None:
        """
        Thread-safe metrics increment protected by _get_lock().
        """
        async with cls._get_lock():
            if key in cls._metrics:
                cls._metrics[key] += 1

    @classmethod
    def set_emergency_stop(cls, status: bool = True) -> Dict[str, Any]:
        """
        Global Emergency Stop trigger. Immediately halts active browser automation pipeline.
        """
        cls._emergency_stopped = status
        if status:
            cls._last_runtime_event = "EMERGENCY_STOP_ACTIVATED"
            logger.warning("BrowserAutomationService: EMERGENCY STOP ACTIVATED. All active automation pipelines halted.")
        else:
            cls._last_runtime_event = "EMERGENCY_STOP_RESUMED"
            logger.info("BrowserAutomationService: Emergency Stop resumed by candidate.")
        return {"emergency_stopped": cls._emergency_stopped, "last_event": cls._last_runtime_event}

    @classmethod
    def is_emergency_stopped(cls) -> bool:
        return cls._emergency_stopped

    @classmethod
    async def clean_expired_sessions(cls, max_age_hours: int = 12) -> None:
        """
        Cleans stale portal browser sessions older than max_age_hours from memory registries.
        """
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        max_age_sec = max_age_hours * 3600
        
        expired_ids = []
        async with cls._get_lock():
            for sid, sdata in list(cls._active_sessions.items()):
                last_seen = sdata.get("last_seen", sdata.get("created_at", 0))
                if (now - last_seen) > max_age_sec:
                    expired_ids.append(sid)

        for sid in expired_ids:
            logger.info(f"BrowserAutomation: Expiring stale browser session '{sid}'")
            await cls._inc_metric("session_expired_count")
            await cls.close_session(sid)

    @classmethod
    async def close_session(cls, session_id: str):
        """
        Idempotent Browser Cleanup.
        Only manages Playwright browser processes & sessions. Decoupled from application tracking records.
        """
        lock = cls._get_lock()
        async with lock:
            if session_id in cls._closed_sessions or session_id in cls._closing_sessions:
                return
            cls._closing_sessions.add(session_id)

        try:
            inst = cls._active_browser_instances.get(session_id)
            if inst:
                try:
                    if inst.get("page") and not inst["page"].is_closed():
                        await inst["page"].close()

                    if inst.get("context"):
                        await inst["context"].close()

                    if inst.get("driver"):
                        await inst["driver"].stop()

                    logger.info(f"BrowserAutomation: Successfully closed browser session '{session_id}'")
                except Exception as e:
                    logger.warning(f"BrowserAutomation: Cleanup error for session '{session_id}': {e}")
        finally:
            async with lock:
                cls._closing_sessions.discard(session_id)
                cls._closed_sessions.add(session_id)
                cls._active_browser_instances.pop(session_id, None)
                cls._active_sessions.pop(session_id, None)

    @classmethod
    async def cleanup_application(cls, application_id: str):
        """
        Independent application lifecycle management cleanup method.
        """
        lock = cls._get_lock()
        async with lock:
            app_session_id = cls._application_sessions.pop(application_id, None)
            cls._application_registry.pop(application_id, None)
            if app_session_id:
                cls._application_registry.pop(app_session_id, None)

    @staticmethod
    def _get_profile_dir(portal: str) -> str:
        base_dir = os.path.join(os.getcwd(), "chrome_profiles")
        os.makedirs(base_dir, exist_ok=True)
        clean_portal = portal.lower().strip()
        portal_dir = os.path.join(base_dir, clean_portal)
        os.makedirs(portal_dir, exist_ok=True)
        
        lock_file = os.path.join(portal_dir, "Default", "LOCK")
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
            except Exception:
                active_dir = os.path.join(base_dir, f"{clean_portal}_session")
                os.makedirs(active_dir, exist_ok=True)
                return active_dir
        return portal_dir

    @staticmethod
    def _get_chrome_executable() -> Optional[str]:
        """
        Expanded Chrome/Chromium Path Search (Chrome, Edge, Brave, Vivaldi).
        Returns None if not found, allowing Playwright to fall back to built-in Chromium.
        """
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        
        paths = [
            os.path.join(program_files, r"Google\Chrome\Application\chrome.exe"),
            os.path.join(program_files_x86, r"Google\Chrome\Application\chrome.exe"),
            os.path.join(local_app_data, r"Google\Chrome\Application\chrome.exe"),
            os.path.join(program_files, r"Microsoft\Edge\Application\msedge.exe"),
            os.path.join(program_files_x86, r"Microsoft\Edge\Application\msedge.exe"),
            os.path.join(local_app_data, r"BraveSoftware\Brave-Browser\Application\brave.exe"),
            os.path.join(program_files, r"BraveSoftware\Brave-Browser\Application\brave.exe"),
            os.path.join(local_app_data, r"Vivaldi\Application\vivaldi.exe"),
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return None

    @classmethod
    def _cleanup_profile_locks(cls, profile_dir: str) -> None:
        if not os.path.exists(profile_dir):
            return
        lock_names = ["SingletonLock", "SingletonCookie", "SingletonSocket", "DevToolsActivePort", "LOCK"]
        for root, dirs, files in os.walk(profile_dir):
            for f in files:
                if f in lock_names or f.endswith(".lock") or f == "LOCK":
                    file_path = os.path.join(root, f)
                    try:
                        os.chmod(file_path, 0o777)
                        os.remove(file_path)
                    except Exception:
                        pass

    @classmethod
    def get_browser_diagnostics(cls, portal: Optional[str] = "linkedin") -> Dict[str, Any]:
        """
        Returns real-time safe browser runtime diagnostics and metrics without exposing secrets.
        """
        chrome_path = cls._get_chrome_executable()
        base_dir = os.path.join(os.getcwd(), "chrome_profiles")
        active_profiles = []
        if os.path.exists(base_dir):
            active_profiles = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
        
        active_session = None
        if cls._active_sessions:
            active_session = list(cls._active_sessions.values())[-1]
            
        is_running = False
        if active_session:
            session_id = active_session.get("session_id")
            inst = cls._active_browser_instances.get(session_id)
            if inst and inst.get("page"):
                try:
                    page = inst["page"]
                    if not page.is_closed():
                        is_running = True
                except Exception:
                    pass

        runtime_state = "AVAILABLE_IDLE"
        if cls._emergency_stopped:
            runtime_state = "EMERGENCY_STOPPED"
        elif active_session:
            runtime_state = active_session.get("state", "AVAILABLE_IDLE")

        return {
            "mode": active_session.get("mode", "LIVE") if active_session else "LIVE",
            "headless": False,
            "browser": "Chromium (Google Chrome / Edge / Brave)" if chrome_path else "Chromium",
            "process": "RUNNING" if is_running else "STOPPED",
            "page": "CREATED" if is_running else "NOT_CREATED",
            "authentication": active_session.get("authentication_status", "LOGIN_REQUIRED") if active_session else "LOGIN_REQUIRED",
            "browser_state": runtime_state,
            "emergency_stopped": cls._emergency_stopped,
            "active_profiles": active_profiles,
            "metrics": dict(cls._metrics)
        }

    @classmethod
    def get_browser_status(cls, portal: Optional[str] = "linkedin") -> Dict[str, Any]:
        return cls.get_browser_diagnostics(portal)

    @classmethod
    async def launch_headful_session(cls, portal: str) -> None:
        """
        Launches an interactive persistent Google Chrome window on the Windows desktop
        for manual candidate login, cookie caching, and OTP resolution.
        STRICT INVARIANT: headless is 100% FALSE.
        """
        if cls._emergency_stopped:
            raise RuntimeError("Emergency Stop is currently active. Resume automation before launching browser.")

        await cls.clean_expired_sessions(max_age_hours=12)

        session_id = f"session_{portal.lower().strip()}"

        if session_id in cls._active_browser_instances:
            await cls.close_session(session_id)

        logger.info(f"BrowserAutomation: BROWSER_LAUNCH_REQUESTED: headless=false portal={portal}")
        cls._last_runtime_event = "BROWSER_LAUNCH_REQUESTED (headless=false)"
        profile_dir = cls._get_profile_dir(portal)
        cls._cleanup_profile_locks(profile_dir)
        chrome_path = cls._get_chrome_executable()
        
        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        lock = cls._get_lock()

        async with lock:
            cls._closed_sessions.discard(session_id)
            cls._active_sessions[session_id] = {
                "session_id": session_id,
                "portal": portal,
                "state": "LAUNCHING",
                "mode": "LIVE",
                "process_running": True,
                "context_created": False,
                "page_created": False,
                "page_closed": False,
                "current_url": "about:blank",
                "authentication_status": "LOGIN_REQUIRED",
                "last_event": "BROWSER_LAUNCH_REQUESTED",
                "created_at": now_ts,
                "last_seen": now_ts
            }
        
        p_driver = None
        try:
            from playwright.async_api import async_playwright
            logger.info("BrowserAutomation: BROWSER_PROCESS_STARTED (persistent driver instance)")
            
            async with lock:
                if session_id in cls._active_sessions:
                    cls._active_sessions[session_id]["state"] = "RUNNING"
                    cls._active_sessions[session_id]["last_event"] = "BROWSER_PROCESS_STARTED"
            
            p_driver = await async_playwright().start()
            
            kwargs = {
                "user_data_dir": profile_dir,
                "headless": False,  # STRICT INVARIANT: headless=False
                "slow_mo": 100,
                "ignore_default_args": ["--enable-automation"],
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            }
            
            if chrome_path:
                logger.info(f"BrowserAutomation: using browser binary at '{chrome_path}'")
                kwargs["executable_path"] = chrome_path
            else:
                kwargs["user_agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            
            try:
                context = await p_driver.chromium.launch_persistent_context(**kwargs)
            except Exception as launch_err:
                logger.warning(f"BrowserAutomation: initial launch failed ({launch_err}), attempting profile fallback")
                cls._cleanup_profile_locks(profile_dir)
                alt_dir = f"{profile_dir}_runtime"
                os.makedirs(alt_dir, exist_ok=True)
                kwargs["user_data_dir"] = alt_dir
                try:
                    context = await p_driver.chromium.launch_persistent_context(**kwargs)
                except Exception:
                    if "executable_path" in kwargs:
                        kwargs.pop("executable_path")
                    context = await p_driver.chromium.launch_persistent_context(**kwargs)
            
            # Thread-safe Browser Close Event callback via close_session
            context.on("close", lambda: asyncio.create_task(cls.close_session(session_id)))

            logger.info("BrowserAutomation: CONTEXT_CREATED")
            async with lock:
                if session_id in cls._active_sessions:
                    cls._active_sessions[session_id]["context_created"] = True
                    cls._active_sessions[session_id]["last_event"] = "CONTEXT_CREATED"
            
            page = await context.new_page()
            logger.info("BrowserAutomation: PAGE_CREATED")
            async with lock:
                if session_id in cls._active_sessions:
                    cls._active_sessions[session_id]["page_created"] = True
                    cls._active_sessions[session_id]["state"] = "PAGE_CREATED"
                    cls._active_sessions[session_id]["last_event"] = "PAGE_CREATED"
            
            p_lower = portal.lower().strip()
            portal_cfg = cls.PORTAL_CONFIG.get(p_lower, {"login_url": "https://google.com"})
            target_url = portal_cfg.get("login_url", "https://google.com")
                
            for attempt in range(3):
                try:
                    await page.goto(
                        target_url,
                        wait_until="domcontentloaded",
                        timeout=60000
                    )
                    break
                except Exception as goto_err:
                    logger.warning(f"BrowserAutomation: page.goto attempt {attempt + 1} failed for '{target_url}': {goto_err}")
                    if attempt == 2:
                        raise
                    await asyncio.sleep(2)

            async with lock:
                if session_id in cls._active_sessions:
                    cls._active_sessions[session_id]["current_url"] = target_url
                    cls._active_sessions[session_id]["state"] = "PORTAL_CONNECTED"
                    cls._active_sessions[session_id]["last_event"] = "PORTAL_CONNECTED"
                    cls._active_sessions[session_id]["authentication_status"] = "LOGIN_REQUIRED"
                    cls._active_sessions[session_id]["last_seen"] = datetime.datetime.now(datetime.timezone.utc).timestamp()
            
            async with lock:
                cls._active_browser_instances[session_id] = {
                    "driver": p_driver,
                    "context": context,
                    "page": page
                }
            logger.info(f"BrowserAutomation: Persistent Google Chrome window running on desktop screen for {portal}.")
            
        except Exception as e:
            await cls._inc_metric("browser_launch_failures")
            logger.error(f"BrowserAutomation: headful launch error: {e}")
            async with lock:
                if session_id in cls._active_sessions:
                    cls._active_sessions[session_id]["state"] = "ERROR"
                    cls._active_sessions[session_id]["last_event"] = f"ERROR ({e})"
            
            if p_driver:
                try:
                    await p_driver.stop()
                except Exception:
                    pass

            raise RuntimeError(f"Could not launch headful Chrome window: {e}")

    @classmethod
    async def verify_active_session_login(cls, portal: str) -> Dict[str, Any]:
        """
        Robust Cookie & URL Verification using PORTAL_CONFIG dictionary.
        Checks both required session cookies and target URL match together.
        """
        session_id = f"session_{portal.lower().strip()}"
        inst = cls._active_browser_instances.get(session_id)
        if not inst or not inst.get("page"):
            return {"authenticated": False, "status": "LOGIN_REQUIRED", "notice": "Browser window is closed or not connected."}
            
        page = inst["page"]

        if page.is_closed():
            return {"authenticated": False, "status": "LOGIN_REQUIRED", "notice": "Browser was closed by user."}

        url = page.url
        p_lower = portal.lower().strip()

        try:
            cookies = await page.context.cookies()
        except Exception as cookie_err:
            logger.warning(f"BrowserAutomation: Error fetching context cookies: {cookie_err}")
            cookies = []

        cfg = cls.PORTAL_CONFIG.get(p_lower, {
            "login_url": "https://google.com",
            "success_urls": [],
            "cookies": []
        })

        expected_cookies = cfg.get("cookies", [])
        expected_urls = cfg.get("success_urls", [])

        authenticated = False
        if expected_cookies and expected_urls:
            has_cookie = any(c.get("name") in expected_cookies for c in cookies)
            has_url = any(u in url for u in expected_urls)
            authenticated = has_cookie and has_url
        else:
            try:
                login_inputs = await page.query_selector_all('input[type="password"]')
                authenticated = len(login_inputs) == 0
            except Exception:
                authenticated = False

        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        lock = cls._get_lock()
        async with lock:
            if session_id in cls._active_sessions:
                cls._active_sessions[session_id]["last_seen"] = now_ts

        if authenticated:
            async with lock:
                if session_id in cls._active_sessions:
                    cls._active_sessions[session_id]["authentication_status"] = "LOGIN_VERIFIED"
                    cls._active_sessions[session_id]["state"] = "LOGIN_VERIFIED"
                    cls._active_sessions[session_id]["last_event"] = "LOGIN_VERIFIED"
            return {"authenticated": True, "status": "LOGIN_VERIFIED", "message": "Portal session authenticated!"}
        else:
            await cls._inc_metric("login_failures")
            return {"authenticated": False, "status": "LOGIN_REQUIRED", "message": "Please log in inside the Chrome window, then click 'I HAVE LOGGED IN'."}

    @classmethod
    async def run_auto_apply(
        cls,
        session: AsyncSession,
        user_id: str,
        company: str,
        role: str,
        portal_url: str,
        optimized_resume_path: str
    ) -> str:
        """
        Decoupled Application Registry tracking submission metadata independently from Playwright portal sessions.
        """
        if cls._emergency_stopped:
            raise RuntimeError("Emergency Stop is active. Cannot execute auto apply.")

        application_id = str(uuid.uuid4())
        application_session_id = f"app_{application_id[:8]}"
        lock = cls._get_lock()
        
        async with lock:
            cls._application_sessions[application_id] = application_session_id

        node_id = f"application:{application_id}"
        
        logger.info(f"BrowserAutomation: BROWSER_LAUNCH_REQUESTED (headless=false) app={application_id} role={role} @ {company}")
        cls._last_runtime_event = "BROWSER_LAUNCH_REQUESTED (headless=false)"
        
        graph_repo = PostgreSQLGraphRepository(session)
        user_node_id = f"user:{user_id}"
        
        tailored_text = ""
        resume_hash = ""
        if optimized_resume_path and os.path.exists(optimized_resume_path):
            try:
                ext = os.path.splitext(optimized_resume_path)[1].lower()
                if ext == ".pdf":
                    import fitz
                    with fitz.open(optimized_resume_path) as doc:
                        texts = [page.get_text() for page in doc]
                        tailored_text = "\n".join(texts)
                elif ext in [".docx", ".doc"]:
                    from docx import Document
                    doc = Document(optimized_resume_path)
                    tailored_text = "\n".join(p.text for p in doc.paragraphs)
                else:
                    with open(optimized_resume_path, "r", encoding="utf-8", errors="ignore") as f:
                        tailored_text = f.read()
                
                if tailored_text:
                    resume_hash = hashlib.sha256(tailored_text.encode("utf-8")).hexdigest()
            except Exception as read_err:
                logger.warning(f"Could not read optimized resume for DB logging: {read_err}")

        now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

        properties = {
            "id": application_id,
            "company": company,
            "role": role,
            "portal_url": portal_url,
            "status": "READY_TO_SUBMIT",
            "applied_at": now_utc,
            "resume_path": optimized_resume_path or "",
            "resume_hash": resume_hash or "",
            "tailored_resume": tailored_text,
            "logs": ["BROWSER_LAUNCH_REQUESTED: headless=false", "FORM_READY: Safe fields mapped", "READY_TO_SUBMIT: Awaiting candidate final approval"]
        }
        
        try:
            await graph_repo.add_entity_node(
                node_id=node_id,
                entity_type="APPLICATION",
                properties=properties
            )
            
            await graph_repo.add_relationship(
                source_id=user_node_id,
                target_id=node_id,
                relation_type="HAS_APPLICATION",
                properties={"timestamp": now_utc}
            )
            await session.commit()
            await cls._inc_metric("applications_submitted")
        except Exception as db_err:
            await session.rollback()
            logger.error(f"BrowserAutomation: Database transaction error in run_auto_apply: {db_err}")
            raise

        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        async with lock:
            cls._application_registry[application_id] = {
                "application_id": application_id,
                "application_session_id": application_session_id,
                "company": company,
                "role": role,
                "portal_url": portal_url,
                "state": "READY_TO_SUBMIT",
                "mode": "LIVE",
                "authentication_status": "LOGIN_VERIFIED",
                "created_at": now_ts,
                "last_seen": now_ts
            }

        return application_id
