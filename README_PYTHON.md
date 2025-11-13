# Gestão Reclame Aqui - Python/Django

Aplicação web completa para Gestão de Reclamações desenvolvida em **Python com Django** e PostgreSQL.

## ✅ Vantagens desta versão

- ✅ **Mais simples** - Python é mais fácil que Ruby
- ✅ **Menos dependências** - Instalação mais rápida
- ✅ **Documentação melhor** - Django tem excelente documentação
- ✅ **Admin integrado** - Painel administrativo automático
- ✅ **ORM poderoso** - Fácil trabalhar com banco de dados

## 🚀 Instalação Rápida

### 1. Instalar Python

1. Baixe Python 3.11 ou superior: **https://www.python.org/downloads/**
2. Durante a instalação, **MARQUE** "Add Python to PATH"
3. Instale

### 2. Instalar dependências

**Opção 1 - Script automático:**
- Clique duas vezes em: `INSTALAR_PYTHON.bat`

**Opção 2 - Manual:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar banco de dados

Crie/edite o arquivo `.env` na raiz do projeto:

```
DB_NAME=gestao_reclame_aqui
DB_USER=postgres
DB_PASSWORD=@Lionnees14
DB_HOST=localhost
DB_PORT=5433
SECRET_KEY=django-insecure-change-me-in-production
```

### 4. Criar banco de dados

**Opção 1 - Script automático:**
- Clique duas vezes em: `CONFIGURAR_BANCO_PYTHON.bat`

**Opção 2 - Manual:**
```bash
venv\Scripts\activate
python manage.py makemigrations
python manage.py migrate
```

### 5. Criar usuário administrador

```bash
python manage.py createsuperuser
```

Siga as instruções para criar um usuário.

### 6. Criar dados de exemplo

```bash
python manage.py create_sample_data
```

Isso cria:
- 1 gestor (gestor / 123456)
- 2 analistas (analista1 / 123456, analista2 / 123456)
- 50 reclamações de exemplo

### 7. Iniciar servidor

**Opção 1 - Script automático:**
- Clique duas vezes em: `INICIAR_PYTHON.bat`

**Opção 2 - Manual:**
```bash
venv\Scripts\activate
python manage.py runserver
```

### 8. Acessar

Abra no navegador: **http://localhost:8000**

**Login padrão:**
- Usuário: `gestor`
- Senha: `123456`

## 📋 Comandos Úteis

```bash
# Ativar ambiente virtual
venv\Scripts\activate

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Criar dados de exemplo
python manage.py create_sample_data

# Iniciar servidor
python manage.py runserver

# Acessar admin
# http://localhost:8000/admin
```

## 🎯 Funcionalidades

- ✅ Autenticação e autorização
- ✅ CRUD completo de reclamações
- ✅ Dashboard com estatísticas
- ✅ Filtros e busca
- ✅ Histórico de atividades
- ✅ Painel administrativo (Django Admin)
- ✅ Interface responsiva

## 🆘 Problemas Comuns

### Erro: "python: comando não encontrado"
- Instale o Python e marque "Add Python to PATH"
- Reinicie o PowerShell

### Erro: "pip: comando não encontrado"
- O Python não foi instalado corretamente
- Reinstale o Python

### Erro de conexão com banco
- Verifique se o PostgreSQL está rodando
- Verifique o arquivo `.env`
- Teste a conexão no pgAdmin

### Erro ao ativar venv
- Certifique-se de estar na pasta do projeto
- Execute: `python -m venv venv` novamente

## 📚 Próximos Passos

1. Explore o dashboard
2. Crie algumas reclamações
3. Teste os filtros
4. Acesse o admin: http://localhost:8000/admin

---

**Muito mais simples que Rails! 🎉**
