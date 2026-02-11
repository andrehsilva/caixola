import os
import secrets
from flask import current_app, url_for
from werkzeug.utils import secure_filename
from supabase import create_client

def get_supabase_client():
    """Inicializa o cliente Supabase usando as variáveis de ambiente."""
    url = current_app.config.get('SUPABASE_URL')
    key = current_app.config.get('SUPABASE_KEY')
    return create_client(url, key)

def save_picture(form_picture_data):
    """Faz upload da imagem para o bucket 'uploads' no Supabase."""
    supabase = get_supabase_client()
    
    # Gera nome único
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture_data.filename)
    picture_fn = random_hex + f_ext

    # Lê os bytes do arquivo para upload
    file_content = form_picture_data.read()
    
    # Upload para o Supabase Storage
    # Certifique-se de que o bucket 'uploads' existe e é público
    try:
        supabase.storage.from_('uploads').upload(
            path=picture_fn,
            file=file_content,
            file_options={"content-type": form_picture_data.content_type}
        )
        return picture_fn
    except Exception as e:
        print(f"Erro no upload para Supabase: {e}")
        return 'default.jpg'

def save_video(form_video_data):
    """Faz upload do vídeo para o bucket 'uploads' no Supabase."""
    supabase = get_supabase_client()
    
    random_hex = secrets.token_hex(8)
    video_fn = secure_filename(form_video_data.filename)
    video_name = f"{random_hex}_{video_fn}"
    
    file_content = form_video_data.read()
    
    try:
        supabase.storage.from_('uploads').upload(
            path=video_name,
            file=file_content,
            file_options={"content-type": form_video_data.content_type}
        )
        return video_name
    except Exception as e:
        print(f"Erro no upload de vídeo para Supabase: {e}")
        return None

def get_media_url(filename):
    if not filename:
        return ""
    if filename == 'default.jpg':
        return url_for('static', filename='default.jpg')

    supabase_url = current_app.config.get('SUPABASE_URL').rstrip('/')
    return f"{supabase_url}/storage/v1/object/public/uploads/{filename}"

def delete_file_from_uploads(filename):
    """Exclui o arquivo do bucket no Supabase."""
    if not filename or filename == 'default.jpg':
        return
    try:
        supabase = get_supabase_client()
        supabase.storage.from_('uploads').remove([filename])
    except Exception as e:
        print(f"Erro ao deletar arquivo no Supabase: {e}")