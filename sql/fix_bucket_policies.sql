-- =====================================================
-- CORRIGIR POLÍTICAS RLS DO BUCKET USER-IMAGES
-- =====================================================

-- Este script corrige as políticas RLS que estão bloqueando o acesso
-- Execute no SQL Editor do Supabase

-- 1. Remove todas as políticas existentes
-- =====================================================
DROP POLICY IF EXISTS "Allow upload to user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow public view of user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow update of user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow delete from user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated upload to user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated view of user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated update of user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated delete from user-images" ON storage.objects;

-- 2. Cria políticas mais permissivas (temporárias para teste)
-- =====================================================

-- Política para permitir upload (qualquer um pode fazer upload)
CREATE POLICY "Allow any upload to user-images" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'user-images');

-- Política para permitir visualização (qualquer um pode ver)
CREATE POLICY "Allow any view of user-images" ON storage.objects
FOR SELECT USING (bucket_id = 'user-images');

-- Política para permitir atualização (qualquer um pode atualizar)
CREATE POLICY "Allow any update of user-images" ON storage.objects
FOR UPDATE USING (bucket_id = 'user-images');

-- Política para permitir exclusão (qualquer um pode deletar)
CREATE POLICY "Allow any delete from user-images" ON storage.objects
FOR DELETE USING (bucket_id = 'user-images');

-- 3. Verifica se o bucket está configurado corretamente
-- =====================================================
SELECT 
    id,
    name,
    public,
    file_size_limit,
    allowed_mime_types,
    created_at
FROM storage.buckets 
WHERE id = 'user-images';

-- Deve retornar uma linha com o bucket user-images.

-- 4. Verifica as políticas criadas
-- =====================================================
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies 
WHERE tablename = 'objects' 
AND schemaname = 'storage'
AND policyname LIKE '%user-images%'
ORDER BY policyname;

-- Deve retornar as 4 políticas criadas acima.

-- =====================================================
-- NOTAS IMPORTANTES:
-- =====================================================
-- 1. Estas políticas são MUITO permissivas (para teste)
-- 2. Qualquer um pode fazer upload/visualizar/deletar
-- 3. Use apenas para testar se o sistema funciona
-- 4. Depois ajuste as políticas conforme sua segurança
-- =====================================================

-- 5. Script para testar se funcionou
-- =====================================================
-- Após executar este script, teste o upload:

-- -- Teste via API (substitua pelos seus valores):
-- -- curl -X POST 'https://your-project.supabase.co/storage/v1/object/user-images/test.jpg' \
-- --   -H 'Authorization: Bearer YOUR_ANON_KEY' \
-- --   -H 'Content-Type: image/jpeg' \
-- --   --data-binary @test-image.jpg

-- 6. Script para políticas mais seguras (opcional)
-- =====================================================
-- Se quiser políticas mais seguras depois do teste:

-- -- Remove políticas permissivas
-- DROP POLICY IF EXISTS "Allow any upload to user-images" ON storage.objects;
-- DROP POLICY IF EXISTS "Allow any view of user-images" ON storage.objects;
-- DROP POLICY IF EXISTS "Allow any update of user-images" ON storage.objects;
-- DROP POLICY IF EXISTS "Allow any delete from user-images" ON storage.objects;

-- -- Cria políticas mais seguras
-- CREATE POLICY "Allow service upload to user-images" ON storage.objects
-- FOR INSERT WITH CHECK (
--     bucket_id = 'user-images' AND
--     auth.role() = 'service_role'
-- );

-- CREATE POLICY "Allow service view of user-images" ON storage.objects
-- FOR SELECT USING (
--     bucket_id = 'user-images' AND
--     auth.role() = 'service_role'
-- );
