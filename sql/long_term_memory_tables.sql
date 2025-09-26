-- =====================================================
-- TABELAS PARA MEMÓRIA DE LONGO PRAZO - BODYFLOW.AI
-- =====================================================

-- 1. USER_PROFILE (Snapshot atual do usuário)
-- =====================================================
CREATE TABLE IF NOT EXISTS user_profile (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL UNIQUE, -- phone number ou customer_id
    name VARCHAR(100),
    age INTEGER,
    height_cm DECIMAL(5,2),
    current_weight_kg DECIMAL(5,2),
    current_body_fat_percent DECIMAL(4,2),
    current_muscle_mass_kg DECIMAL(5,2),
    goal VARCHAR(50), -- 'emagrecimento', 'hipertrofia', 'condicionamento', 'manutencao'
    restrictions JSONB DEFAULT '{}', -- alergias, intolerâncias, preferências
    training_level VARCHAR(20), -- 'iniciante', 'intermediario', 'avancado'
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. USER_BIOIMPEDANCE (Histórico completo de bioimpedância)
-- =====================================================
CREATE TABLE IF NOT EXISTS user_bioimpedance (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL, -- Data quando a bioimpedância foi realizada
    weight_kg DECIMAL(5,2),
    body_fat_percent DECIMAL(4,2),
    muscle_mass_kg DECIMAL(5,2),
    visceral_fat_level INTEGER,
    basal_metabolic_rate INTEGER,
    hydration_percent DECIMAL(4,2),
    bone_mass_kg DECIMAL(5,2),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices para consultas eficientes
    CONSTRAINT fk_user_bioimpedance_user FOREIGN KEY (user_id) REFERENCES user_profile(user_id) ON DELETE CASCADE
);

-- 3. USER_TRAINING_HISTORY (Histórico de treinos)
-- =====================================================
CREATE TABLE IF NOT EXISTS user_training_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL, -- Data quando o treino foi feito
    routine JSONB NOT NULL, -- {exercicios: [{nome, series, reps, peso, duracao}]}
    duration_minutes INTEGER,
    intensity_level VARCHAR(20), -- 'baixa', 'moderada', 'alta'
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_user_training_user FOREIGN KEY (user_id) REFERENCES user_profile(user_id) ON DELETE CASCADE
);

-- 4. USER_DIET_HISTORY (Histórico de planos alimentares)
-- =====================================================
CREATE TABLE IF NOT EXISTS user_diet_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL, -- Data quando o plano foi criado/seguido
    diet_plan JSONB NOT NULL, -- {refeicoes: [{nome, horario, alimentos, macros}]}
    adherence_percent DECIMAL(4,2) DEFAULT 0, -- % de aderência ao plano
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_user_diet_user FOREIGN KEY (user_id) REFERENCES user_profile(user_id) ON DELETE CASCADE
);

-- 5. USER_MEALS (Refeições com fotos e análise)
-- =====================================================
CREATE TABLE IF NOT EXISTS user_meals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL, -- Data quando a refeição aconteceu
    image_url TEXT, -- URL da imagem no Supabase Storage
    description TEXT,
    calories INTEGER,
    macros JSONB DEFAULT '{}', -- {protein: X, carbs: Y, fat: Z}
    items JSONB DEFAULT '[]', -- Lista de alimentos detectados
    source VARCHAR(20) DEFAULT 'user_uploaded', -- 'user_uploaded' ou 'analyzed_by_agent'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_user_meals_user FOREIGN KEY (user_id) REFERENCES user_profile(user_id) ON DELETE CASCADE
);

-- =====================================================
-- ÍNDICES PARA PERFORMANCE
-- =====================================================

