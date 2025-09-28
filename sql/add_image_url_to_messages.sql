-- =====================================================
-- ADICIONAR CAMPO IMAGE_URL NA TABELA MESSAGES
-- =====================================================

-- Este script adiciona um campo para armazenar URLs de imagens
-- enviadas pelos usuários na tabela messages

-- 1. Adiciona o campo image_url na tabela messages
-- =====================================================
ALTER TABLE messages 
ADD COLUMN IF NOT EXISTS image_url TEXT;

-- 2. Adiciona comentário para documentação
-- =====================================================
COMMENT ON COLUMN messages.image_url IS 'URL da imagem armazenada no Supabase Storage (se aplicável)';

-- 3. Cria índice para consultas eficientes por imagem
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_messages_image_url ON messages(image_url) WHERE image_url IS NOT NULL;

-- 4. Cria índice composto para buscar mensagens com imagens por usuário
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_messages_phone_image_url ON messages(phone, image_url) WHERE image_url IS NOT NULL;

-- 5. Adiciona constraint para validar formato de URL (opcional)
-- =====================================================
-- Descomente se quiser validar formato de URL:
-- ALTER TABLE messages 
-- ADD CONSTRAINT messages_image_url_format 
-- CHECK (image_url IS NULL OR image_url ~ '^https?://.*\.supabase\.co/storage/v1/object/public/.*');

-- 6. Verifica se a alteração foi aplicada
-- =====================================================
-- Execute esta consulta para verificar se o campo foi adicionado:

-- SELECT 
--     column_name,
--     data_type,
--     is_nullable,
--     column_default
-- FROM information_schema.columns 
-- WHERE table_name = 'messages' 
-- AND column_name = 'image_url';

-- Deve retornar uma linha com o campo image_url.

-- 7. Exemplo de consulta para buscar mensagens com imagens
-- =====================================================
-- Buscar todas as mensagens com imagens de um usuário:
-- SELECT 
--     phone,
--     body,
--     image_url,
--     direction,
--     created_at
-- FROM messages 
-- WHERE phone = 'seu_telefone_aqui'
-- AND image_url IS NOT NULL
-- ORDER BY created_at DESC;

-- Buscar estatísticas de imagens por usuário:
-- SELECT 
--     phone,
--     COUNT(*) as total_messages,
--     COUNT(image_url) as messages_with_images,
--     ROUND(COUNT(image_url) * 100.0 / COUNT(*), 2) as image_percentage
-- FROM messages 
-- GROUP BY phone
-- ORDER BY messages_with_images DESC;

-- =====================================================
-- NOTAS IMPORTANTES:
-- =====================================================
-- 1. O campo image_url é opcional (pode ser NULL)
-- 2. Armazena URLs públicas do Supabase Storage
-- 3. Permite visualizar imagens enviadas pelos usuários
-- 4. Facilita análise de uso de imagens por usuário
-- 5. Mantém histórico completo de interações
-- 6. URLs são permanentes enquanto a imagem existir no storage
-- =====================================================

-- 8. Script para migrar dados existentes (se necessário)
-- =====================================================
-- Se você tiver dados existentes que precisam ser migrados:

-- -- Exemplo: Atualizar mensagens existentes com URLs de imagens
-- -- (ajuste conforme sua lógica de negócio)
-- UPDATE messages 
-- SET image_url = 'https://exemplo.supabase.co/storage/v1/object/public/user-images/exemplo.jpg'
-- WHERE phone = 'telefone_exemplo'
-- AND body LIKE '%imagem%'
-- AND image_url IS NULL;

-- 9. Script para limpeza de imagens órfãs (opcional)
-- =====================================================
-- Função para encontrar mensagens com URLs de imagens que não existem mais:

-- CREATE OR REPLACE FUNCTION find_orphaned_image_urls()
-- RETURNS TABLE(phone TEXT, image_url TEXT, created_at TIMESTAMP WITH TIME ZONE) AS $$
-- BEGIN
--     RETURN QUERY
--     SELECT m.phone, m.image_url, m.created_at
--     FROM messages m
--     WHERE m.image_url IS NOT NULL
--     AND m.created_at < NOW() - INTERVAL '30 days'  -- Imagens mais antigas que 30 dias
--     ORDER BY m.created_at DESC;
-- END;
-- $$ LANGUAGE plpgsql;

-- -- Para executar:
-- -- SELECT * FROM find_orphaned_image_urls();
