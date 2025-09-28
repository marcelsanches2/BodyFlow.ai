-- =====================================================
-- VERIFICAR E CORRIGIR POLÍTICAS RLS - VERSÃO SIMPLES
-- =====================================================

-- Execute este script no SQL Editor do Supabase
-- Este script verifica e corrige as políticas RLS

-- 1. Verifica se o bucket existe
-- =====================================================
SELECT 
    id,
    name,
    public,
    created_at
FROM storage.buckets 
WHERE id = 'user-images';

-- Se não retornar nada, o bucket não existe
-- Se retornar uma linha, o bucket existe

-- 2. Remove TODAS as políticas existentes
-- =====================================================
DROP POLICY IF EXISTS "Allow service_role upload to user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow service_role view of user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow service_role update of user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow service_role delete from user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow any upload to user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow any view of user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow any update of user-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow any delete from user-images" ON storage.objects;

-- 3. Desabilita RLS temporariamente para teste
-- =====================================================
ALTER TABLE storage.objects DISABLE ROW LEVEL SECURITY;

-- 4. Verifica se RLS foi desabilitado
-- =====================================================
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE tablename = 'objects' 
AND schemaname = 'storage';

-- Deve retornar rowsecurity = false

-- =====================================================
-- TESTE AGORA O UPLOAD!
-- =====================================================
-- Com RLS desabilitado, o upload deve funcionar
-- Execute o teste Python novamente

-- 5. Reabilita RLS após teste (opcional)
-- =====================================================
-- Descomente as linhas abaixo APENAS após confirmar que o upload funciona:

-- ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- -- Cria políticas mais simples
-- CREATE POLICY "Allow all for user-images" ON storage.objects
-- FOR ALL USING (bucket_id = 'user-images');

-- =====================================================
-- NOTAS IMPORTANTES:
-- =====================================================
-- 1. RLS desabilitado = qualquer um pode acessar
-- 2. Use apenas para teste e diagnóstico
-- 3. Reabilite RLS após confirmar que funciona
-- 4. Crie políticas mais específicas depois
-- =====================================================
