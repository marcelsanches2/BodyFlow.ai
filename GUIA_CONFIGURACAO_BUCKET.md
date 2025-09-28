# =====================================================
# GUIA PASSO A PASSO - CONFIGURAR BUCKET DE IMAGENS
# =====================================================

## 🎯 PROBLEMA IDENTIFICADO
O bucket `user-images` não existe no Supabase Storage e há erro de permissão ao tentar criá-lo via código.

## 🔧 SOLUÇÃO: CRIAR BUCKET MANUALMENTE

### PASSO 1: Acesse o Supabase Dashboard
1. Vá para [supabase.com](https://supabase.com)
2. Faça login na sua conta
3. Selecione seu projeto BodyFlow

### PASSO 2: Acesse o SQL Editor
1. No menu lateral, clique em **"SQL Editor"**
2. Clique em **"New query"**

### PASSO 3: Execute o Script SQL
1. Copie e cole o conteúdo do arquivo `sql/create_bucket_simple.sql`
2. Clique em **"Run"** para executar

### PASSO 4: Verifique se o Bucket foi Criado
1. No menu lateral, clique em **"Storage"**
2. Você deve ver o bucket **"user-images"** na lista
3. Se aparecer, o bucket foi criado com sucesso!

### PASSO 5: Teste o Upload
Execute o teste simples:
```bash
python3 test_simple_upload.py
```

## 📋 SCRIPTS DISPONÍVEIS

### Script Simples (Recomendado)
- **Arquivo:** `sql/create_bucket_simple.sql`
- **Descrição:** Cria o bucket com configurações básicas
- **Uso:** Execute no SQL Editor do Supabase

### Script Completo (Alternativo)
- **Arquivo:** `sql/setup_image_storage_bucket.sql`
- **Descrição:** Configuração completa com limites e políticas avançadas
- **Uso:** Execute se quiser configurações mais detalhadas

## 🔍 VERIFICAÇÃO

Após executar o script, verifique:

1. **Bucket existe:** Storage → user-images aparece na lista
2. **Bucket é público:** Deve estar marcado como público
3. **Upload funciona:** Execute `python3 test_simple_upload.py`
4. **Imagem acessível:** URL retornada deve abrir a imagem

## ❌ PROBLEMAS COMUNS

### Erro: "new row violates row-level security policy"
- **Causa:** Permissões do Supabase muito restritivas
- **Solução:** Execute o script `sql/create_bucket_simple.sql` que tem políticas mais permissivas

### Erro: "Bucket not found"
- **Causa:** Bucket não foi criado
- **Solução:** Execute o script SQL no Supabase Dashboard

### Erro: "Unauthorized"
- **Causa:** Chaves de API incorretas ou permissões insuficientes
- **Solução:** Verifique as variáveis de ambiente no `.env.secrets`

## ✅ PRÓXIMOS PASSOS

Após criar o bucket com sucesso:

1. **Execute:** `python3 test_simple_upload.py`
2. **Se funcionar:** Sistema está pronto para receber imagens
3. **Se falhar:** Verifique os logs de erro e ajuste as permissões

## 📞 SUPORTE

Se continuar com problemas:
1. Verifique os logs do Supabase
2. Confirme se as chaves de API estão corretas
3. Teste com uma conta de administrador do Supabase
