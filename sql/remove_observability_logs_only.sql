-- =====================================================
-- REMOÇÃO DA TABELA OBSERVABILITY_LOGS - MIGRAÇÃO PARA SUPABASE LOGS
-- =====================================================

-- ATENÇÃO: Execute este script APENAS após confirmar que a migração
-- para Supabase Logs está funcionando corretamente!

-- 1. Remove apenas a tabela de logs de observabilidade
-- =====================================================
DROP TABLE IF EXISTS observability_logs CASCADE;

-- 2. Verifica se a tabela foi removida
-- =====================================================
-- Execute esta consulta para confirmar a remoção:

-- SELECT table_name 
-- FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- AND table_name = 'observability_logs';

-- Se não retornar nenhuma linha, a tabela foi removida com sucesso.

-- 3. Verifica se a tabela messages ainda existe (deve existir)
-- =====================================================
-- Execute esta consulta para confirmar que messages ainda existe:

-- SELECT table_name 
-- FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- AND table_name = 'messages';

-- Deve retornar uma linha com 'messages'.

-- =====================================================
-- NOTAS IMPORTANTES:
-- =====================================================
-- 1. Esta migração move apenas logs de observabilidade para Supabase Logs
-- 2. A tabela 'messages' é MANTIDA para histórico de chat
-- 3. Os logs de observabilidade agora são capturados automaticamente pelo Supabase
-- 4. Acesse o painel do Supabase para visualizar os logs de observabilidade
-- 5. Configure Log Drains se precisar exportar logs para sistemas externos
-- 6. Esta mudança melhora a performance e reduz o uso do banco de dados
-- =====================================================

-- 4. Script para verificar o status das tabelas
-- =====================================================
-- Execute este script para verificar o status atual:

-- SELECT 
--     table_name,
--     CASE 
--         WHEN table_name = 'messages' THEN '✅ MANTIDA - Histórico de chat'
--         WHEN table_name = 'observability_logs' THEN '❌ REMOVIDA - Migrada para Supabase Logs'
--         ELSE '📋 OUTRAS TABELAS'
--     END as status
-- FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- AND table_name IN ('messages', 'observability_logs')
-- ORDER BY table_name;
