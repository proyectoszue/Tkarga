# -*- coding: utf-8 -*-

import logging
from http import HTTPStatus
from urllib.parse import quote

from werkzeug.exceptions import BadRequest

from odoo import _, http
from odoo.exceptions import MissingError
from odoo.http import Stream, request
from odoo.tools import replace_exceptions, str2bool

from odoo.addons.documents.controllers.documents import ShareRoute as DocumentsShareRoute

_logger = logging.getLogger(__name__)


class ShareRoute(DocumentsShareRoute):

    def _build_attachment_fallback_stream(self, document_sudo, attachment):
        data = attachment.db_datas
        return Stream(
            type='data',
            data=data,
            mimetype=attachment.mimetype,
            download_name=attachment.name or document_sudo.name,
            etag=attachment.checksum,
            last_modified=attachment.write_date,
            size=len(data),
            public=attachment.public,
        )

    def _documents_content_stream(self, document_sudo):
        try:
            return super()._documents_content_stream(document_sudo)
        except OSError as error:
            attachment = document_sudo.attachment_id.sudo()
            if attachment and attachment.db_datas:
                _logger.warning(
                    "Falling back to db_datas for document %s (attachment %s).",
                    document_sudo.id,
                    attachment.id,
                    exc_info=True,
                )
                return self._build_attachment_fallback_stream(document_sudo, attachment)

            _logger.warning(
                "Unable to stream document %s (attachment %s, store_fname=%s).",
                document_sudo.id,
                attachment.id if attachment else False,
                attachment.store_fname if attachment else False,
                exc_info=True,
            )
            raise MissingError(_("The requested document is no longer available.")) from error

    @http.route()
    def documents_content(self, access_token, download=True):
        document_sudo = self._from_access_token(access_token, skip_log=True)
        if not document_sudo:
            Redirect = request.env['documents.redirect'].sudo()
            if document_sudo := Redirect._get_redirection(access_token):
                return request.redirect(
                    f'/odoo/documents/{quote(document_sudo.access_token, safe="")}',
                    HTTPStatus.MOVED_PERMANENTLY,
                )
            raise request.not_found()
        if document_sudo.type == 'url':
            return request.redirect(
                document_sudo.url, code=HTTPStatus.TEMPORARY_REDIRECT, local=False)
        if document_sudo.type == 'folder':
            return self._make_zip(
                f'{document_sudo.name}.zip',
                self._get_folder_children(document_sudo),
            )
        if document_sudo.type == 'binary':
            if not document_sudo.attachment_id:
                raise request.not_found()
            with replace_exceptions(ValueError, by=BadRequest):
                download = str2bool(download)
            with replace_exceptions(ValueError, MissingError, by=request.not_found()):
                stream = self._documents_content_stream(document_sudo)
            try:
                return stream.get_response(as_attachment=download)
            except OSError as error:
                attachment = document_sudo.attachment_id.sudo()
                if stream.type == 'path' and attachment and attachment.db_datas:
                    _logger.warning(
                        "Serving document %s from db_datas after response failure (attachment %s).",
                        document_sudo.id,
                        attachment.id,
                        exc_info=True,
                    )
                    fallback_stream = self._build_attachment_fallback_stream(document_sudo, attachment)
                    return fallback_stream.get_response(as_attachment=download)

                _logger.warning(
                    "Unable to send document %s response (attachment %s, store_fname=%s).",
                    document_sudo.id,
                    attachment.id if attachment else False,
                    attachment.store_fname if attachment else False,
                    exc_info=True,
                )
                raise request.not_found() from error
        raise NotImplementedError(f"unknown document type {document_sudo.type!r}")

    @http.route()
    def documents_upload(
        self,
        ufile,
        access_token='',
        user_folder_id='',
        owner_id='',
        partner_id='',
        res_id='',
        res_model=False,
        allowed_company_ids='',
    ):
        sanitized_partner_id = ''
        if partner_id:
            try:
                partner_id_int = int(partner_id)
            except (TypeError, ValueError):
                partner_id_int = None
            if partner_id_int and request.env['res.partner'].sudo().browse(partner_id_int).exists():
                sanitized_partner_id = str(partner_id_int)
            else:
                _logger.warning(
                    "Ignoring invalid partner_id=%s in documents upload (access_token=%s).",
                    partner_id,
                    access_token,
                )

        files = request.httprequest.files.getlist('ufile')
        filenames = [file.filename for file in files]
        log_context = {
            'user_id': request.env.user.id,
            'access_token': access_token,
            'user_folder_id': user_folder_id,
            'owner_id': owner_id,
            'partner_id': partner_id,
            'partner_id_sanitized': sanitized_partner_id,
            'res_model': res_model,
            'res_id': res_id,
            'allowed_company_ids': allowed_company_ids,
            'files': filenames,
        }
        try:
            return super().documents_upload(
                ufile,
                access_token=access_token,
                user_folder_id=user_folder_id,
                owner_id=owner_id,
                partner_id=sanitized_partner_id,
                res_id=res_id,
                res_model=res_model,
                allowed_company_ids=allowed_company_ids,
            )
        except OSError:
            _logger.exception("Documents upload filesystem failure: %s", log_context)
            return request.make_response(
                _("No fue posible guardar el archivo en el servidor. Verifique permisos, espacio en disco y estado del filestore."),
                headers=[('Content-Type', 'text/plain; charset=utf-8')],
                status=500,
            )
        except Exception as error:
            _logger.exception("Unexpected documents upload failure: %s", log_context)
            return request.make_response(
                f"{type(error).__name__}: {error}",
                headers=[('Content-Type', 'text/plain; charset=utf-8')],
                status=500,
            )
