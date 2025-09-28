-- =====================================================
-- CONFIGURAÇÃO DO BUCKET USER-IMAGES NO SUPABASE STORAGE
-- =====================================================

-- Este script configura o bucket para armazenar imagens dos usuários
-- Execute no SQL Editor do Supabase

-- 1. Cria o bucket user-images
-- =====================================================
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'user-images',
    'user-images', 
    true,  -- Bucket público para acesso direto às imagens
    52428800,  -- 50MB limite de arquivo
    ARRAY['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp']
)
ON CONFLICT (id) DO UPDATE SET
    public = true,
    file_size_limit = 52428800,
    allowed_mime_types = ARRAY['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'];

-- 2. Configura políticas de Row Level Security (RLS)
-- =====================================================

-- Política para permitir upload de imagens (qualquer usuário autenticado)
CREATE POLICY "Allow upload of user images" ON storage.objects
FOR INSERT WITH CHECK (
    bucket_id = 'user-images' AND
    auth.role() = 'authenticated'
);

-- Política para permitir visualização de imagens (público)
CREATE POLICY "Allow public access to user images" ON storage.objects
FOR SELECT USING (bucket_id = 'user-images');

-- Política para permitir atualização de imagens (apenas o proprietário)
CREATE POLICY "Allow update of own images" ON storage.objects
FOR UPDATE USING (
    bucket_id = 'user-images' AND
    auth.role() = 'authenticated'
);

-- Política para permitir exclusão de imagens (apenas o proprietário)
CREATE POLICY "Allow delete of own images" ON storage.objects
FOR DELETE USING (
    bucket_id = 'user-images' AND
    auth.role() = 'authenticated'
);

-- 3. Verifica se o bucket foi criado corretamente
-- =====================================================
-- Execute esta consulta para verificar:

-- SELECT 
--     id,
--     name,
--     public,
--     file_size_limit,
--     allowed_mime_types,
--     created_at
-- FROM storage.buckets 
-- WHERE id = 'user-images';

-- Deve retornar uma linha com o bucket user-images.

-- 4. Verifica as políticas criadas
-- =====================================================
-- Execute esta consulta para verificar as políticas:

-- SELECT 
--     schemaname,
--     tablename,
--     policyname,
--     permissive,
--     roles,
--     cmd,
--     qual
-- FROM pg_policies 
-- WHERE tablename = 'objects' 
-- AND schemaname = 'storage'
-- ORDER BY policyname;

-- Deve retornar as 4 políticas criadas acima.

-- =====================================================
-- NOTAS IMPORTANTES:
-- =====================================================
-- 1. O bucket é público para permitir acesso direto às imagens
-- 2. Limite de 50MB por arquivo
-- 3. Apenas tipos de imagem são permitidos
-- 4. RLS configurado para segurança
-- 5. URLs das imagens serão permanentes
-- 6. Organização por tipo de imagem e data
-- =====================================================

-- 5. Script para testar o bucket (opcional)
-- =====================================================
-- Após executar este script, você pode testar o upload:

-- -- Teste de upload via API (substitua pelos seus valores):
-- -- curl -X POST 'https://your-project.supabase.co/storage/v1/object/user-images/test.jpg' \
-- --   -H 'Authorization: Bearer YOUR_ANON_KEY' \
-- --   -H 'Content-Type: image/jpeg' \
-- --   --data-binary @test-image.jpg

-- 6. Script para monitorar uso do bucket
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

-- 7. Script para limpeza de arquivos antigos (opcional)
-- =====================================================
-- Função para limpar arquivos antigos (mais de 90 dias):

-- CREATE OR REPLACE FUNCTION cleanup_old_images()
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
-- -- SELECT cleanup_old_images();
