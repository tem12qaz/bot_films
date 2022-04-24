from io import BytesIO


def copy_buffer(buffer: BytesIO) -> BytesIO:
    buffer.seek(0)
    buffer_copy = BytesIO(buffer.read())
    buffer.seek(0)
    return buffer_copy
