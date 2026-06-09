# BrightSpot IOT - MVP (GS 2026.1)

Solução de monitoramento ambiental com **Visão Computacional em tempo real** (webcam) e integração opcional com sensores do Arduino via serial.

## Informações

| Campo             | Valor                         |
| ----------------- | ----------------------------- |
| **Curso**         | Engenharia de Software        |
| **Disciplina**    | Physical Computing: IoT & IOB |
| **Professor(a)**  | Yan Gabriel Coelho            |
| **Turma**         | 3ESPX                         |
| **Instituição**   | FIAP                          |
| **Link do Video** |                               |

### Equipe

| Integrante                   | RM     |
| ---------------------------- | ------ |
| Augusto Barcelos Barros      | 565065 |
| Caio Felipe de Lima Bezerra  | 556197 |
| Juan Francisco Alves Muradas | 555541 |
| Lucas Derenze Simidu         | 555931 |
| Sofia Fernandes              | 554873 |

## Descrição da solução

O BrightSpot é uma solução modular de inteligência ambiental criada para apoiar decisões em
ambientes extremos, remotos, desconhecidos ou de difícil acesso. O ecossistema é inspirado na
exploração espacial e atua processando dados de telemetrias captadas por gadgets IoT.

O sistema é composto por:

- **Python + OpenCV/MediaPipe** para capturar vídeo da webcam e fazer inferência visual (presença, movimento e baixa luminosidade);
- **Arduino + sensores** para enviar leituras de temperatura, umidade, luminosidade (LDR) e distância;
- **Classificação de risco** em tempo real com base nos dados visuais e dos sensores.

## Bibliotecas utilizadas

### Python

- OpenCV (`opencv-python`)
- MediaPipe (`mediapipe`)
- NumPy (`numpy`)
- PySerial (`pyserial`)
- Pillow (`pillow`)

### Arduino

- `DHT`
- `ArduinoJson`
- `NewPing`

## Instruções de execução

### Passo 1: Preparando o Arduino (Opcional, para integração de sensores)

1. Suba o código localizado em `Arduino/src/main.cpp` para a sua placa.
2. Certifique-se de manter o monitor serial configurado para **115200 baud**.

### Passo 2: Preparando o ambiente Python

Abra o terminal e navegue até o diretório `Python`. Escolha uma das abordagens abaixo para configurar seu ambiente e instalar as dependências:

#### 🔹 Opção 1 — Usando `pip` (tradicional)

1. **Crie e ative um ambiente virtual:**

```sh
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

2. **Instale as dependências:**

```sh
pip install -r requirements.txt
```

#### 🔹 Opção 2 — Usando `uv` (recomendado)

1. **Instale o `uv` (se ainda não tiver):**

```sh
pip install uv
```

2. **Sincronize as dependências automaticamente:**

```sh
uv sync
```

> Isso cria e gerencia o ambiente virtual automaticamente, sem precisar rodar `venv` ou ativá-lo manualmente.

### Passo 3: Executando a aplicação

Com as dependências instaladas, você já pode rodar o projeto.

> **Atenção:** Se você utilizou o **`uv` (Opção 2)**, basta adicionar o prefixo `uv run` antes de cada comando abaixo (ex: `uv run python -m main`). Se utilizou o **`pip` (Opção 1)** com o ambiente ativado, rode os comandos como estão a seguir:

- **Apenas com webcam:**

```sh
python -m main
```

- **Com webcam + sensores (ajuste a porta conforme sua placa):**

```sh
python -m main --serial-port COM3
```

- **Para ver todas as opções disponíveis:**

```sh
python -m main --help
```
