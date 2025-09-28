-- =====================================================
-- CONFIGURAR BUCKET USER-IMAGES COMO PRIVADO
-- =====================================================

-- Este script torna o bucket user-images privado e configura as permissões adequadas
-- Execute no SQL Editor do Supabase

-- 1. Altera o bucket para privado
-- =====================================================
UPDATE storage.buckets 
SET public = false 
WHERE id = 'user-images';

-- 2. Remove políticas públicas existentes
-- =====================================================
DROP POLICY IF EXISTS "Allow upload to user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow public view of user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow update of user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow delete from user-images" ON storage.objects;

-- 3. Cria políticas para bucket privado
-- =====================================================

-- Política para permitir upload (apenas usuários autenticados)
CREATE POLICY "Allow authenticated upload to user-images" ON storage.objects
FOR INSERT WITH CHECK (
    bucket_id = 'user-images' AND
    auth.role() = 'authenticated'
);

-- Política para permitir visualização (apenas usuários autenticados)
CREATE POLICY "Allow authenticated view of user-images" ON storage.objects
FOR SELECT USING (
    bucket_id = 'user-images' AND
    auth.role() = 'authenticated'
);

-- Política para permitir atualização (apenas usuários autenticados)
CREATE POLICY "Allow authenticated update of user-images" ON storage.objects
FOR UPDATE USING (
    bucket_id = 'user-images' AND
    auth.role() = 'authenticated'
);

-- Política para permitir exclusão (apenas usuários autenticados)
CREATE POLICY "Allow authenticated delete from user-images" ON storage.objects
FOR DELETE USING (
    bucket_id = 'user-images' AND
    auth.role() = 'authenticated'
);

-- 4. Verifica se o bucket foi alterado
-- =====================================================
SELECT 
    id,
    name,
    public,
    created_at
FROM storage.buckets 
WHERE id = 'user-images';

-- Deve retornar public = false

-- =====================================================
-- NOTAS IMPORTANTES:
-- =====================================================
-- 1. Bucket agora é PRIVADO (public = false)
-- 2. Apenas usuários autenticados podem acessar
-- 3. URLs das imagens precisarão de token de autenticação
-- 4. Maior segurança para as imagens dos usuários
-- 5. Código precisa ser ajustado para usar URLs assinadas
-- =====================================================

-- 5. Script para gerar URLs assinadas (exemplo)
-- =====================================================
-- Para acessar imagens privadas, você precisará gerar URLs assinadas:

-- CREATE OR REPLACE FUNCTION get_signed_url(bucket_name text, file_path text, expires_in int default 3600)
-- RETURNS text AS $$
-- DECLARE
--     signed_url text;
-- BEGIN
--     SELECT storage.create_signed_url(bucket_name, file_path, expires_in) INTO signed_url;
--     RETURN signed_url;
-- END;
-- $$ LANGUAGE plpgsql SECURITY DEFINER;

-- Exemplo de uso:
-- SELECT get_signed_url('user-images', 'food/2025/09/27/imagem.jpg', 3600);
