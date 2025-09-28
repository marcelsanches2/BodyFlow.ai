-- =====================================================
-- CONFIGURAÇÃO SIMPLIFICADA DO BUCKET USER-IMAGES
-- =====================================================

-- Execute este script no SQL Editor do Supabase
-- Este script cria o bucket e configura as permissões básicas

-- 1. Cria o bucket user-images (método mais simples)
-- =====================================================
INSERT INTO storage.buckets (id, name, public)
VALUES ('user-images', 'user-images', true)
ON CONFLICT (id) DO NOTHING;

-- 2. Remove políticas existentes (se houver)
-- =====================================================
DROP POLICY IF EXISTS "Allow upload of user images" ON storage.objects;
DROP POLICY IF EXISTS "Allow public access to user images" ON storage.objects;
DROP POLICY IF EXISTS "Allow update of own images" ON storage.objects;
DROP POLICY IF EXISTS "Allow delete of own images" ON storage.objects;

-- 3. Cria políticas simples para o bucket
-- =====================================================

-- Política para permitir upload (qualquer um pode fazer upload)
CREATE POLICY "Allow upload to user-images" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'user-images');

-- Política para permitir visualização (público)
CREATE POLICY "Allow public view of user-images" ON storage.objects
FOR SELECT USING (bucket_id = 'user-images');

-- Política para permitir atualização
CREATE POLICY "Allow update of user-images" ON storage.objects
FOR UPDATE USING (bucket_id = 'user-images');

-- Política para permitir exclusão
CREATE POLICY "Allow delete from user-images" ON storage.objects
FOR DELETE USING (bucket_id = 'user-images');

-- 4. Verifica se foi criado
-- =====================================================
SELECT 
    id,
    name,
    public,
    created_at
FROM storage.buckets 
WHERE id = 'user-images';

-- Se retornar uma linha, o bucket foi criado com sucesso!

-- =====================================================
-- INSTRUÇÕES IMPORTANTES:
-- =====================================================
-- 1. Execute este script no SQL Editor do Supabase
-- 2. Verifique se o bucket aparece na lista de buckets
-- 3. Teste fazendo upload de uma imagem manualmente
-- 4. Se funcionar, o sistema estará pronto para usar
-- =====================================================
