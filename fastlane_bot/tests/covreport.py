import imgkit

wkhtmltopdf_options = {
    "enable-local-file-access": None,
}
imgkit.from_file("htmlcov/index.html", "coverage.png", options=wkhtmltopdf_options)
