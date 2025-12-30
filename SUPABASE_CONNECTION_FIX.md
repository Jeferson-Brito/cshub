# 🔧 Como Corrigir Erro de Conexão com Supabase no Render

## ❌ Problema

Ao tentar fazer login no sistema CSHub deployado no Render, aparece o erro:
```
psycopg.OperationalError: [Errno -2] Name or service not known
```

## ✅ Solução

O problema está na configuração da variável de ambiente no Render. Siga os passos abaixo:

---

## 📋 Passo a Passo

### 1️⃣ Obter a String de Conexão do Supabase

1. Acesse o [painel do Supabase](https://supabase.com/dashboard)
2. Selecione seu projeto
3. No menu lateral, clique em **"Project Settings"** (ícone de engrenagem)
4. Clique em **"Database"**
5. Role até a seção **"Connection string"**
6. Selecione a aba **"Transaction pooler"** (Modo Session)
7. Copie a URI completa que começa com `postgresql://`

A URI terá este formato:
```
postgresql://postgres.budxgfflbfcxsxyoceti:[PASSWORD]@aws-0-south-america-east-1.pooler.supabase.com:6543/postgres
```

> **⚠️ IMPORTANTE**: Substitua `[PASSWORD]` pela sua senha do banco de dados Supabase!

---

### 2️⃣ Configurar no Render

1. Acesse o [painel do Render](https://dashboard.render.com/)
2. Selecione seu serviço **cshub-l8jg**
3. No menu lateral, clique em **"Environment"**
4. Procure pela variável **`DATABASE_URL`**:
   - **Se já existir**: Clique em editar e cole a URI do Supabase
   - **Se NÃO existir**: Clique em **"Add Environment Variable"**
     - **Key**: `DATABASE_URL`
     - **Value**: Cole a URI completa do Supabase

5. **Remova as variáveis individuais** (se existirem) para evitar conflitos:
   - `DB_HOST`
   - `DB_PORT`
   - `DB_NAME`
   - `DB_USER`
   - `DB_PASSWORD`

6. Clique em **"Save Changes"**

---

### 3️⃣ Reiniciar o Serviço

1. No topo da página do seu serviço no Render, clique em **"Manual Deploy"**
2. Selecione **"Clear build cache & deploy"**
3. Aguarde o deploy finalizar (1-3 minutos)

---

### 4️⃣ Verificar se Funcionou

1. Acesse seu site: https://cshub-l8jg.onrender.com/
2. Tente fazer login
3. Verifique os logs no Render:
   - Deve aparecer: `✓ Usando DATABASE_URL`
   - **NÃO** deve mais aparecer o erro `Name or service not known`

---

## 🔍 Exemplo de Variável Correta

```env
DATABASE_URL=postgresql://postgres.budxgfflbfcxsxyoceti:SUA_SENHA_AQUI@aws-0-south-america-east-1.pooler.supabase.com:6543/postgres
```

---

## ❓ Ainda com Problemas?

Se o erro persistir, verifique:
1. ✅ A senha do Supabase está correta na URL
2. ✅ O IP do Render está liberado no Supabase (geralmente automático)
3. ✅ A variável `DATABASE_URL` não tem espaços extras
4. ✅ Outras variáveis de banco foram removidas (`DB_HOST`, etc.)

---

## 📝 Notas Técnicas

- **Porta 6543**: Transaction Pooler (recomendado para Render)
- **Porta 5432**: Conexão direta (não recomendado)
- O Render automaticamente adiciona `?sslmode=require` quando necessário
