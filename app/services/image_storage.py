"""
Serviço de Armazenamento de Imagens no Supabase Storage
"""

import os
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from app.core.config import Config

class ImageStorageService:
    """Serviço para armazenar imagens no Supabase Storage"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            Config.SUPABASE_URL, 
            Config.SUPABASE_KEY
        )
        self.bucket_name = "user-images"  # Nome do bucket no Supabase
        
    async def upload_image(
        self, 
        image_data: bytes, 
        user_phone: str, 
        content_type: str = "image/jpeg",
        image_type: str = "unknown"
    ) -> Optional[str]:
        """
        Faz upload de uma imagem para o Supabase Storage
        
        Args:
            image_data: Dados binários da imagem
            user_phone: Número do telefone do usuário
            content_type: Tipo MIME da imagem (image/jpeg, image/png, etc.)
            image_type: Tipo da imagem (food, bioimpedance, exercise, etc.)
        
        Returns:
            URL assinada da imagem ou None se falhou
        """
        try:
            # Gera nome único para o arquivo
            file_extension = self._get_file_extension(content_type)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            
            # Organiza por tipo de imagem e data
            folder_path = f"{image_type}/{datetime.now().strftime('%Y/%m/%d')}"
            file_name = f"{user_phone}_{timestamp}_{unique_id}{file_extension}"
            file_path = f"{folder_path}/{file_name}"
            
            print(f"📸 ImageStorageService: Fazendo upload de imagem")
            print(f"   📁 Bucket: {self.bucket_name}")
            print(f"   📄 Arquivo: {file_path}")
            print(f"   📏 Tamanho: {len(image_data)} bytes")
            print(f"   🏷️ Tipo: {content_type}")
            
            # Faz upload para o Supabase Storage
            result = self.supabase.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=image_data,
                file_options={
                    "content-type": content_type,
                    "cache-control": "3600"
                }
            )
            
            if result:
                # Gera URL assinada da imagem (válida por 1 hora)
                signed_url_response = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                    path=file_path,
                    expires_in=3600  # 1 hora
                )
                
                # Extrai a URL do response (pode ser dict ou string)
                if isinstance(signed_url_response, dict):
                    signed_url = signed_url_response.get('signedURL') or signed_url_response.get('signedUrl')
                else:
                    signed_url = signed_url_response
                
                print(f"✅ ImageStorageService: Upload concluído com sucesso")
                print(f"   🔗 URL assinada: {signed_url[:100] if signed_url else 'N/A'}...")
                
                return signed_url
            else:
                print(f"❌ ImageStorageService: Falha no upload")
                return None
                
        except Exception as e:
            print(f"❌ ImageStorageService: Erro no upload: {e}")
            return None
    
    async def delete_image(self, image_url: str) -> bool:
        """
        Remove uma imagem do Supabase Storage
        
        Args:
            image_url: URL da imagem a ser removida
        
        Returns:
            True se removida com sucesso, False caso contrário
        """
        try:
            # Extrai o caminho do arquivo da URL
            file_path = self._extract_file_path_from_url(image_url)
            
            if not file_path:
                print(f"❌ ImageStorageService: Não foi possível extrair caminho da URL: {image_url}")
                return False
            
            print(f"🗑️ ImageStorageService: Removendo imagem")
            print(f"   📄 Arquivo: {file_path}")
            
            # Remove o arquivo do storage
            result = self.supabase.storage.from_(self.bucket_name).remove([file_path])
            
            if result:
                print(f"✅ ImageStorageService: Imagem removida com sucesso")
                return True
            else:
                print(f"❌ ImageStorageService: Falha ao remover imagem")
                return False
                
        except Exception as e:
            print(f"❌ ImageStorageService: Erro ao remover imagem: {e}")
            return False
    
    async def get_image_info(self, image_url: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações sobre uma imagem armazenada
        
        Args:
            image_url: URL da imagem
        
        Returns:
            Dicionário com informações da imagem ou None
        """
        try:
            file_path = self._extract_file_path_from_url(image_url)
            
            if not file_path:
                return None
            
            # Lista arquivos para obter informações
            files = self.supabase.storage.from_(self.bucket_name).list(
                path=os.path.dirname(file_path)
            )
            
            file_name = os.path.basename(file_path)
            
            for file_info in files:
                if file_info.get('name') == file_name:
                    return {
                        "name": file_info.get('name'),
                        "size": file_info.get('metadata', {}).get('size'),
                        "created_at": file_info.get('created_at'),
                        "updated_at": file_info.get('updated_at'),
                        "content_type": file_info.get('metadata', {}).get('mimetype'),
                        "url": image_url
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ ImageStorageService: Erro ao obter informações da imagem: {e}")
            return None
    
    def _get_file_extension(self, content_type: str) -> str:
        """
        Retorna a extensão do arquivo baseada no content-type
        """
        extensions = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg", 
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/bmp": ".bmp"
        }
        
        return extensions.get(content_type.lower(), ".jpg")
    
    async def get_signed_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """
        Gera uma nova URL assinada para um arquivo existente
        
        Args:
            file_path: Caminho do arquivo no bucket
            expires_in: Tempo de expiração em segundos (padrão: 1 hora)
        
        Returns:
            URL assinada ou None se falhou
        """
        try:
            signed_url = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                path=file_path,
                expires_in=expires_in
            )
            
            print(f"🔗 ImageStorageService: URL assinada gerada para {file_path}")
            return signed_url
            
        except Exception as e:
            print(f"❌ ImageStorageService: Erro ao gerar URL assinada: {e}")
            return None
    
    def _extract_file_path_from_url(self, image_url: str) -> Optional[str]:
        """
        Extrai o caminho do arquivo da URL do Supabase (pública ou assinada)
        """
        try:
            # URL pública: https://[project].supabase.co/storage/v1/object/public/[bucket]/[path]
            # URL assinada: https://[project].supabase.co/storage/v1/object/sign/[bucket]/[path]?token=...
            
            if "/storage/v1/object/" not in image_url:
                return None
            
            # Para URLs públicas
            if "/storage/v1/object/public/" in image_url:
                parts = image_url.split("/storage/v1/object/public/")
                if len(parts) == 2:
                    bucket_and_path = parts[1]
                    if bucket_and_path.startswith(f"{self.bucket_name}/"):
                        return bucket_and_path[len(f"{self.bucket_name}/"):]
            
            # Para URLs assinadas
            elif "/storage/v1/object/sign/" in image_url:
                parts = image_url.split("/storage/v1/object/sign/")
                if len(parts) == 2:
                    bucket_and_path = parts[1].split("?")[0]  # Remove query parameters
                    if bucket_and_path.startswith(f"{self.bucket_name}/"):
                        return bucket_and_path[len(f"{self.bucket_name}/"):]
            
            return None
            
        except Exception as e:
            print(f"❌ ImageStorageService: Erro ao extrair caminho da URL: {e}")
            return None
    
    async def create_bucket_if_not_exists(self) -> bool:
        """
        Cria o bucket se ele não existir
        
        Returns:
            True se bucket existe ou foi criado, False caso contrário
        """
        try:
            # Lista buckets existentes
            buckets = self.supabase.storage.list_buckets()
            
            bucket_names = [bucket.name for bucket in buckets]
            
            if self.bucket_name not in bucket_names:
                print(f"📦 ImageStorageService: Criando bucket '{self.bucket_name}'")
                
                # Cria o bucket
                result = self.supabase.storage.create_bucket(
                    self.bucket_name,
                    options={
                        "public": True,  # Permite acesso público às imagens
                        "file_size_limit": 50 * 1024 * 1024,  # 50MB limite
                        "allowed_mime_types": [
                            "image/jpeg",
                            "image/png", 
                            "image/gif",
                            "image/webp",
                            "image/bmp"
                        ]
                    }
                )
                
                if result:
                    print(f"✅ ImageStorageService: Bucket '{self.bucket_name}' criado com sucesso")
                    return True
                else:
                    print(f"❌ ImageStorageService: Falha ao criar bucket '{self.bucket_name}'")
                    return False
            else:
                print(f"✅ ImageStorageService: Bucket '{self.bucket_name}' já existe")
                return True
                
        except Exception as e:
            print(f"❌ ImageStorageService: Erro ao verificar/criar bucket: {e}")
            return False


# Instância global do serviço de armazenamento de imagens
image_storage_service = ImageStorageService()
