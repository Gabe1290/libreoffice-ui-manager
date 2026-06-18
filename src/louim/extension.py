# LibreOffice UI Manager
# Initial Python macro entry point.

def hello(*args):
    """Temporary test entry point for the first LOUIM extension."""
    try:
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
            "Hello from LOUIM"
        )
        box.execute()
    except Exception as exc:
        print("LOUIM error:", exc)
