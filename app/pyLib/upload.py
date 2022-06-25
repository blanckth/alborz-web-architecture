# Upload Packages

def allowed_file(filename, allowedList):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowedList
