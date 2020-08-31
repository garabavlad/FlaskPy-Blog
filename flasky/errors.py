from flasky import app
from flask import render_template, make_response


# ERRORS
# 404
@app.errorhandler(404)
def error_404(req):
    app.logger.info(req)
    return make_response(render_template("error/404.html"), 404)


@app.errorhandler(400)
def error_400(req):
    app.logger.info(req)
    return make_response(render_template("error/400.html"), 400)


@app.errorhandler(500)
def error_500(req):
    app.logger.info(req)
    return make_response(render_template("error/500.html"), 500)