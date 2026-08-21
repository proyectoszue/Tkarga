from odoo import models
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import base64

class zue_report_product_catalog(models.Model):
    _name = 'zue.report.product.catalog'
    _description = 'Generador de catálogo de productos con ReportLab'

    def generate_catalog(self):
        # Crear buffer de memoria para el PDF
        buffer = BytesIO()

        # Documento base
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']

        # Título
        elements.append(Paragraph("Catálogo de Productos", title_style))
        elements.append(Spacer(1, 12))

        # Obtener productos (ajusta filtros según necesidad)
        products = self.env['product.template'].search([], limit=50)

        # Encabezado de la tabla
        data = [["Imagen", "Nombre", "Referencia", "Precio"]]

        # Llenar datos
        for product in products:
            # Manejar imagen (campo image_1920)
            if product.image_1920:
                img_data = base64.b64decode(product.image_1920)
                img = Image(BytesIO(img_data), width=50, height=50)
            else:
                img = Paragraph("Sin imagen", styles['Normal'])

            data.append([
                img,
                product.name,
                product.default_code or "",
                "${:,.2f}".format(product.list_price)
            ])

        # Crear tabla
        table = Table(data, colWidths=[60, 200, 100, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        elements.append(table)

        # Construir PDF
        doc.build(elements)

        # Retornar como base64 (para descargar en Odoo)
        pdf_value = base64.b64encode(buffer.getvalue())
        buffer.close()

        # Crear adjunto en Odoo para descargar
        attachment = self.env['ir.attachment'].create({
            'name': 'catalogo_productos.pdf',
            'type': 'binary',
            'datas': pdf_value,
            'res_model': 'product.template',
            'mimetype': 'application/pdf'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/{attachment.id}?download=true",
            'target': 'self',
        }
