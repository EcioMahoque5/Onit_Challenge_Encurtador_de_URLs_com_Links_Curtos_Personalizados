# Serviço de Encurtamento de URLs

Esta aplicação é uma API desenvolvida em Flask que permite o registro de utilizadores, autenticação, e encurtamento de URLs com suporte para links curtos personalizados e validação de domínio. A autenticação é segura, utilizando JWT e bcrypt para hash de senhas.

---

## Passos para Executar a Aplicação

1. **Criar um Ambiente Virtual**

   - No diretório do projeto, crie um ambiente virtual:
     ```bash
     python -m venv venv
     ```
   - Ative o ambiente virtual:
     - **Windows**:
       ```bash
       venv\Scripts\activate
       ```
     - **Linux/Mac**:
       ```bash
       source venv/bin/activate
       ```

2. **Criar o Ficheiro `.env`**

   - Na raiz do projeto, crie um ficheiro chamado `.env`.
   - Adicione as seguintes variáveis:
     ```env
     SECRET_KEY=sua_chave_secreta_aqui
     JWT_SECRET_KEY=sua_chave_secreta_para_jwt
     JWT_HEADER_NAME=x-token
     ```

3. **Instalar os Pacotes Necessários**

   - Certifique-se de que o ambiente virtual está ativado.
   - Instale os pacotes listados no ficheiro `requirements.txt`:
     ```bash
     pip install -r requirements.txt
     ```

4. **Executar a Aplicação**

   - No terminal, com o ambiente virtual ativado, execute o ficheiro principal:
     ```bash
     python main.py
     ```
   - A aplicação será iniciada no endereço padrão: `http://127.0.0.1:5000`.

---

## Endpoints Disponíveis

### 1. **Registo de Utilizador**

- **URL**: `/auth/register_user`
- **Método**: `POST`
- **Descrição**: Regista um novo utilizador com um nome de utilizador único e uma senha segura.
- **Cabeçalhos**:

  ```json
  Content-Type: application/json
  ```

- **Body (JSON)**:

```json
{
  "username": "john_doe",
  "password": "SenhaSegura@123"
}
```

### Requisitos da Password:

- Deve incluir pelo menos:
  - Uma letra maiúscula.
  - Uma letra minúscula.
  - Um número.
  - Um caracter especial (`!@#$%^&*`).
- Comprimento entre **8 e 32 caracteres**.

- **Resposta de Sucesso (201)**:

```json
{
  "success": true,
  "message": "Utilizador registado com sucesso!",
  "data": {
    "id": 1000,
    "username": "john_doe",
    "date_created": "2025-01-22 12:25:00"
  }
}
```

- **Resposta de Erro (400 - Erros de Validação)**:

```json
{
  "success": false,
  "message": "Validations errors",
  "errors": {
    "username": ["username already exists!"],
    "password": [
      "password must include at least one uppercase letter, one lowercase letter, one number, and one special character, and be between 8 and 32 characters long"
    ]
  }
}
```

### 2. **Login**

- **URL**: `/auth/login`
- **Método**: `POST`
- **Descrição**: Autentica o utilizador e retorna um token JWT.
- **Cabeçalho**:

  ```json
  Content-Type: application/json
  ```

  - **Body (JSON)**:

```json
{
  "username": "john_doe",
  "password": "SenhaSegura@123"
}
```

- **Resposta de Sucesso (200)**:

```json
{
  "success": true,
  "message": "Login successful!",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

- **Resposta de Erro (401 - Credenciais Inválidas)**:

```json
{
  "success": false,
  "message": "Invalid username or password!"
}
```

### 3. **Encurtar URL**

- **URL**: `/api/shorten`
- **Método**: `POST`
- **Autenticação**: JWT necessário
- **Descrição**: Encurta uma URL com a opção de criar um link curto personalizado e validar o domínio.
- **Cabeçalho**:

  ```json
  x-token: <JWT_TOKEN>
  Content-Type: application/json
  ```

- **Body (JSON)**:

```json
{
  "originalUrl": "https://exemplo.com",
  "customShortLink": "meuLinkPersonalizado",
  "domain": "short.ly"
}
```

- **Resposta de Sucesso (201)**:

```json
{
  "success": true,
  "short_Link": "meuLinkPersonalizado",
  "original_url": "https://exemplo.com",
  "domain": "short.ly"
}
```

- **Resposta de Erro (400 - Erros de Validação)**:

```json
{
  "success": false,
  "message": "Validation errors",
  "errors": {
    "domain": ["Invalid domain!"]
  }
}
```

- **Resposta de Erro (409 - Short link em uso)**:

```json
{
  "success": false,
  "message": "Custom short link is already taken!"
}
```

### 4. **Redirecionar para URL Original**

- **URL**: `/api/shorten/<shortLink>`
- **Método**: `GET`
- **Descrição**: Redireciona para a URL original associada ao link curto.
- **Resposta**: Redirecionamento HTTP 302.

### 5. **Visualizar Estatísticas**

- **URL**: `/api/stats/<shortLink>`
- **Método**: `GET`
- **Autenticação**: JWT necessário
- **Descrição**: Obtém estatísticas sobre um link curto específico.

- **Resposta de Sucesso (200)**:

```json
{
  "success": true,
  "original_url": "https://exemplo.com",
  "short_link": "meuLinkPersonalizado",
  "domain": "short.ly",
  "clicks": 25
}
```

- **Resposta de Erro (404 - Short link inexistente)**:

```json
{
  "success": false,
  "message": "Short link not found!"
}
```


## Estrutura do Projeto

. ├── app/
│ ├── init.py
│ ├── configs.py
│ ├── routes.py
│ └── validator.py
├── venv/
├── .env
├── main.py
├── requirements.txt
└── README.md



## Observações

Certifique-se de que o arquivo `.env` contém as variáveis:

- **`SECRET_KEY`**: Chave usada para segurança geral do Flask.
- **`JWT_SECRET_KEY`**: Chave secreta usada para gerar e validar tokens JWT.
- **`JWT_HEADER_NAME`**: Nome do cabeçalho personalizado usado para o token (padrão: `x-token`).

  - **Windows**:
    ```bash
    venv\Scripts\activate
    ```
  - **Linux/Mac**:
    ```bash
    source venv/bin/activate
    ```

---

## Demonstração

- **Local**: `http://127.0.0.1:5000/`
- **Hospedado**: