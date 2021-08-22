import cups, os

class PrintFile():

    files = []
    printer = 0

    def __init__(self) -> None:

        # Connect to CUPS
        self.conn = cups.Connection()
        self.printers = self.conn.getPrinters()

    def addFile(self, filepath, name, options):

        self.files.append([filepath, name, options])

    def choosePrinter(self, indexNum):

        for index, printer in enumerate(self.printers):

            print(index, printer, self.printers[printer]["device-uri"])

        self.printer = indexNum


    def printAll(self):

        if self.files:
            # Get the default or choosed printer
            printer_name = list(self.printers.keys())[self.printer]


            # Foreach the files array
            for file in self.files:
                self.conn.printFile (printer_name, file[0], file[1], file[2] if file[2] else {})


            return True
        else:
            print('ERROR: Nothing to print in the List')
            return False





file = open("./open.txt","w")

file.write(chr(27)+chr(112)+chr(0)+chr(25)+chr(250))

file.close()



Print = PrintFile()
Print.addFile('./open.txt', 'Open', {})
Print.printAll()