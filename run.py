import uvicorn
import os
import sys

if __name__ == "__main__":
    # Add root directory to python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    print("=" * 60)
    print("🎯 JOB-HUNTER — Motor de Busca de Vagas com Match IA/NLP")
    print("=" * 60)
    print("🚀 Servidor iniciado com sucesso!")
    print("👉 Abra seu navegador em: http://localhost:8000")
    print("📖 Documentação da API:    http://localhost:8000/docs")
    print("=" * 60)

    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
