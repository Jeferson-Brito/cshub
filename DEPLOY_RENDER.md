# 🚀 Guia de Deploy no Render

Este guia vai te ajudar a fazer o deploy do projeto CSHub no Render e configurar o banco de dados PostgreSQL.

## 📋 Pré-requisitos

1. Conta no Render (gratuita): https://render.com
2. Conta no GitHub (gratuita): https://github.com
3. Projeto já commitado no GitHub

---

## 🔧 Passo 1: Preparar o Projeto no GitHub

### 1.1. Verificar se o projeto está no GitHub

```bash
# Verificar se há um repositório remoto
git remote -v
```

Se não houver, crie um repositório no GitHub e adicione:

```bash
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git branch -M main
git push -u origin main
```

### 1.2. Fazer commit de todas as alterações

```bash
git add .
git commit -m "Preparar para deploy no Render"
git push origin main
```

---

## 🗄️ Passo 2: Criar Banco de Dados Postgres no Render

### 2.1. Acessar o Render

1. Acesse https://dashboard.render.com
2. Faça login com sua conta

### 2.2. Criar Novo Banco de Dados

1. Clique em **"+ New"** no canto superior direito
2. Selecione **"Postgres"** (aparece no menu dropdown)
3. Preencha os campos:
   - **Name**: `cshub-db` (ou outro nome de sua escolha)
   - **Database**: `cshub` (ou outro nome)
   - **User**: Deixe o padrão ou escolha um nome
   - **Region**: Escolha a região mais próxima (ex: `South America (São Paulo)`)
   - **PostgreSQL Version**: Deixe a versão mais recente
   - **Plan**: Escolha **Free** (gratuito)

4. Clique em **"Create Database"**

### 2.3. Anotar as Credenciais

Após criar o banco, você verá as informações de conexão:

1. **Internal Database URL**: Esta é a URL que você deve usar! Ela tem o formato:
   ```
   postgresql://usuario:senha@host:5432/database
   ```
   ⚠️ **COPIE ESTA URL COMPLETA** - você vai usar como `DATABASE_URL`

2. **Outras informações** (caso precise):
   - **Host**: Ex: `dpg-xxxxx-a.singapore-postgres.render.com`
   - **Port**: `5432`
   - **Database**: O nome do banco que você escolheu
   - **User**: O usuário que você escolheu
   - **Password**: A senha gerada (ANOTE BEM!)

⚠️ **IMPORTANTE**: 
- Anote a senha! Ela só aparece uma vez
- Use a **Internal Database URL** (não a External)

---

## 🌐 Passo 3: Criar Web Service no Render

### 3.1. Criar Novo Web Service

1. No dashboard do Render, clique em **"+ New"**
2. Selecione **"Web Service"**
3. Conecte seu repositório GitHub:
   - Se for a primeira vez, autorize o Render a acessar seu GitHub
   - Selecione o repositório `gestao_reclame_aqui`
   - Selecione a branch `main`

### 3.2. Configurar o Web Service

Preencha os campos:

- **Name**: `cshub` (ou outro nome)
- **Region**: Escolha a mesma região do banco de dados
- **Branch**: `main`
- **Root Directory**: Deixe em branco (ou `.` se necessário)
- **Environment**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt && python manage.py collectstatic --noinput
  ```
- **Start Command**: 
  ```
  gunicorn gestao_reclame_aqui.wsgi:application --config gunicorn_config.py
  ```
  
  Ou se preferir sem arquivo de config:
  ```
  gunicorn gestao_reclame_aqui.wsgi:application --timeout 120 --workers 2
  ```
- **Plan**: Escolha **Free** (gratuito)

### 3.3. Configurar Variáveis de Ambiente

Na seção **"Environment Variables"**, adicione as seguintes variáveis:

#### Variáveis Obrigatórias:

| Key | Value | Descrição |
|-----|-------|-----------|
| `SECRET_KEY` | `sua-chave-secreta-aqui` | Gere uma chave secreta Django (veja abaixo) |
| `DEBUG` | `False` | Desativa modo debug em produção |
| `ALLOWED_HOSTS` | `seu-app.onrender.com` | Substitua pelo domínio do seu app |
| `DATABASE_URL` | `postgresql://user:password@host:port/database` | URL completa do banco (veja abaixo) |

