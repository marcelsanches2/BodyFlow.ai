-- =====================================================
-- CONFIGURAÇÃO DE SEGURANÇA SEM MODIFICAR RLS
-- =====================================================

-- Este script configura segurança sem modificar políticas RLS
-- Execute no SQL Editor do Supabase

-- 1. Verifica se o bucket está configurado corretamente
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

-- 2. Verifica políticas atuais (apenas visualização)
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

-- 3. Verifica se RLS está habilitado
-- =====================================================
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE tablename = 'objects' 
AND schemaname = 'storage';

-- Se rowsecurity = true, RLS está habilitado
-- Se rowsecurity = false, RLS está desabilitado

-- =====================================================
-- SOLUÇÕES ALTERNATIVAS:
-- =====================================================

-- OPÇÃO 1: Usar bucket público com URLs assinadas
-- =====================================================
-- Se não conseguir modificar políticas RLS, pode usar bucket público
-- mas sempre gerar URLs assinadas para acesso temporário

-- UPDATE storage.buckets 
-- SET public = true 
-- WHERE id = 'user-images';

-- OPÇÃO 2: Verificar se já existe política permissiva
-- =====================================================
-- Algumas políticas podem já permitir acesso do service_role

-- OPÇÃO 3: Usar configuração atual
-- =====================================================
-- Se o sistema já está funcionando, pode manter como está

-- =====================================================
-- NOTAS IMPORTANTES:
-- =====================================================
-- 1. Erro "must be owner" é normal no Supabase
-- 2. Apenas proprietário do banco pode modificar RLS
-- 3. Sistema pode funcionar com políticas existentes
-- 4. URLs assinadas fornecem segurança adicional
-- 5. Bucket privado + URLs assinadas = boa segurança
-- =====================================================

-- 4. Script para testar configuração atual
-- =====================================================
-- Execute este teste para verificar se está funcionando:

-- -- Teste de upload via API (substitua pelos seus valores):
-- -- curl -X POST 'https://your-project.supabase.co/storage/v1/object/user-images/test.jpg' \
-- --   -H 'Authorization: Bearer YOUR_SERVICE_ROLE_KEY' \
-- --   -H 'Content-Type: image/jpeg' \
-- --   --data-binary @test-image.jpg

-- 5. Script para monitorar uso do bucket
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

-- 6. Recomendações de segurança
-- =====================================================
-- Mesmo sem modificar RLS, você pode manter segurança:

-- 1. Bucket privado (public = false)
-- 2. URLs assinadas para acesso temporário
-- 3. SERVICE_ROLE para operações da aplicação
-- 4. Monitoramento de acesso
-- 5. Limpeza periódica de arquivos antigos
