-- =====================================================
-- RECRIAÇÃO DA TABELA MESSAGES - HISTÓRICO DE CHAT
-- =====================================================

-- Esta tabela armazena o histórico de mensagens dos usuários
-- É essencial para o funcionamento do sistema de memória

-- 1. Cria a tabela messages
-- =====================================================
CREATE TABLE IF NOT EXISTS messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    phone VARCHAR(50) NOT NULL, -- Número do telefone do usuário
    body TEXT NOT NULL, -- Conteúdo da mensagem
    direction VARCHAR(20) NOT NULL CHECK (direction IN ('inbound', 'outbound')), -- Direção da mensagem
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- Timestamp de criação
    
    -- Índices para consultas eficientes
    CONSTRAINT messages_phone_check CHECK (phone IS NOT NULL AND phone != ''),
    CONSTRAINT messages_body_check CHECK (body IS NOT NULL AND body != ''),
    CONSTRAINT messages_direction_check CHECK (direction IN ('inbound', 'outbound'))
);

-- 2. Cria índices para otimizar consultas
-- =====================================================

-- Índice para buscar mensagens por telefone
CREATE INDEX IF NOT EXISTS idx_messages_phone ON messages(phone);

-- Índice para buscar mensagens por telefone e timestamp (histórico)
CREATE INDEX IF NOT EXISTS idx_messages_phone_created_at ON messages(phone, created_at DESC);

-- Índice para buscar mensagens por direção
CREATE INDEX IF NOT EXISTS idx_messages_direction ON messages(direction);

-- Índice para buscar mensagens por timestamp (análises temporais)
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);

-- 3. Cria política de Row Level Security (RLS) se necessário
-- =====================================================
-- Descomente as linhas abaixo se quiser habilitar RLS

-- ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- -- Política para permitir inserção de mensagens
-- CREATE POLICY "Allow message insertion" ON messages
--     FOR INSERT WITH CHECK (true);

-- -- Política para permitir leitura de mensagens (ajuste conforme necessário)
-- CREATE POLICY "Allow message reading" ON messages
--     FOR SELECT USING (true);

-- 4. Comentários para documentação
-- =====================================================
COMMENT ON TABLE messages IS 'Tabela para armazenar histórico de mensagens dos usuários';
COMMENT ON COLUMN messages.phone IS 'Número do telefone do usuário';
COMMENT ON COLUMN messages.body IS 'Conteúdo da mensagem';
COMMENT ON COLUMN messages.direction IS 'Direção da mensagem: inbound (recebida) ou outbound (enviada)';
COMMENT ON COLUMN messages.created_at IS 'Timestamp de quando a mensagem foi criada';

-- 5. Verifica se a tabela foi criada corretamente
-- =====================================================
-- Execute esta consulta para verificar se a tabela foi criada:

-- SELECT 
--     table_name,
--     column_name,
--     data_type,
--     is_nullable,
--     column_default
-- FROM information_schema.columns 
-- WHERE table_name = 'messages' 
-- ORDER BY ordinal_position;

-- =====================================================
-- NOTAS IMPORTANTES:
-- =====================================================
-- 1. Esta tabela é essencial para o funcionamento do sistema
-- 2. Armazena histórico de conversas dos usuários
-- 3. Usada pelo MemoryManager para recuperar contexto
-- 4. Não deve ser removida (diferente da tabela observability_logs)
-- 5. Considere implementar limpeza automática de mensagens antigas
-- =====================================================

-- 6. Script opcional para limpeza de mensagens antigas
-- =====================================================
-- Descomente e ajuste conforme necessário para limpar mensagens antigas

-- CREATE OR REPLACE FUNCTION cleanup_old_messages()
-- RETURNS void AS $$
-- BEGIN
--     -- Remove mensagens mais antigas que 90 dias
--     DELETE FROM messages 
--     WHERE created_at < NOW() - INTERVAL '90 days';
--     
--     -- Log da limpeza
--     RAISE NOTICE 'Mensagens antigas removidas: %', ROW_COUNT;
-- END;
-- $$ LANGUAGE plpgsql;

-- -- Para executar a limpeza manualmente:
-- -- SELECT cleanup_old_messages();

-- -- Para agendar limpeza automática (requer pg_cron):
-- -- SELECT cron.schedule('cleanup-messages', '0 2 * * *', 'SELECT cleanup_old_messages();');