-- Índices para consultas por usuário e data
CREATE INDEX IF NOT EXISTS idx_user_bioimpedance_user_date ON user_bioimpedance(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_user_training_user_date ON user_training_history(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_user_diet_user_date ON user_diet_history(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_user_meals_user_date ON user_meals(user_id, date DESC);

-- Índices para consultas temporais
CREATE INDEX IF NOT EXISTS idx_user_bioimpedance_date ON user_bioimpedance(date DESC);
CREATE INDEX IF NOT EXISTS idx_user_training_date ON user_training_history(date DESC);
CREATE INDEX IF NOT EXISTS idx_user_diet_date ON user_diet_history(date DESC);
CREATE INDEX IF NOT EXISTS idx_user_meals_date ON user_meals(date DESC);

-- =====================================================
-- TRIGGERS PARA SINCRONIZAÇÃO AUTOMÁTICA
-- =====================================================

-- Função para atualizar snapshot do perfil quando bioimpedância é inserida
CREATE OR REPLACE FUNCTION update_profile_from_bioimpedance()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE user_profile 
    SET 
        current_weight_kg = NEW.weight_kg,
        current_body_fat_percent = NEW.body_fat_percent,
        current_muscle_mass_kg = NEW.muscle_mass_kg,
        updated_at = NOW()
    WHERE user_id = NEW.user_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para bioimpedância
DROP TRIGGER IF EXISTS trigger_update_profile_bioimpedance ON user_bioimpedance;
CREATE TRIGGER trigger_update_profile_bioimpedance
    AFTER INSERT ON user_bioimpedance
    FOR EACH ROW
    EXECUTE FUNCTION update_profile_from_bioimpedance();

-- =====================================================
-- VIEWS PARA CONSULTAS COMUNS
-- =====================================================

-- View para evolução do usuário (últimos 30 dias)
CREATE OR REPLACE VIEW user_evolution_30d AS
SELECT 
    up.user_id,
    up.name,
    up.current_weight_kg,
    up.current_body_fat_percent,
    up.current_muscle_mass_kg,
    up.goal,
    up.training_level,
    -- Última bioimpedância
    (SELECT date FROM user_bioimpedance ub WHERE ub.user_id = up.user_id ORDER BY date DESC LIMIT 1) as last_bioimpedance_date,
    -- Estatísticas dos últimos 30 dias
    (SELECT COUNT(*) FROM user_training_history uth WHERE uth.user_id = up.user_id AND uth.date >= CURRENT_DATE - INTERVAL '30 days') as training_sessions_30d,
    (SELECT AVG(adherence_percent) FROM user_diet_history udh WHERE udh.user_id = up.user_id AND udh.date >= CURRENT_DATE - INTERVAL '30 days') as avg_diet_adherence_30d,
    (SELECT SUM(calories) FROM user_meals um WHERE um.user_id = up.user_id AND um.date >= CURRENT_DATE - INTERVAL '30 days') as total_calories_30d,
    (SELECT COUNT(*) FROM user_meals um WHERE um.user_id = up.user_id AND um.date >= CURRENT_DATE - INTERVAL '30 days') as meals_logged_30d
FROM user_profile up;

-- View para resumo semanal
CREATE OR REPLACE VIEW user_weekly_summary AS
SELECT 
    up.user_id,
    up.name,
    DATE_TRUNC('week', CURRENT_DATE) as week_start,
    -- Treinos da semana
    (SELECT COUNT(*) FROM user_training_history uth 
     WHERE uth.user_id = up.user_id 
     AND uth.date >= DATE_TRUNC('week', CURRENT_DATE)) as weekly_training_sessions,
    -- Calorias da semana
    (SELECT SUM(calories) FROM user_meals um 
     WHERE um.user_id = up.user_id 
     AND um.date >= DATE_TRUNC('week', CURRENT_DATE)) as weekly_calories,
    -- Refeições logadas da semana
    (SELECT COUNT(*) FROM user_meals um 
     WHERE um.user_id = up.user_id 
     AND um.date >= DATE_TRUNC('week', CURRENT_DATE)) as weekly_meals_logged
FROM user_profile up;

-- =====================================================
-- POLÍTICAS RLS (Row Level Security)
-- =====================================================

-- Habilitar RLS em todas as tabelas
ALTER TABLE user_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_bioimpedance ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_training_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_diet_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_meals ENABLE ROW LEVEL SECURITY;

-- Políticas básicas (ajustar conforme necessário)
-- Por enquanto, permitir acesso total para desenvolvimento
-- Em produção, implementar políticas baseadas em user_id

-- =====================================================
-- COMENTÁRIOS PARA DOCUMENTAÇÃO
-- =====================================================

COMMENT ON TABLE user_profile IS 'Snapshot atual do perfil do usuário - sempre contém os dados mais recentes';
COMMENT ON TABLE user_bioimpedance IS 'Histórico completo de medições de bioimpedância';
COMMENT ON TABLE user_training_history IS 'Histórico de treinos realizados pelo usuário';
COMMENT ON TABLE user_diet_history IS 'Histórico de planos alimentares seguidos';
COMMENT ON TABLE user_meals IS 'Registro de refeições com fotos e análise nutricional';

COMMENT ON COLUMN user_profile.restrictions IS 'JSONB com alergias, intolerâncias e preferências alimentares';
COMMENT ON COLUMN user_training_history.routine IS 'JSONB com exercícios, séries, repetições e pesos';
COMMENT ON COLUMN user_diet_history.diet_plan IS 'JSONB com refeições, horários e macronutrientes';
COMMENT ON COLUMN user_meals.macros IS 'JSONB com proteína, carboidratos e gorduras';
COMMENT ON COLUMN user_meals.items IS 'JSONB com lista de alimentos identificados na imagem';


