# LibreOffice UI Manager — standalone development macro.
#
# This is intentionally NOT part of the .oxt extension. Its only job is to
# prove that Python/UNO execution and the message-box dialog work in this
# LibreOffice install, isolated from any extension-packaging problems.
#
# Install with tools/install-dev-macro.sh, then run from Writer via:
#   Tools > Macros > Organize Macros > Python...
#   -> My Macros > louim_hello > hello -> Run

def hello(*args):
    """Show the 'Hello from LOUIM' dialog. Same logic as the extension entry point."""
    import uno
    from com.sun.star.awt.MessageBoxType import INFOBOX
    from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK

    ctx = XSCRIPTCONTEXT.getComponentContext()
    smgr = ctx.getServiceManager()
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)

    desktop = XSCRIPTCONTEXT.getDesktop()
    frame = desktop.getCurrentFrame()
    window = frame.getContainerWindow()

    box = toolkit.createMessageBox(
        window,
        INFOBOX,
        BUTTONS_OK,
        "LibreOffice UI Manager",
        "Hello from LOUIM (standalone dev macro)",
    )
    box.execute()


# Expose the entry point to the LibreOffice script provider.
g_exportedScripts = (hello,)
