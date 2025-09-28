-- =====================================================
-- CONFIGURAR BUCKET USER-IMAGES APENAS PARA SERVICE_ROLE
-- =====================================================

-- Este script configura o bucket para permitir apenas o service_role
-- (sua aplicação) enviar e ler imagens
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
DROP POLICY IF EXISTS "Allow any upload to user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow any view of user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow any update of user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow any delete from user-images" ON storage.objects;

-- 2. Cria políticas restritivas apenas para service_role
-- =====================================================

-- Política para permitir upload apenas para service_role
CREATE POLICY "Allow service_role upload to user-images" ON storage.objects
FOR INSERT WITH CHECK (
    bucket_id = 'user-images' AND
    auth.role() = 'service_role'
);

-- Política para permitir visualização apenas para service_role
CREATE POLICY "Allow service_role view of user-images" ON storage.objects
FOR SELECT USING (
    bucket_id = 'user-images' AND
    auth.role() = 'service_role'
);

-- Política para permitir atualização apenas para service_role
CREATE POLICY "Allow service_role update of user-images" ON storage.objects
FOR UPDATE USING (
    bucket_id = 'user-images' AND
    auth.role() = 'service_role'
);

-- Política para permitir exclusão apenas para service_role
CREATE POLICY "Allow service_role delete from user-images" ON storage.objects
FOR DELETE USING (
    bucket_id = 'user-images' AND
    auth.role() = 'service_role'
);

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

-- Deve retornar as 4 políticas criadas acima, todas com service_role.

-- =====================================================
-- NOTAS IMPORTANTES:
-- =====================================================
-- 1. Apenas service_role pode acessar o bucket
-- 2. Máxima segurança para suas imagens
-- 3. Aplicação pode enviar e ler imagens normalmente
-- 4. Usuários externos não podem acessar diretamente
-- 5. URLs assinadas funcionarão para acesso temporário
-- =====================================================

-- 5. Script para testar se funcionou
-- =====================================================
-- Após executar este script, teste o upload da sua aplicação:

-- -- Sua aplicação deve conseguir fazer upload normalmente
-- -- URLs assinadas serão geradas para acesso temporário
-- -- Apenas você (service_role) tem acesso direto

-- 6. Script para verificar acesso (opcional)
-- =====================================================
-- Para verificar se as políticas estão funcionando:

-- -- Teste com service_role (deve funcionar):
-- -- SELECT * FROM storage.objects WHERE bucket_id = 'user-images' LIMIT 5;

-- -- Teste com anon (deve falhar):
-- -- SET ROLE anon;
-- -- SELECT * FROM storage.objects WHERE bucket_id = 'user-images' LIMIT 5;
-- -- RESET ROLE;

-- 7. Script para monitorar uso do bucket
-- =====================================================
-- Consulta para ver estatísticas do bucket:

-- SELECT 
--     COUNT(*) as total_files,
--     SUM(metadata->>'size')::bigint as total_size_bytes,
--     ROUND(SUM(metadata->>'size')::bigint / 1024.0 / 1024.0, 2) as total_size_mb,
--     MIN(created_at) as oldest_file,
--     MAX(created_at) as newest_file
-- FROM storage.objects 
-- WHERE bucket_id = 'user-images';
