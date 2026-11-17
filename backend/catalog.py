# Catalog of Pre-set Categories, Roles, Skills, Shifts, and Contract Types

JOB_CATEGORIES = {
    "administracao": {
        "name": "Administração & Finanças",
        "icon": "fa-briefcase",
        "roles": [
            "Assistente Administrativo",
            "Auxiliar Administrativo",
            "Analista Administrativo",
            "Analista Financeiro",
            "Assistente Financeiro",
            "Auxiliar de Escritório",
            "Faturista",
            "Contador",
            "Assistente Contábil",
            "Recepcionista"
        ],
        "skills": [
            "Excel Avançado",
            "Contas a Pagar e Receber",
            "Fluxo de Caixa",
            "Emissão de Notas Fiscais",
            "Faturamento",
            "Sistemas ERP (SAP, Totvs)",
            "Rotinas Administrativas",
            "Conciliação Bancária",
            "Redação Empresarial",
            "Organização de Arquivos"
        ]
    },
    "rh": {
        "name": "Recursos Humanos & DP",
        "icon": "fa-users",
        "roles": [
            "Assistente de RH",
            "Auxiliar de Departamento Pessoal",
            "Analista de Recursos Humanos",
            "Analista de R&S (Recrutamento e Seleção)",
            "Analista de Departamento Pessoal",
            "Business Partner (BP)",
            "Coordenador de RH",
            "Estagiário de RH"
        ],
        "skills": [
            "Recrutamento e Seleção",
            "Folha de Pagamento",
            "Legislação Trabalhista (CLT)",
            "eSocial",
            "Controle de Ponto",
            "Benefícios e Admissão",
            "Treinamento e Desenvolvimento",
            "Entrevistas por Competência",
            "Clima Organizacional",
            "Gupy e Plataformas de Vagas"
        ]
    },
    "logistica": {
        "name": "Logística & Estoque",
        "icon": "fa-truck-fast",
        "roles": [
            "Auxiliar de Logística",
            "Assistente de Logística",
            "Operador de Empilhadeira",
            "Conferente de Mercadorias",
            "Estoquista",
            "Auxiliar de Expedição",
            "Analista de Logística",
            "Almoxarife",
            "Motorista Entregador",
            "Coordenador de Logística"
        ],
        "skills": [
            "Controle de Estoque",
            "Conferência e Expedição",
            "Sistemas WMS",
            "Roteirização de Entregas",
            "Operação de Empilhadeira (CNH)",
            "Inventário Cíclico",
            "Organização de Armazém",
            "Separação de Pedidos (Picking)",
            "Nota Fiscal de Transporte (CT-e)",
            "Gestão de Frotas"
        ]
    },
    "vendas_marketing": {
        "name": "Vendas, Atendimento & Marketing",
        "icon": "fa-chart-line",
        "roles": [
            "Vendedor Interno",
            "Vendedor Externo",
            "Operador de Telemarketing / SAC",
            "Atendente de Loja",
            "Representante Comercial",
            "Assistente de Marketing",
            "Analista de Marketing Digital",
            "Social Media",
            "SDR (Pré-vendas)",
            "Executivo de Contas (B2B)"
        ],
        "skills": [
            "Técnicas de Negociação",
            "Atendimento ao Cliente",
            "CRM (HubSpot, RD Station, Salesforce)",
            "Prospecção Ativa (Cold Call / Inbound)",
            "Metas e Indicadores de Vendas",
            "Marketing Digital e Redes Sociais",
            "Gestão de Tráfego Pago (Google Ads / Meta Ads)",
            "Comunicação Persuasiva",
            "Pós-Venda e Fidelização",
            "Elaboração de Propostas"
        ]
    },
    "tecnologia": {
        "name": "Tecnologia & Programação",
        "icon": "fa-laptop-code",
        "roles": [
            "Desenvolvedor Backend",
            "Desenvolvedor Frontend",
            "Desenvolvedor Full Stack",
            "Suporte Técnico / Helpdesk",
            "Analista de Dados",
            "Analista de QA (Testes)",
            "Engenheiro de DevOps",
            "Técnico de Informática",
            "UI/UX Designer",
            "Estagiário de TI"
        ],
        "skills": [
            "Python",
            "JavaScript",
            "SQL / Bancos de Dados",
            "HTML & CSS",
            "FastAPI / Django",
            "React / Vue",
            "Git & GitHub",
            "Docker",
            "Manutenção de Computadores",
            "Redes e Infraestrutura"
        ]
    },
    "operacional": {
        "name": "Serviços Gerais & Operacional",
        "icon": "fa-screwdriver-wrench",
        "roles": [
            "Auxiliar de Limpeza / ASG",
            "Porteiro / Controlador de Acesso",
            "Auxiliar de Produção",
            "Copeiro(a)",
            "Zelador",
            "Operador de Caixa",
            "Repositor de Mercadorias",
            "Vigilante / Segurança",
            "Cozinheiro / Auxiliar de Cozinha",
            "Montador"
        ],
        "skills": [
            "Pontualidade e Responsabilidade",
            "Atendimento ao Público",
            "Trabalho em Equipe",
            "Normas de Segurança do Trabalho",
            "Operação de Caixa (PDV)",
            "Organização e Higienização",
            "Controle de Acesso de Visitantes",
            "Linha de Produção Industrial",
            "Agilidade Manual",
            "Preparo e Manipulação de Alimentos"
        ]
    }
}

