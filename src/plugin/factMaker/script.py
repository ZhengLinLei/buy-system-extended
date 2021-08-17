#           Zheng Lin Lei
#       
#   Receipt creator for thermal printer 
#   This project is own project for https://github.com/ZhengLinLei/buy-system
#
#   Print with https://github.com/ZhengLinLei/cups-python-printer software

from datetime import datetime

# EXAMPLE OBJECT

# {
#     product: [
#         ['Indv. Price', 'Name', 'Amount', 'Price']
#         ...
#     ]
#     subtotal: '0.00'
#     tax: '0.00'
#     total: '0.00'
#     id: 'xxxxxxx'
#     name: 'xxx',
#     nif: 'xxxx',
#     address: 'xxx',
#     tel: 'xxxx'
# }

def FactMaker(object, comment):


    Template = '''
    <!DOCTYPE html>
        <html lang="en">

        <head>
            <meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Recibo ZLL</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Libre+Barcode+39&display=swap" rel="stylesheet"><style>body{font-size:14px}*{margin:0;padding:0;box-sizing:border-box;font-family:'Roboto',Arial,Helvetica,sans-serif}.barcode{font-family:'Libre Barcode 39',cursive;font-size:42px}.info{margin:10px 0}#top,#bot{border-bottom:1px solid #EEE}#bot{margin:10px 0 0}table{width:100%;border-collapse:collapse}td{padding:5px}.tabletitle{padding:5px;font-size:14px;background:#EEE}.tabletitle td{text-align:center}.right{float:right}table.total td{padding:2px}</style>
        </head>
        <body>
            <div id="invoice-POS">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <p>**#0#**</p>
                    <p>**#1#**</p>
                </div>
                <center id="top">
                    <div class="info">
                        <h1>Bazar y<br>Alimentación</h1>
                    </div>
                    <div class="info" style="padding: 20px 0;">
                        <h3>Factura</h3>
                        <br>
                        <br>
                        <div style="display: flex;justify-content: space-around;">
                            <p>
                                xxxxx</br>
                                <b>NIF:</b> xxxxxxxx<br>
                                <br>
                                <b>CIF:</b> xxxxxxxxx</br>
                                <b>Tel.</b> xxxxxxxxx</br>
                            </p>
                            <p>
                                **#7#**</br>
                                <b>NIF:</b> **#8#**<br>
                                <br>
                                **#9#**</br>
                                <b>Tel.</b> **#10#**</br>
                            </p>
                        </div>
                        <div style="padding: 5px;margin:20px 3mm;border: 1px solid #000;">
                            <p>Num. factura: **#6#**</p>
                            <p>Fecha emision: **#1#**</p>
                            <p>Hora emision: **#0#**</p>
                            <p>Emitido para: xxxxxx</p>
                        </div>
                    </div>
                </center>
                <div id="bot">
                    <div id="table">
                        <table>
                            <tr class="tabletitle">
                                <td class="item">
                                    <h5>PRE.</h5>
                                </td>
                                <td class="Hours">
                                    <h5>PROD.</h5>
                                </td>
                                <td class="Rate">
                                    <h5>SUMA</h5>
                                </td>
                            </tr>

                            **#2#**
                            
                        </table>
                        <div class="payment" style="display:flex; justify-content: flex-end; margin-top: 10px;">
                            <table class="total" style="width: 50%; margin: 10px 0;">
                                <tr>
                                    <td><b>Sub Total:</b></td>
                                    <td class="right">**#3#** €</td>
                                </tr>
                                <tr>
                                    <td>Añadido:</td>
                                    <td class="right">**#4#** €</td>
                                </tr>
                                <tr>
                                    <td style="font-size:14px"><h3>Total:</h3></td>
                                    <td class="right" style="font-size:14px"><b>**#5#** €</b></td>
                                </tr>
                            </table>
                        </div>
                    </div>
                </div>
                <footer style="margin: 20px 0; text-align: center;">
                    <h4>IVA INCLUIDO (21%)</h4>
                    <h4>FACTURA EMITIDA</h4>
                    <p class="barcode" style="margin-top: 10px;">**#6#**</p>
                    <h5>**#6#**</h5>
                    <div style="margin: 50px 0; text-align:justify; font-size: 12px; color: rgb(49, 48, 48);">
                        <p>En vista del cumplimiento de la normativa europea 2016/679 sobre Protección de datos (RGPD) le informamos que el tratamiento de los datos proporcionados por Ud. será responsabilidad de (Nombre de responsables, representantes o delegados de tratamiento) con el objetivo de (Finalidad del Tratamiento), y que además se compromete a no ceder o comunicar la información a terceros. Puede ejercer sus derechos de acceso, rectificación, cancelación o supresión del tratamiento a través del local dirección física.</p><br>
                        <p>El importe de dicha factura es el total del importe incluido los IVA, dichos impuestos representan el 21% del total. Cualquier duda sobre el precio puede comunicarlo al local correspondiente </p><br>
                        <p>Reclamaciones en el local: xxxxxxxxx</p>
                    </div>
                    <div style="margin: 20px 0;">
                        <h4>Firma o cuño</h4>
                        <div style="height: 90px;margin:20px 0;border: 1px solid black;"></div>
                    </div>
                    <p>
                        **#11#**
                    </p>
                </footer>
            </div>
        </body>
        </html>
    '''


    Prod_template = '''
    
                    <tr class="service">
                        <td class="tableitem">
                            <p class="itemtext">**#0#**</p>
                        </td>
                        <td class="tableitem">
                            <p class="itemtext">
                                <p><b>**#1#**</b> x **#2#**</p>
                            </p>
                        </td>
                        <td class="tableitem right">
                            <p class="itemtext">**#3#**</p>
                        </td>
                    </tr>

    '''

    HTML_text = ''

    for prod in object['product']:

        template = Prod_template

        for index, value in enumerate(prod):

            template = template.replace(f'**#{index}#**', value)


        HTML_text += template


    Input_order = [
        datetime.today().strftime('%H : %M'),
        datetime.today().strftime('%Y-%m-%d'),
        HTML_text,
        object['subtotal'],
        object['tax'],
        object['total'],
        object['id'],
        object['name'],
        object['nif'],
        object['address'] if object['address'] else '',
        object['tel'] if object['tel'] else 'No añadir',
        'Copia para remitente 1/2' if comment else 'Copia para emisor 2/2' 
    ]

    for i, v in enumerate(Input_order):

        Template = Template.replace(f'**#{i}#**', v)


    return Template


