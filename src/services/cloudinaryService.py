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

        self.image_processor = ImageProcessor(max_size=(1080, 1080), quality=80)

    async def upload_optimized_image(
        self, 
        file_contents: bytes, 
        folder: str, 
        public_id: str
    ) -> str:

        try:
            logging.info("Iniciando otimização da imagem no pool de threads.")
            optimized_contents = await run_in_threadpool(
                self.image_processor.optimize_image, 
                file_contents, 
                'JPEG' 
            )
            logging.info("Otimização concluída. Tamanho otimizado: %d bytes.", len(optimized_contents))

        except RuntimeError as e:
            logging.error(f"Erro de otimização: {e}")
            raise Exception(f"Falha ao processar a imagem: {e}")

        try:

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