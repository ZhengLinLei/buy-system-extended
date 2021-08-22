import win32print

def OpenCashDrawer(printerName) :   
    printerHandler = win32print.OpenPrinter(printerName)
    cashDraweOpenCommand = chr(27)+chr(112)+chr(0)+chr(25)+chr(250)
    win32print.StartDocPrinter(printerHandler, 1, ('Cash Drawer Open',None,'RAW')) 
    win32print.WritePrinter( printerHandler, cashDraweOpenCommand)
    win32print.EndDocPrinter(printerHandler)
    win32print.ClosePrinter(printerHandler)

OpenCashDrawer("YourPrinterName")