SHIFT_OPTIONS = [
    {"id": "integral", "name": "Integral (Comercial / 8h)", "keywords": ["integral", "comercial", "44h", "40h", "8h", "horário comercial"]},
    {"id": "manha", "name": "Manhã (Matutino)", "keywords": ["manhã", "matutino", "06:00", "07:00", "08:00"]},
    {"id": "tarde", "name": "Tarde (Vespertino)", "keywords": ["tarde", "vespertino", "13:00", "14:00"]},
    {"id": "noite", "name": "Noite (Noturno)", "keywords": ["noite", "noturno", "adicional noturno", "escala noturna"]},
    {"id": "escala", "name": "Escala 12x36 / 6x1", "keywords": ["12x36", "6x1", "escala", "turnos rotativos"]},
    {"id": "flexivel", "name": "Flexível", "keywords": ["flexível", "horário livre", "flexibilidade"]}
]

CONTRACT_OPTIONS = [
    {"id": "aprendiz", "name": "Menor Aprendiz / Jovem Aprendiz", "keywords": ["jovem aprendiz", "menor aprendiz", "aprendiz", "lei da aprendizagem"]},
    {"id": "estagio", "name": "Estágio", "keywords": ["estágio", "estagio", "estagiário", "estagiario", "estagiária", "bolsa auxílio"]},
    {"id": "clt", "name": "CLT (Efetivo)", "keywords": ["clt", "efetivo", "carteira assinada"]},
    {"id": "pj", "name": "PJ (Pessoa Jurídica)", "keywords": ["pj", "prestador de serviço", "prestador"]},
    {"id": "temporario", "name": "Temporário / Freelance", "keywords": ["temporário", "temporario", "freelance", "diária"]}
]

EXPERIENCE_LEVELS = [
    {"id": "aprendiz", "name": "Jovem / Menor Aprendiz", "keywords": ["aprendiz", "jovem aprendiz", "menor aprendiz"]},
    {"id": "estagio", "name": "Estágio", "keywords": ["estágio", "estagiário", "estagio"]},
    {"id": "junior", "name": "Júnior (Iniciante / Auxiliar / Assistente)", "keywords": ["júnior", "junior", "jr", "auxiliar", "assistente", "iniciante", "entry level"]},
    {"id": "pleno", "name": "Pleno (Intermediário / Analista)", "keywords": ["pleno", "pl", "analista"]},
    {"id": "senior", "name": "Sênior / Especialista / Coordenação", "keywords": ["sênior", "senior", "sr", "especialista", "coordenador", "gerente", "supervisor", "lead", "head"]}
]
