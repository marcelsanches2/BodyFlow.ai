-- Script para criar tabelas necessárias no Supabase
-- Execute este script no SQL Editor do Supabase

-- Tabela de sessões
CREATE TABLE IF NOT EXISTS sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    active BOOLEAN DEFAULT true,
    summary TEXT DEFAULT '',
    active_topic VARCHAR(100) DEFAULT '',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_interaction_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions(active);
CREATE INDEX IF NOT EXISTS idx_sessions_last_interaction ON sessions(last_interaction_at);

-- Tabela de logs de observabilidade
CREATE TABLE IF NOT EXISTS observability_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    log_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_observability_logs_created_at ON observability_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_observability_logs_data ON observability_logs USING GIN(log_data);

-- Tabela de mapeamento de canais (Telegram/WhatsApp)
CREATE TABLE IF NOT EXISTS user_channels (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    channel_type VARCHAR(20) NOT NULL CHECK (channel_type IN ('telegram', 'whatsapp')),
    channel_id VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(channel_type, channel_id)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_user_channels_customer_id ON user_channels(customer_id);
CREATE INDEX IF NOT EXISTS idx_user_channels_channel_type ON user_channels(channel_type);
CREATE INDEX IF NOT EXISTS idx_user_channels_channel_id ON user_channels(channel_id);
CREATE INDEX IF NOT EXISTS idx_user_channels_phone ON user_channels(phone_number);
CREATE INDEX IF NOT EXISTS idx_user_channels_active ON user_channels(is_active);

-- Atualizar tabela customers para suportar perfil JSON e validação de telefone
ALTER TABLE customers 
ADD COLUMN IF NOT EXISTS profile JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS last_profile_update TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS phone_validated_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS phone_last_used_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS phone_validation_source VARCHAR(20) DEFAULT 'telegram' CHECK (phone_validation_source IN ('telegram', 'whatsapp')),
ADD COLUMN IF NOT EXISTS telegram_chat_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS telegram_user_id VARCHAR(50);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_customers_profile ON customers USING GIN(profile);
CREATE INDEX IF NOT EXISTS idx_customers_onboarding ON customers(onboarding_completed);
CREATE INDEX IF NOT EXISTS idx_customers_phone_validated ON customers(phone_validated_at);
CREATE INDEX IF NOT EXISTS idx_customers_phone_last_used ON customers(phone_last_used_at);
CREATE INDEX IF NOT EXISTS idx_customers_telegram_chat ON customers(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_customers_telegram_user ON customers(telegram_user_id);

-- Comentários para documentação
COMMENT ON TABLE sessions IS 'Controle de sessões de usuários com timeout';
COMMENT ON TABLE observability_logs IS 'Logs de telemetria e observabilidade do sistema ADK';
COMMENT ON TABLE user_channels IS 'Mapeamento de usuários entre canais (Telegram/WhatsApp)';
COMMENT ON COLUMN user_channels.channel_type IS 'Tipo de canal: telegram ou whatsapp';
COMMENT ON COLUMN user_channels.channel_id IS 'ID único do canal (Telegram ID ou WhatsApp number)';
COMMENT ON COLUMN user_channels.phone_number IS 'Número de telefone normalizado para ambos os canais';
COMMENT ON COLUMN customers.profile IS 'Perfil completo do usuário em formato JSON';
COMMENT ON COLUMN customers.onboarding_completed IS 'Flag indicando se o onboarding foi completado';
COMMENT ON COLUMN customers.last_profile_update IS 'Timestamp da última atualização do perfil';
