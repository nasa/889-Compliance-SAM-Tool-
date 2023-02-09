# ------------------------------------------------------------------------------
# Copyright 2022 by the U. S. Government as represented by the Administrator of
# the National Aeronautics and Space Administration.  All Other Rights Reserved.

# The 889 Compliance SAM Tool is licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
# ------------------------------------------------------------------------------

"""
This is the main flask application with endpoints, configuration, etc.

Returns:
    flask app: Application factory pattern. Returns a flask application.
"""
import datetime
from logging.config import dictConfig

import os

from flask_weasyprint import HTML, render_pdf
from flask import Flask, render_template, request

from samtools.sam_api.entity_information import search_sam_v3


def create_app(name=__name__):
    """Create a flask application of the SAM Tool

    Args:
        name (str, optional): name of the application. Defaults to __name__.

    Raises:
        Exception:

    Returns:
        flask app: returns the flask app.
    """
    _setup_logging()
    app = Flask(name, instance_relative_config=True)

    app.config.from_object("samtools.config.Default")
    app.config.from_pyfile("samtools.cfg")
    if app.config["SAM_API_KEY"] is None:
        raise Exception("SAM_API_KEY has not been set")

    @app.route("/")
    def welcome():
        app.logger.info(request)
        return render_template(
            "base.html",
            version=app.config["VERSION_STRING"],
            contact_email=app.config["CONTACT_EMAIL"],
            external_links=app.config["EXTERNAL_LINKS"],
            toast_messages=_get_nonexpired_messages(
                app.config["RECENT_WEBSITE_UPDATE_MESSAGES"]
            ),
        )

    @app.route("/api/entity-information/v3/entities", methods=["GET"])
    def search_v3():
        app.logger.info(request)
        try:
            return search_sam_v3(request.args, host_url=request.host_url)
        except Exception as exception:
            app.logger.error(exception)
            return {"success": False, "errors": ["400 Bad Request"]}

    @app.route("/api/file-download/summary", methods=["GET"])
    def get_compliance_summary_pdf():
        app.logger.info(request)
        try:
            response = search_sam_v3(request.args, host_url=request.host_url)
        except Exception as exception:
            app.logger.error(exception)
            return {"success": False, "errors": ["400 Bad Request"]}

        if not response["success"]:
            app.logger.error(response)
            return {"success": False, "errors": ["400 Bad Request"]}

        if len(response["entityData"]) != 1:
            app.logger.error(response)
            return {"success": False, "errors": ["400 Bad Request"]}

        return _get_summary_pdf_response(
            response["entityData"][0],
            host_url=request.host_url,
            external_links=app.config["EXTERNAL_LINKS"],
        )

    return app


def _setup_logging():
    debug = os.environ.get("FLASK_DEBUG", False)
    if debug == "1":
        debug = True

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                },
                "access": {
                    "format": "%(message)s",
                },
            },
            "handlers": {
                "console": {
                    "level": "INFO",
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
                "error_file": {
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "formatter": "default",
                    "filename": "/var/log/gunicorn/error.log",
                    "when": "D",
                    "backupCount": 15,
                    "delay": "True",
                },
                "access_file": {
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "formatter": "access",
                    "filename": "/var/log/gunicorn/access.log",
                    "when": "D",
                    "backupCount": 15,
                    "delay": "True",
                },
            },
            "loggers": {
                "gunicorn.error": {
                    "handlers": ["console"] if debug else ["console", "error_file"],
                    "level": "ERROR",
                    "propagate": False,
                },
                "gunicorn.access": {
                    "handlers": ["console"] if debug else ["console", "access_file"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
            "root": {
                "level": "DEBUG" if debug else "INFO",
                "handlers": ["console"],
            },
        }
    )


def _get_summary_pdf_response(entity, host_url, external_links):
    html = render_template(
        "sam_summary_pdf_template.html",
        date_generated=datetime.datetime.now().strftime("%B %-d, %Y"),
        entityData=entity,
        host_url=host_url,
        external_links=external_links,
    )
    filename = _get_pdf_filename(entity["entityRegistration"]["legalBusinessName"])
    return render_pdf(HTML(string=html), download_filename=filename)


def _get_pdf_filename(legal_business_name):
    cleaned_name = legal_business_name.replace(".", "").replace(",", "")
    return f"Record of Section 889 Compliance - {cleaned_name}.pdf"


def _get_nonexpired_messages(messages):
    non_expired_messages = []
    for message in messages:
        if message["expiration_date"].date() >= datetime.datetime.now().date():
            non_expired_messages.append(message["message"])
    return non_expired_messages
