from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api, _
import zipfile, os, io, base64
import xml.etree.ElementTree as ET

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer, KeepInFrame
from reportlab.lib.pagesizes import letter
from io import BytesIO
from odoo.modules.module import get_resource_from_path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from PIL import Image as PILImage


class AccountMove(models.Model):
    _inherit = 'account.move'

    def generate_catalog(self):
        buffer = BytesIO()
        # Configuración del documento
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            name="CenteredTitle",
            parent=styles["Heading1"],
            alignment=TA_CENTER,
            fontSize=16,
            textColor=colors.HexColor("#1F4E79"),
            spaceAfter=20
        )

        name_style = ParagraphStyle('name_style', fontSize=10, alignment=1)  # centrado
        price_style = ParagraphStyle('price_style', fontSize=9, textColor=colors.HexColor("#4CAF50"), alignment=1)
        desc_style = ParagraphStyle('desc_style', fontSize=8, alignment=1, leading=10)

        # Título
        elements.append(Paragraph("Catálogo de Productos", title_style))
        elements.append(Spacer(1, 12))

        # Productos
        products = self.env['product.template'].search([], limit=20)

        # Agrupar en filas de 4 columnas
        row = []
        data = []
        for idx, product in enumerate(products, start=1):
            # Imagen
            img_data = self.get_image_or_default(product)
            # img = Paragraph("Sin imagen", styles['Normal'])

            img = Image(img_data, width=100, height=100)
            img.hAlign = 'CENTER'

            # Info de producto
            name_para = Paragraph((product.name[:50]).ljust(50), name_style)
            price_para = Paragraph("${:,.2f}".format(product.list_price), price_style)
            desc_para = Paragraph(product.description_sale or "", desc_style)

            # # Contenedor fijo para la descripción (3 renglones aprox.)
            # desc_frame = KeepInFrame(
            #     maxWidth=120,  # ancho máximo de la celda
            #     maxHeight=100,  # alto para aprox. 3 líneas
            #     content=[name_para],
            #     hAlign='CENTER',
            #     vAlign='TOP'
            # )

            # Celda como lista de elementos (Flowable)
            cell_content = [img,
                            Spacer(1, 8),
                            price_para,
                            Spacer(1, 5),
                            name_para]

            # Añadir celda a la fila
            row.append(cell_content)

            # Si ya hay 4 columnas, agregar la fila a la tabla y resetear
            if len(row) == 4:
                data.append(row)
                row = []

        # Si quedaron celdas sueltas, completamos con vacíos para que cierre la fila
        if row:
            while len(row) < 4:
                row.append("")
            data.append(row)

        # Crear tabla de tarjetas
        table = Table(data, colWidths=[130, 130, 130, 130], rowHeights=180)

        table.setStyle(TableStyle([
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),  # Color texto encabezado
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            # ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        elements.append(table)

        # Construir PDF
        doc.build(elements)

        # Guardar como adjunto
        pdf_value = base64.b64encode(buffer.getvalue())
        buffer.close()

        filename = 'catalogo_productos.pdf'

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': pdf_value,
            'res_model': 'product.template',
            'mimetype': 'application/pdf'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/{attachment.id}?download=true&filename={filename}",
            'target': 'self',
        }

    def get_image_or_default(self, record):
        img_data = ''
        """Retorna la imagen del registro o la imagen por defecto."""
        if record.image_1920:
            img_data = base64.b64decode(record.image_1920)

            # WEBP siempre empieza con b'RIFF' y luego contiene b'WEBP'
            if img_data.startswith(b'RIFF') and b'WEBP' in img_data[8:16]:
                img_data = None

        if not record.image_1920 or not img_data:
            # Ruta de la imagen por defecto dentro del módulo
            default_image_path = get_resource_from_path(
                'zue_electronic_invoice',  # Nombre exacto del módulo
                'static/src/img',
                'default.png'
            )

            # Leer y convertir a base64
            with open(default_image_path, 'rb') as f:
                img_data = f.read()

        image_bytes = BytesIO(img_data)

        return image_bytes




