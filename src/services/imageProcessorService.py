# src.service.imagem_proecessor.py
from PIL import Image
import io
from typing import Tuple, Union

class ImageProcessor:
    """
    Classe para processar e otimizar imagens (Operação SÍNCRONA).
    """
    def __init__(self, max_size: Tuple[int, int] = (1200, 1200), quality: int = 85):
        self.MAX_SIZE = max_size
        self.QUALITY = quality
        
    # Este método é SÍNCRONO e será chamado via run_in_threadpool
    def optimize_image(self, file_contents: bytes, output_format: str = 'JPEG') -> bytes:
        try:
            image = Image.open(io.BytesIO(file_contents))
            
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')

            # Redimensionamento
            image.thumbnail(self.MAX_SIZE)
            
            output_buffer = io.BytesIO()
            
            # Compressão
            if output_format == 'JPEG':
                image.save(output_buffer, format=output_format, quality=self.QUALITY, optimize=True)
            else:
                image.save(output_buffer, format=output_format)

            output_buffer.seek(0)
            return output_buffer.read()
            
        except Exception as e:
            # Não precisa fechar o buffer aqui, pois ele é local
            print(f"Erro no processamento da imagem com Pillow: {e}")
            raise RuntimeError("Não foi possível processar a imagem para otimização.")