#### Como obter os valores:

**1. SECRET_KEY:**
Execute no terminal local:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**2. DATABASE_URL:**
No Render, vá até seu banco de dados Postgres e copie a **"Internal Database URL"**. 
- Ela já vem completa e pronta para usar
- Formato: `postgresql://usuario:senha@host:5432/database`
- Cole o valor completo no campo `DATABASE_URL`

**3. ALLOWED_HOSTS:**
Após criar o web service, você receberá uma URL como `cshub-xxxxx.onrender.com`. Use essa URL.

#### Variáveis Opcionais (mas recomendadas):

| Key | Value | Descrição |
|-----|-------|-----------|
| `INIT_DB` | `true` | Executa migrações automaticamente na primeira vez |

### 3.4. Criar o Web Service

Clique em **"Create Web Service"**

---

## 🔄 Passo 4: Executar Migrações

### 4.1. Via Shell do Render (Recomendado)

1. No dashboard do Render, vá até seu Web Service
2. Clique na aba **"Shell"**
3. Execute os comandos:

```bash
python manage.py migrate
python manage.py create_admin_user
```

### 4.2. Ou via Variável de Ambiente

Se você adicionou `INIT_DB=true`, as migrações serão executadas automaticamente na primeira inicialização.

---

## ✅ Passo 5: Verificar o Deploy

1. Aguarde o build completar (pode levar alguns minutos)
2. Acesse a URL do seu app (ex: `https://cshub-xxxxx.onrender.com`)
3. Faça login com as credenciais do admin criado

---

## 🔄 Passo 6: Migrar Dados do Banco Local (Opcional)

Se você quiser migrar os dados do banco local para o Render:

### 6.1. Exportar Dados Locais

No seu computador local:

```bash
# Ativar ambiente virtual
venv\Scripts\activate

# Exportar dados
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > backup.json
```

### 6.2. Importar no Render

1. No Render, vá até o Shell do seu Web Service
2. Faça upload do arquivo `backup.json` (ou copie o conteúdo)
3. Execute:

```bash
python manage.py loaddata backup.json
```

---

## 🛠️ Solução de Problemas

### Erro: "Database connection failed"

- Verifique se a `DATABASE_URL` está correta
- Certifique-se de usar a **Internal Database URL** (não a External)
- Verifique se o banco de dados está ativo no Render

### Erro: "Static files not found"

- Certifique-se de que o `collectstatic` está no build command
- Verifique se o `whitenoise` está no `requirements.txt`

### Erro: "Application error"

- Verifique os logs no Render (aba "Logs")
- Certifique-se de que `DEBUG=False` em produção
- Verifique se todas as variáveis de ambiente estão configuradas

### Site não carrega CSS/JS

- Verifique se `DEBUG=False` está configurado
- Certifique-se de que o `collectstatic` foi executado
- Verifique se o `whitenoise` está configurado no `settings.py`

---

## 📝 Checklist Final

- [ ] Projeto commitado no GitHub
- [ ] Banco de dados Postgres criado no Render
- [ ] Internal Database URL copiada
- [ ] Web Service criado no Render
- [ ] Variáveis de ambiente configuradas
- [ ] Migrações executadas
- [ ] Usuário admin criado
- [ ] Site acessível e funcionando
- [ ] Dados migrados (se necessário)

---

## 🎉 Pronto!

Seu projeto está no ar! Compartilhe a URL com sua equipe.

**Lembre-se:**
- O plano Free do Render pode "adormecer" após 15 minutos de inatividade
- O primeiro acesso após dormir pode levar alguns segundos para "acordar"
- Para produção, considere um plano pago para melhor performance

---

## 📞 Suporte

Se tiver problemas, verifique:
1. Logs do Render (aba "Logs" no dashboard)
2. Logs do build (aba "Events")
3. Configurações das variáveis de ambiente

