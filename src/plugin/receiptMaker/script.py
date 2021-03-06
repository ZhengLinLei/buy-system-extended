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
# }

def ReceiptMaker(object):


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
                    <div class="info">
                        <p>
                            CIF: xxxxxxxxx</br>
                            Tel. xxxxxxxxx</br>
                        </p>
                    </div>
                </center>
                <div id="bot">
                    <div id="table">
                        <table>
                            <tr class="tabletitle">
                                <td class="amount">
                                    <h5>CANT.</h5>
                                </td>
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
                            <tr class="tabletitle">

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
                    <h4>**#9#**</h4>
                    <div style="margin: 20px 0 50px 0;">
                        <div style="display: flex; justify-content: space-around;">
                            <div><b>Pagado: </b> **#7#** €</div>
                            <div><b>Cambio: </b> **#8#** €</div>
                        </div>
                    </div>
                    <h4>IVA INCLUIDO</h4>
                    <h4>GRACIAS POR SU COMPRA</h4>
                    <p class="barcode" style="margin-top: 10px;">**#6#**</p>
                    <h5>**#6#**</h5>
                </footer>
            </div>
        </body>
        </html>

    '''


    Prod_template = '''
    
                    <tr class="service">
                        <td class="tableitem">
                            <p class="itemtext">**#3#** x</p>
                        </td>
                        <td class="tableitem">
                            <p class="itemtext">**#4#**</p>
                        </td>
                        <td class="tableitem">
                            <p class="itemtext">
                                <p>**#1#**</p>
                            </p>
                        </td>
                        <td class="tableitem right">
                            <p class="itemtext">**#5#**</p>
                        </td>
                    </tr>

    '''

    HTML_text = ''

    for prod in object['product']['data']:

        template = Prod_template

        for index, value in enumerate(prod.values()):

            value = '{:.2f}'.format(float(value)) if index == 4 or index == 5 else str(value)            

            template = template.replace(f'**#{index}#**', value)


        HTML_text += template


    DATETIME = datetime.strptime(object['datetime'], '%Y-%m-%d %H:%M:%S')

    Input_order = [
        DATETIME.strftime('%H : %M'),
        DATETIME.strftime('%Y-%m-%d'),
        HTML_text,
        object['subtotal'],
        object['tax'],
        object['total'],
        object['id'],
        object['pay_price'],
        object['change_price'],
        'EFECTIVO' if object['method_pay'] == 'money' else 'TARJETA CREDITO/DEBITO'
    ]

    #'datetime': self.data[1],
    #'product': self.data[2],
    #'subtotal': str(subtotal),
    #'tax': str(tax),
    #'total': str(total),
    #'id': id,
    #'nettotal': str(nettotal),
    #'iva': str(iva),
    #'pay_price': pay_price,
    #'change_price': change_price,
    #'total_amount': total_amount,
    #'method_pay': self.data[5]

    for i, v in enumerate(Input_order):

        Template = Template.replace(f'**#{i}#**', v)


    return Template


