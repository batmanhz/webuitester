from browser_use.browser.session import BrowserSession
import logging

logger = logging.getLogger(__name__)

def apply_browser_use_patches():
    """
    Apply monkey patches to browser_use library to fix known issues.
    """
    original_reset = BrowserSession.reset

    async def patched_reset(self):
        """
        Patched reset method to ensure _watchdogs_attached is reset.
        """
        # Call the original reset method
        await original_reset(self)
        
        # Apply the fix: reset _watchdogs_attached flag
        # This ensures watchdogs are re-attached when the session is reused
        self._watchdogs_attached = False
        logger.info("[Patch] Applied fix: Reset _watchdogs_attached to False in BrowserSession.reset")

    # Apply the patch
    BrowserSession.reset = patched_reset
    logger.info("Applied monkey patch to BrowserSession.reset")
