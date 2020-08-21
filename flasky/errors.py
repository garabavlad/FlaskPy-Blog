from flasky import app
from flask import render_template, make_response


# ERRORS
# 404
@app.errorhandler(404)
def error_404(req):
    app.logger.info(req)
    return make_response(render_template("error/404.html"), 404)


@app.errorhandler(400)
def bad_request(req):
    app.logger.info(req)
    return make_response(render_template("error/400.html"), 400)


@app.errorhandler(500)
def server_error(req):
    app.logger.info(req)
    return make_response(render_template("error/500.html"), 500)