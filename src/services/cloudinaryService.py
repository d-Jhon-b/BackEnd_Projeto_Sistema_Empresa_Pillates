# src.service.CloudinaryService.py
import cloudinary
import cloudinary.uploader
from typing import Dict, Any, List
from src.database.envConfig.envCloudinary import EnvCloudinary 
from src.services.imageProcessorService import ImageProcessor 
from starlette.concurrency import run_in_threadpool
import logging
import io

class CloudinaryService:
    def __init__(self):
        env_config = EnvCloudinary().get_config()
        self.CLOUD_NAME = env_config["CLOUDINARY_CLOUD_NAME"]
        self.API_KEY = env_config["CLOUDINARY_API_KEY"]
        self.API_SECRET = env_config["CLOUDINARY_API_SECRET"]
        
        cloudinary.config(
            cloud_name=self.CLOUD_NAME,
            api_key=self.API_KEY,
            api_secret=self.API_SECRET,
            secure=True
        )
        
        # 3. Inicializa o processador de imagem (síncrono)
        # Configuração: Largura/Altura Máxima 1080px, Qualidade 80%
        self.image_processor = ImageProcessor(max_size=(1080, 1080), quality=80)

    async def upload_optimized_image(
        self, 
        file_contents: bytes, 
        folder: str, 
        public_id: str
    ) -> str:
        """
        1. Processa a imagem (operação síncrona).
        2. Faz o upload para o Cloudinary (operação I/O).
        3. Retorna a URL segura.
        """
        
        # 1. Otimização no Pool de Threads (Para não travar o loop de eventos)
        try:
            logging.info("Iniciando otimização da imagem no pool de threads.")
            # Chama o método síncrono do Pillow de forma assíncrona
            optimized_contents = await run_in_threadpool(
                self.image_processor.optimize_image, 
                file_contents, 
                'JPEG' # Formato de saída otimizado
            )
            logging.info("Otimização concluída. Tamanho otimizado: %d bytes.", len(optimized_contents))

        except RuntimeError as e:
            logging.error(f"Erro de otimização: {e}")
            raise Exception(f"Falha ao processar a imagem: {e}")

        # 2. Upload para o Cloudinary
        try:
            # Upload usa a conexão HTTP, que o Cloudinary SDK trata. 
            # Não precisa de run_in_threadpool para o SDK do Cloudinary.
            upload_result = cloudinary.uploader.upload(
                optimized_contents, 
                folder=folder,
                public_id=public_id,
                resource_type="image",
                format="jpg" 
            )
            
            secure_url = upload_result.get("secure_url")
            if not secure_url:
                 raise Exception("Cloudinary não retornou uma URL segura.")
                 
            return secure_url
            
        except Exception as e:
            logging.error(f"Erro no upload para Cloudinary: {e}")
            raise Exception(f"Falha ao enviar a imagem para a nuvem: {e}")