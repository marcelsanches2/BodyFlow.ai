-- =====================================================
-- REABILITAR RLS E CONFIGURAR POLÍTICAS DE SEGURANÇA
-- =====================================================

-- Este script reabilita o RLS e cria políticas seguras
-- Execute no SQL Editor do Supabase

-- 1. Reabilita Row Level Security
-- =====================================================
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- 2. Remove todas as políticas existentes
-- =====================================================
DROP POLICY IF EXISTS "Allow service_role upload to user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow service_role view of user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow service_role update of user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow service_role delete from user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow any upload to user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow any view of user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow any update of user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow any delete from user-images" ON storage.objects;

-- 3. Cria políticas seguras para service_role
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

-- 4. Verifica se RLS foi reabilitado
-- =====================================================
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE tablename = 'objects' 
AND schemaname = 'storage';

-- Deve retornar rowsecurity = true

-- 5. Verifica as políticas criadas
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

-- 6. Verifica configuração do bucket
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

-- =====================================================
-- NOTAS IMPORTANTES:
-- =====================================================
-- 1. RLS reabilitado para máxima segurança
-- 2. Apenas service_role pode acessar o bucket
-- 3. URLs assinadas funcionarão normalmente
-- 4. Máxima proteção das imagens dos usuários
-- 5. Sistema funcionará normalmente com SERVICE_ROLE
-- =====================================================

-- 7. Script para testar se funcionou
-- =====================================================
-- Após executar este script, teste o upload:

-- -- Sua aplicação deve conseguir fazer upload normalmente
-- -- URLs assinadas serão geradas para acesso temporário
-- -- Apenas service_role tem acesso direto ao bucket

-- 8. Script para monitorar segurança
-- =====================================================
-- Consulta para verificar tentativas de acesso não autorizado:

-- SELECT 
--     COUNT(*) as total_access_attempts,
--     COUNT(CASE WHEN auth.role() = 'service_role' THEN 1 END) as service_role_access,
--     COUNT(CASE WHEN auth.role() = 'anon' THEN 1 END) as anon_access,
--     COUNT(CASE WHEN auth.role() NOT IN ('service_role', 'anon') THEN 1 END) as other_access
-- FROM storage.objects 
-- WHERE bucket_id = 'user-images';

-- 9. Script para limpeza de arquivos antigos (opcional)
-- =====================================================
-- Função para limpar arquivos antigos (mais de 90 dias):

-- CREATE OR REPLACE FUNCTION cleanup_old_user_images()
-- RETURNS void AS $$
-- BEGIN
--     DELETE FROM storage.objects 
--     WHERE bucket_id = 'user-images'
--     AND created_at < NOW() - INTERVAL '90 days';
--     
--     RAISE NOTICE 'Arquivos antigos removidos: %', ROW_COUNT;
-- END;
-- $$ LANGUAGE plpgsql;

-- -- Para executar a limpeza:
-- -- SELECT cleanup_old_user_images();
