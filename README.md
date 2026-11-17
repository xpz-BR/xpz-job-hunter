# 🎯 Job-Hunter

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/Frontend-HTML%20%7C%20CSS%20%7C%20JS-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="Vanilla Frontend" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License" />
</p>

> **Job-Hunter** é um agregador e motor inteligente de busca de empregos que calcula em tempo real o **percentual de compatibilidade (%)** entre o seu perfil profissional (habilidades, nível de experiência e interesses) e as vagas disponíveis no mercado.

---

## ✨ Funcionalidades Principais

- 👤 **Perfil Dinâmico do Candidato:** Cadastre suas competências técnicas (hard skills), cargos de interesse, senioridade (estágio, júnior, pleno, sênior) e modalidade de trabalho (remoto/presencial).
- 🔍 **Rastreamento Multi-Fonte em Tempo Real:**
  - **JobSpy:** Rastreia vagas diretamente do **LinkedIn, Indeed e Glassdoor**.
  - **Remotive API:** Vagas remotas em tecnologia atualizadas globalmente.
  - **Arbeitnow API:** Oportunidades adicionais de tech e trabalho flexível.
- 📊 **Cálculo Inteligente de Compatibilidade (% Match):**
  - **Hard Skills (50%):** Analisa termos técnicos, variações e sinônimos (ex: *JS/JavaScript*, *Python/FastAPI*).
  - **Cargo / Título (30%):** Avalia a similaridade semântica entre o cargo almejado e a vaga.
  - **Senioridade & Modalidade (20%):** Bonifica oportunidades adequadas ao nível e preferências (ex: Home Office).
- 🎨 **Painel Visual Moderno & Responsivo:**
  - Barrinhas de compatibilidade coloridas (Verde para Super Match, Âmbar para Bom Match).
  - Destaque das tecnologias correspondentes vs. tecnologias pedidas que você ainda não tem.
- 💾 **Persistência Local com SQLite:**
  - Seus dados de perfil e suas **vagas salvas/favoritas** ficam salvas no SQLite local, sem necessidade de configurar servidores de banco de dados pesados.
- ⚡ **Zero Framework Overhead:** Frontend limpo e rápido construído em HTML5, CSS3 moderno e JavaScript puro.

---

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologia | Motivação |
|---|---|---|
| **Backend** | Python 3 + FastAPI | Alta performance assíncrona e documentação interativa automática |
| **Banco de Dados** | SQLite 3 | Leve, portátil e sem configurações complexas para quem clona o repositório |
| **Scraping / APIs** | `python-jobspy` & `requests` | Rastreia de forma agregada Indeed, LinkedIn e consome APIs abertas |
| **Frontend** | HTML5, CSS3 Moderno, JavaScript (ES6) | Interface dark mode polida, responsiva e rápida |

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- **Python 3.10** ou superior instalado.
- **Git** instalado.

### 1. Clonar o Repositório
```bash
git clone https://github.com/xpz-BR/xpz-job-hunter.git
cd xpz-job-hunter
```

### 2. Criar e Ativar o Ambiente Virtual
No Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

No Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar as Dependências
```bash
pip install -r backend/requirements.txt
```

### 4. Iniciar a Aplicação
```bash
python run.py
```

Acesse no seu navegador:
- 🌐 **Interface Web:** [http://localhost:8000](http://localhost:8000)
- 📖 **Swagger / Docs da API:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📁 Estrutura de Pastas

```text
Job-Hunter/
├── backend/
│   ├── app.py              # API FastAPI com rotas de perfil, busca e favoritos
│   ├── database.py         # Gerenciamento de tabelas e queries no SQLite
│   ├── matcher.py          # Algoritmo de cálculo de compatibilidade (%)
│   ├── scraper.py          # Integração JobSpy + Remotive + Fallbacks
│   └── requirements.txt    # Dependências do projeto
├── frontend/
│   ├── index.html          # Interface principal do usuário
│   ├── style.css           # Estilos modernos em tema escuro
│   └── app.js              # Lógica interativa de busca, perfil e favoritos
├── run.py                  # Script de inicialização facilitada
├── .gitignore              # Arquivos e diretórios ignorados pelo Git
└── README.md               # Documentação do projeto
```

---

## 🤝 Como Contribuir

Contribuições são super bem-vindas!
1. Faça um Fork do projeto.
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`).
3. Commit suas alterações (`git commit -m 'feat: adiciona nova funcionalidade'`).
4. Faça o push para a branch (`git push origin feature/nova-funcionalidade`).
5. Abra um **Pull Request**.

---

## 📝 Licença

Este projeto está sob a licença [MIT](LICENSE). Desenvolvido por [xpz-BR](https://github.com/xpz-BR).
