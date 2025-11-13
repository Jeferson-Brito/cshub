# 🚀 Guia de Deploy - CSHub

Este guia irá ajudá-lo a colocar o CSHub em produção para que toda a equipe possa acessar.

## 📋 Opções de Hospedagem

### 1. **Render.com** (Recomendado - Gratuito)
- ✅ Plano gratuito disponível
- ✅ PostgreSQL gratuito incluído
- ✅ Deploy automático via GitHub
- ✅ HTTPS automático
- ✅ Fácil configuração

### 2. **Railway.app** (Alternativa)
- ✅ Plano gratuito com créditos
- ✅ PostgreSQL incluído
- ✅ Deploy via GitHub
- ✅ Interface moderna

### 3. **DigitalOcean** (Pago, mas barato)
- 💰 ~$5-12/mês
- ✅ Controle total
- ✅ PostgreSQL gerenciado disponível

### 4. **Heroku** (Pago)
- 💰 ~$7/mês (não tem mais plano gratuito)
- ✅ Fácil de usar
- ✅ PostgreSQL incluído

---

## 🎯 Deploy no Render.com (Passo a Passo)

### Passo 1: Preparar o Código

1. **Criar conta no GitHub** (se ainda não tiver):
   - Acesse: https://github.com
   - Crie uma conta gratuita

2. **Criar repositório no GitHub**:
   - Clique em "New repository"
   - Nome: `cshub` (ou outro nome)
   - Marque como **Private** (recomendado)
   - Clique em "Create repository"

3. **Enviar código para o GitHub**:
   ```bash
   # No terminal, dentro da pasta do projeto:
   git init
   git add .
   git commit -m "Initial commit - CSHub"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/cshub.git
   git push -u origin main
   ```

### Passo 2: Configurar no Render.com

1. **Criar conta no Render**:
   - Acesse: https://render.com
   - Clique em "Get Started for Free"
   - Faça login com GitHub

2. **Criar Banco de Dados PostgreSQL**:
   - No dashboard do Render, clique em "New +"
   - Selecione "PostgreSQL"
   - Nome: `cshub-db`
   - Plano: **Free** (ou Starter se precisar de mais recursos)
   - Região: Escolha a mais próxima (ex: São Paulo se disponível)
   - Clique em "Create Database"
   - ⚠️ **ANOTE** as credenciais do banco (aparecem na tela):
     - `Host`
     - `Port`
     - `Database`
     - `User`
     - `Password`

3. **Criar Web Service**:
   - No dashboard, clique em "New +"
   - Selecione "Web Service"
   - Conecte seu repositório GitHub
   - Selecione o repositório `cshub`
   - Configure:
     - **Name**: `cshub`
     - **Region**: Mesma região do banco
     - **Branch**: `main`
     - **Root Directory**: (deixe vazio)
     - **Runtime**: `Python 3`
     - **Build Command**: 
       ```bash
       pip install -r requirements.txt && python manage.py collectstatic --noinput
       ```
     - **Start Command**: 
       ```bash
       gunicorn gestao_reclame_aqui.wsgi:application
       ```

4. **Configurar Variáveis de Ambiente**:
   - Na página do Web Service, vá em "Environment"
   - Adicione as seguintes variáveis:
   
   ```
   SECRET_KEY=sua-chave-secreta-aqui-gerada-aleatoriamente
   DEBUG=False
   ALLOWED_HOSTS=seu-app.onrender.com
   
   DB_NAME=nome-do-banco
   DB_USER=usuario-do-banco
   DB_PASSWORD=senha-do-banco
   DB_HOST=host-do-banco
   DB_PORT=5432
   ```
   
   ⚠️ **IMPORTANTE**:
   - Substitua `seu-app.onrender.com` pelo domínio que o Render fornecer
   - Use as credenciais do banco que você anotou
   - Para gerar `SECRET_KEY`, execute no terminal:
     ```python
     python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
     ```

5. **Salvar e Deploy**:
   - Clique em "Create Web Service"
   - O Render começará a fazer o deploy automaticamente
   - Aguarde alguns minutos (primeira vez pode levar 5-10 minutos)

### Passo 3: Executar Migrações

Após o deploy inicial:

1. No dashboard do Render, vá para seu Web Service
2. Clique na aba "Shell"
3. Execute os comandos:
   ```bash
   python manage.py migrate
   python manage.py create_admin_user
   python manage.py create_sample_data  # Opcional - para dados de teste
   ```

### Passo 4: Acessar o Sistema

1. O Render fornecerá uma URL como: `https://cshub.onrender.com`
2. Acesse essa URL no navegador
3. Faça login com as credenciais do administrador:
   - Usuário: `jefersonbrito`
   - E-mail: `jeffersonbrito245@gmail.com`
   - Senha: `@Lionnees14`

---

## 🔧 Configurações Adicionais

### Atualizar ALLOWED_HOSTS

Após o deploy, você receberá uma URL do Render. Atualize a variável de ambiente:

```
ALLOWED_HOSTS=seu-app.onrender.com,www.seu-app.onrender.com
```

### Domínio Personalizado (Opcional)

Se quiser usar um domínio próprio (ex: `cshub.suaempresa.com`):

1. No Render, vá em "Settings" do Web Service
2. Role até "Custom Domains"
3. Adicione seu domínio
4. Configure o DNS conforme instruções do Render
5. Atualize `ALLOWED_HOSTS` com o novo domínio

---

## 🔄 Atualizações Futuras

Para atualizar o sistema:

1. Faça suas alterações no código local
2. Commit e push para o GitHub:
   ```bash
   git add .
   git commit -m "Descrição das alterações"
   git push
   ```
3. O Render detectará automaticamente e fará novo deploy

---

## 🛠️ Troubleshooting

### Erro: "DisallowedHost"
- Verifique se `ALLOWED_HOSTS` está configurado corretamente
- Certifique-se de incluir o domínio completo (com `https://` removido)

### Erro: "Database connection failed"
- Verifique as credenciais do banco nas variáveis de ambiente
- Certifique-se de que o banco está na mesma região do Web Service

### Erro: "Static files not found"
- Execute `python manage.py collectstatic` no Shell do Render
- Verifique se `whitenoise` está no `requirements.txt` (já está)

### Site lento na primeira requisição
- Normal no plano gratuito do Render
- O servidor "dorme" após 15 minutos de inatividade
- Primeira requisição após dormir pode levar 30-60 segundos

---

## 📊 Monitoramento

No dashboard do Render você pode:
- Ver logs em tempo real
- Monitorar uso de recursos
- Ver histórico de deploys
- Acessar o shell para comandos Django

---

## 🔐 Segurança

### Checklist de Segurança:

- ✅ `DEBUG=False` em produção
- ✅ `SECRET_KEY` único e seguro
- ✅ `ALLOWED_HOSTS` configurado
- ✅ HTTPS habilitado (automático no Render)
- ✅ Cookies seguros (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`)
- ✅ Senhas fortes para usuários

### Backup do Banco de Dados:

1. No Render, vá para seu banco PostgreSQL
2. Clique em "Backups"
3. Configure backups automáticos (disponível em planos pagos)
4. Para backup manual, use o shell:
   ```bash
   pg_dump -h host -U user -d database > backup.sql
   ```

---

## 💡 Dicas

1. **Plano Gratuito do Render**:
   - Serviço pode "dormir" após inatividade
   - Primeira requisição após dormir é mais lenta
   - Para evitar isso, considere o plano Starter ($7/mês)

2. **Performance**:
   - Use cache quando possível
   - Otimize consultas ao banco
   - Considere CDN para arquivos estáticos (Render já otimiza)

3. **Notificações**:
   - Configure alertas no Render para falhas de deploy
   - Configure e-mail para notificações importantes do sistema

---

## 📞 Suporte

- **Render Docs**: https://render.com/docs
- **Django Deploy**: https://docs.djangoproject.com/en/stable/howto/deployment/
- **GitHub Issues**: Para problemas específicos do código

---

## ✅ Checklist Final

Antes de considerar o deploy completo:

- [ ] Código enviado para GitHub
- [ ] Banco PostgreSQL criado no Render
- [ ] Web Service criado e configurado
- [ ] Variáveis de ambiente configuradas
- [ ] Migrações executadas
- [ ] Usuário administrador criado
- [ ] Teste de login realizado
- [ ] Teste de criação de reclamação
- [ ] Backup configurado (recomendado)
- [ ] Equipe informada sobre acesso

---

**Pronto! Seu sistema está no ar! 🎉**

